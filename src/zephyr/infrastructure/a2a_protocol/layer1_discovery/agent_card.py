# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer1_discovery.agent_card
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_registry
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] core types imported from zephyr.shared.protocols.a2a; no duplicate definitions
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_agent_card | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Agent Card 模型 — A2A Layer 1 Discovery

Core types (AgentCard, AgentCapability) are imported from
zephyr.shared.protocols.a2a.a2a_registry.
"""

from zephyr.shared.protocols.a2a.a2a_registry import AgentCapability, AgentCard  # noqa: F401
