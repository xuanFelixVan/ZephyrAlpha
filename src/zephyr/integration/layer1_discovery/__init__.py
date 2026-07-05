# [A_module] module_id=MOD-ORC_layer1_discovery | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export from shared protocols
from zephyr.shared.protocols.a2a.a2a_registry import *  # noqa: F403

__all__ = [
    "A2ARegistryProtocol",
    "AgentCapability",
    "AgentCard",
    "IdentityVerifierProtocol",
]

__version__ = "0.10.0"
