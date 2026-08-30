# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""
Layer 1: 发现+身份 — Agent Card 模型, AGENTS.md 注册, JWT 身份验证

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: AgentCapability, AgentCard, A2ARegistry, IdentityVerifier
#   code: __init__.py import L43
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 A2ARegistry, AgentCapability, AgentCard, IdentityVerifier, a2a_registry, ag…
#   desc: __init__ import L43；__all__ 7 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（7 符号）
#   name_en: __all__
#   intro: A2ARegistry, AgentCapability, AgentCard, IdentityVerifier, a2a_registry, agent_…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
