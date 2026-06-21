# [A_module] module_id=MOD-INF_legacy_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §3

# [MODULE] zephyr.infrastructure.a2a_protocol.legacy_protocol

# [INVARIANTS] core types imported from zephyr.shared.protocols.a2a; no duplicate definitions

# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md

# [CONSUMERS] zephyr.infrastructure.a2a_protocol

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 agent_id 和 protocol_layer

# [TESTS] tests/test_a2a_protocol.py

"""[BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §3

G-CT-008 — A2ACommunication Pydantic V2 BaseModel agent-to-agent 通信数据结构.

Core types (MessageType, A2ACommunication) are imported from
zephyr.shared.protocols.a2a.a2a_protocol.
"""

from __future__ import annotations

from zephyr.shared.protocols.a2a.a2a_protocol import MessageType, A2ACommunication  # noqa: F401
