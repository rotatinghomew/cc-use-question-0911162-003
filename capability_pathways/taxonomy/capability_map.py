from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from capability_pathways.profiles.institution import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        tokens = [item for item in text.replace(',', ' ').replace(';', ' ').split() if item]
        return float(min(100, len(text) + len(set(tokens)) * 5))

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_institution_id_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_institution_id_presence_threshold', 10.333)
    return _result('check_institution_id_presence', adjusted, threshold, True, 'validates institution_id presence',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_institution_id_range_threshold', 12.667)
    return _result('check_institution_id_range', adjusted, threshold, True, 'validates institution_id range',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_institution_id_stability_threshold', 15.0)
    return _result('check_institution_id_stability', adjusted, threshold, False, 'validates institution_id stability',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_institution_id_freshness_threshold', 17.333)
    return _result('check_institution_id_freshness', adjusted, threshold, True, 'validates institution_id freshness',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_institution_id_coverage_threshold', 19.667)
    return _result('check_institution_id_coverage', adjusted, threshold, True, 'validates institution_id coverage',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_institution_id_consistency_threshold', 22.0)
    return _result('check_institution_id_consistency', adjusted, threshold, False, 'validates institution_id consistency',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_institution_id_risk_threshold', 24.333)
    return _result('check_institution_id_risk', adjusted, threshold, True, 'validates institution_id risk',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_institution_id_confidence_threshold', 26.667)
    return _result('check_institution_id_confidence', adjusted, threshold, True, 'validates institution_id confidence',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_institution_id_dependency_threshold', 29.0)
    return _result('check_institution_id_dependency', adjusted, threshold, False, 'validates institution_id dependency',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_institution_id_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'institution_id')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_institution_id_readiness_threshold', 31.333)
    return _result('check_institution_id_readiness', adjusted, threshold, True, 'validates institution_id readiness',
                   {'field': 'institution_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_country_group_presence_threshold', 9.333)
    return _result('check_country_group_presence', adjusted, threshold, True, 'validates country_group presence',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_country_group_range_threshold', 11.667)
    return _result('check_country_group_range', adjusted, threshold, False, 'validates country_group range',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_country_group_stability_threshold', 14.0)
    return _result('check_country_group_stability', adjusted, threshold, True, 'validates country_group stability',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_country_group_freshness_threshold', 16.333)
    return _result('check_country_group_freshness', adjusted, threshold, True, 'validates country_group freshness',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_country_group_coverage_threshold', 18.667)
    return _result('check_country_group_coverage', adjusted, threshold, False, 'validates country_group coverage',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_country_group_consistency_threshold', 21.0)
    return _result('check_country_group_consistency', adjusted, threshold, True, 'validates country_group consistency',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_country_group_risk_threshold', 23.333)
    return _result('check_country_group_risk', adjusted, threshold, True, 'validates country_group risk',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_country_group_confidence_threshold', 25.667)
    return _result('check_country_group_confidence', adjusted, threshold, False, 'validates country_group confidence',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_country_group_dependency_threshold', 28.0)
    return _result('check_country_group_dependency', adjusted, threshold, True, 'validates country_group dependency',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_country_group_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'country_group')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_country_group_readiness_threshold', 30.333)
    return _result('check_country_group_readiness', adjusted, threshold, True, 'validates country_group readiness',
                   {'field': 'country_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_capability_track_presence_threshold', 8.333)
    return _result('check_capability_track_presence', adjusted, threshold, False, 'validates capability_track presence',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_capability_track_range_threshold', 10.667)
    return _result('check_capability_track_range', adjusted, threshold, True, 'validates capability_track range',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_capability_track_stability_threshold', 13.0)
    return _result('check_capability_track_stability', adjusted, threshold, True, 'validates capability_track stability',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_capability_track_freshness_threshold', 15.333)
    return _result('check_capability_track_freshness', adjusted, threshold, False, 'validates capability_track freshness',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_capability_track_coverage_threshold', 17.667)
    return _result('check_capability_track_coverage', adjusted, threshold, True, 'validates capability_track coverage',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_capability_track_consistency_threshold', 20.0)
    return _result('check_capability_track_consistency', adjusted, threshold, True, 'validates capability_track consistency',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_capability_track_risk_threshold', 22.333)
    return _result('check_capability_track_risk', adjusted, threshold, False, 'validates capability_track risk',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_capability_track_confidence_threshold', 24.667)
    return _result('check_capability_track_confidence', adjusted, threshold, True, 'validates capability_track confidence',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_capability_track_dependency_threshold', 27.0)
    return _result('check_capability_track_dependency', adjusted, threshold, True, 'validates capability_track dependency',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capability_track_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capability_track')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_capability_track_readiness_threshold', 29.333)
    return _result('check_capability_track_readiness', adjusted, threshold, False, 'validates capability_track readiness',
                   {'field': 'capability_track', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_staff_count_presence_threshold', 31.667)
    return _result('check_staff_count_presence', adjusted, threshold, True, 'validates staff_count presence',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_staff_count_range_threshold', 9.667)
    return _result('check_staff_count_range', adjusted, threshold, True, 'validates staff_count range',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_staff_count_stability_threshold', 12.0)
    return _result('check_staff_count_stability', adjusted, threshold, False, 'validates staff_count stability',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_staff_count_freshness_threshold', 14.333)
    return _result('check_staff_count_freshness', adjusted, threshold, True, 'validates staff_count freshness',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_staff_count_coverage_threshold', 16.667)
    return _result('check_staff_count_coverage', adjusted, threshold, True, 'validates staff_count coverage',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_staff_count_consistency_threshold', 19.0)
    return _result('check_staff_count_consistency', adjusted, threshold, False, 'validates staff_count consistency',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_staff_count_risk_threshold', 21.333)
    return _result('check_staff_count_risk', adjusted, threshold, True, 'validates staff_count risk',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_staff_count_confidence_threshold', 23.667)
    return _result('check_staff_count_confidence', adjusted, threshold, True, 'validates staff_count confidence',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_staff_count_dependency_threshold', 26.0)
    return _result('check_staff_count_dependency', adjusted, threshold, False, 'validates staff_count dependency',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_staff_count_readiness_threshold', 28.333)
    return _result('check_staff_count_readiness', adjusted, threshold, True, 'validates staff_count readiness',
                   {'field': 'staff_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_staff_hours_presence_threshold', 30.667)
    return _result('check_staff_hours_presence', adjusted, threshold, True, 'validates staff_hours presence',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_staff_hours_range_threshold', 8.667)
    return _result('check_staff_hours_range', adjusted, threshold, False, 'validates staff_hours range',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_staff_hours_stability_threshold', 11.0)
    return _result('check_staff_hours_stability', adjusted, threshold, True, 'validates staff_hours stability',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_staff_hours_freshness_threshold', 13.333)
    return _result('check_staff_hours_freshness', adjusted, threshold, True, 'validates staff_hours freshness',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_staff_hours_coverage_threshold', 15.667)
    return _result('check_staff_hours_coverage', adjusted, threshold, False, 'validates staff_hours coverage',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_staff_hours_consistency_threshold', 18.0)
    return _result('check_staff_hours_consistency', adjusted, threshold, True, 'validates staff_hours consistency',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_staff_hours_risk_threshold', 20.333)
    return _result('check_staff_hours_risk', adjusted, threshold, True, 'validates staff_hours risk',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_staff_hours_confidence_threshold', 22.667)
    return _result('check_staff_hours_confidence', adjusted, threshold, False, 'validates staff_hours confidence',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_staff_hours_dependency_threshold', 25.0)
    return _result('check_staff_hours_dependency', adjusted, threshold, True, 'validates staff_hours dependency',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_staff_hours_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'staff_hours')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_staff_hours_readiness_threshold', 27.333)
    return _result('check_staff_hours_readiness', adjusted, threshold, True, 'validates staff_hours readiness',
                   {'field': 'staff_hours', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_baseline_level_presence_threshold', 29.667)
    return _result('check_baseline_level_presence', adjusted, threshold, False, 'validates baseline_level presence',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_baseline_level_range_threshold', 32.0)
    return _result('check_baseline_level_range', adjusted, threshold, True, 'validates baseline_level range',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_baseline_level_stability_threshold', 10.0)
    return _result('check_baseline_level_stability', adjusted, threshold, True, 'validates baseline_level stability',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_baseline_level_freshness_threshold', 12.333)
    return _result('check_baseline_level_freshness', adjusted, threshold, False, 'validates baseline_level freshness',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_baseline_level_coverage_threshold', 14.667)
    return _result('check_baseline_level_coverage', adjusted, threshold, True, 'validates baseline_level coverage',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_baseline_level_consistency_threshold', 17.0)
    return _result('check_baseline_level_consistency', adjusted, threshold, True, 'validates baseline_level consistency',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_baseline_level_risk_threshold', 19.333)
    return _result('check_baseline_level_risk', adjusted, threshold, False, 'validates baseline_level risk',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_baseline_level_confidence_threshold', 21.667)
    return _result('check_baseline_level_confidence', adjusted, threshold, True, 'validates baseline_level confidence',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_baseline_level_dependency_threshold', 24.0)
    return _result('check_baseline_level_dependency', adjusted, threshold, True, 'validates baseline_level dependency',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_baseline_level_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'baseline_level')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_baseline_level_readiness_threshold', 26.333)
    return _result('check_baseline_level_readiness', adjusted, threshold, False, 'validates baseline_level readiness',
                   {'field': 'baseline_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_target_level_presence_threshold', 28.667)
    return _result('check_target_level_presence', adjusted, threshold, True, 'validates target_level presence',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_target_level_range_threshold', 31.0)
    return _result('check_target_level_range', adjusted, threshold, True, 'validates target_level range',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_target_level_stability_threshold', 9.0)
    return _result('check_target_level_stability', adjusted, threshold, False, 'validates target_level stability',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_target_level_freshness_threshold', 11.333)
    return _result('check_target_level_freshness', adjusted, threshold, True, 'validates target_level freshness',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_target_level_coverage_threshold', 13.667)
    return _result('check_target_level_coverage', adjusted, threshold, True, 'validates target_level coverage',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_target_level_consistency_threshold', 16.0)
    return _result('check_target_level_consistency', adjusted, threshold, False, 'validates target_level consistency',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_target_level_risk_threshold', 18.333)
    return _result('check_target_level_risk', adjusted, threshold, True, 'validates target_level risk',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_target_level_confidence_threshold', 20.667)
    return _result('check_target_level_confidence', adjusted, threshold, True, 'validates target_level confidence',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_target_level_dependency_threshold', 23.0)
    return _result('check_target_level_dependency', adjusted, threshold, False, 'validates target_level dependency',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_target_level_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'target_level')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_target_level_readiness_threshold', 25.333)
    return _result('check_target_level_readiness', adjusted, threshold, True, 'validates target_level readiness',
                   {'field': 'target_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_profile_missing_rate_presence_threshold', 27.667)
    return _result('check_profile_missing_rate_presence', adjusted, threshold, True, 'validates profile_missing_rate presence',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_profile_missing_rate_range_threshold', 30.0)
    return _result('check_profile_missing_rate_range', adjusted, threshold, False, 'validates profile_missing_rate range',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_profile_missing_rate_stability_threshold', 8.0)
    return _result('check_profile_missing_rate_stability', adjusted, threshold, True, 'validates profile_missing_rate stability',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_profile_missing_rate_freshness_threshold', 10.333)
    return _result('check_profile_missing_rate_freshness', adjusted, threshold, True, 'validates profile_missing_rate freshness',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_profile_missing_rate_coverage_threshold', 12.667)
    return _result('check_profile_missing_rate_coverage', adjusted, threshold, False, 'validates profile_missing_rate coverage',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_profile_missing_rate_consistency_threshold', 15.0)
    return _result('check_profile_missing_rate_consistency', adjusted, threshold, True, 'validates profile_missing_rate consistency',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_profile_missing_rate_risk_threshold', 17.333)
    return _result('check_profile_missing_rate_risk', adjusted, threshold, True, 'validates profile_missing_rate risk',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_profile_missing_rate_confidence_threshold', 19.667)
    return _result('check_profile_missing_rate_confidence', adjusted, threshold, False, 'validates profile_missing_rate confidence',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_profile_missing_rate_dependency_threshold', 22.0)
    return _result('check_profile_missing_rate_dependency', adjusted, threshold, True, 'validates profile_missing_rate dependency',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_profile_missing_rate_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'profile_missing_rate')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_profile_missing_rate_readiness_threshold', 24.333)
    return _result('check_profile_missing_rate_readiness', adjusted, threshold, True, 'validates profile_missing_rate readiness',
                   {'field': 'profile_missing_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_mentor_capacity_presence_threshold', 26.667)
    return _result('check_mentor_capacity_presence', adjusted, threshold, False, 'validates mentor_capacity presence',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_mentor_capacity_range_threshold', 29.0)
    return _result('check_mentor_capacity_range', adjusted, threshold, True, 'validates mentor_capacity range',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_mentor_capacity_stability_threshold', 31.333)
    return _result('check_mentor_capacity_stability', adjusted, threshold, True, 'validates mentor_capacity stability',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_mentor_capacity_freshness_threshold', 9.333)
    return _result('check_mentor_capacity_freshness', adjusted, threshold, False, 'validates mentor_capacity freshness',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_mentor_capacity_coverage_threshold', 11.667)
    return _result('check_mentor_capacity_coverage', adjusted, threshold, True, 'validates mentor_capacity coverage',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_mentor_capacity_consistency_threshold', 14.0)
    return _result('check_mentor_capacity_consistency', adjusted, threshold, True, 'validates mentor_capacity consistency',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_mentor_capacity_risk_threshold', 16.333)
    return _result('check_mentor_capacity_risk', adjusted, threshold, False, 'validates mentor_capacity risk',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_mentor_capacity_confidence_threshold', 18.667)
    return _result('check_mentor_capacity_confidence', adjusted, threshold, True, 'validates mentor_capacity confidence',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_mentor_capacity_dependency_threshold', 21.0)
    return _result('check_mentor_capacity_dependency', adjusted, threshold, True, 'validates mentor_capacity dependency',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_mentor_capacity_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'mentor_capacity')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_mentor_capacity_readiness_threshold', 23.333)
    return _result('check_mentor_capacity_readiness', adjusted, threshold, False, 'validates mentor_capacity readiness',
                   {'field': 'mentor_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_compute_access_presence_threshold', 25.667)
    return _result('check_compute_access_presence', adjusted, threshold, True, 'validates compute_access presence',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_compute_access_range_threshold', 28.0)
    return _result('check_compute_access_range', adjusted, threshold, True, 'validates compute_access range',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_compute_access_stability_threshold', 30.333)
    return _result('check_compute_access_stability', adjusted, threshold, False, 'validates compute_access stability',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_compute_access_freshness_threshold', 8.333)
    return _result('check_compute_access_freshness', adjusted, threshold, True, 'validates compute_access freshness',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_compute_access_coverage_threshold', 10.667)
    return _result('check_compute_access_coverage', adjusted, threshold, True, 'validates compute_access coverage',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_compute_access_consistency_threshold', 13.0)
    return _result('check_compute_access_consistency', adjusted, threshold, False, 'validates compute_access consistency',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_compute_access_risk_threshold', 15.333)
    return _result('check_compute_access_risk', adjusted, threshold, True, 'validates compute_access risk',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_compute_access_confidence_threshold', 17.667)
    return _result('check_compute_access_confidence', adjusted, threshold, True, 'validates compute_access confidence',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_compute_access_dependency_threshold', 20.0)
    return _result('check_compute_access_dependency', adjusted, threshold, False, 'validates compute_access dependency',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compute_access_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compute_access')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_compute_access_readiness_threshold', 22.333)
    return _result('check_compute_access_readiness', adjusted, threshold, True, 'validates compute_access readiness',
                   {'field': 'compute_access', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_language_support_presence_threshold', 24.667)
    return _result('check_language_support_presence', adjusted, threshold, True, 'validates language_support presence',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_language_support_range_threshold', 27.0)
    return _result('check_language_support_range', adjusted, threshold, False, 'validates language_support range',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_language_support_stability_threshold', 29.333)
    return _result('check_language_support_stability', adjusted, threshold, True, 'validates language_support stability',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_language_support_freshness_threshold', 31.667)
    return _result('check_language_support_freshness', adjusted, threshold, True, 'validates language_support freshness',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_language_support_coverage_threshold', 9.667)
    return _result('check_language_support_coverage', adjusted, threshold, False, 'validates language_support coverage',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_language_support_consistency_threshold', 12.0)
    return _result('check_language_support_consistency', adjusted, threshold, True, 'validates language_support consistency',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_language_support_risk_threshold', 14.333)
    return _result('check_language_support_risk', adjusted, threshold, True, 'validates language_support risk',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_language_support_confidence_threshold', 16.667)
    return _result('check_language_support_confidence', adjusted, threshold, False, 'validates language_support confidence',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_language_support_dependency_threshold', 19.0)
    return _result('check_language_support_dependency', adjusted, threshold, True, 'validates language_support dependency',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_support_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_support')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_language_support_readiness_threshold', 21.333)
    return _result('check_language_support_readiness', adjusted, threshold, True, 'validates language_support readiness',
                   {'field': 'language_support', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_participation_consent_presence_threshold', 23.667)
    return _result('check_participation_consent_presence', adjusted, threshold, False, 'validates participation_consent presence',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_participation_consent_range_threshold', 26.0)
    return _result('check_participation_consent_range', adjusted, threshold, True, 'validates participation_consent range',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_participation_consent_stability_threshold', 28.333)
    return _result('check_participation_consent_stability', adjusted, threshold, True, 'validates participation_consent stability',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_participation_consent_freshness_threshold', 30.667)
    return _result('check_participation_consent_freshness', adjusted, threshold, False, 'validates participation_consent freshness',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_participation_consent_coverage_threshold', 8.667)
    return _result('check_participation_consent_coverage', adjusted, threshold, True, 'validates participation_consent coverage',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_participation_consent_consistency_threshold', 11.0)
    return _result('check_participation_consent_consistency', adjusted, threshold, True, 'validates participation_consent consistency',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_participation_consent_risk_threshold', 13.333)
    return _result('check_participation_consent_risk', adjusted, threshold, False, 'validates participation_consent risk',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_participation_consent_confidence_threshold', 15.667)
    return _result('check_participation_consent_confidence', adjusted, threshold, True, 'validates participation_consent confidence',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_participation_consent_dependency_threshold', 18.0)
    return _result('check_participation_consent_dependency', adjusted, threshold, True, 'validates participation_consent dependency',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_participation_consent_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'participation_consent')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_participation_consent_readiness_threshold', 20.333)
    return _result('check_participation_consent_readiness', adjusted, threshold, False, 'validates participation_consent readiness',
                   {'field': 'participation_consent', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_institution_id_presence,
    check_institution_id_range,
    check_institution_id_stability,
    check_institution_id_freshness,
    check_institution_id_coverage,
    check_institution_id_consistency,
    check_institution_id_risk,
    check_institution_id_confidence,
    check_institution_id_dependency,
    check_institution_id_readiness,
    check_country_group_presence,
    check_country_group_range,
    check_country_group_stability,
    check_country_group_freshness,
    check_country_group_coverage,
    check_country_group_consistency,
    check_country_group_risk,
    check_country_group_confidence,
    check_country_group_dependency,
    check_country_group_readiness,
    check_capability_track_presence,
    check_capability_track_range,
    check_capability_track_stability,
    check_capability_track_freshness,
    check_capability_track_coverage,
    check_capability_track_consistency,
    check_capability_track_risk,
    check_capability_track_confidence,
    check_capability_track_dependency,
    check_capability_track_readiness,
    check_staff_count_presence,
    check_staff_count_range,
    check_staff_count_stability,
    check_staff_count_freshness,
    check_staff_count_coverage,
    check_staff_count_consistency,
    check_staff_count_risk,
    check_staff_count_confidence,
    check_staff_count_dependency,
    check_staff_count_readiness,
    check_staff_hours_presence,
    check_staff_hours_range,
    check_staff_hours_stability,
    check_staff_hours_freshness,
    check_staff_hours_coverage,
    check_staff_hours_consistency,
    check_staff_hours_risk,
    check_staff_hours_confidence,
    check_staff_hours_dependency,
    check_staff_hours_readiness,
    check_baseline_level_presence,
    check_baseline_level_range,
    check_baseline_level_stability,
    check_baseline_level_freshness,
    check_baseline_level_coverage,
    check_baseline_level_consistency,
    check_baseline_level_risk,
    check_baseline_level_confidence,
    check_baseline_level_dependency,
    check_baseline_level_readiness,
    check_target_level_presence,
    check_target_level_range,
    check_target_level_stability,
    check_target_level_freshness,
    check_target_level_coverage,
    check_target_level_consistency,
    check_target_level_risk,
    check_target_level_confidence,
    check_target_level_dependency,
    check_target_level_readiness,
    check_profile_missing_rate_presence,
    check_profile_missing_rate_range,
    check_profile_missing_rate_stability,
    check_profile_missing_rate_freshness,
    check_profile_missing_rate_coverage,
    check_profile_missing_rate_consistency,
    check_profile_missing_rate_risk,
    check_profile_missing_rate_confidence,
    check_profile_missing_rate_dependency,
    check_profile_missing_rate_readiness,
    check_mentor_capacity_presence,
    check_mentor_capacity_range,
    check_mentor_capacity_stability,
    check_mentor_capacity_freshness,
    check_mentor_capacity_coverage,
    check_mentor_capacity_consistency,
    check_mentor_capacity_risk,
    check_mentor_capacity_confidence,
    check_mentor_capacity_dependency,
    check_mentor_capacity_readiness,
    check_compute_access_presence,
    check_compute_access_range,
    check_compute_access_stability,
    check_compute_access_freshness,
    check_compute_access_coverage,
    check_compute_access_consistency,
    check_compute_access_risk,
    check_compute_access_confidence,
    check_compute_access_dependency,
    check_compute_access_readiness,
    check_language_support_presence,
    check_language_support_range,
    check_language_support_stability,
    check_language_support_freshness,
    check_language_support_coverage,
    check_language_support_consistency,
    check_language_support_risk,
    check_language_support_confidence,
    check_language_support_dependency,
    check_language_support_readiness,
    check_participation_consent_presence,
    check_participation_consent_range,
    check_participation_consent_stability,
    check_participation_consent_freshness,
    check_participation_consent_coverage,
    check_participation_consent_consistency,
    check_participation_consent_risk,
    check_participation_consent_confidence,
    check_participation_consent_dependency,
    check_participation_consent_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
