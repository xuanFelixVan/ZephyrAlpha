# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.cognitive.cognitive_load_budget
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
# [A_module] module_id=MOD-UNK_cognitive_load_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Cognitive Load Budget — v0.16.0 R223

Blindspot: Owner decision fatigue unmodeled; notification rate constant regardless of owner state.
Risk: R223 — 1-person operator overwhelmed; critical alerts missed from context switching.

Mitigation: Owner cognitive load budget tracking with adaptive notification pacing.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class DecisionRecord:
    decision_id: str
    severity: int
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False


@dataclass
class CognitiveLoadBudget:
    max_decisions_per_hour: int = 12
    max_decisions_per_day: int = 50
    fatigue_weight_severity_high: float = 3.0
    decisions_hourly: list[float] = field(default_factory=list)
    decisions_daily: list[float] = field(default_factory=list)
    fatigue_score: float = 0.0

    def request(self, decision_id: str, severity: int) -> bool:
        now = time.time()
        self.decisions_hourly = [t for t in self.decisions_hourly if now - t < 3600]
        self.decisions_daily = [t for t in self.decisions_daily if now - t < 86400]
        weighted_hourly = sum(severity / 10.0 * self.fatigue_weight_severity_high for t in self.decisions_hourly)
        if weighted_hourly > self.max_decisions_per_hour:
            return False
        if len(self.decisions_daily) >= self.max_decisions_per_day:
            return False
        self.decisions_hourly.append(now)
        self.decisions_daily.append(now)
        self.fatigue_score = len(self.decisions_hourly) / self.max_decisions_per_hour
        return True

    def defer(self, decision_id: str, delay_seconds: float) -> None:
        pass
