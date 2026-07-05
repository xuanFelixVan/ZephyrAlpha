# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_schemas
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_schemas
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
# [A_module] module_id=MOD-INF_a2a_schemas | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A Message/Part 系统 — Layer 2 Communication

Core types (PartType, A2AMessagePart, A2AMessage) are imported from
zephyr.shared.protocols.a2a.a2a_schemas.
"""

from zephyr.shared.protocols.a2a.a2a_schemas import A2AMessage, A2AMessagePart, PartType  # noqa: F401
