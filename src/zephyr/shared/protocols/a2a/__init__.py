# [A_module] module_id=MOD-SHR_a2a | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a
# [INVARIANTS] a2a contains only Protocol interfaces and data contracts; no concrete implementations; no imports from zephyr.infrastructure or zephyr.integration
# [MODIFY-GUARD] no concrete implementations; no cross-domain imports
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] zephyr.integration.agent_communication; zephyr.infrastructure.a2a_protocol; zephyr.integration.mcp.gateway_server
# [ERROR_CONTRACT] import errors only
# [TESTS] tests/test_shared_protocols.py
# [TTL] permanent

"""A2A Protocol — shared interface definitions.

Canonical location for Agent-to-Agent protocol interfaces and data contracts.
Both D-ORCH (orchestration) and D-INFRA (infrastructure) depend on this module
for type-level agreements, breaking the direct D-ORCH -> D-INFRA dependency.
"""

from zephyr.shared.protocols.a2a.a2a_coordination import (
    AgentRole,
    DispatchedTask,
    MergeStrategy,
    ResultMerge,
    TaskDispatchProtocol,
    TaskStatus,
)
from zephyr.shared.protocols.a2a.a2a_governance import (
    A2AGovernanceRecord,
    GovernanceAdapterProtocol,
    Phase4HoldProtocol,
)
from zephyr.shared.protocols.a2a.a2a_protocol import (
    A2ACommunication,
    A2ACommunicationProtocol,
    MessageType,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)
from zephyr.shared.protocols.a2a.a2a_registry import (
    A2ARegistryProtocol,
    AgentCapability,
    AgentCard,
    IdentityVerifierProtocol,
)
from zephyr.shared.protocols.a2a.a2a_schemas import (
    A2AMessage,
    A2AMessagePart,
    A2AStateMachine,
    A2ATask,
    A2ATaskStatus,
    ContextPackage,
    HandoffManagerProtocol,
    HandoffRecord,
    MessageRouterProtocol,
    PartType,
    PushNotifierProtocol,
)

# DM-367: re-export module names for audit registration
from . import a2a_coordination, a2a_governance, a2a_protocol, a2a_registry, a2a_schemas

__all__ = [
    "A2ACommunication",
    "A2ACommunicationProtocol",
    "A2AGovernanceRecord",
    "A2AMessage",
    "A2AMessagePart",
    "A2ARegistryProtocol",
    "A2AStateMachine",
    "A2ATask",
    "A2ATaskStatus",
    "AgentCapability",
    "AgentCard",
    "AgentRole",
    "ContextPackage",
    "DispatchedTask",
    "GovernanceAdapterProtocol",
    "HandoffManagerProtocol",
    "HandoffRecord",
    "IdentityVerifierProtocol",
    "MergeStrategy",
    "MessageRouterProtocol",
    "MessageType",
    "PartType",
    "Phase4HoldProtocol",
    "PushNotifierProtocol",
    "ResultMerge",
    "SecurityContext",
    "SecurityDecision",
    "SecurityResult",
    "TaskDispatchProtocol",
    "TaskStatus",
    "a2a_coordination",
    "a2a_governance",
    "a2a_protocol",
    "a2a_registry",
    "a2a_schemas",
]

__version__ = "0.1.0"
