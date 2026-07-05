# [A_module] module_id=MOD-INF_a2a_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol
# [INVARIANTS] core types imported from zephyr.shared.protocols.a2a; no duplicate definitions
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
基础设施 Infrastructure — A2A Protocol 模块 (MOD-INF-025)

三层五协议总架构:
  Layer 1 (发现+身份): Agent Card, AGENTS.md 注册, JWT 身份
  Layer 2 (通信+任务): Task 状态机, Message/Part Schema, 上下文包
  Layer 3 (协调+仲裁): Coordinator, Living Spec, 死锁防护

Core types are imported from zephyr.shared.protocols.a2a.
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

from . import layer1_discovery, layer2_communication
from .governance.governance_adapter import GovernanceAdapter


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
    "a2a_card_registry",
    "layer1_discovery",
    "layer2_communication",
    "layer3_coordination",
    "legacy_auditor",
    "legacy_governance_adapter",
    "legacy_protocol",
    "local_first_arch",
    "migration_strategy",
    "multi_agent",
    "multi_model_consensus",
    "offline_autonomy",
    "offline_resilience",
    "phase_hold",
    "prompt_lifecycle",
    "realtime_streaming",
]

__version__ = "0.10.0"

_SUBMODULES = [
    "a2a_card_registry",
    "legacy_auditor",
    "legacy_governance_adapter",
    "legacy_protocol",
    "local_first_arch",
    "migration_strategy",
    "multi_agent",
    "multi_model_consensus",
    "offline_autonomy",
    "offline_resilience",
    "phase_hold",
    "prompt_lifecycle",
    "realtime_streaming",
]


def __getattr__(name: str):
    if name == "layer3_coordination":
        import importlib

        mod = importlib.import_module("zephyr.infrastructure.a2a_protocol.layer3_coordination")
        globals()[name] = mod
        return mod
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.infrastructure.a2a_protocol.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
