# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution.online_feature_importance
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_online_feature_importance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Online Feature Importance — v0.7.0 R73

Blindspot: Feature importance computed offline; stale in real-time.
Risk: R73 — Importance rankings lag; wrong features drive diagnosis.
"""

from dataclasses import dataclass, field


@dataclass
class OnlineFeatureImportance:
    scores: dict[str, float] = field(default_factory=dict)

    def update(self, feature: str, importance: float) -> None:
        self.scores[feature] = importance
