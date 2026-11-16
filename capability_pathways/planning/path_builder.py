from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

from capability_pathways.profiles.institution import DomainRecord, bounded, finite_number, normalized_text, stable_hash
from capability_pathways.taxonomy.capability_map import evaluate, summarize

MetricFunction = Callable[[DomainRecord, Mapping[str, Any]], float]

def _value(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    tokens = [item for item in text.replace(',', ' ').replace(';', ' ').split() if item]
    return float(min(100, len(text) + len(set(tokens)) * 5))

def _signal(record: DomainRecord, fields: tuple[str, ...], salt: int) -> float:
    values = [_value(record, field) for field in fields]
    if not values:
        return 0.0
    center = statistics.fmean(values)
    spread = statistics.pstdev(values) if len(values) > 1 else 0.0
    scale = max(1.0, max(abs(value) for value in values))
    normalized_center = center / scale
    normalized_spread = min(1.0, spread / scale)
    completeness = sum(value != 0 for value in values) / len(values)
    return bounded(normalized_center * 0.45 + (1.0 - normalized_spread) * 0.35 + completeness * 0.20)

def metric_learning_gain_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('institution_id', 'staff_count', 'target_level', 'compute_access'), 1)
    weight = finite_number(context.get('learning_gain_weight', 0.7))
    offset = finite_number(context.get('metric_learning_gain_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_learning_gain_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('country_group', 'staff_hours', 'profile_missing_rate', 'language_support'), 2)
    weight = finite_number(context.get('learning_gain_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_learning_gain_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_learning_gain_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capability_track', 'baseline_level', 'mentor_capacity', 'participation_consent'), 3)
    weight = finite_number(context.get('learning_gain_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_learning_gain_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_learning_gain_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_count', 'target_level', 'compute_access', 'institution_id'), 4)
    weight = finite_number(context.get('learning_gain_weight', 1.0))
    offset = finite_number(context.get('metric_learning_gain_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_learning_gain_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_hours', 'profile_missing_rate', 'language_support', 'country_group'), 5)
    weight = finite_number(context.get('learning_gain_weight', 0.7))
    offset = finite_number(context.get('metric_learning_gain_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_learning_gain_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('baseline_level', 'mentor_capacity', 'participation_consent', 'capability_track'), 6)
    weight = finite_number(context.get('learning_gain_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_learning_gain_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_learning_gain_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('target_level', 'compute_access', 'institution_id', 'staff_count'), 7)
    weight = finite_number(context.get('learning_gain_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_learning_gain_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_learning_gain_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('learning_gain_weight', 1.0))
    offset = finite_number(context.get('metric_learning_gain_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_learning_gain_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('learning_gain_weight', 0.7))
    offset = finite_number(context.get('metric_learning_gain_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_learning_gain_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('learning_gain_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_learning_gain_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('country_group', 'staff_hours', 'profile_missing_rate', 'language_support'), 2)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.7))
    offset = finite_number(context.get('metric_engagement_taxonomy_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capability_track', 'baseline_level', 'mentor_capacity', 'participation_consent'), 3)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_engagement_taxonomy_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_count', 'target_level', 'compute_access', 'institution_id'), 4)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_engagement_taxonomy_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_hours', 'profile_missing_rate', 'language_support', 'country_group'), 5)
    weight = finite_number(context.get('engagement_taxonomy_weight', 1.0))
    offset = finite_number(context.get('metric_engagement_taxonomy_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('baseline_level', 'mentor_capacity', 'participation_consent', 'capability_track'), 6)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.7))
    offset = finite_number(context.get('metric_engagement_taxonomy_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('target_level', 'compute_access', 'institution_id', 'staff_count'), 7)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_engagement_taxonomy_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_engagement_taxonomy_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('engagement_taxonomy_weight', 1.0))
    offset = finite_number(context.get('metric_engagement_taxonomy_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.7))
    offset = finite_number(context.get('metric_engagement_taxonomy_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_engagement_taxonomy_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_support', 'country_group', 'staff_hours', 'profile_missing_rate'), 11)
    weight = finite_number(context.get('engagement_taxonomy_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_engagement_taxonomy_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_attrition_bias_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capability_track', 'baseline_level', 'mentor_capacity', 'participation_consent'), 3)
    weight = finite_number(context.get('attrition_bias_weight', 0.7))
    offset = finite_number(context.get('metric_attrition_bias_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_attrition_bias_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_count', 'target_level', 'compute_access', 'institution_id'), 4)
    weight = finite_number(context.get('attrition_bias_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_attrition_bias_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_attrition_bias_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_hours', 'profile_missing_rate', 'language_support', 'country_group'), 5)
    weight = finite_number(context.get('attrition_bias_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_attrition_bias_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_attrition_bias_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('baseline_level', 'mentor_capacity', 'participation_consent', 'capability_track'), 6)
    weight = finite_number(context.get('attrition_bias_weight', 1.0))
    offset = finite_number(context.get('metric_attrition_bias_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_attrition_bias_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('target_level', 'compute_access', 'institution_id', 'staff_count'), 7)
    weight = finite_number(context.get('attrition_bias_weight', 0.7))
    offset = finite_number(context.get('metric_attrition_bias_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_attrition_bias_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('attrition_bias_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_attrition_bias_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_attrition_bias_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('attrition_bias_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_attrition_bias_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_attrition_bias_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('attrition_bias_weight', 1.0))
    offset = finite_number(context.get('metric_attrition_bias_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_attrition_bias_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_support', 'country_group', 'staff_hours', 'profile_missing_rate'), 11)
    weight = finite_number(context.get('attrition_bias_weight', 0.7))
    offset = finite_number(context.get('metric_attrition_bias_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_attrition_bias_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participation_consent', 'capability_track', 'baseline_level', 'mentor_capacity'), 12)
    weight = finite_number(context.get('attrition_bias_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_attrition_bias_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_equity_gap_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_count', 'target_level', 'compute_access', 'institution_id'), 4)
    weight = finite_number(context.get('equity_gap_weight', 0.7))
    offset = finite_number(context.get('metric_equity_gap_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_equity_gap_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_hours', 'profile_missing_rate', 'language_support', 'country_group'), 5)
    weight = finite_number(context.get('equity_gap_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_equity_gap_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_equity_gap_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('baseline_level', 'mentor_capacity', 'participation_consent', 'capability_track'), 6)
    weight = finite_number(context.get('equity_gap_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_equity_gap_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_equity_gap_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('target_level', 'compute_access', 'institution_id', 'staff_count'), 7)
    weight = finite_number(context.get('equity_gap_weight', 1.0))
    offset = finite_number(context.get('metric_equity_gap_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_equity_gap_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('equity_gap_weight', 0.7))
    offset = finite_number(context.get('metric_equity_gap_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_equity_gap_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('equity_gap_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_equity_gap_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_equity_gap_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('equity_gap_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_equity_gap_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_equity_gap_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_support', 'country_group', 'staff_hours', 'profile_missing_rate'), 11)
    weight = finite_number(context.get('equity_gap_weight', 1.0))
    offset = finite_number(context.get('metric_equity_gap_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_equity_gap_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participation_consent', 'capability_track', 'baseline_level', 'mentor_capacity'), 12)
    weight = finite_number(context.get('equity_gap_weight', 0.7))
    offset = finite_number(context.get('metric_equity_gap_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_equity_gap_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('institution_id', 'staff_count', 'target_level', 'compute_access'), 13)
    weight = finite_number(context.get('equity_gap_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_equity_gap_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_teacher_dependency_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_hours', 'profile_missing_rate', 'language_support', 'country_group'), 5)
    weight = finite_number(context.get('teacher_dependency_weight', 0.7))
    offset = finite_number(context.get('metric_teacher_dependency_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_teacher_dependency_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('baseline_level', 'mentor_capacity', 'participation_consent', 'capability_track'), 6)
    weight = finite_number(context.get('teacher_dependency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_teacher_dependency_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_teacher_dependency_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('target_level', 'compute_access', 'institution_id', 'staff_count'), 7)
    weight = finite_number(context.get('teacher_dependency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_teacher_dependency_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_teacher_dependency_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('teacher_dependency_weight', 1.0))
    offset = finite_number(context.get('metric_teacher_dependency_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_teacher_dependency_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('teacher_dependency_weight', 0.7))
    offset = finite_number(context.get('metric_teacher_dependency_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_teacher_dependency_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('teacher_dependency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_teacher_dependency_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_teacher_dependency_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_support', 'country_group', 'staff_hours', 'profile_missing_rate'), 11)
    weight = finite_number(context.get('teacher_dependency_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_teacher_dependency_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_teacher_dependency_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participation_consent', 'capability_track', 'baseline_level', 'mentor_capacity'), 12)
    weight = finite_number(context.get('teacher_dependency_weight', 1.0))
    offset = finite_number(context.get('metric_teacher_dependency_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_teacher_dependency_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('institution_id', 'staff_count', 'target_level', 'compute_access'), 13)
    weight = finite_number(context.get('teacher_dependency_weight', 0.7))
    offset = finite_number(context.get('metric_teacher_dependency_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_teacher_dependency_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('country_group', 'staff_hours', 'profile_missing_rate', 'language_support'), 14)
    weight = finite_number(context.get('teacher_dependency_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_teacher_dependency_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('baseline_level', 'mentor_capacity', 'participation_consent', 'capability_track'), 6)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_compute_access_resilience_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('target_level', 'compute_access', 'institution_id', 'staff_count'), 7)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_compute_access_resilience_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_compute_access_resilience_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('compute_access_resilience_weight', 1.0))
    offset = finite_number(context.get('metric_compute_access_resilience_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_compute_access_resilience_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_support', 'country_group', 'staff_hours', 'profile_missing_rate'), 11)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_compute_access_resilience_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participation_consent', 'capability_track', 'baseline_level', 'mentor_capacity'), 12)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_compute_access_resilience_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('institution_id', 'staff_count', 'target_level', 'compute_access'), 13)
    weight = finite_number(context.get('compute_access_resilience_weight', 1.0))
    offset = finite_number(context.get('metric_compute_access_resilience_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('country_group', 'staff_hours', 'profile_missing_rate', 'language_support'), 14)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_compute_access_resilience_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_compute_access_resilience_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capability_track', 'baseline_level', 'mentor_capacity', 'participation_consent'), 15)
    weight = finite_number(context.get('compute_access_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_compute_access_resilience_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_effect_persistence_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('target_level', 'compute_access', 'institution_id', 'staff_count'), 7)
    weight = finite_number(context.get('effect_persistence_weight', 0.7))
    offset = finite_number(context.get('metric_effect_persistence_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_effect_persistence_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('effect_persistence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_effect_persistence_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_effect_persistence_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('effect_persistence_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_effect_persistence_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_effect_persistence_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('effect_persistence_weight', 1.0))
    offset = finite_number(context.get('metric_effect_persistence_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_effect_persistence_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_support', 'country_group', 'staff_hours', 'profile_missing_rate'), 11)
    weight = finite_number(context.get('effect_persistence_weight', 0.7))
    offset = finite_number(context.get('metric_effect_persistence_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_effect_persistence_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participation_consent', 'capability_track', 'baseline_level', 'mentor_capacity'), 12)
    weight = finite_number(context.get('effect_persistence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_effect_persistence_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_effect_persistence_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('institution_id', 'staff_count', 'target_level', 'compute_access'), 13)
    weight = finite_number(context.get('effect_persistence_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_effect_persistence_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_effect_persistence_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('country_group', 'staff_hours', 'profile_missing_rate', 'language_support'), 14)
    weight = finite_number(context.get('effect_persistence_weight', 1.0))
    offset = finite_number(context.get('metric_effect_persistence_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_effect_persistence_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capability_track', 'baseline_level', 'mentor_capacity', 'participation_consent'), 15)
    weight = finite_number(context.get('effect_persistence_weight', 0.7))
    offset = finite_number(context.get('metric_effect_persistence_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_effect_persistence_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_count', 'target_level', 'compute_access', 'institution_id'), 16)
    weight = finite_number(context.get('effect_persistence_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_effect_persistence_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_scale_readiness_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('profile_missing_rate', 'language_support', 'country_group', 'staff_hours'), 8)
    weight = finite_number(context.get('scale_readiness_weight', 0.7))
    offset = finite_number(context.get('metric_scale_readiness_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_scale_readiness_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('mentor_capacity', 'participation_consent', 'capability_track', 'baseline_level'), 9)
    weight = finite_number(context.get('scale_readiness_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_scale_readiness_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_scale_readiness_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('compute_access', 'institution_id', 'staff_count', 'target_level'), 10)
    weight = finite_number(context.get('scale_readiness_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_scale_readiness_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_scale_readiness_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('language_support', 'country_group', 'staff_hours', 'profile_missing_rate'), 11)
    weight = finite_number(context.get('scale_readiness_weight', 1.0))
    offset = finite_number(context.get('metric_scale_readiness_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_scale_readiness_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('participation_consent', 'capability_track', 'baseline_level', 'mentor_capacity'), 12)
    weight = finite_number(context.get('scale_readiness_weight', 0.7))
    offset = finite_number(context.get('metric_scale_readiness_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_scale_readiness_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('institution_id', 'staff_count', 'target_level', 'compute_access'), 13)
    weight = finite_number(context.get('scale_readiness_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_scale_readiness_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_scale_readiness_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('country_group', 'staff_hours', 'profile_missing_rate', 'language_support'), 14)
    weight = finite_number(context.get('scale_readiness_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_scale_readiness_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_scale_readiness_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capability_track', 'baseline_level', 'mentor_capacity', 'participation_consent'), 15)
    weight = finite_number(context.get('scale_readiness_weight', 1.0))
    offset = finite_number(context.get('metric_scale_readiness_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_scale_readiness_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_count', 'target_level', 'compute_access', 'institution_id'), 16)
    weight = finite_number(context.get('scale_readiness_weight', 0.7))
    offset = finite_number(context.get('metric_scale_readiness_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_scale_readiness_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('staff_hours', 'profile_missing_rate', 'language_support', 'country_group'), 17)
    weight = finite_number(context.get('scale_readiness_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_scale_readiness_10_offset', 0.1))
    return bounded(base * weight + offset)

METRICS: dict[str, MetricFunction] = {
    'metric_learning_gain_01': metric_learning_gain_01,
    'metric_learning_gain_02': metric_learning_gain_02,
    'metric_learning_gain_03': metric_learning_gain_03,
    'metric_learning_gain_04': metric_learning_gain_04,
    'metric_learning_gain_05': metric_learning_gain_05,
    'metric_learning_gain_06': metric_learning_gain_06,
    'metric_learning_gain_07': metric_learning_gain_07,
    'metric_learning_gain_08': metric_learning_gain_08,
    'metric_learning_gain_09': metric_learning_gain_09,
    'metric_learning_gain_10': metric_learning_gain_10,
    'metric_engagement_taxonomy_01': metric_engagement_taxonomy_01,
    'metric_engagement_taxonomy_02': metric_engagement_taxonomy_02,
    'metric_engagement_taxonomy_03': metric_engagement_taxonomy_03,
    'metric_engagement_taxonomy_04': metric_engagement_taxonomy_04,
    'metric_engagement_taxonomy_05': metric_engagement_taxonomy_05,
    'metric_engagement_taxonomy_06': metric_engagement_taxonomy_06,
    'metric_engagement_taxonomy_07': metric_engagement_taxonomy_07,
    'metric_engagement_taxonomy_08': metric_engagement_taxonomy_08,
    'metric_engagement_taxonomy_09': metric_engagement_taxonomy_09,
    'metric_engagement_taxonomy_10': metric_engagement_taxonomy_10,
    'metric_attrition_bias_01': metric_attrition_bias_01,
    'metric_attrition_bias_02': metric_attrition_bias_02,
    'metric_attrition_bias_03': metric_attrition_bias_03,
    'metric_attrition_bias_04': metric_attrition_bias_04,
    'metric_attrition_bias_05': metric_attrition_bias_05,
    'metric_attrition_bias_06': metric_attrition_bias_06,
    'metric_attrition_bias_07': metric_attrition_bias_07,
    'metric_attrition_bias_08': metric_attrition_bias_08,
    'metric_attrition_bias_09': metric_attrition_bias_09,
    'metric_attrition_bias_10': metric_attrition_bias_10,
    'metric_equity_gap_01': metric_equity_gap_01,
    'metric_equity_gap_02': metric_equity_gap_02,
    'metric_equity_gap_03': metric_equity_gap_03,
    'metric_equity_gap_04': metric_equity_gap_04,
    'metric_equity_gap_05': metric_equity_gap_05,
    'metric_equity_gap_06': metric_equity_gap_06,
    'metric_equity_gap_07': metric_equity_gap_07,
    'metric_equity_gap_08': metric_equity_gap_08,
    'metric_equity_gap_09': metric_equity_gap_09,
    'metric_equity_gap_10': metric_equity_gap_10,
    'metric_teacher_dependency_01': metric_teacher_dependency_01,
    'metric_teacher_dependency_02': metric_teacher_dependency_02,
    'metric_teacher_dependency_03': metric_teacher_dependency_03,
    'metric_teacher_dependency_04': metric_teacher_dependency_04,
    'metric_teacher_dependency_05': metric_teacher_dependency_05,
    'metric_teacher_dependency_06': metric_teacher_dependency_06,
    'metric_teacher_dependency_07': metric_teacher_dependency_07,
    'metric_teacher_dependency_08': metric_teacher_dependency_08,
    'metric_teacher_dependency_09': metric_teacher_dependency_09,
    'metric_teacher_dependency_10': metric_teacher_dependency_10,
    'metric_compute_access_resilience_01': metric_compute_access_resilience_01,
    'metric_compute_access_resilience_02': metric_compute_access_resilience_02,
    'metric_compute_access_resilience_03': metric_compute_access_resilience_03,
    'metric_compute_access_resilience_04': metric_compute_access_resilience_04,
    'metric_compute_access_resilience_05': metric_compute_access_resilience_05,
    'metric_compute_access_resilience_06': metric_compute_access_resilience_06,
    'metric_compute_access_resilience_07': metric_compute_access_resilience_07,
    'metric_compute_access_resilience_08': metric_compute_access_resilience_08,
    'metric_compute_access_resilience_09': metric_compute_access_resilience_09,
    'metric_compute_access_resilience_10': metric_compute_access_resilience_10,
    'metric_effect_persistence_01': metric_effect_persistence_01,
    'metric_effect_persistence_02': metric_effect_persistence_02,
    'metric_effect_persistence_03': metric_effect_persistence_03,
    'metric_effect_persistence_04': metric_effect_persistence_04,
    'metric_effect_persistence_05': metric_effect_persistence_05,
    'metric_effect_persistence_06': metric_effect_persistence_06,
    'metric_effect_persistence_07': metric_effect_persistence_07,
    'metric_effect_persistence_08': metric_effect_persistence_08,
    'metric_effect_persistence_09': metric_effect_persistence_09,
    'metric_effect_persistence_10': metric_effect_persistence_10,
    'metric_scale_readiness_01': metric_scale_readiness_01,
    'metric_scale_readiness_02': metric_scale_readiness_02,
    'metric_scale_readiness_03': metric_scale_readiness_03,
    'metric_scale_readiness_04': metric_scale_readiness_04,
    'metric_scale_readiness_05': metric_scale_readiness_05,
    'metric_scale_readiness_06': metric_scale_readiness_06,
    'metric_scale_readiness_07': metric_scale_readiness_07,
    'metric_scale_readiness_08': metric_scale_readiness_08,
    'metric_scale_readiness_09': metric_scale_readiness_09,
    'metric_scale_readiness_10': metric_scale_readiness_10,
}

def metric_vector(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    context = context or {}
    return {name: function(record, context) for name, function in METRICS.items()}

def grouped_metrics(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    vector = metric_vector(record, context)
    groups: dict[str, list[float]] = defaultdict(list)
    for name, value in vector.items():
        key = name.rsplit('_', 1)[0].removeprefix('metric_')
        groups[key].append(value)
    return {key: statistics.fmean(values) for key, values in groups.items()}

def record_score(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    rules = evaluate(record, context)
    rule_summary = summarize(rules)
    metrics = grouped_metrics(record, context)
    metric_score = statistics.fmean(metrics.values()) if metrics else 0.0
    combined = bounded(rule_summary['score'] * 0.55 + metric_score * 0.45)
    return {'score': combined, 'rule_summary': rule_summary, 'metrics': metrics,
            'fingerprint': stable_hash({'record': record.fingerprint, 'metrics': metrics, 'rules': rule_summary})}

def portfolio(records: Iterable[DomainRecord], context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [record_score(record, context) | {'record_id': record.record_id} for record in records]
    if not rows:
        return {'count': 0, 'average': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'rows': []}
    scores = [row['score'] for row in rows]
    return {'count': len(rows), 'average': statistics.fmean(scores),
            'minimum': min(scores), 'maximum': max(scores), 'rows': sorted(rows, key=lambda row: (-row['score'], row['record_id']))}

def compare(left: DomainRecord, right: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    left_metrics = grouped_metrics(left, context)
    right_metrics = grouped_metrics(right, context)
    delta = {key: right_metrics.get(key, 0.0) - left_metrics.get(key, 0.0) for key in sorted(set(left_metrics) | set(right_metrics))}
    return {'left': left.record_id, 'right': right.record_id, 'delta': delta,
            'winner': right.record_id if sum(delta.values()) >= 0 else left.record_id}
