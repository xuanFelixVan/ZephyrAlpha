# [A_module] module_id=MOD-ORC_layer1_discovery | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export from shared protocols
# 5.93.6 修复：import * → 显式导入
from zephyr.shared.protocols.a2a.a2a_registry import (
    A2ARegistryProtocol,
    AgentCapability,
    AgentCard,
    IdentityVerifierProtocol,
)

__all__ = [
    "A2ARegistryProtocol",
    "AgentCapability",
    "AgentCard",
    "IdentityVerifierProtocol",
]

__version__ = "0.10.0"
