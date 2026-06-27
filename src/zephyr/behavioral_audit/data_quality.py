# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.data_quality
# [DOMAIN] D-SECURITY
# [DEPENDENCIES] zephyr.behavioral_audit.__init__
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_data_quality | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

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


DQ_SPECS: dict[DQDimension, DQSpec] = {
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


DQ_DIM_COUNT: int = 6
