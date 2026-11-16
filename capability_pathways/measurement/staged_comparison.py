from __future__ import annotations

import math
import statistics
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from capability_pathways.pathway_signal.pathway_feasibility import pathway_feasibility
from capability_pathways.planning.dependency_graph import adjusted_effect
from capability_pathways.profiles.institution import (
    ContractError,
    DomainRecord,
    bounded,
    normalized_text,
    require_fields,
    stable_hash,
)


STAGE_COMPLETED = "completed"
STAGE_AWAITING = "awaiting"
STAGE_CLOSED = "closed"

LEVEL_EFFECT = "effect"
LEVEL_DIRECTIONAL = "directional"
LEVEL_INSUFFICIENT = "insufficient"
LEVEL_NOT_APPLICABLE = "not_applicable"

_LEVEL_RANK = {LEVEL_INSUFFICIENT: 0, LEVEL_DIRECTIONAL: 1, LEVEL_EFFECT: 2}
_STAGE_LABELS = {STAGE_COMPLETED: "已完成培训", STAGE_AWAITING: "等待/在培", STAGE_CLOSED: "已退出"}

_ANALYTIC_KEYS = (
    "as_of",
    "baseline_band",
    "min_comparable",
    "missing_ceiling",
    "attrition_ceiling",
)

_DEFAULTS: dict[str, Any] = {
    "as_of": None,
    "baseline_band": 0.20,
    "min_comparable": 2,
    "missing_ceiling": 0.35,
    "attrition_ceiling": 0.30,
    "expansion_slots": 1,
    "mentor_capacity_floor": 0.0,
    "compute_access_floor": 0.0,
    "allow_readiness_only": True,
}


def _setting(context: Mapping[str, Any] | None, key: str) -> Any:
    value = (context or {}).get(key, _DEFAULTS[key])
    return _DEFAULTS[key] if value is None else value


