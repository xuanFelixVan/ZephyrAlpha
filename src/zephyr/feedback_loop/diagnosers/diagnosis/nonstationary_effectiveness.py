# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.diagnosis.nonstationary_effectiveness
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_nonstationary_effectiveness | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Nonstationary Effectiveness — v0.37.0 R455

Blindspot: FLE actions modeled under stationarity assumptions;
effectiveness collapses when data distribution shifts (e.g. post-breach, flash crash).

Risk: R455 — FLE continues applying ineffective actions after regime change.

Mitigation: Rolling-window effectiveness scoring. Compare recent action outcomes
against historical baseline. If rolling effectiveness drops >30% from baseline,
trigger diagnostic reset + model recalibration request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EffectivenessState(str, Enum):
    NOMINAL = "NOMINAL"
    DEGRADING = "DEGRADING"
    INEFFECTIVE = "INEFFECTIVE"


@dataclass
class NonstationaryEffectiveness:
    window_size: int = 50
    degradation_threshold: float = 0.3

    state: EffectivenessState = EffectivenessState.NOMINAL
    baseline_score: float = 0.8
    rolling_window: list[float] = field(default_factory=list)
    current_score: float = 0.8
    degradation_started_at: float = 0.0

    def record_outcome(self, success: bool) -> EffectivenessState:
        self.rolling_window.append(1.0 if success else 0.0)
        if len(self.rolling_window) > self.window_size:
            self.rolling_window = self.rolling_window[-self.window_size :]

        if len(self.rolling_window) >= 10:
            self.current_score = sum(self.rolling_window) / len(self.rolling_window)
            self.baseline_score = 0.9 * self.baseline_score + 0.1 * self.current_score

        if len(self.rolling_window) >= self.window_size:
            drop = (self.baseline_score - self.current_score) / max(self.baseline_score, 0.01)
            if drop > self.degradation_threshold:
                if self.state is not EffectivenessState.INEFFECTIVE:
                    import time

                    self.degradation_started_at = time.time()
                self.state = EffectivenessState.INEFFECTIVE
            elif drop > self.degradation_threshold * 0.5:
                self.state = EffectivenessState.DEGRADING
            else:
                self.state = EffectivenessState.NOMINAL

        return self.state

    def needs_recalibration(self) -> bool:
        return self.state is EffectivenessState.INEFFECTIVE
