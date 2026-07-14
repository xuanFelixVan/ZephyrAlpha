# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.data_governance.data_quality
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_data_quality | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ARCH-031: migrated from governance/governance/data_quality.py to root (canonical per [MODULE] annotation)
from typing import Final

from enum import Enum

from pydantic import BaseModel


class DQDimension(str, Enum):
    COMPLETENESS = "Completeness"
    ACCURACY = "Accuracy"
    CONSISTENCY = "Consistency"
    TIMELINESS = "Timeliness"
    UNIQUENESS = "Uniqueness"
    VALIDITY = "Validity"


class DQSpec(BaseModel):
    dimension: DQDimension
    label: str
    metric: str
    threshold: float = 0.95
    check_func: str = ""


DQ_SPECS: Final[dict[DQDimension, DQSpec]] = {
    DQDimension.COMPLETENESS: DQSpec(
        dimension=DQDimension.COMPLETENESS,
        label="完整性",
        metric="missing_pct",
        threshold=0.99,
        check_func="check_completeness",
    ),
    DQDimension.ACCURACY: DQSpec(
        dimension=DQDimension.ACCURACY,
        label="准确性",
        metric="deviation_sigma",
        threshold=0.95,
        check_func="check_accuracy",
    ),
    DQDimension.CONSISTENCY: DQSpec(
        dimension=DQDimension.CONSISTENCY,
        label="一致性",
        metric="recon_diff",
        threshold=0.99,
        check_func="check_consistency",
    ),
    DQDimension.TIMELINESS: DQSpec(
        dimension=DQDimension.TIMELINESS,
        label="时效性",
        metric="latency_ms",
        threshold=0.95,
        check_func="check_timeliness",
    ),
    DQDimension.UNIQUENESS: DQSpec(
        dimension=DQDimension.UNIQUENESS,
        label="唯一性",
        metric="duplicate_rate",
        threshold=0.99,
        check_func="check_uniqueness",
    ),
    DQDimension.VALIDITY: DQSpec(
        dimension=DQDimension.VALIDITY,
        label="有效性",
        metric="schema_violation_rate",
        threshold=0.99,
        check_func="check_validity",
    ),
}


def get_dq_spec(dim: DQDimension) -> DQSpec | None:
    return DQ_SPECS.get(dim)


def score_dq(dim: DQDimension, value: float) -> float:
    spec = DQ_SPECS.get(dim)
    if spec is None:
        return 0.0
    return min(1.0, value / spec.threshold)


DQ_DIM_COUNT: Final[int] = 6