def _optional_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _parse_time(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def stage_of(record: DomainRecord) -> str:
    """Derive the observed programme stage from evidence, not from the decision workflow state.

    The workflow state is advanced by the internal decision engine and cannot be used as
    evidence that an institution finished training.  Only explicit status fields or
    measurement/withdrawal evidence are trusted.
    """
    declared = normalized_text(record.payload.get("completion_status") or record.payload.get("cohort_status"))
    if declared in {"completed", "complete", "finished", "measured", "done", "graduated"}:
        return STAGE_COMPLETED
    if declared in {"awaiting", "waiting", "queued", "upcoming", "planned", "enrolled"}:
        return STAGE_AWAITING
    if declared in {"closed", "withdrawn", "dropped", "exited", "archived"}:
        return STAGE_CLOSED
    if record.payload.get("measured_at") or record.payload.get("observed_at"):
        return STAGE_COMPLETED
    attrition = _optional_number(record.payload.get("attrition_rate"))
    if attrition is not None and attrition >= 1.0:
        return STAGE_CLOSED
    if record.payload.get("withdrawn_at") or record.payload.get("withdrawal_reason"):
        return STAGE_CLOSED
    return STAGE_AWAITING


def baseline_level(record: DomainRecord) -> float | None:
    value = _optional_number(record.payload.get("baseline_level"))
    return value if value is not None and value > 0 else None


def outcome_level(record: DomainRecord) -> float | None:
    value = _optional_number(record.payload.get("target_level"))
    return value if value is not None and value > 0 else None


def observation_window(record: DomainRecord, stage: str, as_of: Any = None) -> dict[str, Any]:
    start_raw = (record.payload.get("activated_at") or record.payload.get("enrolled_at")
                 or record.payload.get("started_at") or record.payload.get("queued_at"))
    end_raw = record.payload.get("measured_at") or record.payload.get("observed_at")
    start, end, as_of_time = _parse_time(start_raw), _parse_time(end_raw), _parse_time(as_of)
    result: dict[str, Any] = {"start": str(start_raw) if start_raw else None,
                              "end": str(end_raw) if end_raw else None,
                              "days": None, "status": "unknown", "source": "none"}
    if stage == STAGE_COMPLETED:
        if start is not None and end is not None:
            days = (end - start).total_seconds() / 86400.0
            result.update(end=str(end_raw), days=days,
                          status="observed" if days >= 0 else "invalid",
                          source="payload.activated_at+payload.measured_at")
        elif end is not None:
            result.update(end=str(end_raw), status="partial", source="payload.measured_at_only")
        elif start is not None:
            # Training started but the outcome has no measured timestamp: the window cannot be verified.
            result.update(status="partial", source="payload.activated_at_only")
        return result
    if stage == STAGE_AWAITING:
        result["status"] = "open" if start is not None else "not_started"
        result["source"] = "payload.activated_at" if start is not None else "none"
        if start is not None and as_of_time is not None:
            result["days"] = max(0.0, (as_of_time - start).total_seconds() / 86400.0)
            result["source"] = "payload.activated_at+as_of"
        return result
    result["status"] = "closed"
    if start is not None:
        result["source"] = "payload.activated_at"
    return result


def attrition_of(record: DomainRecord, stage: str) -> dict[str, Any]:
    if stage == STAGE_CLOSED:
        return {"rate": 1.0, "source": "closed_state"}
    raw = _optional_number(record.payload.get("attrition_rate"))
    if raw is not None:
        return {"rate": bounded(raw), "source": "payload.attrition_rate"}
    staff = _optional_number(record.payload.get("staff_count"))
    remaining = _optional_number(record.payload.get("staff_remaining"))
    if staff is not None and remaining is not None and staff > 0:
        return {"rate": bounded(1.0 - remaining / staff), "source": "staff_count-staff_remaining"}
    return {"rate": None, "source": "unknown"}


def _comparable_candidates(target: DomainRecord, records: Iterable[DomainRecord], band: float
                           ) -> tuple[list[DomainRecord], list[DomainRecord], list[dict[str, Any]], int]:
    target_baseline = baseline_level(target)
    target_track = normalized_text(target.payload.get("capability_track"))
    target_institution = normalized_text(target.payload.get("institution_id", target.record_id))
    matched: list[DomainRecord] = []
    excluded: list[dict[str, Any]] = []
    considered = 0
    for candidate in records:
        if candidate.record_id == target.record_id:
            continue
        candidate_institution = normalized_text(candidate.payload.get("institution_id", candidate.record_id))
        if candidate_institution == target_institution:
            excluded.append({"record_id": candidate.record_id, "reason": "same_institution"})
            continue
        if stage_of(candidate) != STAGE_COMPLETED:
            excluded.append({"record_id": candidate.record_id, "reason": "not_completed"})
            continue
        considered += 1
        candidate_baseline = baseline_level(candidate)
        if candidate_baseline is None or outcome_level(candidate) is None:
            excluded.append({"record_id": candidate.record_id, "reason": "missing_baseline_or_outcome"})
            continue
        if target_baseline is None:
            continue
        tolerance = max(1.0, abs(target_baseline) * band)
        if abs(candidate_baseline - target_baseline) > tolerance:
            excluded.append({"record_id": candidate.record_id, "reason": "baseline_out_of_band"})
            continue
        matched.append(candidate)
    same_track = [candidate for candidate in matched
                  if normalized_text(candidate.payload.get("capability_track")) == target_track]
    return matched, same_track, excluded, considered


def _missing_scope(target: DomainRecord, group: list[DomainRecord], as_of: Any) -> dict[str, Any]:
    missing_fields = require_fields(target)
    target_rate = _optional_number(target.payload.get("profile_missing_rate"))
    group_rates = [rate for rate in (_optional_number(item.payload.get("profile_missing_rate")) for item in group)
                   if rate is not None]
    rates = list(group_rates) + ([target_rate] if target_rate is not None else [])
    missing_window = sum(observation_window(item, stage_of(item), as_of)["status"] != "observed"
                         for item in group)
    missing_attrition = sum(attrition_of(item, stage_of(item))["rate"] is None for item in group)
    if target_rate is None and not group_rates:
        scope = "unknown"
    elif not group:
        scope = "target_only"
    elif target_rate is None or len(group_rates) < len(group) or missing_fields:
        scope = "partial"
    else:
        scope = "complete"
    return {
        "target_missing_rate": target_rate,
        "required_fields_missing": missing_fields,
        "comparable_missing_range": [min(rates), max(rates)] if rates else None,
        "missing_window_count": missing_window,
        "missing_attrition_count": missing_attrition,
        "scope": scope,
    }


def _cap(level: str, ceiling: str) -> str:
    return level if _LEVEL_RANK[level] <= _LEVEL_RANK[ceiling] else ceiling


def _estimate(target: DomainRecord, group: list[DomainRecord], min_comparable: int) -> dict[str, Any] | None:
    if not group:
        return None
    target_effect = adjusted_effect(target)
    group_effects = [adjusted_effect(item) for item in group]
    comparator_mean = statistics.fmean(item["adjusted"] for item in group_effects)
    difference = target_effect["adjusted"] - comparator_mean
    group_spread = statistics.pstdev([item["adjusted"] for item in group_effects]) if len(group) > 1 else 0.12
    small_group_penalty = 0.10 if len(group) < min_comparable else 0.0
    half_width = ((1.0 - target_effect["reliability"]) * 0.12
                  + group_spread / math.sqrt(max(1, len(group))) + small_group_penalty)
    return {
        "target_observed_gain": target_effect["observed"],
        "target_adjusted_gain": target_effect["adjusted"],
        "target_reliability": target_effect["reliability"],
        "comparator_adjusted_gain": comparator_mean,
        "comparator_dispersion": group_spread,
        "difference": difference,
        "interval": [difference - half_width, difference + half_width],
    }


def _statement(stage: str, level: str, baseline: float | None, window: Mapping[str, Any],
               group: list[DomainRecord], track_matched: bool, scope: Mapping[str, Any],
               estimate: Mapping[str, Any] | None, caveats: list[str]) -> str:
    baseline_text = f"{baseline:.2f}" if baseline is not None else "未知"
    if stage == STAGE_AWAITING:
        return (f"起始水平 {baseline_text}；尚无结果观测，观察窗口状态为 {window['status']}；"
                f"不能把目标值当作已实现效果，也不能与已完成机构直接比较；"
                f"缺失率 {scope['target_missing_rate'] if scope['target_missing_rate'] is not None else '未报告'}。")
    if stage == STAGE_CLOSED:
        return f"机构已退出，起始水平 {baseline_text}；退出本身属于流失，不能用于估计培训效果。"
    if level == LEVEL_INSUFFICIENT:
        missing = scope["target_missing_rate"]
        missing_text = f"{missing:.2f}" if missing is not None else "未报告"
        return (f"数据不足：起始水平 {baseline_text}，可比组 {len(group)} 家，"
                f"观察窗口 {window['status']}，缺失率 {missing_text}；"
                f"未形成效果结论，未使用其他机构观测补齐。")
    if estimate is None:
        return f"数据不足：起始水平 {baseline_text}，尚未形成可用估计。"
    low, high = estimate["interval"]
    group_text = "同能力轨道" if track_matched else "跨轨道"
    prefix = "效果证据" if level == LEVEL_EFFECT else "方向性判断"
    caveat_text = f"；限制：{'；'.join(caveats)}" if caveats else ""
    missing_text = (f"{scope['comparable_missing_range'][0]:.2f}–{scope['comparable_missing_range'][1]:.2f}"
                    if scope["comparable_missing_range"] else "未报告")
    window_text = (f"{window['days']:.0f} 天（{window['start']}→{window['end']}）"
                   if window["days"] is not None else f"{window['status']}（{window['start']}→{window['end']}）")
    return (f"{prefix}：起始水平 {baseline_text}；观察窗口 {window_text}；"
            f"可比组 {len(group)} 家（{group_text}）；"
            f"缺失率范围 {missing_text}；校正后差异 {estimate['difference']:+.3f}"
            f"（{low:+.3f}~{high:+.3f}）{caveat_text}。")


def _conclusion(record: DomainRecord, stage: str, window: Mapping[str, Any], group: list[DomainRecord],
                same_track: list[DomainRecord], track_matched: bool, scope: Mapping[str, Any],
                attrition: Mapping[str, Any], estimate: Mapping[str, Any] | None,
                context: Mapping[str, Any] | None) -> dict[str, Any]:
    min_comparable = int(_setting(context, "min_comparable"))
    missing_ceiling = float(_setting(context, "missing_ceiling"))
    attrition_ceiling = float(_setting(context, "attrition_ceiling"))
    caveats: list[str] = []
    if stage == STAGE_AWAITING:
        level = LEVEL_NOT_APPLICABLE
        caveats.append("等待资源或仍在培训，尚无结果观测")
    elif stage == STAGE_CLOSED:
        level = LEVEL_INSUFFICIENT
        caveats.append("机构已退出，结果受流失影响")
    else:
        level = LEVEL_EFFECT
        target_missing = scope["target_missing_rate"]
        if baseline_level(record) is None or outcome_level(record) is None:
            level = LEVEL_INSUFFICIENT
            caveats.append("起始水平或结果水平缺失")
        elif not group:
            level = LEVEL_INSUFFICIENT
            caveats.append("没有已完成的基线可比机构")
        elif len(group) < min_comparable:
            level = _cap(level, LEVEL_DIRECTIONAL)
            caveats.append(f"可比组仅 {len(group)} 家，少于 {min_comparable} 家")
        if window["status"] != "observed":
            level = _cap(level, LEVEL_DIRECTIONAL)
            caveats.append(f"观察窗口不可核验（{window['status']}）")
        if len(same_track) < len(group):
            caveats.append("可比组包含不同能力轨道机构")
        if target_missing is None:
            level = _cap(level, LEVEL_DIRECTIONAL)
            caveats.append("缺失率未报告")
        elif target_missing > missing_ceiling:
            level = _cap(level, LEVEL_INSUFFICIENT if target_missing > min(0.9, missing_ceiling * 2) else LEVEL_DIRECTIONAL)
            caveats.append(f"缺失率 {target_missing:.2f} 超过阈值 {missing_ceiling:.2f}")
        if attrition["rate"] is None:
            level = _cap(level, LEVEL_DIRECTIONAL)
            caveats.append("流失率未报告")
        elif attrition["rate"] > attrition_ceiling:
            level = _cap(level, LEVEL_DIRECTIONAL)
            caveats.append(f"流失率 {attrition['rate']:.2f} 超过阈值 {attrition_ceiling:.2f}")
        if scope["missing_window_count"]:
            level = _cap(level, LEVEL_DIRECTIONAL)
            caveats.append(f"可比组 {scope['missing_window_count']} 家观察窗口缺失")
        if scope["missing_attrition_count"]:
            level = _cap(level, LEVEL_DIRECTIONAL)
            caveats.append(f"可比组 {scope['missing_attrition_count']} 家流失率缺失")
        if level != LEVEL_EFFECT:
            estimate = None if level == LEVEL_INSUFFICIENT else estimate
    statement = _statement(stage, level, baseline_level(record), window, group, track_matched, scope,
                           estimate, caveats)
    return {"level": level, "statement": statement, "caveats": caveats}


def institution_comparison(record: DomainRecord, records: Iterable[DomainRecord],
                           context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    records = list(records)
    stage = stage_of(record)
    band = float(_setting(context, "baseline_band"))
    min_comparable = int(_setting(context, "min_comparable"))
    as_of = _setting(context, "as_of")
    window = observation_window(record, stage, as_of)
    attrition = attrition_of(record, stage)
    if stage == STAGE_COMPLETED:
        matched, same_track, excluded, considered = _comparable_candidates(record, records, band)
        group = same_track if len(same_track) >= min_comparable else matched
        track_matched = len(same_track) >= min_comparable
    else:
        matched, same_track, excluded, considered = [], [], [], 0
        group, track_matched = [], False
    scope = _missing_scope(record, group, as_of)
    estimate = _estimate(record, group, min_comparable) if stage == STAGE_COMPLETED else None
    readiness = {"pathway_feasibility": pathway_feasibility(record.payload).score,
                 "mentor_capacity": _optional_number(record.payload.get("mentor_capacity")),
                 "compute_access": _optional_number(record.payload.get("compute_access"))}
    conclusion = _conclusion(record, stage, window, group, same_track, track_matched, scope, attrition,
                             estimate, context)
    if conclusion["level"] == LEVEL_INSUFFICIENT:
        estimate = None
    return {
        "record_id": record.record_id,
        "institution_id": record.payload.get("institution_id", record.record_id),
        "stage": stage,
        "stage_label": _STAGE_LABELS[stage],
        "readiness": readiness,
        "starting_level": {
            "baseline": baseline_level(record),
            "outcome": outcome_level(record) if stage == STAGE_COMPLETED else None,
            "source": "payload.baseline_level" if baseline_level(record) is not None else "missing",
            "outcome_source": "payload.target_level" if stage == STAGE_COMPLETED else "not_observed",
        },
        "observation_window": window,
        "comparable_group": {
            "record_ids": [item.record_id for item in group],
            "size": len(group),
            "minimum": min_comparable,
            "track_matched": track_matched,
            "criteria": {"same_capability_track": track_matched,
                         "baseline_tolerance": max(1.0, abs(baseline_level(record) or 0.0) * band)},
            "considered": considered,
            "excluded": excluded,
        },
        "missing_scope": scope | {"attrition_rate": attrition["rate"], "attrition_source": attrition["source"]},
        "estimate": estimate,
        "conclusion": conclusion,
    }


def _comparison_inputs(records: Iterable[DomainRecord], context: Mapping[str, Any] | None) -> str:
    context = context or {}
    analytic = {key: _setting(context, key) for key in _ANALYTIC_KEYS}
    return stable_hash({"records": [{"record_id": item.record_id, "version": item.version,
                                     "fingerprint": item.fingerprint} for item in records],
                        "context": analytic})


def analytic_context(context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Resolved analysis settings so a stored comparison can be replayed exactly."""
    return {key: _setting(context, key) for key in _ANALYTIC_KEYS}


def staged_report(records: Iterable[DomainRecord], context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = dict(context or {})
    records = list(records)
    rows = [institution_comparison(record, records, context) for record in records]
    if not rows:
        raise ContractError("staged comparison requires at least one record")
    stages: dict[str, int] = {}
    levels: dict[str, int] = {}
    for row in rows:
        stages[row["stage"]] = stages.get(row["stage"], 0) + 1
        level = row["conclusion"]["level"]
        levels[level] = levels.get(level, 0) + 1
    completed = [row for row in rows if row["stage"] == STAGE_COMPLETED]
    covered = sum(row["comparable_group"]["size"] > 0 for row in completed)
    return {
        "as_of": _setting(context, "as_of"),
        "settings": analytic_context(context),
        "input_fingerprint": _comparison_inputs(records, context),
        "records": rows,
        "cohorts": {
            "counts": stages,
            "conclusion_counts": levels,
            "completed_with_comparators": covered,
            "completed_total": len(completed),
            "awaiting_used_as_outcome_comparator": 0,
        },
        "method": {
            "unit": "record",
            "stage_evidence": {
                "completed": "completion_status/cohort_status=completed or a measured_at/observed_at timestamp",
                "awaiting": "no outcome evidence yet (default)",
                "closed": "withdrawal fields or attrition_rate>=1",
            },
            "outcome_rule": "payload.target_level 只在机构已完成且观察窗口可核验时视为结果观测；未完成机构的目标值不参与效果估计",
            "rules": [
                "等待资源的机构没有结果观测，只报告起始水平与准备度，不给出效果估计",
                "可比组只由已完成机构组成，并限制在起始水平带宽内",
                "观察窗口、流失率或缺失率不可核验时，结论降为方向性判断",
                "可比组不足时收窄结论，不用其他机构观测补成确定效果",
            ],
        },
    }


def _row_score(row: Mapping[str, Any]) -> float:
    level = row["conclusion"]["level"]
    missing = row["missing_scope"]["target_missing_rate"]
    missing_penalty = min(0.15, (missing if missing is not None else 0.35) * 0.2)
    if level in (LEVEL_EFFECT, LEVEL_DIRECTIONAL):
        difference = (row["estimate"] or {}).get("difference", 0.0)
        base = 0.55 if level == LEVEL_EFFECT else 0.42
        return bounded(base + max(-0.10, min(0.10, difference)) * 0.8 - missing_penalty)
    if row["stage"] == STAGE_AWAITING:
        feasibility = row["readiness"]["pathway_feasibility"]
        return bounded(0.22 + feasibility * 0.25 - missing_penalty * 0.5)
    return 0.05


def _basis(row: Mapping[str, Any]) -> tuple[str, str, bool]:
    level = row["conclusion"]["level"]
    if level == LEVEL_EFFECT:
        return ("completed_effect_estimate", "已有可比效果证据，可按同窗口扩容并继续监测", False)
    if level == LEVEL_DIRECTIONAL:
        return ("directional_estimate", "仅有方向性证据，扩容前需补足观察窗口或缺失数据", True)
    if row["stage"] == STAGE_AWAITING:
        return ("readiness_only", "仅有起始水平与准备度，适合小规模试运行，不得按已完成效果计", True)
    return ("insufficient_evidence", "数据不足，暂不纳入扩容", True)


RESOURCE_KEYS = ("expansion_slots", "mentor_capacity_floor", "compute_access_floor", "allow_readiness_only")


def resolved_resources(resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
    resources = dict(resources or {})
    return {key: resources.get(key, _DEFAULTS[key]) for key in RESOURCE_KEYS}


def plan_inputs(report: Mapping[str, Any], resources: Mapping[str, Any] | None = None) -> str:
    """Fingerprint of everything an expansion plan depends on."""
    return stable_hash({"comparison": report["input_fingerprint"], "resources": resolved_resources(resources)})


def recommend_expansions(report: Mapping[str, Any], resources: Mapping[str, Any] | None = None) -> dict[str, Any]:
    resources = dict(resources or {})
    slots = max(0, int(resources.get("expansion_slots", _DEFAULTS["expansion_slots"])))
    mentor_floor = float(resources.get("mentor_capacity_floor", _DEFAULTS["mentor_capacity_floor"]))
    compute_floor = float(resources.get("compute_access_floor", _DEFAULTS["compute_access_floor"]))
    allow_readiness = bool(resources.get("allow_readiness_only", _DEFAULTS["allow_readiness_only"]))
    candidates: list[dict[str, Any]] = []
    for row in report["records"]:
        mentor = row["readiness"]["mentor_capacity"]
        compute = row["readiness"]["compute_access"]
        basis, condition, conditional = _basis(row)
        level = row["conclusion"]["level"]
        tier = {LEVEL_EFFECT: 3, LEVEL_DIRECTIONAL: 2, LEVEL_NOT_APPLICABLE: 1, LEVEL_INSUFFICIENT: 0}[level]
        reasons: list[str] = []
        excluded = False
        if row["starting_level"]["baseline"] is None:
            excluded, tier = True, -1
            reasons.append("起始水平缺失，无法评估")
        if level == LEVEL_INSUFFICIENT:
            excluded, tier = True, -1
            reasons.append("数据不足，暂不纳入扩容；需补充观察后再判断")
        if row["stage"] == STAGE_CLOSED:
            excluded, tier = True, -1
            reasons.append("机构已退出，不纳入扩容")
        elif row["stage"] == STAGE_AWAITING and row["observation_window"]["status"] == "open":
            reasons.append("观察窗口已开始，扩容将按已在培机构处理")
        if row["stage"] == STAGE_AWAITING and not allow_readiness:
            excluded = True
            reasons.append("当前策略不允许仅凭准备度扩容")
        if mentor_floor and (mentor is None or mentor < mentor_floor):
            excluded = True
            reasons.append(f"导师资源低于可用下限 {mentor_floor:.2f}")
        if compute_floor and (compute is None or compute < compute_floor):
            excluded = True
            reasons.append(f"算力资源低于可用下限 {compute_floor:.2f}")
        candidates.append({
            "record_id": row["record_id"],
            "institution_id": row["institution_id"],
            "stage": row["stage"],
            "evidence_level": level,
            "basis": basis,
            "condition": condition,
            "conditional": conditional,
            "tier": tier,
            "score": _row_score(row),
            "reasons": reasons,
            "excluded": excluded,
            "starting_level": row["starting_level"],
            "observation_window": row["observation_window"],
            "comparable_group_size": row["comparable_group"]["size"],
            "missing_scope": {key: row["missing_scope"][key] for key in
                              ("scope", "target_missing_rate", "comparable_missing_range",
                               "attrition_rate")},
            "estimate": row["estimate"],
            "conclusion": row["conclusion"],
        })
    ranked = sorted((item for item in candidates if not item["excluded"]),
                    key=lambda item: (-item["tier"], -item["score"], item["record_id"]))
    selected = ranked[:slots]
    deferred = ranked[slots:]
    excluded = [item for item in candidates if item["excluded"]]
    inputs = plan_inputs(report, resources)
    plan_id = inputs[:24]
    summary = {
        "selected": len(selected),
        "deferred": len(deferred),
        "excluded": len(excluded),
        "effect_backed": sum(item["evidence_level"] == LEVEL_EFFECT for item in selected),
        "directional": sum(item["evidence_level"] == LEVEL_DIRECTIONAL for item in selected),
        "readiness_only": sum(item["basis"] == "readiness_only" for item in selected),
        "insufficient": sum(item["evidence_level"] == LEVEL_INSUFFICIENT for item in candidates),
    }
    caveats: list[str] = []
    if selected and summary["effect_backed"] == 0:
        caveats.append("本轮入选机构均无完整效果证据，只能按准备度或方向性判断试运行")
    if slots and not selected:
        caveats.append("在现有资源下限下没有机构满足扩容条件，名额保持空缺")
    if any(item["conditional"] for item in selected):
        caveats.append("入选机构附带条件，扩容后仍需按观察窗口复核")
    return {
        "plan_id": plan_id,
        "input_fingerprint": inputs,
        "comparison_fingerprint": report["input_fingerprint"],
        "resources": resolved_resources(resources),
        "slots": slots,
        "selected": selected,
        "deferred": deferred,
        "excluded": excluded,
        "unfilled_slots": max(0, slots - len(selected)),
        "summary": summary | {"caveats": caveats},
    }
