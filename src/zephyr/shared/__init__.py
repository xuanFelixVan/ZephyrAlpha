# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-SHR-shared | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: typing 子模块符号 1个
#   fields: Any
#   code: typing
# - id: I2
#   name: __version__ 子模块符号 1个
#   fields: __version__
#   code: zephyr.shared.__version__
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.shared.__init__
#   intro: 5.93.3 治本（R102 EXECUTE）：PEP 562 __getattr__ 惰性导出。
#   desc: MOD-GOVERNANCE 包入口，包级聚合再导出并声明 __all__（88项）
#   inputs: I1 I2
#   outputs: zephyr.shared 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（88项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.shared 包公共 API
#   name_en: __all__ 88项
#   intro: 5.93.3 治本（R102 EXECUTE）：PEP 562 __getattr__ 惰性导出。——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

__all__ = [
    "MIN_COMPATIBLE_SHARED_VERSION",
    "AdaptiveSampler",
    "AiAuditGuard",
    "AiUnderstandabilityConstraint",
    "AlertEscalation",
    "AlertManager",
    "AlertPrecisionTracker",
    "BlueprintCodeAuditor",
    "BudgetAwarePrompt",
    "CapacityCalibrator",
    "CapacityDigitalTwin",
    "CapacityFingerprint",
    "CapacityGovernanceLoop",
    "CapacityRunbookGenerator",
    "CodeEconomyAnalyzer",
    "CombinatorialGate",
    "ConflictReport",
    "ContractBus",
    "ContractBusError",
    "ContractDefinition",
    "ContractEnforcer",
    "ContractRegistry",
    "ContractViolationError",
    "CoreIntegrityGuard",
    "CostEstimator",
    "CostRecord",
    "DecisionRecord",
    "DegradationChain",
    "DependencyCapacityGuard",
    "DomainEvent",
    "DualChannelAlert",
    "ErrorBudgetTracker",
    "ErrorRecord",
    "Event",
    "EventBus",
    "EventBusBackpressure",
    "EventHandler",
    "EventPriority",
    "EventType",
    "F",
    "FaultIsolator",
    "HeartbeatServer",
    "InvalidTransitionError",
    "LongevityMonitor",
    "ModelCapacityProbe",
    "ModuleBirthRegistry",
    "OutcomeRecord",
    "OwnerTrustGauge",
    "PromptRecord",
    "ReasoningSpans",
    "S",
    "SandboxExecutor",
    "SessionAuditTrail",
    "SessionRecord",
    "SideEffect",
    "SloReviewAssistant",
    "StateDefinition",
    "StateMachine",
    "StateMachineConfig",
    "StateMachineRegistry",
    "StateMachineRegistryError",
    "TaskHeartbeat",
    "ToolCallRecord",
    "Transition",
    "TransitionGuard",
    "TransitionGuardError",
    "TtlCleanupEngine",
    "VersionMismatchError",
    "VibeExperimentTracker",
    "ZephyrLogger",
    "__version__",
    "api_index",
    "bus",
    "check_shared_version",
    "context",
    "enforce_contract",
    "get_bus",
    "get_state_machine_registry",
    "logger",
    "version_compatible",
    "version_eq",
    "version_gt",
    "version_gte",
    "version_lt",
    "version_lte",
    "version_major",
    "version_minor",
    "version_patch",
]

# 5.93.3 治本（R102 EXECUTE）：PEP 562 __getattr__ 惰性导出。
# 原状态：__all__ 列 89 个符号名但零 import 语句、无 __getattr__——
# `from zephyr.shared import X` 必失败（AttributeError），"虚假广告"= AI 幻觉陷阱。
# 现通过 __getattr__ 实现惰性导入：符号→子模块映射机械派生，
# 首次访问时 importlib.import_module 并 getattr，结果缓存到模块 __dict__。
# token_utils 已从 __all__ 移除：跨包引用 infrastructure.capacity_assurance.token_budget，
# 非机械派生（shared→infrastructure 属层级违规），用户应直接从规范位置导入。
import importlib
import logging
import sys
from typing import Any

