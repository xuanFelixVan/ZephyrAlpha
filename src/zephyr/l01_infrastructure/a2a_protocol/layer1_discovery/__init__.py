# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §
"""Layer 1: 发现+身份 — Agent Card 模型, AGENTS.md 注册, JWT 身份验证"""

from .agent_card import AgentCard, AgentCapability
from .a2a_registry import A2ARegistry
from .identity_verifier import IdentityVerifier

__all__ = [
    'AgentCard', 'AgentCapability',
    'A2ARegistry',
    'IdentityVerifier',
    'a2a_registry', 'agent_card', 'identity_verifier',
]

__version__ = "0.10.0"