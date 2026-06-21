# [A_module] module_id=MOD-SEC__infrastructure | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.behavioral_audit._infrastructure
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.behavioral_audit.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py

from zephyr.behavioral_audit.absence_manager import (
    OwnerStatus,
    EscalationEntry,
    AbsenceManagerConfig,
    record_activity,
    check_absence,
    escalate_if_absent,
    detect_owner_return,
    set_severity_limit,
)
from zephyr.behavioral_audit.ai_context_injector import (
    InjectionLevel,
    HealthSnapshot,
    TopDriftItem,
    InjectedContext,
    build_health_snapshot,
    build_top_drifts,
    inject_minimal,
    inject_standard,
    inject_full,
)
from zephyr.behavioral_audit.alert_router import Alert, AlertRouter
from zephyr.behavioral_audit.baseline_manager import DiffReport, BaselineManager
from zephyr.behavioral_audit.canary_controller import (
    CanaryComparison,
    CanaryResult,
    CanaryRun,
    CanaryConfig,
    classify_event_id,
    run_canary,
    promote_detector,
    rollback_detector,
    get_canary_history,
)
from zephyr.behavioral_audit.cold_start import (
    ColdStartResult,
    init_directories,
    init_database,
    detect_missing_env,
    bootstrap,
    session_entry_activate,
)
from zephyr.behavioral_audit.config_consistency import (
    ConfigSource,
    ConfigConflict,
    ConfigAuditReport,
    parse_yaml_config,
    parse_env_config,
    extract_hardcoded_defaults,
    detect_conflicts,
    generate_config_sync,
    run_config_audit,
)
from zephyr.behavioral_audit.dashboard import DashboardData, Dashboard
from zephyr.behavioral_audit.gate_persistence import GatePersistence
from zephyr.behavioral_audit.handoff_manager import (
    FileIntegrityRecord,
    HandoffPackage,
    build_handoff_package,
    serialize_package,
    load_package,
    verify_integrity,
    resume_workflow,
    abort_handoff,
)
from zephyr.behavioral_audit.resource_guard import (
    DegradationLevel,
    ResourceStatus,
    ResourceLimits,
    ResourceSnapshot,
    snapshot,
    apply_degradation,
    guard_loop,
    stop_guard_loop,
    is_guard_running,
    set_critical_handler,
    validate_scalability,
)

_SUBMODULES = [
    "absence_manager",
    "ai_context_injector",
    "alert_router",
    "baseline_manager",
    "canary_controller",
    "cold_start",
    "config_consistency",
    "dashboard",
    "gate_persistence",
    "handoff_manager",
    "resource_guard",
]

__all__ = [
    "OwnerStatus",
    "EscalationEntry",
    "AbsenceManagerConfig",
    "record_activity",
    "check_absence",
    "escalate_if_absent",
    "detect_owner_return",
    "set_severity_limit",
    "InjectionLevel",
    "HealthSnapshot",
    "TopDriftItem",
    "InjectedContext",
    "build_health_snapshot",
    "build_top_drifts",
    "inject_minimal",
    "inject_standard",
    "inject_full",
    "Alert",
    "AlertRouter",
    "DiffReport",
    "BaselineManager",
    "CanaryComparison",
    "CanaryResult",
    "CanaryRun",
    "CanaryConfig",
    "classify_event_id",
    "run_canary",
    "promote_detector",
    "rollback_detector",
    "get_canary_history",
    "ColdStartResult",
    "init_directories",
    "init_database",
    "detect_missing_env",
    "bootstrap",
    "session_entry_activate",
    "ConfigSource",
    "ConfigConflict",
    "ConfigAuditReport",
    "parse_yaml_config",
    "parse_env_config",
    "extract_hardcoded_defaults",
    "detect_conflicts",
    "generate_config_sync",
    "run_config_audit",
    "DashboardData",
    "Dashboard",
    "GatePersistence",
    "FileIntegrityRecord",
    "HandoffPackage",
    "build_handoff_package",
    "serialize_package",
    "load_package",
    "verify_integrity",
    "resume_workflow",
    "abort_handoff",
    "DegradationLevel",
    "ResourceStatus",
    "ResourceLimits",
    "ResourceSnapshot",
    "snapshot",
    "apply_degradation",
    "guard_loop",
    "stop_guard_loop",
    "is_guard_running",
    "set_critical_handler",
    "validate_scalability",
]
