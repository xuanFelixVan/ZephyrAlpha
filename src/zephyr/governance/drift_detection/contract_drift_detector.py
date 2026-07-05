# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.contract_drift_detector
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/infra_ops/observability/contract_metrics.py(委托调用)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] z-score>5.0判定为漂移;baseline_std==0时使用0.001防止除零;DriftAlert写入_drift_buffer
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md;src/zephyr/infra_ops/observability/contract_metrics.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] baseline不存在→返回None;z-score<=5.0→返回None
# [TESTS] tests/telemetry/
# [A_module] module_id=MOD-SEC_contract_drift_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""contract_drift_detector — 契约漂移检测器。

从 MOD-INF-015 contract_metrics.py 迁移而来（v3.0.0 委托决策）。
职责归属：MOD-INF-023 (Drift Detector)。
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

    if abs(baseline_std) < 1e-9:  # 5.167.5 修复: 浮点==0比较改 < epsilon (路径漂移 governance/→governance/drift_detection/)
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
