from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from capability_pathways.profiles.institution import ContractError, Decision, DomainRecord, records_from_fixture, stable_hash
from capability_pathways.portfolio.path_store import PLAN_STATUSES, Repository
from capability_pathways.delivery.cohort_gates import advance_for_outcome, decide
from capability_pathways.measurement.outcome_report import export_bundle, verify_bundle
from capability_pathways.measurement.staged_comparison import (
    analytic_context,
    plan_inputs,
    recommend_expansions,
    staged_report,
)
from capability_pathways.planning.dependency_graph import derive_context
from capability_pathways.pathway_signal.pathway_feasibility import augment_context

class Application:
    def __init__(self, database: str | Path, context: Mapping[str, Any] | None = None):
        self.repository = Repository(database)
        self.context = dict(context or {})

    # -- ingestion / decisions -------------------------------------------------

    def ingest(self, record: DomainRecord) -> DomainRecord:
        current = self.repository.get_record(record.record_id)
        if current is None:
            self.repository.save_record(record)
            return record
        if current.fingerprint == record.fingerprint:
            return current
        replacement = DomainRecord(record.record_id, record.payload, current.state,
                                   current.version + 1, record.occurred_at, record.source)
        self.repository.save_record(replacement, expected_version=current.version)
        return replacement

    def process(self, record: DomainRecord) -> tuple[DomainRecord, Decision]:
        stored = self.ingest(record)
        context = dict(self.context)
        context.update(derive_context(stored, self.repository))
        context.update(augment_context(stored, self.repository))
        decision = decide(stored, context)
        self.repository.save_decision(decision)
        advanced = advance_for_outcome(stored, decision)
        if advanced.fingerprint != stored.fingerprint:
            self.repository.save_record(advanced, expected_version=stored.version)
        return advanced, decision

    # -- staged comparison -----------------------------------------------------

    def _settings(self, resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
        merged = dict(self.context)
        merged.update({key: value for key, value in (resources or {}).items() if value is not None})
        return analytic_context(merged)

    def compare(self, resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
        records = self.repository.list_records()
        if not records:
            raise ContractError("no records are available for comparison")
        comparison = staged_report(records, self._settings(resources))
        self.repository.save_comparison(comparison)
        return comparison

    def publish_plan(self, comparison: Mapping[str, Any],
                     resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
        plan = recommend_expansions(comparison, resources or {})
        self.repository.save_plan(plan)
        self.repository.mark_plans_stale(plan["input_fingerprint"])
        return self.repository.get_plan(plan["plan_id"]) or plan

    def refresh(self, resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
        resources = dict(self.repository.resources() if resources is None else resources)
        comparison = self.compare(resources)
        plan = self.publish_plan(comparison, resources)
        return {"comparison": comparison, "expansion_plan": plan,
                "stale_plans": [row["plan_id"] for row in self.repository.plan_rows("stale")]}

    def update_resources(self, updates: Mapping[str, Any]) -> dict[str, Any]:
        merged = self.repository.resources()
        merged.update({key: value for key, value in updates.items() if value is not None})
        self.repository.save_resources(merged)
        return self.refresh(merged)

    def correct_record(self, record_id: str, updates: Mapping[str, Any]) -> dict[str, Any]:
        current = self.repository.get_record(record_id)
        if current is None:
            raise ContractError(f"unknown record: {record_id}")
        corrected = current.with_payload(updates)
        self.repository.save_record(corrected, expected_version=current.version)
        # Re-run the profile decision so stored decisions match the corrected picture.
        context = dict(self.context)
        context.update(derive_context(corrected, self.repository))
        context.update(augment_context(corrected, self.repository))
        decision = decide(corrected, context)
        self.repository.save_decision(decision)
        # Every plan built on the old picture is out of date until it is rebuilt below.
        staleness = self.repository.mark_plans_stale(None)
        refreshed = self.refresh(self.repository.resources())
        refreshed["stale_plans"] = sorted(set(staleness) | set(refreshed["stale_plans"]))
        return refreshed | {"record_id": corrected.record_id, "version": corrected.version,
                            "payload": corrected.payload, "decision": decision.outcome}

    def _current_plan_inputs(self) -> str:
        resources = self.repository.resources()
        current = staged_report(self.repository.list_records(), self._settings(resources))
        return plan_inputs(current, resources)

    def plan_action(self, plan_id: str, status: str) -> dict[str, Any]:
        if status not in PLAN_STATUSES:
            raise ContractError(f"unsupported plan status: {status}")
        if self.repository.get_plan(plan_id) is None:
            raise ContractError(f"unknown expansion plan: {plan_id}")
        if status == "adopted":
            plan = self.repository.get_plan(plan_id)
            if plan is None:
                raise ContractError(f"unknown expansion plan: {plan_id}")
            current = self._current_plan_inputs()
            if plan["input_fingerprint"] != current:
                self.repository.mark_plans_stale(current)
                raise ContractError("expansion plan is out of date; refresh before adopting")
        plan = self.repository.set_plan_status(plan_id, status)
        if status == "adopted":
            self.repository.supersede_drafts(plan_id)
        return plan

    # -- fixture run -----------------------------------------------------------

    def run_fixture(self, fixture: Mapping[str, Any], output: str | Path,
                    resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
        records = records_from_fixture(fixture)
        fixture_hash = stable_hash({"fixture": fixture, "resources": resources or {}})
        run_id = self.repository.begin_run(fixture_hash, len(records))
        completed = self.repository.completed_run(run_id)
        if completed is not None:
            return completed
        decisions: dict[str, Decision] = {}
        final_records: list[DomainRecord] = []
        for record in records:
            final_record, decision = self.process(record)
            final_records.append(final_record)
            decisions[record.record_id] = decision
        stored_resources = self.repository.resources()
        active_resources = dict(stored_resources if resources is None else resources)
        if resources is not None:
            self.repository.save_resources(active_resources)
        comparison = self.compare(active_resources)
        plan = self.publish_plan(comparison, active_resources)
        snapshot = self.repository.snapshot()
        if snapshot["chain_errors"]:
            raise ContractError("audit chain verification failed")
        if self.repository.analysis_errors():
            raise ContractError("stored comparison or plan failed verification")
        manifest = export_bundle(output, final_records, decisions, snapshot, self.repository.event_rows(),
                                 comparison, plan)
        result = {"run_id": run_id, "fixture_hash": fixture_hash, "records": len(final_records),
                  "decisions": len(decisions), "manifest": manifest, "snapshot": snapshot,
                  "comparison": {"input_fingerprint": comparison["input_fingerprint"],
                                 "cohorts": comparison["cohorts"]},
                  "expansion_plan": {"plan_id": plan["plan_id"], "summary": plan["summary"],
                                     "resources": plan["resources"]}}
        self.repository.finish_run(run_id, result)
        return result

    def inspect(self) -> dict[str, Any]:
        return {"snapshot": self.repository.snapshot(),
                "records": [record.__dict__ for record in self.repository.list_records()],
                "decisions": self.repository.decision_rows(),
                "comparison": self.repository.latest_comparison(),
                "expansion_plans": self.repository.plan_rows(),
                "resources": self.repository.resources()}


def load_fixture(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read fixture: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("fixture root must be an object")
    return value


def run(fixture_path: str | Path, database: str | Path, output: str | Path,
        context: Mapping[str, Any] | None = None, resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return Application(database, context).run_fixture(load_fixture(fixture_path), output, resources)


def verify(database: str | Path, output: str | Path) -> dict[str, Any]:
    repository = Repository(database)
    chain_errors = repository.verify_chain()
    bundle_errors = verify_bundle(output)
    analysis_errors = repository.analysis_errors()
    return {"ok": not chain_errors and not bundle_errors and not analysis_errors,
            "chain_errors": chain_errors, "bundle_errors": bundle_errors,
            "analysis_errors": analysis_errors, "snapshot": repository.snapshot()}
