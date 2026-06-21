# [A_module] module_id=MOD-ORC_layer1_discovery | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# Re-export from shared protocols
from zephyr.shared.protocols.a2a.a2a_registry import *  # noqa: F401,F403

# DM-367: re-export local shim modules
from . import a2a_registry, identity_verifier  # noqa: F401

__all__ = [
    'AgentCard', 'AgentCapability',
    'A2ARegistryProtocol',
    'IdentityVerifierProtocol',
    'a2a_registry', 'identity_verifier',
]

__version__ = "0.10.0"
