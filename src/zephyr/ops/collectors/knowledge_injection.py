# [A_module] module_id=MOD-UNK_knowledge_injection | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.collectors.knowledge_injection

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
