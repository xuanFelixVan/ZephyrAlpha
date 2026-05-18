# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.collectors.knowledge_capture

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Knowledge Capture — v0.4.0 R30

Blindspot: Successful diagnoses not captured for future reuse.
Risk: R30 — Repeated diagnosis of same anomaly wastes resources.
"""
from dataclasses import dataclass, field

@dataclass
class KnowledgeCapture:
    captured: list[dict] = field(default_factory=list)

    def capture(self, diagnosis: dict) -> None:
        self.captured.append(diagnosis)
