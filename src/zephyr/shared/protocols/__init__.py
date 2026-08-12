# [A_module] module_id=MOD-SHR-protocols | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

"""

Shared Protocols — cross-domain interface definitions.

This package contains typing.Protocol interfaces and Pydantic data contracts
shared between orchestration (D-ORCH) and infrastructure (D-INFRA) domains.
No concrete implementations live here — only interface contracts.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: a2a 子包协议定义 Python模块集
#   fields: A2A消息/消息部件/任务/任务状态/Agent卡/Agent能力/角色/状态机/注册表/治理记录等 Protocol接口 与 Pydantic数据契约
#   code: zephyr.shared.protocols.a2a
# 层: 算法
# - id: A1
#   name_zh: ① 协议符号聚合再导出
#   name_en: package re-export
#   intro: 把 a2a 子包定义的22个协议与数据契约符号汇总成统一导入入口
#   desc: from zephyr.shared.protocols.a2a import 22个符号 → __all__ 白名单导出 本包不含任何具体实现
#   inputs: I1
#   outputs: 22个导出符号
#   invariant: 仅Protocol接口与数据契约 无具体实现
# 层: 输出
# - id: O1
#   name_zh: 共享协议契约符号集
#   name_en: shared protocol contracts
#   intro: 编排域与基础设施域共同依赖的跨域接口契约
#   invariant: 导入只可能出import错误 无运行时异常
#   downstream: zephyr.integration.agent_communication; zephyr.infrastructure.a2a_protocol
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