# 模块级 logger（__all__ 中 "logger" 的真源——shared 包自身的 logger 实例）
logger: logging.Logger = logging.getLogger("zephyr.shared")

# __version__ 特殊处理：既是子模块名又是字符串属性。
# importlib.import_module("zephyr.shared.__version__") 会把模块对象写入 __dict__["__version__"]，
# 覆盖字符串。必须在模块加载时显式提取字符串值，确保 from zephyr.shared import __version__ 返回 "0.14.0"。
from zephyr.shared.__version__ import __version__  # noqa: E402  保持字符串语义

# 符号 → 子模块路径映射（相对 zephyr.shared，指向具体 .py 文件避免子包 __init__ 副作用）
_SYMBOL_TO_SUBMODULE: dict[str, str] = {
    # __version__.py（版本常量 + 函数；__version__ 是字符串属性而非模块）
    "MIN_COMPATIBLE_SHARED_VERSION": "__version__",
    "VersionMismatchError": "__version__",
    "__version__": "__version__",
    "check_shared_version": "__version__",
    "version_compatible": "__version__",
    "version_eq": "__version__",
    "version_gt": "__version__",
    "version_gte": "__version__",
    "version_lt": "__version__",
    "version_lte": "__version__",
    "version_major": "__version__",
    "version_minor": "__version__",
    "version_patch": "__version__",
    # event_bus.py（EventBus 及相关类型 + 全局 bus 实例）
    "DomainEvent": "event_bus",
    "Event": "event_bus",
    "EventBus": "event_bus",
    "EventBusBackpressure": "event_bus",
    "EventHandler": "event_bus",
    "EventPriority": "event_bus",
    "EventType": "event_bus",
    "bus": "event_bus",
    # contracts.contract_bus（ContractBus API + F TypeVar）
    "ContractBus": "contracts.contract_bus",
    "ContractBusError": "contracts.contract_bus",
    "ContractDefinition": "contracts.contract_bus",
    "ContractEnforcer": "contracts.contract_bus",
    "ContractRegistry": "contracts.contract_bus",
    "ContractViolationError": "contracts.contract_bus",
    "F": "contracts.contract_bus",
    "enforce_contract": "contracts.contract_bus",
    "get_bus": "contracts.contract_bus",
    # lifecycle.state_machine（StateMachine + S TypeVar + 转换类型）
    "ConflictReport": "lifecycle.state_machine",
    "InvalidTransitionError": "lifecycle.state_machine",
    "S": "lifecycle.state_machine",
    "SideEffect": "lifecycle.state_machine",
    "StateDefinition": "lifecycle.state_machine",
    "StateMachine": "lifecycle.state_machine",
    "StateMachineConfig": "lifecycle.state_machine",
    "StateMachineRegistry": "lifecycle.state_machine",
    "StateMachineRegistryError": "lifecycle.state_machine",
    "Transition": "lifecycle.state_machine",
    "TransitionGuard": "lifecycle.state_machine",
    "TransitionGuardError": "lifecycle.state_machine",
    "get_state_machine_registry": "lifecycle.state_machine",
    # lifecycle.*（其他生命周期模块）
    "LongevityMonitor": "lifecycle.longevity_monitor",
    "TaskHeartbeat": "lifecycle.task_heartbeat",
    "TtlCleanupEngine": "lifecycle.ttl_cleanup_engine",
    # alerts.*（告警体系）
    "AlertEscalation": "alerts.alert_escalation",
    "AlertManager": "alerts.alert_manager",
    "AlertPrecisionTracker": "alerts.alert_precision_tracker",
    "DualChannelAlert": "alerts.dual_channel_alert",
    "HeartbeatServer": "alerts.heartbeat_server",
    # ai_guards.*（AI 守卫）
    "AiAuditGuard": "ai_guards.ai_audit_guard",
    "CombinatorialGate": "ai_guards.combinatorial_gate",
    "CoreIntegrityGuard": "ai_guards.core_integrity_guard",
    # blueprint_tools.*（蓝图工具）
    "AiUnderstandabilityConstraint": "blueprint_tools.ai_understandability_constraint",
    "BlueprintCodeAuditor": "blueprint_tools.blueprint_code_auditor",
    # capacity_governance.*（容量治理）
    "AdaptiveSampler": "capacity_governance.adaptive_sampler",
    "BudgetAwarePrompt": "capacity_governance.budget_aware_prompt",
    "CapacityCalibrator": "capacity_governance.capacity_calibrator",
    "CapacityDigitalTwin": "capacity_governance.capacity_digital_twin",
    "CapacityFingerprint": "capacity_governance.capacity_fingerprint",
    "CapacityGovernanceLoop": "capacity_governance.capacity_governance_loop",
    "CapacityRunbookGenerator": "capacity_governance.capacity_runbook_generator",
    "CostEstimator": "capacity_governance.cost_estimator",
    "DependencyCapacityGuard": "capacity_governance.dependency_capacity_guard",
    "ModelCapacityProbe": "capacity_governance.model_capacity_probe",
    # maintenance.*（维护工具）
    "CodeEconomyAnalyzer": "maintenance.code_economy_analyzer",
    "OwnerTrustGauge": "maintenance.owner_trust_gauge",
    "SloReviewAssistant": "maintenance.slo_review_assistant",
    # observability.*（可观测性）
    "ReasoningSpans": "observability.reasoning_spans",
    # resilience.*（弹性）
    "DegradationChain": "resilience.degradation_chain",
    "ErrorBudgetTracker": "resilience.error_budget_tracker",
    "FaultIsolator": "resilience.fault_isolator",
    # security.*（安全沙箱）
    "SandboxExecutor": "security.sandbox_executor",
    # session.session_audit（会话审计记录）
    "CostRecord": "session.session_audit",
    "DecisionRecord": "session.session_audit",
    "ErrorRecord": "session.session_audit",
    "OutcomeRecord": "session.session_audit",
    "PromptRecord": "session.session_audit",
    "SessionAuditTrail": "session.session_audit",
    "SessionRecord": "session.session_audit",
    "ToolCallRecord": "session.session_audit",
    # protocols.*（协议注册）
    "ModuleBirthRegistry": "protocols.module_birth_registry",
    # versioning.*（版本实验跟踪）
    "VibeExperimentTracker": "versioning.vibe_experiment_tracker",
    # utils.*（工具）
    "ZephyrLogger": "utils.logging",
    "context": "utils.context",
    # api.*（API 索引）
    "api_index": "api.api_index",
}

