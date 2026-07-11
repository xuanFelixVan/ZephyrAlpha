# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.health.dr_resilience_metrics
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_dr_resilience_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""DR Resilience Metrics — v0.17.0+ R231-R236

4 项 DR 指标采集：
  - R231 dr_drill_pass_rate: 最近 N 次 drill 的通过率
  - R232 rpo_violation_count: RPO 超限累计次数
  - R233 rto_violation_count: RTO 超限累计次数
  - R234 dr_recovery_time_trend: 历史恢复时间趋势
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class DRDrillRecord:
    drill_id: str
    timestamp: float
    rpo_seconds: float
    rto_seconds: float
    passed: bool
    rpo_target: float = 300.0
    rto_target: float = 900.0


@dataclass
class DRResilienceMetrics:
    history: deque[DRDrillRecord] = field(default_factory=lambda: deque(maxlen=100))
    rpo_violations: int = 0
    rto_violations: int = 0
    target_drill_interval_days: int = 90

    def record(self, record: DRDrillRecord) -> None:
        self.history.append(record)
        if record.rpo_seconds > record.rpo_target:
            self.rpo_violations += 1
        if record.rto_seconds > record.rto_target:
            self.rto_violations += 1

    def pass_rate(self) -> float:
        if not self.history:
            return 1.0
        return sum(1 for d in self.history if d.passed) / len(self.history)

    def days_since_last_drill(self) -> float:
        if not self.history:
            return float("inf")
        return (time.time() - self.history[-1].timestamp) / 86400.0

    def drill_overdue(self) -> bool:
        return self.days_since_last_drill() > self.target_drill_interval_days
