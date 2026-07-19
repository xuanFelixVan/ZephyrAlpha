# [A_module] module_id=MOD-SHR_shared | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""zephyr.shared 包入口 —— PEP 562 惰性导出（架构债务 5.93.3 治本）。

历史问题（5.93.3）：原 __all__ 列 89 个名称但包内零 import，
`from zephyr.shared import X` 必然 ImportError —— AI 幻觉陷阱。
治本：__all__ 裁剪至真实可导入集（84 个）+ PEP 562 __getattr__ 惰性解析。

裁剪裁定（2026-07-19，5.93.3 施工）：
  - 删除 5 个名称：
      F / logger              —— 多模块重复定义（F 是各处独立 TypeVar；logger 是
                                各模块模块级 logger），无 canonical，属歧义名称
      api_index / token_utils —— shared/ 下无此符号也无此模块（幽灵条目）
      context                 —— 是 shared/context/ 包目录名而非导出符号
  - 撞名裁定 canonical（同一名称多处定义，取唯一映射）：
      EventType / EventHandler -> zephyr.shared.event_bus
        （M-07 事件总线真源；infra/observer.py 的同名定义是独立观察器类型）
      ContractRegistry / ContractViolationError -> zephyr.shared.contracts.contract_bus
        （ContractBus 真源；contracts/core/ 下的同名定义属契约版本子系统）
      VersionMismatchError -> zephyr.shared.__version__
        （shared 版本模块真源；contracts/core/registry.py 的同名定义属契约版本子系统）

