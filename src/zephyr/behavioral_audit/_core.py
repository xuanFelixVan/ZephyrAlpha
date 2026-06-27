# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.behavioral_audit._core
# [DOMAIN] D-SECURITY
# [DEPENDENCIES] zephyr.behavioral_audit.drift_engine; zephyr.behavioral_audit.drift_models; zephyr.behavioral_audit.events; zephyr.behavioral_audit.state_machine; zephyr.behavioral_audit.detector_dispatcher
# [CONSUMERS] zephyr.behavioral_audit.__init__
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
# [TTL] task_bound
from zephyr.behavioral_audit.drift_engine import (
    build_report,
    load_detector_registry,
    push_to_evolution_engine,
    scan,
    scan_on_commit,
    scan_phase_gate,
    scheduled_deep,
    scheduled_light,
)
from zephyr.behavioral_audit.drift_models import (
    BaselineSnapshot,
    BreakingChange,
    BulkDriftEvent,
    CascadeEvent,
    ConfigConflict,
    Detector,
    DriftBudget,
    DriftEvent,
    DriftReport,
    DriftState,
    ForensicsReport,
    OrphanClassification,
    OrphanFile,
    Runbook,
    ScanLevel,
    ScanResult,
    Severity,
)
from zephyr.behavioral_audit.events import DriftType
from zephyr.behavioral_audit.state_machine import (
    DriftEventRecord,
    DriftStateMachine,
    InvalidTransitionError,
)

_SUBMODULES = [
    "architecture_contracts",
    "architecture_principles",
    "brain_integration",
    "dashboard",
    "dependency_manager",
    "integration_test_runner",
    "ml_engineering",
    "model_drift_monitor",
    "performance_baseline",
    "regime_detector",
    "system_topology",
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
    "ForensicsReport",
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
