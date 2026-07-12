# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.model_rotation
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
# [A_module] module_id=MOD-UNK_model_rotation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Model Rotation — v0.9.0 R125

Blindspot: Single model reliance creates SPOF in diagnosis pipeline.
Risk: R125 — Model degradation without rotation causes systemic diagnosis failure.
"""

from dataclasses import dataclass, field


@dataclass
class ModelRotation:
    models: list[str] = field(default_factory=list)
    active: str = ""

    def rotate(self) -> str:
        if not self.models:
            return self.active
        idx = (self.models.index(self.active) + 1) % len(self.models) if self.active in self.models else 0
        self.active = self.models[idx]
        return self.active
