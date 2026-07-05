# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.toil_quantification
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
# [A_module] module_id=MOD-UNK_toil_quantification | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Toil Quantification — v0.37.0 R457

Blindspot: Repetitive manual operational tasks accumulate;
no measurement of toil prevents automation prioritization.

Risk: R457 — Rising toil silently consumes operator bandwidth;
burnout risk without visibility (Google SRE concept).

Mitigation: Classify FLE actions by automation level. Track manual-intervention
events. Compute toil ratio = manual_actions / total_actions. Escalate when
toil ratio exceeds 20% for any 7-day window.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ActionClass(str, Enum):
    FULLY_AUTOMATED = "FULLY_AUTOMATED"
    SEMI_AUTOMATED = "SEMI_AUTOMATED"
    MANUAL_REQUIRED = "MANUAL_REQUIRED"


@dataclass
class ToilQuantification:
    toil_threshold: float = 0.2
    window_days: int = 7

    action_history: list[dict] = field(default_factory=list)
    total_actions: int = 0
    manual_actions: int = 0
    current_toil_ratio: float = 0.0

    def record_action(self, action_class: ActionClass) -> float:
        now = time.time()
        self.total_actions += 1
        if action_class is ActionClass.MANUAL_REQUIRED:
            self.manual_actions += 1

        self.action_history.append(
            {
                "ts": now,
                "class": action_class.value,
            }
        )

        cutoff = now - self.window_days * 86400
        self.action_history = [a for a in self.action_history if a["ts"] > cutoff]

        window_manual = sum(1 for a in self.action_history if a["class"] == ActionClass.MANUAL_REQUIRED.value)
        window_total = len(self.action_history)
        self.current_toil_ratio = window_manual / max(window_total, 1)

        return self.current_toil_ratio

    def is_toil_excessive(self) -> bool:
        return self.current_toil_ratio > self.toil_threshold

    def get_top_toil_sources(self, top_n: int = 5) -> list[dict]:
        source_counts: dict[str, int] = {}
        for a in self.action_history:
            if a["class"] == ActionClass.MANUAL_REQUIRED.value:
                source_counts[a.get("source", "unknown")] = source_counts.get(a.get("source", "unknown"), 0) + 1
        return sorted(
            [{"source": k, "count": v} for k, v in source_counts.items()],
            key=lambda x: -x["count"],
        )[:top_n]
