from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from capability_pathways.measurement.staged_comparison import (
    LEVEL_DIRECTIONAL,
    LEVEL_EFFECT,
    LEVEL_INSUFFICIENT,
    LEVEL_NOT_APPLICABLE,
    STAGE_AWAITING,
    STAGE_CLOSED,
    STAGE_COMPLETED,
    institution_comparison,
    recommend_expansions,
    stage_of,
    staged_report,
)
from capability_pathways.profiles.institution import ContractError, records_from_fixture
from capability_pathways.portfolio.path_store import Repository
from capability_pathways.programme_office import Application


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "staged_expansion.json"


def load_records():
    return records_from_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))


def placement(record_id: str, baseline: float, outcome: float, **updates):
    payload = {
        "institution_id": record_id,
        "country_group": "g",
        "capability_track": "track-foundation",
        "staff_count": 20,
        "staff_hours": 400,
        "baseline_level": baseline,
        "target_level": outcome,
        "profile_missing_rate": 0.1,
        "mentor_capacity": 0.6,
        "compute_access": 0.6,
        "language_support": "zh",
        "participation_consent": 0.9,
        "completion_status": "completed",
        "activated_at": "2026-01-01T00:00:00+00:00",
        "measured_at": "2026-06-01T00:00:00+00:00",
        "attrition_rate": 0.1,
    }
    payload.update(updates)
    return payload


def record(record_id: str, lane: list[dict], **updates):
    records = records_from_fixture({"records": [{"record_id": item.pop("record_id"), "payload": item}
                                                for item in lane]})
    for item in records:
        if item.record_id == record_id:
            return item
    raise AssertionError("record not found")


class StageClassificationTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()

    def test_stage_comes_from_evidence_not_workflow_state(self):
        completed = next(item for item in self.records if item.record_id == "stage-cohort-a-01")
        awaiting = next(item for item in self.records if item.record_id == "stage-cohort-b-01")
        self.assertEqual(stage_of(completed), STAGE_COMPLETED)
        self.assertEqual(stage_of(awaiting), STAGE_AWAITING)
        # The decision engine moves records to archived; that must not be read as withdrawal.
        terminated = completed.with_state("archived")
        self.assertEqual(stage_of(terminated), STAGE_COMPLETED)

    def test_withdrawal_is_closed(self):
        closed = next(item for item in self.records if item.record_id == "stage-cohort-c-03")
        self.assertEqual(stage_of(closed), STAGE_CLOSED)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        records = []
        records.append(placement("base-01", 40.0, 45.0))
        records.append(placement("base-02", 41.0, 45.5))
        records.append(placement("base-03", 39.5, 44.0))
        records.append(placement("target", 40.5, 46.0))
        records.append(placement("waiting", 41.0, 60.0, completion_status="awaiting", staff_hours=0))
        self.records = records_from_fixture({"records": [
            {"record_id": item.pop("institution_id"), "payload": item} for item in records]})
        self.by_id = {item.record_id: item for item in self.records}

    def test_waiting_institutions_never_get_effect_estimates(self):
        row = institution_comparison(self.by_id["waiting"], self.records)
        self.assertEqual(row["stage"], STAGE_AWAITING)
        self.assertEqual(row["conclusion"]["level"], LEVEL_NOT_APPLICABLE)
        self.assertIsNone(row["estimate"])
        self.assertEqual(row["starting_level"]["outcome"], None)
        self.assertIsNone(row["observation_window"]["days"])

    def test_awaiting_records_are_never_comparators(self):
        report = staged_report(self.records)
        for row in report["records"]:
            self.assertNotIn("waiting", row["comparable_group"]["record_ids"])
        self.assertEqual(report["cohorts"]["awaiting_used_as_outcome_comparator"], 0)

    def test_comparable_group_respects_baseline_band(self):
        far = records_from_fixture({"records": [
            {"record_id": "far", "payload": placement("far", 80.0, 90.0)},
            {"record_id": "target", "payload": placement("target", 40.0, 48.0)},
            {"record_id": "near", "payload": placement("near", 41.0, 44.0)},
        ]})
        row = institution_comparison(far[1], far)
        self.assertEqual(row["comparable_group"]["record_ids"], ["near"])
        self.assertTrue(any(item["reason"] == "baseline_out_of_band" for item in row["comparable_group"]["excluded"]))
        self.assertIn(row["conclusion"]["level"], {LEVEL_DIRECTIONAL, LEVEL_INSUFFICIENT})

    def test_same_institution_versions_are_not_comparators(self):
        target = self.by_id["target"]
        sibling_payload = placement("target", 40.5, 42.0)
        sibling_payload["institution_id"] = target.record_id
        sibling = records_from_fixture({"records": [{"record_id": "sibling", "payload": sibling_payload}]})[0]
        rows = institution_comparison(target, self.records + [sibling])
        self.assertNotIn("sibling", rows["comparable_group"]["record_ids"])
        self.assertTrue(any(item["reason"] == "same_institution" for item in rows["comparable_group"]["excluded"]))

    def test_effect_level_requires_a_full_group_and_window(self):
        row = institution_comparison(self.by_id["target"], self.records)
        self.assertEqual(row["conclusion"]["level"], LEVEL_EFFECT)
        self.assertEqual(row["observation_window"]["status"], "observed")
        self.assertGreaterEqual(row["comparable_group"]["size"], 2)
        self.assertIn("效果证据", row["conclusion"]["statement"])
        self.assertIn("观察窗口", row["conclusion"]["statement"])
        self.assertIn("缺失率", row["conclusion"]["statement"])

    def test_thin_group_narrows_to_directional(self):
        lane = records_from_fixture({"records": [
            {"record_id": "only", "payload": placement("only", 40.0, 44.0)},
            {"record_id": "target", "payload": placement("target", 40.2, 46.0)},
        ]})
        row = institution_comparison(lane[1], lane)
        self.assertEqual(row["conclusion"]["level"], LEVEL_DIRECTIONAL)
        self.assertTrue(any("少于" in caveat for caveat in row["conclusion"]["caveats"]))
        self.assertIn("方向性判断", row["conclusion"]["statement"])

    def test_missing_window_downgrades_evidence(self):
        lane = records_from_fixture({"records": [
            {"record_id": "a", "payload": placement("a", 40.0, 45.0)},
            {"record_id": "b", "payload": placement("b", 41.0, 45.0)},
            {"record_id": "target", "payload": placement("target", 40.2, 46.0, measured_at=None)},
        ]})
        row = institution_comparison(lane[2], lane)
        self.assertNotEqual(row["conclusion"]["level"], LEVEL_EFFECT)
        self.assertEqual(row["observation_window"]["status"], "partial")
        self.assertTrue(any("观察窗口" in caveat for caveat in row["conclusion"]["caveats"]))

    def test_high_attrition_downgrades_evidence(self):
        lane = records_from_fixture({"records": [
            {"record_id": "a", "payload": placement("a", 40.0, 45.0)},
            {"record_id": "b", "payload": placement("b", 41.0, 45.0)},
            {"record_id": "target", "payload": placement("target", 40.2, 46.0, attrition_rate=0.9)},
        ]})
        row = institution_comparison(lane[2], lane)
        self.assertNotEqual(row["conclusion"]["level"], LEVEL_EFFECT)
        self.assertIn(row["missing_scope"]["attrition_rate"], (0.9, 1.0))

    def test_missing_baseline_cannot_be_backfilled(self):
        lane = records_from_fixture({"records": [
            {"record_id": "a", "payload": placement("a", 40.0, 45.0)},
            {"record_id": "target", "payload": placement("target", 40.0, 46.0, baseline_level=None)},
        ]})
        row = institution_comparison(lane[1], lane)
        self.assertEqual(row["conclusion"]["level"], LEVEL_INSUFFICIENT)
        self.assertIsNone(row["estimate"])
        self.assertIn("数据不足", row["conclusion"]["statement"])

    def test_high_missing_rate_is_bounded_not_filled(self):
        lane = records_from_fixture({"records": [
            {"record_id": "a", "payload": placement("a", 40.0, 45.0)},
            {"record_id": "b", "payload": placement("b", 41.0, 45.0)},
            {"record_id": "target", "payload": placement("target", 40.2, 46.0, profile_missing_rate=0.95)},
        ]})
        row = institution_comparison(lane[2], lane)
        self.assertEqual(row["conclusion"]["level"], LEVEL_INSUFFICIENT)
        self.assertIsNone(row["estimate"])
        self.assertIn("缺失率", row["conclusion"]["statement"])


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()
        self.report = staged_report(self.records)
        self.by_id = {row["record_id"]: row for row in self.report["records"]}

    def test_effect_backed_institutions_outrank_readiness_only(self):
        plan = recommend_expansions(self.report, {"expansion_slots": 4})
        selected = [item["record_id"] for item in plan["selected"]]
        self.assertTrue(selected)
        self.assertTrue(all(item["basis"] != "readiness_only" for item in plan["selected"][:1]))
        readiness = [item for item in plan["deferred"] + plan["selected"] if item["basis"] == "readiness_only"]
        self.assertTrue(all(item["conditional"] for item in readiness))
        self.assertTrue(all(item["evidence_level"] == LEVEL_NOT_APPLICABLE for item in readiness))

    def test_insufficient_and_closed_are_not_selected(self):
        plan = recommend_expansions(self.report, {"expansion_slots": 20})
        chosen = {item["record_id"] for item in plan["selected"]}
        self.assertNotIn("stage-cohort-c-02", chosen)
        self.assertNotIn("stage-cohort-c-03", chosen)
        directional = next(item for item in plan["selected"] if item["record_id"] == "stage-cohort-c-01")
        self.assertEqual(directional["evidence_level"], LEVEL_DIRECTIONAL)
        self.assertTrue(directional["conditional"])

    def test_tight_resources_leave_slots_unfilled_instead_of_promoting_noise(self):
        plan = recommend_expansions(self.report, {"expansion_slots": 10,
                                                  "mentor_capacity_floor": 0.95,
                                                  "compute_access_floor": 0.95})
        self.assertEqual(plan["selected"], [])
        self.assertEqual(plan["unfilled_slots"], 10)
        self.assertTrue(all(item["excluded"] for item in plan["excluded"]))

    def test_selected_are_ranked_and_deterministic(self):
        first = recommend_expansions(self.report, {"expansion_slots": 3})
        second = recommend_expansions(self.report, {"expansion_slots": 3})
        self.assertEqual(first["plan_id"], second["plan_id"])
        scores = [item["score"] for item in first["selected"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_plan_states_task_limits(self):
        plan = recommend_expansions(self.report, {"expansion_slots": 20,
                                                  "mentor_capacity_floor": 0.95,
                                                  "compute_access_floor": 0.95})
        self.assertTrue(any("名额保持空缺" in caveat for caveat in plan["summary"]["caveats"]))
        report = staged_report([record for record in self.records if stage_of(record) == STAGE_AWAITING])
        readiness = recommend_expansions(report, {"expansion_slots": 1})
        self.assertTrue(any("无完整效果证据" in caveat for caveat in readiness["summary"]["caveats"]))

    def test_plan_carries_evidence_context(self):
        plan = recommend_expansions(self.report, {"expansion_slots": 1})
        item = plan["selected"][0]
        for key in ("starting_level", "observation_window", "comparable_group_size", "missing_scope",
                    "conclusion", "basis"):
            self.assertIn(key, item)
        self.assertIn("effect", item["basis"] + item["evidence_level"])


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "state.sqlite3"
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def application(self, **kwargs):
        application = Application(self.database, **kwargs)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", kwargs.pop("resources", None)
                                if kwargs else None)
        return application

    def test_run_persists_comparison_and_plan(self):
        application = Application(self.database)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", {"expansion_slots": 2})
        snapshot = application.repository.snapshot()
        self.assertEqual(snapshot["counts"]["comparisons"], 1)
        self.assertEqual(snapshot["counts"]["expansion_plans"], 1)
        self.assertEqual(snapshot["plan_states"], {"draft": 1})
        self.assertEqual(snapshot["chain_errors"], [])

    def test_resource_change_refreshes_and_stales_pending_plan(self):
        application = Application(self.database)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", {"expansion_slots": 3})
        old_plan = application.repository.plan_rows()[-1]
        result = application.update_resources({"expansion_slots": 1})
        self.assertIn(old_plan["plan_id"], result["stale_plans"])
        plans = {item["plan_id"]: item["status"] for item in application.repository.plan_rows()}
        self.assertEqual(plans[old_plan["plan_id"]], "stale")
        self.assertEqual(result["expansion_plan"]["slots"], 1)
        self.assertEqual(plans[result["expansion_plan"]["plan_id"]], "draft")

    def test_stale_plan_cannot_be_adopted(self):
        application = Application(self.database)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", {"expansion_slots": 3})
        old_plan = application.repository.plan_rows()[-1]
        application.update_resources({"expansion_slots": 1})
        with self.assertRaisesRegex(ContractError, "out of date"):
            application.plan_action(old_plan["plan_id"], "adopted")

    def test_current_plan_can_be_adopted_once(self):
        application = Application(self.database)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", {"expansion_slots": 2})
        plan = application.repository.plan_rows()[-1]
        adopted = application.plan_action(plan["plan_id"], "adopted")
        self.assertEqual(adopted["status"], "adopted")
        with self.assertRaisesRegex(ContractError, "only a current draft"):
            application.plan_action(plan["plan_id"], "adopted")

    def test_adopting_one_plan_supersedes_other_drafts(self):
        application = Application(self.database)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", {"expansion_slots": 3})
        first = application.repository.plan_rows()[-1]
        application.plan_action(first["plan_id"], "adopted")
        second = application.update_resources({"expansion_slots": 2})["expansion_plan"]
        application.plan_action(second["plan_id"], "adopted")
        statuses = {item["plan_id"]: item["status"] for item in application.repository.plan_rows()}
        self.assertEqual(statuses[first["plan_id"]], "superseded")
        self.assertEqual(statuses[second["plan_id"]], "adopted")

    def test_correcting_profile_refreshes_unfinished_judgement(self):
        application = Application(self.database)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", {"expansion_slots": 2})
        before = application.repository.plan_rows()[-1]
        before_ids = [item["record_id"] for item in before["selected"]]
        before_version = application.repository.get_record("stage-cohort-a-01").version
        result = application.correct_record("stage-cohort-a-01",
                                            {"baseline_level": 95.0, "target_level": 96.0})
        after = result["expansion_plan"]
        self.assertEqual(after["status"], "draft")
        self.assertNotEqual(before["plan_id"], after["plan_id"])
        self.assertIn(before["plan_id"], result["stale_plans"])
        self.assertNotEqual(before_ids, [item["record_id"] for item in after["selected"]])
        corrected = application.repository.get_record("stage-cohort-a-01")
        self.assertGreater(corrected.version, before_version)
        self.assertEqual(corrected.payload["baseline_level"], 95.0)
        self.assertEqual(application.repository.snapshot()["chain_errors"], [])

    def test_repeated_analysis_is_idempotent(self):
        application = Application(self.database)
        application.run_fixture(self.fixture, Path(self.temp.name) / "out", {"expansion_slots": 2})
        first = application.compare()
        second = application.compare()
        self.assertEqual(first["input_fingerprint"], second["input_fingerprint"])
        self.assertEqual(application.repository.snapshot()["counts"]["comparisons"], 1)


class IsolationTests(unittest.TestCase):
    def test_other_institutions_are_not_used_as_outcomes(self):
        records = load_records()
        target = next(item for item in records if item.record_id == "stage-cohort-c-02")
        row = institution_comparison(target, records)
        self.assertEqual(row["comparable_group"]["size"], 0)
        self.assertIsNone(row["estimate"])
        self.assertEqual(row["conclusion"]["level"], LEVEL_INSUFFICIENT)
        self.assertIn("未使用其他机构观测补齐", row["conclusion"]["statement"])


if __name__ == "__main__":
    unittest.main()
