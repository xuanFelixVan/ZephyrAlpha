# [A_module] module_id=MOD-SHR_protocols | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols
# [INVARIANTS] protocols contains only Protocol interfaces and data contracts; no concrete implementations
# [MODIFY-GUARD] no concrete implementations in this package
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] zephyr.integration.agent_communication; zephyr.infrastructure.a2a_protocol
# [ERROR_CONTRACT] import errors only — no runtime exceptions from Protocol definitions
# [TESTS] tests/test_shared_protocols.py
# [TTL] permanent

"""Shared Protocols — cross-domain interface definitions.

This package contains typing.Protocol interfaces and Pydantic data contracts
shared between orchestration (D-ORCH) and infrastructure (D-INFRA) domains.
No concrete implementations live here — only interface contracts.
"""

from zephyr.shared.protocols.a2a import (
    A2ACommunication,
    A2ACommunicationProtocol,
    A2AGovernanceRecord,
    A2AMessage,
    A2AMessagePart,
    A2ARegistryProtocol,
    A2AStateMachine,
    A2ATask,
    A2ATaskStatus,
    AgentCapability,
    AgentCard,
    AgentRole,
    DispatchedTask,
    GovernanceAdapterProtocol,
    IdentityVerifierProtocol,
    MergeStrategy,
    MessageType,
    PartType,
    Phase4HoldProtocol,
    ResultMerge,
    TaskDispatchProtocol,
    TaskStatus,
)

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
    "DispatchedTask",
    "GovernanceAdapterProtocol",
    "IdentityVerifierProtocol",
    "MergeStrategy",
    "MessageType",
    "PartType",
    "Phase4HoldProtocol",
    "ResultMerge",
    "TaskDispatchProtocol",
    "TaskStatus",
]
