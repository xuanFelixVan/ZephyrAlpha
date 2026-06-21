# [A_module] module_id=MOD-GOV_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# Re-export from shared protocols
from zephyr.shared.protocols.a2a.a2a_protocol import *  # noqa: F401,F403

# DM-367: re-export local shim modules
from . import auditor, governance_adapter, phase_hold, protocol  # noqa: F401

__all__ = ['A2ACommunicationProtocol', 'MessageType', 'A2ACommunication',
           'SecurityDecision', 'SecurityContext', 'SecurityResult',
           'auditor', 'governance_adapter', 'phase_hold', 'protocol']

__version__ = "0.1.0"
__module_id__ = "MOD-INF-025"
