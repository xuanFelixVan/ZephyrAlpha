# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.health.fle_self_slo_metrics
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_fle_self_slo_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""FLE Self SLO Metrics — v0.17.0+ R249-R254

七维SLO自观指标：
  - MTTD: Mean-Time-To-Detect (异常发生->FLE检测)
  - MTTR: Mean-Time-To-Repair (FLE检测->修复完成)
  - MTTI: Mean-Time-To-Identify (异常发生->根因识别)
  - FP_RATE: 假阳性率
  - AVAILABILITY: FLE自体可用性
  - NET_VALUE: 净价值 (修复收益 - 修复成本)
  - ACTION_HARMFUL_RATE: 有害修复率 (Verdict.HARMFUL / total actions)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class FLESLOMetric:
    dimension: str
    current: float
    target: float
    unit: str = ""


@dataclass
class FLESelfSLO:
    mttd_target: float = 60.0
    mttr_target: float = 300.0
    mtti_target: float = 300.0
    fp_rate_target: float = 0.1
    availability_target: float = 99.9
    harmful_rate_target: float = 0.05

    detection_events: list[tuple[float, float]] = field(default_factory=list)
    repair_events: list[tuple[float, float]] = field(default_factory=list)
    total_detections: int = 0
    false_positives: int = 0
    total_repairs: int = 0
    harmful_repairs: int = 0
    total_cost: float = 0.0
    total_benefit: float = 0.0
    uptime_start: float = field(default_factory=time.time)
    downtime: float = 0.0

    def current_metrics(self) -> list[FLESLOMetric]:
        mttd = 0.0
        if self.detection_events:
            mttd = sum(d - a for a, d in self.detection_events) / len(self.detection_events)
        mttr = 0.0
        if self.repair_events:
            mttr = sum(r - d for d, r in self.repair_events) / len(self.repair_events)
        fp_rate = self.false_positives / max(self.total_detections, 1)
        total_runtime = max(time.time() - self.uptime_start - self.downtime, 1.0)
        availability = max(0.0, (total_runtime - self.downtime) / total_runtime * 100.0)
        harmful_rate = self.harmful_repairs / max(self.total_repairs, 1)
        net_value = self.total_benefit - self.total_cost
        return [
            FLESLOMetric("MTTD", mttd, self.mttd_target, "s"),
            FLESLOMetric("MTTR", mttr, self.mttr_target, "s"),
            FLESLOMetric("MTTI", 0.0, self.mtti_target, "s"),
            FLESLOMetric("FP_RATE", fp_rate, self.fp_rate_target, "%"),
            FLESLOMetric("AVAILABILITY", availability, self.availability_target, "%"),
            FLESLOMetric("NET_VALUE", net_value, 0.0, "$"),
            FLESLOMetric("HARMFUL_RATE", harmful_rate, self.harmful_rate_target, "%"),
        ]
