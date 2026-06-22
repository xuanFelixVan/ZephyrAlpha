# [A_module] module_id=MOD-ORC_agent_communication | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a
# [INVARIANTS] all symbols imported from zephyr.shared.protocols.a2a; no direct imports from zephyr.infrastructure
# [MODIFY-GUARD] no direct infrastructure imports
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""
L01 Orchestration — A2A Protocol 模块 (MOD-ORCH-xxx)

Interface shim: all symbols re-exported from
zephyr.shared.protocols.a2a (core interfaces and data contracts).

DM-384: Removed direct dependency on zephyr.infrastructure.a2a_protocol.
All shared types now come from zephyr.shared.protocols.a2a.
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
    ContextPackage,
    DispatchedTask,
    GovernanceAdapterProtocol,
    HandoffManagerProtocol,
    HandoffRecord,
    IdentityVerifierProtocol,
    MergeStrategy,
    MessageRouterProtocol,
    MessageType,
    PartType,
    Phase4HoldProtocol,
    PushNotifierProtocol,
    ResultMerge,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
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
    "layer1_discovery",
    "layer2_communication",
]

__version__ = "0.10.0"

_SUBPACKAGES = [
    "layer1_discovery",
    "layer2_communication",
]


def __getattr__(name: str):
    if name in _SUBPACKAGES:
        import importlib

        mod = importlib.import_module(f"zephyr.shared.protocols.a2a.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
