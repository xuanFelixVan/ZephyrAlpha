# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.integration.governance.__init___from_orches
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_protocol; zephyr.integration.governance.auditor; zephyr.integration.governance.governance_adapter; zephyr.integration.governance.phase_hold; zephyr.integration.governance.protocol
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# Re-export from shared protocols
from zephyr.shared.protocols.a2a.a2a_protocol import *  # noqa: F403

# DM-367: re-export local shim modules
from . import auditor, governance_adapter, phase_hold, protocol

__all__ = [
    "A2ACommunication",
    "A2ACommunicationProtocol",
    "MessageType",
    "SecurityContext",
    "SecurityDecision",
    "SecurityResult",
    "auditor",
    "governance_adapter",
    "phase_hold",
    "protocol",
]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-025"
