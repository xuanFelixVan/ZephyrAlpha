# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.collectors.knowledge_injection

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Knowledge Injection — v0.8.0 R102

Blindspot: Human expert knowledge cannot be injected into FLE KB.
Risk: R102 — FLE relearns what owner already knows.
"""
from dataclasses import dataclass, field

@dataclass
class KnowledgeInjection:
    injected: list[dict] = field(default_factory=list)

    def inject(self, knowledge: dict) -> None:
        self.injected.append(knowledge)
