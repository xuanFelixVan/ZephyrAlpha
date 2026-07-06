# [A_module] module_id=MOD-INF_layer1_discovery | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer1_discovery
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Layer 1: 发现+身份 — Agent Card 模型, AGENTS.md 注册, JWT 身份验证"""

from zephyr.shared.protocols.a2a.a2a_registry import AgentCapability, AgentCard

from . import a2a_registry, agent_card, identity_verifier
from .a2a_registry import A2ARegistry
from .identity_verifier import IdentityVerifier

__all__ = [
    "A2ARegistry",
    "AgentCapability",
    "AgentCard",
    "IdentityVerifier",
    "a2a_registry",
    "agent_card",
    "identity_verifier",
]

__version__ = "0.10.0"
