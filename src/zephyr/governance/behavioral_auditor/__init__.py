# [A_module] module_id=MOD-GOV_behavioral_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [TTL] permanent
from __future__ import annotations

"""[BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md

[MODULE] zephyr.governance.behavioral_auditor

[INVARIANTS] 漂移检测结果不可伪造;基线不可被污染;检测器注册表不可绕过

[MODIFY-GUARD] docs/03_modules/infrastructure_runtime_integration/drift-detector/blueprint.md

[CONSUMERS] zephyr.integration.runtime_core; zephyr.security.access_control; zephyr.infrastructure.pipeline

[STABILITY] stable

[SAFETY] H

[AI_AUTONOMY] human_gated

[ERROR_CONTRACT] 异常必须包含 detector_id 和 drift_type

[TESTS] tests/test_behavioral_auditor.py

behavioral-auditor — MOD-INF-023 · 行为审计器 / 漂移检测引擎"""

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
from zephyr.gov_drift.ai_construction_detectors import AIConstructionDetectors
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
from zephyr.gov_drift.backcompat_checker import (
    CompatBreakEvent,
    FunctionSignature,
    compare_signatures,
    detect_intentional_breaks,
    extract_signatures,
    find_renamed_functions,
    run_backcompat_check,
    scan_impact,
)
from zephyr.gov_drift.baseline_manager import BaselineManager, DiffReport
from zephyr.gov_drift.baseline_poisoning_guard import (
    FileBaselineSnapshot,
    HashChainEntry,
    MultiBaselineVote,
    build_hash_chain,
    cross_validate_baseline,
    generate_integrity_manifest,
    multi_baseline_vote,
    verify_hash_chain,
)
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
from zephyr.gov_drift.cascade_detector import (
    CascadeAlert,
    CascadeConfig,
    CascadeEventRecord,
    detect_cascade,
    dry_run_impact_analysis,
    is_auto_fix_paused,
)
from zephyr.gov_drift.chaos_injector import (
    ChaosInjection,
    ChaosInjectionType,
    ChaosMetrics,
    ChaosPhase,
    ChaosResult,
    import_hallucination,
    inject_fake_todo_bomb,
    inject_path_rename,
    inject_yaml_field_flip,
    run_chaos_experiment,
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
from zephyr.gov_drift.contract_drift_detector import DriftAlert as ContractDriftAlert
from zephyr.gov_drift.contract_drift_detector import detect_contract_drift
from zephyr.gov_drift.correlation_engine import CorrelationEngine, CorrelationReport
from zephyr.gov_drift.credibility_engine import CredibilityEngine, CredibilityScore
from zephyr.gov_drift.cross_module_score import (
    CrossModuleReport,
    CrossModuleScorer,
    ModuleScore,
)
from zephyr.gov_drift.dashboard import Dashboard, DashboardData
from zephyr.gov_drift.detector_dispatcher import (
    DetectorDispatcher,
    DetectorResult,
    ResultCache,
    get_max_parallel_for_level,
)
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
from zephyr.gov_drift.drift_hotfix_bypass import HotfixAuditEntry, HotfixBypass
from zephyr.gov_drift.drift_infrastructure import (
    CheckpointWriter,
    EnvDiffReport,
    MaintenanceWindow,
    PartialDeploymentRecord,
    RecoveryManager,
    check_budget_for_gate,
    check_large_diff,
    consume_budget,
    declare_maintenance_window,
    detect_partial_deployment,
    differential_detection,
    get_maintenance_window,
    get_or_create_budget,
    register_env_tags,
)
# ARCH-034 P3: DriftState/DriftEvent 从 drift_models 导入（canonical 10态/12字段版本）
# events.py 的同名类已改名 ManagedDriftState/ManagedDriftEvent（4态/9字段，管理事件专用）
# 两者职责不同：drift_models=扫描结果数据载体, events.Managed*=管理事件状态机
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
from zephyr.gov_drift.drift_result_types import (
    DBSchemaDriftResult,
    DepVersionDriftResult,
    DocCodeCoevolutionResult,
    KnowledgeGraphSyncResult,
    SecurityPolicyDriftResult,
    SemanticDriftResult,
    TestCoverageDriftResult,
    detect_concept_cardinality,
    detect_db_schema_drift,
    detect_dep_version_drift,
    detect_doc_code_coevolution,
    detect_enum_value_sync,
    detect_knowledge_graph_sync,
    detect_ownership_consistency,
    detect_security_policy_drift,
    detect_test_coverage_drift,
)
from zephyr.gov_drift.drift_training import (
    AITrainingLoopResult,
    CrossLanguageConfig,
    DriftTrainingPattern,
    detect_ai_training_loop,
    detect_cross_language_drift,
    detect_python_dead_code,
    extract_training_patterns,
    inject_patterns_to_prompt,
    parse_python_imports,
    parse_python_public_api,
    track_training_effectiveness,
)
# ARCH-034 P3: DriftType(5值) 从 events 导入（唯一定义源，无同名冲突）
# 之前 drift_models 导入块不含 DriftType，此处补齐；events 的 DriftState/DriftEvent
# 已改名 Managed*，不再从此导入（消除"后导入覆盖前导入"的包命名空间静默错乱）
from zephyr.gov_drift.events import DriftType
from zephyr.gov_drift.file_attr_checker import (
    FileAttrIssue,
    capture_baseline,
    check_encoding,
    check_size_anomaly,
)
from zephyr.gov_drift.forensics_engine import (
    ForensicsConfig,
    ForensicsReport,
    ForensicsTimelineEntry,
    generate_forensics_report,
    git_checkout_snapshot,
    replay_baseline_history,
    serialize_report,
)
from zephyr.gov_drift.gate_persistence import GatePersistence
from zephyr.gov_drift.git_bisector import BisectResult, GitBisector
from zephyr.gov_drift.gitignore_auditor import (
    GitignoreAudit,
    audit_gitignore,
    find_over_ignored_critical,
    find_uncovered_types,
    find_untracked_generated,
    parse_gitignore,
)
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
from zephyr.gov_drift.headless_scanner import (
    HeadlessDiffEntry,
    InterruptLog,
    headless_scan_light,
    parse_interrupt_log,
)
from zephyr.gov_drift.incremental_scanner import (
    ChangeSet,
    DetectorFileMapping,
    FileChange,
    IncrementalScanner,
)
from zephyr.gov_drift.naming_magic_checker import NamingMagicAlert, scan_naming_magic
from zephyr.gov_drift.orphan_scanner import (
    OrphanResource,
    find_orphan_data,
    find_orphan_docs,
    find_orphan_scripts,
    scan_orphan_resources,
)
from zephyr.gov_drift.python_compat import (
    PythonCompatIssue,
    auto_fix_compat,
    generate_compat_report,
    scan_python_compat,
)
from zephyr.gov_drift.reconciler import AutoFixer, FixSnapshot, Suggestion
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
from zephyr.gov_drift.roi_engine import ROIEngine, ROIScore
from zephyr.gov_drift.rollback_bridge import DriftRollbackBridge
from zephyr.gov_drift.runbook_generator import (
    build_runbook_frontmatter,
    generate_bulk_runbook,
    generate_runbook,
)
from zephyr.gov_drift.scan_mutex import QueuedScan, ScanLockRecord, ScanMutex
from zephyr.gov_drift.self_check import (
    bootstrap_self_check,
    check_core_files,
    check_registry_parsable,
    run_self_check,
    sha256_file,
)
from zephyr.gov_drift.suppression_learner import SuppressionLearner, SuppressionRule
from zephyr.gov_drift.symlink_checker import SymlinkIssue, check_broken_symlinks
from zephyr.gov_drift.tamper_proof_audit import (
    AnomalyAlert,
    AuditRecord,
    count_states,
    detect_anomalies,
    generate_audit_log,
    setup_append_only,
    snapshot_event_hash,
)
from zephyr.gov_drift.test_fixture_checker import (
    FixtureDriftEvent,
    run_fixture_check,
    scan_expected_output_drift,
    scan_fixture_schema_drift,
    scan_mock_target_drift,
)
from zephyr.gov_drift.trend_analyzer import TrendAlert, TrendAnalyzer, TrendMetrics
from zephyr.infrastructure.auto_fix_engine.state_machine import (
    DriftEventRecord,
    DriftStateMachine,
    InvalidFixTransitionError,
)

__all__ = [
    "AIConstructionDetectors",
    "AITrainingLoopResult",
    "AbsenceManagerConfig",
    "Alert",
    "AlertRouter",
    "AnomalyAlert",
    "AuditRecord",
    "AutoFixer",
    "BaselineManager",
    "BaselineSnapshot",
    "BisectResult",
    "BreakingChange",
    "BulkDriftEvent",
    "CanaryComparison",
    "CanaryConfig",
    "CanaryResult",
    "CanaryRun",
    "CascadeAlert",
    "CascadeConfig",
    "CascadeEvent",
    "CascadeEventRecord",
    "ChangeSet",
    "ChaosInjection",
    "ChaosInjectionType",
    "ChaosMetrics",
    "ChaosPhase",
    "ChaosResult",
    "CheckpointWriter",
    "ColdStartResult",
    "CompatBreakEvent",
    "ConfigAuditReport",
    "ConfigConflict",
    "ConfigSource",
    "ContractDriftAlert",
    "CorrelationEngine",
    "CorrelationReport",
    "CredibilityEngine",
    "CredibilityScore",
    "CrossLanguageConfig",
    "CrossModuleReport",
    "CrossModuleScorer",
    "DBSchemaDriftResult",
    "Dashboard",
    "DashboardData",
    "DegradationLevel",
    "DepVersionDriftResult",
    "Detector",
    "DetectorDispatcher",
    "DetectorFileMapping",
    "DetectorResult",
    "DiffReport",
    "DocCodeCoevolutionResult",
    "DriftBudget",
    "DriftEvent",
    "DriftEventRecord",
    "DriftReport",
    "DriftRollbackBridge",
    "DriftState",
    "DriftStateMachine",
    "DriftTrainingPattern",
    "DriftType",
    "EnvDiffReport",
    "EscalationEntry",
    "FileAttrIssue",
    "FileBaselineSnapshot",
    "FileChange",
    "FileIntegrityRecord",
    "FixSnapshot",
    "FixtureDriftEvent",
    "ForensicsConfig",
    "ForensicsReport",
    "ForensicsTimelineEntry",
    "FunctionSignature",
    "GatePersistence",
    "GitBisector",
    "GitignoreAudit",
    "HandoffPackage",
    "HashChainEntry",
    "HeadlessDiffEntry",
    "HealthSnapshot",
    "HotfixAuditEntry",
    "HotfixBypass",
    "IncrementalScanner",
    "InjectedContext",
    "InjectionLevel",
    "InterruptLog",
    "InvalidFixTransitionError",
    "KnowledgeGraphSyncResult",
    "MaintenanceWindow",
    "ModuleScore",
    "MultiBaselineVote",
    "NamingMagicAlert",
    "OrphanClassification",
    "OrphanFile",
    "OrphanResource",
    "OwnerStatus",
    "PartialDeploymentRecord",
    "PythonCompatIssue",
    "QueuedScan",
    "ROIEngine",
    "ROIScore",
    "RecoveryManager",
    "ResourceLimits",
    "ResourceSnapshot",
    "ResourceStatus",
    "ResultCache",
    "Runbook",
    "ScanLevel",
    "ScanLockRecord",
    "ScanMutex",
    "ScanResult",
    "SecurityPolicyDriftResult",
    "SemanticDriftResult",
    "Severity",
    "Suggestion",
    "SuppressionLearner",
    "SuppressionRule",
    "SymlinkIssue",
    "TestCoverageDriftResult",
    "TopDriftItem",
    "TrendAlert",
    "TrendAnalyzer",
    "TrendMetrics",
    "abort_handoff",
    "ai_construction_detectors",
    "apply_degradation",
    "audit_gitignore",
    "auto_fix_compat",
    "bootstrap",
    "bootstrap_self_check",
    "build_handoff_package",
    "build_hash_chain",
    "build_health_snapshot",
    "build_report",
    "build_runbook_frontmatter",
    "build_top_drifts",
    "capture_baseline",
    "chaos_injector",
    "check_absence",
    "check_broken_symlinks",
    "check_budget_for_gate",
    "check_core_files",
    "check_encoding",
    "check_large_diff",
    "check_registry_parsable",
    "check_size_anomaly",
    "classify_event_id",
    "cold_start",
    "compare_signatures",
    "consume_budget",
    "contract_drift_detector",
    "correlation_engine",
    "count_states",
    "credibility_engine",
    "cross_validate_baseline",
    "declare_maintenance_window",
    "detect_ai_training_loop",
    "detect_anomalies",
    "detect_cascade",
    "detect_concept_cardinality",
    "detect_conflicts",
    "detect_contract_drift",
    "detect_cross_language_drift",
    "detect_db_schema_drift",
    "detect_dep_version_drift",
    "detect_doc_code_coevolution",
    "detect_enum_value_sync",
    "detect_intentional_breaks",
    "detect_knowledge_graph_sync",
    "detect_missing_env",
    "detect_owner_return",
    "detect_ownership_consistency",
    "detect_partial_deployment",
    "detect_python_dead_code",
    "detect_security_policy_drift",
    "detect_test_coverage_drift",
    "differential_detection",
    "drift_engine",
    "drift_hotfix_bypass",
    "drift_infrastructure",
    "drift_models",
    "drift_result_types",
    "dry_run_impact_analysis",
    "escalate_if_absent",
    "events",
    "extract_hardcoded_defaults",
    "extract_signatures",
    "extract_training_patterns",
    "find_orphan_data",
    "find_orphan_docs",
    "find_orphan_scripts",
    "find_over_ignored_critical",
    "find_renamed_functions",
    "find_uncovered_types",
    "find_untracked_generated",
    "forensics_engine",
    "generate_audit_log",
    "generate_bulk_runbook",
    "generate_compat_report",
    "generate_config_sync",
    "generate_forensics_report",
    "generate_integrity_manifest",
    "generate_runbook",
    "get_canary_history",
    "get_maintenance_window",
    "get_max_parallel_for_level",
    "get_or_create_budget",
    "git_checkout_snapshot",
    "guard_loop",
    "headless_scan_light",
    "import_hallucination",
    "init_database",
    "init_directories",
    "inject_fake_todo_bomb",
    "inject_full",
    "inject_minimal",
    "inject_path_rename",
    "inject_patterns_to_prompt",
    "inject_standard",
    "inject_yaml_field_flip",
    "is_auto_fix_paused",
    "is_guard_running",
    "load_detector_registry",
    "load_package",
    "multi_baseline_vote",
    "orphan_scanner",
    "parse_env_config",
    "parse_gitignore",
    "parse_interrupt_log",
    "parse_python_imports",
    "parse_python_public_api",
    "parse_yaml_config",
    "promote_detector",
    "push_to_evolution_engine",
    "record_activity",
    "register_env_tags",
    "replay_baseline_history",
    "resume_workflow",
    "rollback_detector",
    "run_backcompat_check",
    "run_canary",
    "run_chaos_experiment",
    "run_config_audit",
    "run_fixture_check",
    "run_self_check",
    "scan",
    "scan_expected_output_drift",
    "scan_fixture_schema_drift",
    "scan_impact",
    "scan_mock_target_drift",
    "scan_naming_magic",
    "scan_on_commit",
    "scan_orphan_resources",
    "scan_phase_gate",
    "scan_python_compat",
    "scheduled_deep",
    "scheduled_light",
    "self_check",
    "self_test_verifier",
    "serialize_package",
    "serialize_report",
    "session_entry_activate",
    "set_critical_handler",
    "set_severity_limit",
    "setup_append_only",
    "sha256_file",
    "snapshot",
    "snapshot_event_hash",
    "stop_guard_loop",
    "track_training_effectiveness",
    "validate_scalability",
    "verify_hash_chain",
    "verify_integrity",
]


def __getattr__(name: str):
    # __all__ 里的子模块名（如 absence_manager）实际位于 zephyr.governance.drift_detection.*，
    # 用 __getattr__ 按需 lazy 加载（替代已删除的 eager `from . import ...` 块）
    import importlib

    try:
        mod = importlib.import_module(f"zephyr.governance.drift_detection.{name}")
        globals()[name] = mod
        return mod
    except ImportError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
