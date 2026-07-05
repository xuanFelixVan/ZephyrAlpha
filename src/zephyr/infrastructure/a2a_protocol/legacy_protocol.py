# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] zephyr.infrastructure.a2a_protocol.legacy_protocol
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_protocol
# [CONSUMERS] zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] core types imported from zephyr.shared.protocols.a2a; no duplicate definitions
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 agent_id 和 protocol_layer
# [TESTS] tests/test_a2a_protocol.py
# [A_module] module_id=MOD-INF_legacy_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §3

G-CT-008 — A2ACommunication Pydantic V2 BaseModel agent-to-agent 通信数据结构.

Core types (MessageType, A2ACommunication) are imported from
zephyr.shared.protocols.a2a.a2a_protocol.
"""

from __future__ import annotations

from zephyr.shared.protocols.a2a.a2a_protocol import A2ACommunication, MessageType  # noqa: F401
