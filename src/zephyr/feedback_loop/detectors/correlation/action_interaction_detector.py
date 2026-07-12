# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.action_interaction_detector
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_action_interaction_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Action Interaction Detector — v0.38.0 R472

Blindspot: Multiple simultaneous FLE actions interfere with each other —
"polypharmacy" for automated fixes. Action A + Action B together produce
unexpected side effects that neither produces alone.

Risk: R472 — Two repairs undo each other; combined side effects create new
anomalies; FLE oscillates between contradictory fixes without realizing
interaction is the root cause.

Mitigation: Build pairwise action interaction matrix. Track co-occurring
actions within configurable time window. When two actions together produce
negative outcomes while individually they're effective -> flag interaction.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ActionInteractionDetector:
    interaction_window: float = 300.0
    min_co_occurrence: int = 3

    active_actions: dict[str, float] = field(default_factory=dict)
    interaction_matrix: dict[str, dict[str, list[float]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )
    interaction_alerts: list[dict] = field(default_factory=list)

    def record_action(self, action_id: str, action_type: str, outcome_score: float) -> None:
        now = time.time()
        self.active_actions = {k: v for k, v in self.active_actions.items() if now - v < self.interaction_window}
        self.active_actions[action_type] = now

        co_occurring = [a for a in self.active_actions if a != action_type]
        for co_action in co_occurring:
            pair = tuple(sorted([action_type, co_action]))
            key_a, key_b = pair
            if key_b not in self.interaction_matrix[key_a]:
                self.interaction_matrix[key_a][key_b] = []
            self.interaction_matrix[key_a][key_b].append(outcome_score)
            if len(self.interaction_matrix[key_a][key_b]) > 100:
                self.interaction_matrix[key_a][key_b] = self.interaction_matrix[key_a][key_b][-100:]

    def detect_interaction(self) -> list[dict]:
        alerts = []
        for action_a in self.interaction_matrix:
            for action_b in self.interaction_matrix[action_a]:
                scores = self.interaction_matrix[action_a][action_b]
                if len(scores) < self.min_co_occurrence:
                    continue
                mean_score = sum(scores) / len(scores)
                if mean_score < -0.3:
                    alerts.append(
                        {
                            "action_a": action_a,
                            "action_b": action_b,
                            "co_occurrence_count": len(scores),
                            "mean_outcome": round(mean_score, 3),
                            "severity": "HIGH" if mean_score < -0.6 else "MEDIUM",
                            "recommendation": "sequentialize_actions" if mean_score < -0.6 else "increase_cooldown",
                        }
                    )

        if alerts:
            self.interaction_alerts.extend(alerts)
        return alerts

    def get_interaction_heatmap(self) -> dict:
        heatmap = {}
        for action_a in self.interaction_matrix:
            for action_b in self.interaction_matrix[action_a]:
                scores = self.interaction_matrix[action_a][action_b]
                if len(scores) >= self.min_co_occurrence:
                    key = f"{action_a}+{action_b}"
                    heatmap[key] = {
                        "count": len(scores),
                        "mean_outcome": round(sum(scores) / len(scores), 3),
                    }
        return heatmap

    def clear_stale(self, max_age: float = 86400.0) -> int:
        before = len(self.interaction_alerts)
        cutoff = time.time() - max_age
        self.interaction_alerts = [a for a in self.interaction_alerts if a.get("ts", 0) > cutoff]
        return before - len(self.interaction_alerts)
