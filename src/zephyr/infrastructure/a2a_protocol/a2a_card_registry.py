# [A_module] module_id=MOD-INF_a2a_card_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.a2a_card_registry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A Card Registry — 全局 Agent Card 注册单例"""

from .layer1_discovery.a2a_registry import A2ARegistry

card_registry = A2ARegistry()
