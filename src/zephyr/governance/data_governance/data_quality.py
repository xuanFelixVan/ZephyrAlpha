# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.data_governance.data_quality
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ARCH-031: migrated from governance/governance/data_quality.py to root (canonical per [MODULE] annotation)
from enum import Enum
from typing import Final

from pydantic import BaseModel


class DQDimension(str, Enum):
    # B4 SLA 四维度：COMPLETENESS / CONSISTENCY / FRESHNESS / ANOMALY
    # 扩展维度：ACCURACY / TIMELINESS / UNIQUENESS / VALIDITY
    COMPLETENESS = "Completeness"
    ACCURACY = "Accuracy"
    ANOMALY = "Anomaly"            # B4: 异常检测（时序突变/离群）
    CONSISTENCY = "Consistency"
    FRESHNESS = "Freshness"        # B4: 新鲜度（数据年龄，区别于 TIMELINESS 处理延迟）
    TIMELINESS = "Timeliness"
    UNIQUENESS = "Uniqueness"
    VALIDITY = "Validity"


class DQSpec(BaseModel):
    dimension: DQDimension
    label: str
    metric: str
    threshold: float = 0.95
    check_func: str = ""
    # 方向标记：True 表示 value 越小越健康（如 age_seconds、outlier_rate），
    # 此时 threshold 为"上限"。score_dq 据此决定 value/threshold 的方向，
    # 避免"年龄越大分越高"类荒谬结果。默认 False（value 越大越健康，threshold 为下限）。
    lower_is_better: bool = False


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
    DQDimension.ANOMALY: DQSpec(
        dimension=DQDimension.ANOMALY,
        label="异常检测",
        metric="zscore_outlier_rate",  # 离群率，越小越好
        threshold=0.01,  # 离群率上限 1%（lower_is_better=True 下 threshold 为上限）
        check_func="check_anomaly",
        lower_is_better=True,
    ),
    DQDimension.CONSISTENCY: DQSpec(
        dimension=DQDimension.CONSISTENCY,
        label="一致性",
        metric="recon_diff",
        threshold=0.99,
        check_func="check_consistency",
    ),
    DQDimension.FRESHNESS: DQSpec(
        dimension=DQDimension.FRESHNESS,
        label="新鲜度",
        metric="age_seconds",  # 数据年龄 now-last_updated，越小越好
        threshold=60.0,  # 数据年龄上限 60s（lower_is_better=True 下 threshold 为上限）
        check_func="check_freshness",
        lower_is_better=True,
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
    # lower_is_better=True：value 越小越健康，得分 = 1 - min(1, value/threshold)
    # lower_is_better=False：value 越大越健康，得分 = min(1, value/threshold)
    if spec.lower_is_better:
        return max(0.0, 1.0 - min(1.0, value / spec.threshold))
    return min(1.0, value / spec.threshold)


DQ_DIM_COUNT: Final[int] = 8  # B4 四维度 + 扩展四维度