# 需要返回模块对象本身（而非模块内的符号）的名称
_MODULE_SYMBOLS: frozenset[str] = frozenset({"api_index", "context"})


def __getattr__(name: str) -> Any:
    """PEP 562 惰性导出——首次访问时从子模块加载并缓存到模块 __dict__。

    首次 `from zephyr.shared import EventBus` 触发本函数：
    1. 查 _SYMBOL_TO_SUBMODULE 得到 "event_bus"
    2. importlib.import_module("zephyr.shared.event_bus")
    3. getattr(module, "EventBus")
    4. 写入 sys.modules[__name__].__dict__["EventBus"] = <class EventBus>
    5. 后续访问直接命中 __dict__，不再走 __getattr__
    """
    submod = _SYMBOL_TO_SUBMODULE.get(name)
    if submod is None:
        raise AttributeError(f"module 'zephyr.shared' has no attribute {name!r}")

    module = importlib.import_module(f"zephyr.shared.{submod}")

    if name in _MODULE_SYMBOLS:
        # api_index/context 是模块引用，返回模块本身
        value: Any = module
    else:
        try:
            value = getattr(module, name)
        except AttributeError:
            raise AttributeError(f"module 'zephyr.shared.{submod}' has no attribute {name!r}") from None

    # 缓存到模块 __dict__，后续访问直接命中
    sys.modules[__name__].__dict__[name] = value
    return value


def __dir__() -> list[str]:
    """PEP 562 dir() 支持——返回 __all__ + 模块属性，便于 IDE/REPL 补全。"""
    return sorted(set(__all__) | set(sys.modules[__name__].__dict__))
