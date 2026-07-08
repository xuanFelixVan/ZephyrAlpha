# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.regime_gain_scheduling
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
# [A_module] module_id=MOD-UNK_regime_gain_scheduling | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Regime Gain Scheduling — v0.37.0 R453

Blindspot: FLE uses uniform sensitivity across all market regimes;
high-vol regimes cause false alarms; low-vol regimes miss signals.

Risk: R453 — One-size-fits-all sensitivity causes regime-specific blind spots.

Mitigation: Per-regime gain scheduling. Map current market regime to gain multiplier.
Low vol -> higher sensitivity; high vol -> damped response to avoid noise-triggered actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MarketRegime(str, Enum):
    CALM = "CALM"
    NORMAL = "NORMAL"
    VOLATILE = "VOLATILE"
    CRISIS = "CRISIS"


@dataclass
class RegimeGainScheduling:
    gain_map: dict[str, float] = field(
        default_factory=lambda: {
            "CALM": 1.5,
            "NORMAL": 1.0,
            "VOLATILE": 0.6,
            "CRISIS": 0.3,
        }
    )

    current_regime: MarketRegime = MarketRegime.NORMAL
    current_gain: float = 1.0
    regime_transition_count: int = 0

    def set_regime(self, regime: MarketRegime) -> float:
        if regime != self.current_regime:
            self.regime_transition_count += 1
        self.current_regime = regime
        self.current_gain = self.gain_map.get(regime.value, 1.0)
        return self.current_gain

    def apply_gain(self, raw_score: float) -> float:
        return raw_score * self.current_gain

    def detect_regime_from_volatility(self, vol_percentile: float) -> MarketRegime:
        if vol_percentile > 0.9:
            return MarketRegime.CRISIS
        elif vol_percentile > 0.7:
            return MarketRegime.VOLATILE
        elif vol_percentile < 0.2:
            return MarketRegime.CALM
        return MarketRegime.NORMAL
