# ============================================================================
# _infrastructure 聚合 — 基础设施簇（功能域门面，ARCH-034）
# ============================================================================
# 职责：缺勤管理/AI上下文注入/告警路由/基线管理/金丝雀控制/冷启动/配置一致性/仪表盘等
# 归属规则：*_manager/*_controller/*_router/cold_start/dashboard/gate_persistence/
#   handoff_manager/resource_guard
# 完整模块清单见 __init__.py 顶部"模块地图"
# ============================================================================
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.gov_drift._infrastructure
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.absence_manager; zephyr.gov_drift.ai_context_injector; zephyr.gov_drift.alert_router; zephyr.gov_drift.baseline_manager; zephyr.gov_drift.canary_controller; zephyr.gov_drift.cold_start; zephyr.gov_drift.config_consistency; zephyr.gov_drift.dashboard; zephyr.gov_drift.gate_persistence; zephyr.gov_drift.handoff_manager; zephyr.gov_drift.resource_guard
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
# [A_module] module_id=MOD-SEC__infrastructure | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.gov_drift.absence_manager import (
    AbsenceManagerConfig,
    EscalationEntry,
    OwnerStatus,
    check_absence,
    detect_owner_return,
    escalate_if_absent,
    record_activity,
    set_severity_limit,
)
from zephyr.gov_drift.ai_context_injector import (
    HealthSnapshot,
    InjectedContext,
    InjectionLevel,
    TopDriftItem,
    build_health_snapshot,
    build_top_drifts,
    inject_full,
    inject_minimal,
    inject_standard,
)
from zephyr.gov_drift.alert_router import Alert, AlertRouter
from zephyr.gov_drift.baseline_manager import BaselineManager, DiffReport
from zephyr.gov_drift.canary_controller import (
    CanaryComparison,
    CanaryConfig,
    CanaryResult,
    CanaryRun,
    classify_event_id,
    get_canary_history,
    promote_detector,
    rollback_detector,
    run_canary,
)
from zephyr.gov_drift.cold_start import (
    ColdStartResult,
    bootstrap,
    detect_missing_env,
    init_database,
    init_directories,
    session_entry_activate,
)
from zephyr.gov_drift.config_consistency import (
    ConfigAuditReport,
    ConfigConflict,
    ConfigSource,
    detect_conflicts,
    extract_hardcoded_defaults,
    generate_config_sync,
    parse_env_config,
    parse_yaml_config,
    run_config_audit,
)
from zephyr.gov_drift.dashboard import Dashboard, DashboardData
from zephyr.gov_drift.gate_persistence import GatePersistence
from zephyr.gov_drift.handoff_manager import (
    FileIntegrityRecord,
    HandoffPackage,
    abort_handoff,
    build_handoff_package,
    load_package,
    resume_workflow,
    serialize_package,
    verify_integrity,
)
from zephyr.gov_drift.resource_guard import (
    DegradationLevel,
    ResourceLimits,
    ResourceSnapshot,
    ResourceStatus,
    apply_degradation,
    guard_loop,
    is_guard_running,
    set_critical_handler,
    snapshot,
    stop_guard_loop,
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
    "AbsenceManagerConfig",
    "Alert",
    "AlertRouter",
    "BaselineManager",
    "CanaryComparison",
    "CanaryConfig",
    "CanaryResult",
    "CanaryRun",
    "ColdStartResult",
    "ConfigAuditReport",
    "ConfigConflict",
    "ConfigSource",
    "Dashboard",
    "DashboardData",
    "DegradationLevel",
    "DiffReport",
    "EscalationEntry",
    "FileIntegrityRecord",
    "GatePersistence",
    "HandoffPackage",
    "HealthSnapshot",
    "InjectedContext",
    "InjectionLevel",
    "OwnerStatus",
    "ResourceLimits",
    "ResourceSnapshot",
    "ResourceStatus",
    "TopDriftItem",
    "abort_handoff",
    "apply_degradation",
    "bootstrap",
    "build_handoff_package",
    "build_health_snapshot",
    "build_top_drifts",
    "check_absence",
    "classify_event_id",
    "detect_conflicts",
    "detect_missing_env",
    "detect_owner_return",
    "escalate_if_absent",
    "extract_hardcoded_defaults",
    "generate_config_sync",
    "get_canary_history",
    "guard_loop",
    "init_database",
    "init_directories",
    "inject_full",
    "inject_minimal",
    "inject_standard",
    "is_guard_running",
    "load_package",
    "parse_env_config",
    "parse_yaml_config",
    "promote_detector",
    "record_activity",
    "resume_workflow",
    "rollback_detector",
    "run_canary",
    "run_config_audit",
    "serialize_package",
    "session_entry_activate",
    "set_critical_handler",
    "set_severity_limit",
    "snapshot",
    "stop_guard_loop",
    "validate_scalability",
    "verify_integrity",
]
