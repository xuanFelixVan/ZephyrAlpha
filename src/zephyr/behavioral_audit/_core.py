# [A_module] module_id=MOD-SEC__core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.behavioral_audit._core
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.behavioral_audit.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py

from zephyr.behavioral_audit.drift_engine import (
    load_detector_registry,
    scan,
    scan_on_commit,
    scheduled_light,
    scheduled_deep,
    scan_phase_gate,
    build_report,
    push_to_evolution_engine,
)
from zephyr.behavioral_audit.drift_models import (
    DriftState,
    ScanLevel,
    Severity,
    OrphanClassification,
    DriftEvent,
    BaselineSnapshot,
    ScanResult,
    DriftReport,
    DriftBudget,
    Runbook,
    CascadeEvent,
    BulkDriftEvent,
    ForensicsReport,
    ConfigConflict,
    BreakingChange,
    OrphanFile,
    Detector,
)
from zephyr.behavioral_audit.events import DriftType, DriftState as EventsDriftState, DriftEvent as EventsDriftEvent
from zephyr.behavioral_audit.state_machine import (
    InvalidTransitionError,
    DriftStateMachine,
    DriftEventRecord,
)
from zephyr.behavioral_audit.detector_dispatcher import (
    DetectorResult,
    ResultCache,
    DetectorDispatcher,
    get_max_parallel_for_level,
)

_SUBMODULES = [
    "architecture_contracts",
    "architecture_principles",
    "brain_integration",
    "dashboard",
    "dependency_manager",
    "drift_cron_scheduler",
    "integration_test_runner",
    "ml_engineering",
    "model_drift_monitor",
    "performance_baseline",
    "regime_detector",
    "system_topology",
]

__all__ = [
    "load_detector_registry",
    "scan",
    "scan_on_commit",
    "scheduled_light",
    "scheduled_deep",
    "scan_phase_gate",
    "build_report",
    "push_to_evolution_engine",
    "DriftState",
    "ScanLevel",
    "Severity",
    "OrphanClassification",
    "DriftEvent",
    "BaselineSnapshot",
    "ScanResult",
    "DriftReport",
    "DriftBudget",
    "Runbook",
    "CascadeEvent",
    "BulkDriftEvent",
    "ForensicsReport",
    "ConfigConflict",
    "BreakingChange",
    "OrphanFile",
    "Detector",
    "DriftType",
    "InvalidTransitionError",
    "DriftStateMachine",
    "DriftEventRecord",
    "DetectorResult",
    "ResultCache",
    "DetectorDispatcher",
    "get_max_parallel_for_level",
]
