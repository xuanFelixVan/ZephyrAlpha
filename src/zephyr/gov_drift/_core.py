# ============================================================================
# _core 聚合 — 核心引擎与状态机（功能域门面，ARCH-034）
# ============================================================================
# 职责：drift扫描调度、事件类型、状态机、检测器分发、架构契约/原则、脑集成等核心功能
# 归属规则：events/state_machine/detector_dispatcher/architecture_*/brain_integration/
#   dependency_manager/integration_test_runner/ml_engineering/model_drift_monitor/
#   performance_baseline/regime_detector/drift_engine/drift_models
# 完整模块清单见 __init__.py 顶部"模块地图"
# ============================================================================
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.gov_drift._core
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.drift_engine; zephyr.gov_drift.drift_models; zephyr.gov_drift.events; zephyr.gov_drift.state_machine; zephyr.gov_drift.detector_dispatcher
# [CONSUMERS] zephyr.gov_drift.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py
# [A_module] module_id=MOD-SEC__core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.gov_drift.drift_engine import (
    build_report,
    load_detector_registry,
    push_to_evolution_engine,
    scan,
    scan_on_commit,
    scan_phase_gate,
    scheduled_deep,
    scheduled_light,
)
from zephyr.gov_drift.drift_models import (
    BaselineSnapshot,
    BreakingChange,
    BulkDriftEvent,
    CascadeEvent,
    Detector,
    DriftBudget,
    DriftEvent,
    DriftReport,
    DriftState,
    OrphanClassification,
    OrphanFile,
    Runbook,
    ScanLevel,
    ScanResult,
    Severity,
)
# ARCH-034 P3: ConfigConflict canonical 真源为 config_consistency（drift_models 存根已删除）
from zephyr.gov_drift.config_consistency import ConfigConflict
from zephyr.gov_drift.events import DriftType, ManagedDriftEvent, ManagedDriftState
from zephyr.gov_drift.state_machine import (
    DriftEventRecord,
    DriftStateMachine,
    InvalidTransitionError,
)

_SUBMODULES = [
    "brain_integration",
    "dashboard",
]

__all__ = [
    "BaselineSnapshot",
    "BreakingChange",
    "BulkDriftEvent",
    "CascadeEvent",
    "ConfigConflict",
    "Detector",
    "DetectorDispatcher",
    "DetectorResult",
    "DriftBudget",
    "DriftEvent",
    "DriftEventRecord",
    "DriftReport",
    "DriftState",
    "DriftStateMachine",
    "DriftType",
    "InvalidTransitionError",
    "OrphanClassification",
    "OrphanFile",
    "ResultCache",
    "Runbook",
    "ScanLevel",
    "ScanResult",
    "Severity",
    "build_report",
    "get_max_parallel_for_level",
    "load_detector_registry",
    "push_to_evolution_engine",
    "scan",
    "scan_on_commit",
    "scan_phase_gate",
    "scheduled_deep",
    "scheduled_light",
]