惰性机制：本文件零 eager import —— `import zephyr.shared` 不触发任何子模块
加载（保持 shared 包轻量、避免循环导入）；首次访问属性时经 __getattr__ 查
_LAZY_IMPORTS 表 importlib.import_module 后 getattr，并 setattr 缓存。
"""

from __future__ import annotations

import importlib as _importlib
import sys as _sys
from typing import Any as _Any

# 符号 -> 定义该符号的子模块（AST 扫描 src/zephyr/shared/**/*.py 模块级
# ClassDef/FunctionDef/Assign/AnnAssign 取唯一定义点派生；撞名见上方裁定）
_LAZY_IMPORTS: dict[str, str] = {
    "AdaptiveSampler": "zephyr.shared.capacity_governance.adaptive_sampler",
    "AiAuditGuard": "zephyr.shared.ai_guards.ai_audit_guard",
    "AiUnderstandabilityConstraint": "zephyr.shared.blueprint_tools.ai_understandability_constraint",
    "AlertEscalation": "zephyr.shared.alerts.alert_escalation",
    "AlertManager": "zephyr.shared.alerts.alert_manager",
    "AlertPrecisionTracker": "zephyr.shared.alerts.alert_precision_tracker",
    "BlueprintCodeAuditor": "zephyr.shared.blueprint_tools.blueprint_code_auditor",
    "BudgetAwarePrompt": "zephyr.shared.capacity_governance.budget_aware_prompt",
    "CapacityCalibrator": "zephyr.shared.capacity_governance.capacity_calibrator",
    "CapacityDigitalTwin": "zephyr.shared.capacity_governance.capacity_digital_twin",
    "CapacityFingerprint": "zephyr.shared.capacity_governance.capacity_fingerprint",
    "CapacityGovernanceLoop": "zephyr.shared.capacity_governance.capacity_governance_loop",
    "CapacityRunbookGenerator": "zephyr.shared.capacity_governance.capacity_runbook_generator",
    "CodeEconomyAnalyzer": "zephyr.shared.maintenance.code_economy_analyzer",
    "CombinatorialGate": "zephyr.shared.ai_guards.combinatorial_gate",
    "ConflictReport": "zephyr.shared.lifecycle.state_machine",
    "ContractBus": "zephyr.shared.contracts.contract_bus",
    "ContractBusError": "zephyr.shared.contracts.contract_bus",
    "ContractDefinition": "zephyr.shared.contracts.contract_bus",
    "ContractEnforcer": "zephyr.shared.contracts.contract_bus",
    "ContractRegistry": "zephyr.shared.contracts.contract_bus",
    "ContractViolationError": "zephyr.shared.contracts.contract_bus",
    "CoreIntegrityGuard": "zephyr.shared.ai_guards.core_integrity_guard",
    "CostEstimator": "zephyr.shared.capacity_governance.cost_estimator",
    "CostRecord": "zephyr.shared.session.session_audit",
    "DecisionRecord": "zephyr.shared.session.session_audit",
    "DegradationChain": "zephyr.shared.resilience.degradation_chain",
    "DependencyCapacityGuard": "zephyr.shared.capacity_governance.dependency_capacity_guard",
    "DomainEvent": "zephyr.shared.event_bus",
    "DualChannelAlert": "zephyr.shared.alerts.dual_channel_alert",
    "ErrorBudgetTracker": "zephyr.shared.resilience.error_budget_tracker",
    "ErrorRecord": "zephyr.shared.session.session_audit",
    "Event": "zephyr.shared.event_bus",
    "EventBus": "zephyr.shared.event_bus",
    "EventBusBackpressure": "zephyr.shared.event_bus",
    "EventHandler": "zephyr.shared.event_bus",
    "EventPriority": "zephyr.shared.event_bus",
    "EventType": "zephyr.shared.event_bus",
    "FaultIsolator": "zephyr.shared.resilience.fault_isolator",
    "HeartbeatServer": "zephyr.shared.alerts.heartbeat_server",
    "InvalidTransitionError": "zephyr.shared.lifecycle.state_machine",
    "LongevityMonitor": "zephyr.shared.lifecycle.longevity_monitor",
    "MIN_COMPATIBLE_SHARED_VERSION": "zephyr.shared.__version__",
    "ModelCapacityProbe": "zephyr.shared.capacity_governance.model_capacity_probe",
    "ModuleBirthRegistry": "zephyr.shared.protocols.module_birth_registry",
    "OutcomeRecord": "zephyr.shared.session.session_audit",
    "OwnerTrustGauge": "zephyr.shared.maintenance.owner_trust_gauge",
    "PromptRecord": "zephyr.shared.session.session_audit",
    "ReasoningSpans": "zephyr.shared.observability.reasoning_spans",
    "S": "zephyr.shared.lifecycle.state_machine",
    "SandboxExecutor": "zephyr.shared.security.sandbox_executor",
    "SessionAuditTrail": "zephyr.shared.session.session_audit",
    "SessionRecord": "zephyr.shared.session.session_audit",
    "SideEffect": "zephyr.shared.lifecycle.state_machine",
    "SloReviewAssistant": "zephyr.shared.maintenance.slo_review_assistant",
    "StateDefinition": "zephyr.shared.lifecycle.state_machine",
    "StateMachine": "zephyr.shared.lifecycle.state_machine",
    "StateMachineConfig": "zephyr.shared.lifecycle.state_machine",
    "StateMachineRegistry": "zephyr.shared.lifecycle.state_machine",
    "StateMachineRegistryError": "zephyr.shared.lifecycle.state_machine",
    "TaskHeartbeat": "zephyr.shared.lifecycle.task_heartbeat",
    "ToolCallRecord": "zephyr.shared.session.session_audit",
    "Transition": "zephyr.shared.lifecycle.state_machine",
    "TransitionGuard": "zephyr.shared.lifecycle.state_machine",
    "TransitionGuardError": "zephyr.shared.lifecycle.state_machine",
    "TtlCleanupEngine": "zephyr.shared.lifecycle.ttl_cleanup_engine",
    "VersionMismatchError": "zephyr.shared.__version__",
    "VibeExperimentTracker": "zephyr.shared.versioning.vibe_experiment_tracker",
    "ZephyrLogger": "zephyr.shared.utils.logging",
    "__version__": "zephyr.shared.__version__",
    "bus": "zephyr.shared.event_bus",
    "check_shared_version": "zephyr.shared.__version__",
    "enforce_contract": "zephyr.shared.contracts.contract_bus",
    "get_bus": "zephyr.shared.contracts.contract_bus",
    "get_state_machine_registry": "zephyr.shared.lifecycle.state_machine",
    "version_compatible": "zephyr.shared.__version__",
    "version_eq": "zephyr.shared.__version__",
    "version_gt": "zephyr.shared.__version__",
    "version_gte": "zephyr.shared.__version__",
    "version_lt": "zephyr.shared.__version__",
    "version_lte": "zephyr.shared.__version__",
    "version_major": "zephyr.shared.__version__",
    "version_minor": "zephyr.shared.__version__",
    "version_patch": "zephyr.shared.__version__",
}

__all__ = [
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
    "FaultIsolator",
    "HeartbeatServer",
    "InvalidTransitionError",
    "LongevityMonitor",
    "MIN_COMPATIBLE_SHARED_VERSION",
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
    "bus",
    "check_shared_version",
    "enforce_contract",
    "get_bus",
    "get_state_machine_registry",
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


def __getattr__(name: str) -> _Any:
    """PEP 562 惰性属性解析：按需导入子模块并返回其顶层符号。"""
    module_path = _LAZY_IMPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = _importlib.import_module(module_path)
    try:
        value = getattr(module, name)
    except AttributeError:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r} "
            f"(_LAZY_IMPORTS 指向 {module_path!r}，但该模块无此符号 -> 请修正映射表)"
        ) from None
    setattr(_sys.modules[__name__], name, value)
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
