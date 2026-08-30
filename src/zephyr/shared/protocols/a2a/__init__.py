# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

"""
A2A Protocol — shared interface definitions.

Canonical location for Agent-to-Agent protocol interfaces and data contracts.
Both D-ORCH (orchestration) and D-INFRA (infrastructure) depend on this module
for type-level agreements, breaking the direct D-ORCH -> D-INFRA dependency.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: AgentRole, ArbitrationRole, DispatchedTask, MergeStrategy, ResultMerg…
#   code: __init__.py import L48
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 A2ACommunication, A2ACommunicationProtocol, A2AGovernanceRecord, A2AMessage…
#   desc: __init__ import L48；__all__ 36 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（36 符号）
#   name_en: __all__
#   intro: A2ACommunication, A2ACommunicationProtocol, A2AGovernanceRecord, A2AMessage, A2…
#   downstream: zephyr.integration.agent_communication; zephyr.infrastructure.a2a_protocol; zep…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.protocols.a2a.a2a_coordination import (
    AgentRole,
    ArbitrationRole,
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
    "ArbitrationRole",
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
