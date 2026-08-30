# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.contract_drift_detector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] z-score>5.0判定为漂移;baseline_std==0时使用0.001防止除零;DriftAlert写入_drift_buffer
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md;src/zephyr/infra_ops/observability/contract_metrics.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] baseline不存在->返回None;z-score<=5.0->返回None
# [TESTS] tests/telemetry/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
contract_drift_detector — 契约漂移检测器。

从 MOD-INF-015 contract_metrics.py 迁移而来（v3.0.0 委托决策）。
职责归属：MOD-INF-023 (Drift Detector)。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: contract_id 参数
#   fields: 参数 contract_id，类型注解 str
#   code: contract_drift_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: field_name 参数
#   fields: 参数 field_name，类型注解 str
#   code: contract_drift_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: current_value 参数
#   fields: 参数 current_value，类型注解 float
#   code: contract_drift_detector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: baseline_median 参数
#   fields: 参数 baseline_median，类型注解 float | None
#   code: contract_drift_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① detect_contract_drift
#   name_en: detect_contract_drift
#   intro: detect_contract_drift(contract_id, field_name, current_valu…
#   desc: 源码 L85-L129
#   inputs: contract_id field_name current_value baseline_median baseline_std fie…
#   outputs: DriftAlert | None
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: DriftAlert | None
#   name_en: DriftAlert | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

_logger = logging.getLogger(__name__)


@dataclass
class DriftAlert:
    contract_id: str
    field_name: str
    statistic: str = "z_score"
    current_value: float = 0.0
    baseline_value: float = 0.0
    deviation_pct: float = 0.0


def detect_contract_drift(
    contract_id: str,
    field_name: str,
    current_value: float,
    baseline_median: float | None = None,
    baseline_std: float | None = None,
    field_baselines: dict | None = None,
    drift_buffer: list | None = None,
) -> DriftAlert | None:
    if baseline_median is None or baseline_std is None:
        key = f"{contract_id}:{field_name}"
        if field_baselines and key in field_baselines:
            baseline_median = field_baselines[key].get("median", 0.0)
            baseline_std = field_baselines[key].get("std", 1.0)
        else:
            return None

    if (
        abs(baseline_std) < 1e-9
    ):  # 5.167.5 修复: 浮点==0比较改 < epsilon (路径漂移 governance/->governance/drift_detection/)
        baseline_std = 0.001

    deviation = abs(current_value - baseline_median) / baseline_std

    if deviation > 5.0:
        deviation_pct = abs(current_value - baseline_median) / max(abs(baseline_median), 0.001) * 100
        alert = DriftAlert(
            contract_id=contract_id,
            field_name=field_name,
            statistic="z_score",
            current_value=current_value,
            baseline_value=baseline_median,
            deviation_pct=deviation_pct,
        )
        if drift_buffer is not None:
            drift_buffer.append(alert)
        _logger.warning(
            "[Drift] %s.%s z-score=%.1f — 可能发生契约漂移",
            contract_id,
            field_name,
            deviation,
        )
        return alert

    return None
