from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class DomainSignal:
    code: str
    score: float
    severity: str
    evidence: dict[str, Any]

def number(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = float(payload.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if value != value or value in (float('inf'), float('-inf')) else value

def ratio(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    value = number(payload, key, default)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def pathway_feasibility(payload: Mapping[str, Any]) -> DomainSignal:
    baseline=max(0.0,number(payload,'baseline_level')); target=max(0.0,number(payload,'target_level'))
    gap=max(0.0,target-baseline); hours=max(0.0,number(payload,'staff_hours')); staff=max(1.0,number(payload,'staff_count',1))
    mentor=ratio(payload,'mentor_capacity'); compute=ratio(payload,'compute_access'); language=ratio(payload,'language_support'); consent=ratio(payload,'participation_consent'); missing=ratio(payload,'profile_missing_rate')
    intensity=min(1.0,hours/staff/max(1.0,gap*12.0)); bottleneck=min(mentor,compute,language,consent)
    score=clamp(intensity*.34+bottleneck*.38+(1-missing)*.18+(1-min(1.0,gap/10.0))*.10)
    severity='critical' if gap>0 and bottleneck<.2 else 'warning' if missing>.35 or intensity<.45 else 'info'
    return DomainSignal('pathway_feasibility',score,severity,{'capability_gap':gap,'intensity':intensity,'resource_bottleneck':bottleneck,'missing_rate':missing})

def peer_distribution(records: Iterable[Any], group_field: str='country_group')->dict[str,Any]:
    rows=[pathway_feasibility(getattr(r,'payload',r)) for r in records]
    return {'count':len(rows),'blocked':sum(s.severity=='critical' for s in rows),'average':sum(s.score for s in rows)/len(rows) if rows else 0.0}

def augment_context(record:Any,repository:Any)->dict[str,Any]:
    signal=pathway_feasibility(record.payload); peers=peer_distribution(repository.list_records())
    return {'domain_signal':signal.score,'domain_severity':signal.severity,'blocked_pathways':peers['blocked'],'peer_average':peers['average']}
