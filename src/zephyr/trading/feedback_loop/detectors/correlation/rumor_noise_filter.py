# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation.rumor_noise_filter
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_rumor_noise_filter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Rumor Noise Filter — v0.37.0 R460

Blindspot: FLE processes unverified market news/rumors as factual signals;
triggers unnecessary actions based on noise.

Risk: R460 — Rumor-driven FLE actions cause false trades or premature shutdown.

Mitigation: Multi-source corroboration requirement. News must be confirmed
by ≥2 independent sources before FLE acts on it. Unconfirmed signals
→ logging only, no actions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class SignalCredibility(str, Enum):
    CONFIRMED = "CONFIRMED"
    UNVERIFIED = "UNVERIFIED"
    RUMOR = "RUMOR"
    FALSE = "FALSE"


@dataclass
class RumorNoiseFilter:
    min_sources: int = 2
    corroboration_window: float = 300.0

    pending_signals: dict[str, list[dict]] = field(default_factory=dict)

    def ingest_signal(self, signal_id: str, source: str, content: str) -> SignalCredibility:
        now = time.time()

        if signal_id not in self.pending_signals:
            self.pending_signals[signal_id] = []

        self.pending_signals[signal_id] = [
            s for s in self.pending_signals[signal_id] if now - s["ts"] < self.corroboration_window
        ]

        self.pending_signals[signal_id].append(
            {
                "source": source,
                "content": content,
                "ts": now,
            }
        )

        unique_sources = {s["source"] for s in self.pending_signals[signal_id]}

        if len(unique_sources) >= self.min_sources:
            return SignalCredibility.CONFIRMED
        return SignalCredibility.UNVERIFIED

    def can_act_on(self, signal_id: str) -> bool:
        return (
            self.ingest_signal(signal_id, "", "") == SignalCredibility.CONFIRMED
            if signal_id in self.pending_signals
            else False
        )

    def get_unverified_count(self) -> int:
        return sum(
            1 for sources in self.pending_signals.values() if len({s["source"] for s in sources}) < self.min_sources
        )
