# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.drift.gradual_poisoning_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_gradual_poisoning_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Gradual Poisoning Detector — v0.15.0 R210

Blindspot: Attacker slowly poisons training data; drift too gradual for single-window detection.
Risk: R210 — 30-day slow poisoning corrupts FLE behavior; detector sees "normal" in short windows.

Mitigation: Long-term trend analysis with cumulative deviation tracking across multiple time scales.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class PoisoningSignal:
    short_term_mean: float = 0.0
    long_term_mean: float = 0.0
    cumulative_deviation: float = 0.0


@dataclass
class GradualPoisoningDetector:
    short_window: deque[float] = field(default_factory=lambda: deque(maxlen=100))
    long_window: deque[float] = field(default_factory=lambda: deque(maxlen=1000))
    threshold: float = 3.0

    def observe(self, value: float) -> PoisoningSignal:
        self.short_window.append(value)
        self.long_window.append(value)
        st_mean = sum(self.short_window) / len(self.short_window) if self.short_window else value
        lt_mean = sum(self.long_window) / len(self.long_window) if self.long_window else value
        return PoisoningSignal(
            short_term_mean=st_mean, long_term_mean=lt_mean, cumulative_deviation=abs(st_mean - lt_mean)
        )

    def is_poisoned(self) -> bool:
        if len(self.long_window) < 100:
            return False
        signal = self.observe(0.0)
        return signal.cumulative_deviation > self.threshold
