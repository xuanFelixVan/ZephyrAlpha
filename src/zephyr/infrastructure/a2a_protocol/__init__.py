# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: A2A 核心类型定义 zephyr.shared.protocols.a2a
#   fields: 30个核心类型/协议（AgentCard/A2ATask/A2AMessage/TaskStatus 等）
#   code: __init__.py L24-56
# - id: I2
#   name: 本地子模块与治理适配器
#   fields: layer1_discovery + layer2_communication + governance.A2AAuditor/GovernanceAdapter
#   code: __init__.py L58-60
# - id: I3
#   name: 属性访问请求 name 参数
#   fields: 被访问的子模块属性名（str）
#   code: __getattr__ L127
# 层: 算法
# - id: A1
#   name_zh: ① 核心类型再导出聚合
#   name_en: 模块级 import + __all__
#   intro: 把 shared.protocols.a2a 的30个类型和本地治理类聚成统一命名空间
#   desc: 静态导入30核心类型+layer1/layer2子模块+A2AAuditor/GovernanceAdapter，__all__ 列出31个导出符号
#   inputs: I1 I2
#   outputs: 31个导出符号的统一命名空间
#   invariant: 核心类型只再导出，不允许重复定义（[INVARIANTS] 头）
# - id: A2
#   name_zh: ② 子模块懒加载
#   name_en: __getattr__
#   intro: 首次访问时用 importlib 动态导入 layer3_coordination 等11个子模块
#   desc: name 命中 layer3_coordination 或 _SUBMODULES(10个) 则 importlib.import_module 并缓存进 globals，否则 raise AttributeError
#   inputs: I3
#   outputs: 动态加载的子模块对象
# 层: 输出
# - id: O1
#   name_zh: A2A 协议统一对外命名空间
#   name_en: zephyr.infrastructure.a2a_protocol
#   intro: 对外提供三层五协议架构的全部类型与13个子模块入口
#   invariant: __version__ = 0.10.0
#   downstream: zephyr.governance 包（__init__.py L115 懒加载引用）；头部 [CONSUMERS] 为空
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A2
# A1 --> O1
# A2 --> O1
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
    ArbitrationRole,
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
from .governance.auditor import A2AAuditor
from .governance.governance_adapter import GovernanceAdapter

__all__ = [
    "A2ACommunication",
    "A2ACommunicationProtocol",
    "A2AAuditor",
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
    "a2a_card_registry",
    "layer1_discovery",
    "layer2_communication",
    "layer3_coordination",
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
