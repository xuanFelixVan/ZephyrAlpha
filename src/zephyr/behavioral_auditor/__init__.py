# [BLUEPRINT] MOD-INF-011 | src/zephyr/behavioral_auditor/__init__.py | §
from .__main__ import main
from . import absence_manager
from . import ai_context_injector
from . import alert_router
from . import architecture_contracts
from . import architecture_principles
from . import backcompat_checker
from . import baseline_manager
from . import baseline_poisoning_guard
from . import benchmark_integrity
from . import brain_integration
from . import canary_controller
from . import cascade_detector
from . import code_review_ai
from . import config_consistency
from . import cross_env_consistency
from . import cross_module_score
from . import dashboard
from . import data_classification
from . import data_lifecycle
from . import data_quality
from . import data_source_reliability
from . import dependency_manager
from . import detector_dispatcher
from . import drift_cron_scheduler
from . import drift_training
from . import file_attr_checker
from . import gate_persistence
from . import git_bisector
from . import gitignore_auditor
from . import handoff_manager
from . import headless_scanner
from . import incremental_scanner
from . import integration_test_runner
from . import ml_engineering
from . import model_drift_monitor
from . import naming_magic_checker
from . import performance_baseline
from . import python_compat
from . import reconciler
from . import regime_detector
from . import resource_guard
from . import roi_engine
from . import rollback_bridge
from . import runbook_generator
from . import scan_mutex
from . import state_machine
from . import suppression_learner
from . import symlink_checker
from . import system_topology
from . import tamper_proof_audit
from . import test_fixture_checker
from . import trend_analyzer
"""[BLUEPRINT] MOD-INF-033 | 03_modules/_cross_layer/behavioral-auditor/blueprint.md | §


[MODULE] zephyr.behavioral_auditor


[INVARIANTS] 漂移检测结果不可伪造;基线不可被污染;检测器注册表不可绕过


[MODIFY-GUARD] docs/03_modules/l01_infrastructure/drift-detector/blueprint.md


[CONSUMERS] zephyr.runtime; zephyr.agent_rbac; zephyr.pipeline


[STABILITY] stable


[SAFETY] H


[AI_AUTONOMY] human_gated


[ERROR_CONTRACT] 异常必须包含 detector_id 和 drift_type


[TESTS] tests/test_behavioral_auditor.py





behavioral_auditor — MOD-INF-023 · 行为审计器 / 漂移检测引擎"""



from __future__ import annotations





from zephyr.behavioral_auditor.contract_drift_detector import DriftAlert as ContractDriftAlert, detect_contract_drift


from zephyr.behavioral_auditor.absence_manager import (


    OwnerStatus,


    EscalationEntry,


    AbsenceManagerConfig,


    record_activity,


    check_absence,


    escalate_if_absent,


    detect_owner_return,


    set_severity_limit,


)


from zephyr.behavioral_auditor.ai_construction_detectors import AIConstructionDetectors


from zephyr.behavioral_auditor.ai_context_injector import (


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


from zephyr.behavioral_auditor.alert_router import Alert, AlertRouter


from zephyr.behavioral_auditor.backcompat_checker import (


    CompatBreakEvent,


    FunctionSignature,


    extract_signatures,


    compare_signatures,


    find_renamed_functions,


    scan_impact,


    detect_intentional_breaks,


    run_backcompat_check,


)


from zephyr.behavioral_auditor.baseline_manager import DiffReport, BaselineManager


from zephyr.behavioral_auditor.baseline_poisoning_guard import (


    BaselineSnapshot,


    MultiBaselineVote,


    HashChainEntry,


    cross_validate_baseline,


    multi_baseline_vote,


    build_hash_chain,


    verify_hash_chain,


    generate_integrity_manifest,


)


from zephyr.behavioral_auditor.canary_controller import (


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


from zephyr.behavioral_auditor.cascade_detector import (


    CascadeEvent,


    CascadeAlert,


    CascadeConfig,


    detect_cascade,


    dry_run_impact_analysis,


    is_auto_fix_paused,


)


from zephyr.behavioral_auditor.chaos_injector import (


    ChaosInjectionType,


    ChaosPhase,


    ChaosResult,


    ChaosInjection,


    ChaosMetrics,


    inject_path_rename,


    inject_yaml_field_flip,


    inject_fake_todo_bomb,


    import_hallucination,


    run_chaos_experiment,


)


from zephyr.behavioral_auditor.cold_start import (


    ColdStartResult,


    init_directories,


    init_database,


    detect_missing_env,


    bootstrap,


    session_entry_activate,


)


from zephyr.behavioral_auditor.config_consistency import (


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


from zephyr.behavioral_auditor.correlation_engine import CorrelationReport, CorrelationEngine


from zephyr.behavioral_auditor.credibility_engine import CredibilityScore, CredibilityEngine


from zephyr.behavioral_auditor.cross_module_score import (


    ModuleScore,


    CrossModuleReport,


    CrossModuleScorer,


)


from zephyr.behavioral_auditor.dashboard import DashboardData, Dashboard


from zephyr.behavioral_auditor.detector_dispatcher import (


    DetectorResult,


    ResultCache,


    DetectorDispatcher,


    get_max_parallel_for_level,


)


from zephyr.behavioral_auditor.drift_engine import (


    load_detector_registry,


    scan,


    scan_on_commit,


    scheduled_light,


    scheduled_deep,


    scan_phase_gate,


    build_report,


    push_to_evolution_engine,


)


from zephyr.behavioral_auditor.drift_hotfix_bypass import HotfixAuditEntry, HotfixBypass


from zephyr.behavioral_auditor.drift_infrastructure import (


    MaintenanceWindow,


    get_maintenance_window,


    declare_maintenance_window,


    check_large_diff,


    get_or_create_budget,


    consume_budget,


    check_budget_for_gate,


    CheckpointWriter,


    RecoveryManager,


    register_env_tags,


    EnvDiffReport,


    differential_detection,


    PartialDeploymentRecord,


    detect_partial_deployment,


)


from zephyr.behavioral_auditor.drift_models import (


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


from zephyr.behavioral_auditor.drift_result_types import (


    SemanticDriftResult,


    detect_concept_cardinality,


    detect_enum_value_sync,


    detect_ownership_consistency,


    DBSchemaDriftResult,


    detect_db_schema_drift,


    DepVersionDriftResult,


    detect_dep_version_drift,


    SecurityPolicyDriftResult,


    detect_security_policy_drift,


    DocCodeCoevolutionResult,


    detect_doc_code_coevolution,


    TestCoverageDriftResult,


    detect_test_coverage_drift,


    KnowledgeGraphSyncResult,


    detect_knowledge_graph_sync,


)


from zephyr.behavioral_auditor.drift_training import (


    DriftTrainingPattern,


    AITrainingLoopResult,


    extract_training_patterns,


    inject_patterns_to_prompt,


    track_training_effectiveness,


    detect_ai_training_loop,


    CrossLanguageConfig,


    parse_python_imports,


    parse_python_public_api,


    detect_python_dead_code,


    detect_cross_language_drift,


)


from zephyr.behavioral_auditor.events import DriftType, DriftState, DriftEvent


from zephyr.behavioral_auditor.file_attr_checker import (


    FileAttrIssue,


    capture_baseline,


    check_size_anomaly,


    check_encoding,


)


from zephyr.behavioral_auditor.forensics_engine import (


    ForensicsTimelineEntry,


    ForensicsReport,


    ForensicsConfig,


    replay_baseline_history,


    git_checkout_snapshot,


    generate_forensics_report,


    serialize_report,


)


from zephyr.behavioral_auditor.gate_persistence import GatePersistence


from zephyr.behavioral_auditor.git_bisector import BisectResult, GitBisector


from zephyr.behavioral_auditor.gitignore_auditor import (


    GitignoreAudit,


    parse_gitignore,


    find_untracked_generated,


    find_over_ignored_critical,


    find_uncovered_types,


    audit_gitignore,


)


from zephyr.behavioral_auditor.handoff_manager import (


    FileIntegrityRecord,


    HandoffPackage,


    build_handoff_package,


    serialize_package,


    load_package,


    verify_integrity,


    resume_workflow,


    abort_handoff,


)


from zephyr.behavioral_auditor.headless_scanner import (


    HeadlessDiffEntry,


    InterruptLog,


    headless_scan_light,


    parse_interrupt_log,


)


from zephyr.behavioral_auditor.incremental_scanner import (


    FileChange,


    ChangeSet,


    DetectorFileMapping,


    IncrementalScanner,


)


from zephyr.behavioral_auditor.naming_magic_checker import NamingMagicAlert, scan_naming_magic


from zephyr.behavioral_auditor.orphan_scanner import (


    OrphanResource,


    find_orphan_scripts,


    find_orphan_data,


    find_orphan_docs,


    scan_orphan_resources,


)


from zephyr.behavioral_auditor.python_compat import (


    PythonCompatIssue,


    scan_python_compat,


    auto_fix_compat,


    generate_compat_report,


)


from zephyr.behavioral_auditor.reconciler import FixSnapshot, Suggestion, AutoFixer


from zephyr.behavioral_auditor.resource_guard import (


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


from zephyr.behavioral_auditor.roi_engine import ROIScore, ROIEngine


from zephyr.behavioral_auditor.rollback_bridge import DriftRollbackBridge


from zephyr.behavioral_auditor.runbook_generator import (


    build_runbook_frontmatter,


    generate_runbook,


    generate_bulk_runbook,


)


from zephyr.behavioral_auditor.scan_mutex import ScanLockRecord, QueuedScan, ScanMutex


from zephyr.behavioral_auditor.self_check import (


    sha256_file,


    check_core_files,


    check_registry_parsable,


    bootstrap_self_check,


    run_self_check,


)


from zephyr.behavioral_auditor.state_machine import (


    InvalidTransitionError,


    DriftStateMachine,


    DriftEventRecord,


)


from zephyr.behavioral_auditor.suppression_learner import SuppressionRule, SuppressionLearner


from zephyr.behavioral_auditor.symlink_checker import SymlinkIssue, check_broken_symlinks


from zephyr.behavioral_auditor.tamper_proof_audit import (


    AuditRecord,


    AnomalyAlert,


    setup_append_only,


    snapshot_event_hash,


    count_states,


    generate_audit_log,


    detect_anomalies,


)


from zephyr.behavioral_auditor.test_fixture_checker import (


    FixtureDriftEvent,


    scan_fixture_schema_drift,


    scan_mock_target_drift,


    scan_expected_output_drift,


    run_fixture_check,


)


from zephyr.behavioral_auditor.trend_analyzer import TrendMetrics, TrendAlert, TrendAnalyzer












__all__ = [


    'abort_handoff',


    'absence_manager',


    'ai_construction_detectors',


    'ai_context_injector',


    'alert_router',


    'apply_degradation',


    'audit_gitignore',


    'auto_fix_compat',


    'backcompat_checker',


    'baseline_manager',


    'baseline_poisoning_guard',


    'bootstrap',


    'bootstrap_self_check',


    'brain_integration',


    'build_handoff_package',


    'build_hash_chain',


    'build_health_snapshot',


    'build_report',


    'build_runbook_frontmatter',


    'build_top_drifts',


    'canary_controller',


    'capture_baseline',


    'cascade_detector',


    'chaos_injector',


    'check_absence',


    'check_broken_symlinks',


    'check_budget_for_gate',


    'check_core_files',


    'check_encoding',


    'check_large_diff',


    'check_registry_parsable',


    'check_size_anomaly',


    'classify_event_id',


    'cold_start',


    'compare_signatures',


    'config_consistency',


    'consume_budget',


    'contract_drift_detector',


    'correlation_engine',


    'count_states',


    'credibility_engine',


    'cross_module_score',


    'cross_validate_baseline',


    'dashboard',


    'declare_maintenance_window',


    'detect_ai_training_loop',


    'detect_anomalies',


    'detect_cascade',


    'detect_concept_cardinality',


    'detect_contract_drift',


    'detect_conflicts',


    'detect_cross_language_drift',


    'detect_db_schema_drift',


    'detect_dep_version_drift',


    'detect_doc_code_coevolution',


    'detect_enum_value_sync',


    'detect_intentional_breaks',


    'detect_knowledge_graph_sync',


    'detect_missing_env',


    'detect_owner_return',


    'detect_ownership_consistency',


    'detect_partial_deployment',


    'detect_python_dead_code',


    'detect_security_policy_drift',


    'detect_test_coverage_drift',


    'detector_dispatcher',


    'differential_detection',


    'drift_cron_scheduler',


    'drift_engine',


    'drift_hotfix_bypass',


    'drift_infrastructure',


    'drift_models',


    'drift_result_types',


    'drift_training',


    'dry_run_impact_analysis',


    'escalate_if_absent',


    'events',


    'extract_hardcoded_defaults',


    'extract_signatures',


    'extract_training_patterns',


    'file_attr_checker',


    'find_orphan_data',


    'find_orphan_docs',


    'find_orphan_scripts',


    'find_over_ignored_critical',


    'find_renamed_functions',


    'find_uncovered_types',


    'find_untracked_generated',


    'forensics_engine',


    'gate_persistence',


    'generate_audit_log',


    'generate_bulk_runbook',


    'generate_compat_report',


    'generate_config_sync',


    'generate_forensics_report',


    'generate_integrity_manifest',


    'generate_runbook',


    'get_canary_history',


    'get_maintenance_window',


    'get_max_parallel_for_level',


    'get_or_create_budget',


    'git_bisector',


    'git_checkout_snapshot',


    'gitignore_auditor',


    'guard_loop',


    'handoff_manager',


    'headless_scan_light',


    'headless_scanner',


    'import_hallucination',


    'incremental_scanner',


    'init_database',


    'init_directories',


    'inject_fake_todo_bomb',


    'inject_full',


    'inject_minimal',


    'inject_path_rename',


    'inject_patterns_to_prompt',


    'inject_standard',


    'inject_yaml_field_flip',


    'integration_test_runner',


    'is_auto_fix_paused',


    'is_guard_running',


    'load_detector_registry',


    'load_package',


    'multi_baseline_vote',


    'naming_magic_checker',


    'orphan_scanner',


    'parse_env_config',


    'parse_gitignore',


    'parse_interrupt_log',


    'parse_python_imports',


    'parse_python_public_api',


    'parse_yaml_config',


    'promote_detector',


    'push_to_evolution_engine',


    'python_compat',


    'reconciler',


    'record_activity',


    'register_env_tags',


    'replay_baseline_history',


    'resource_guard',


    'resume_workflow',


    'roi_engine',


    'rollback_bridge',


    'rollback_detector',


    'run_backcompat_check',


    'run_canary',


    'run_chaos_experiment',


    'run_config_audit',


    'run_fixture_check',


    'run_self_check',


    'runbook_generator',


    'scan',


    'scan_expected_output_drift',


    'scan_fixture_schema_drift',


    'scan_impact',


    'scan_mock_target_drift',


    'scan_mutex',


    'scan_naming_magic',


    'scan_on_commit',


    'scan_orphan_resources',


    'scan_phase_gate',


    'scan_python_compat',


    'scheduled_deep',


    'scheduled_light',


    'self_check',


    'self_test_verifier',


    'serialize_package',


    'serialize_report',


    'session_entry_activate',


    'set_critical_handler',


    'set_severity_limit',


    'setup_append_only',


    'sha256_file',


    'snapshot',


    'snapshot_event_hash',


    'state_machine',


    'stop_guard_loop',


    'suppression_learner',


    'symlink_checker',


    'tamper_proof_audit',


    'test_fixture_checker',


    'track_training_effectiveness',


    'trend_analyzer',


    'validate_scalability',


    'verify_hash_chain',


    'verify_integrity',


    'AbsenceManagerConfig',


    'AIConstructionDetectors',


    'AITrainingLoopResult',


    'Alert',


    'AlertRouter',


    'AnomalyAlert',


    'AuditRecord',


    'AutoFixer',


    'BaselineManager',


    'BaselineSnapshot',


    'BisectResult',


    'BreakingChange',


    'BulkDriftEvent',


    'CanaryComparison',


    'CanaryConfig',


    'CanaryResult',


    'CanaryRun',


    'CascadeAlert',


    'CascadeConfig',


    'CascadeEvent',


    'ChangeSet',


    'ChaosInjection',


    'ChaosInjectionType',


    'ChaosMetrics',


    'ChaosPhase',


    'ChaosResult',


    'CheckpointWriter',


    'ColdStartResult',


    'CompatBreakEvent',


    'ConfigAuditReport',


    'ContractDriftAlert',


    'ConfigConflict',


    'ConfigSource',


    'CorrelationEngine',


    'CorrelationReport',


    'CredibilityEngine',


    'CredibilityScore',


    'CrossLanguageConfig',


    'CrossModuleReport',


    'CrossModuleScorer',


    'Dashboard',


    'DashboardData',


    'DBSchemaDriftResult',


    'DegradationLevel',


    'DepVersionDriftResult',


    'Detector',


    'DetectorDispatcher',


    'DetectorFileMapping',


    'DetectorResult',


    'DiffReport',


    'DocCodeCoevolutionResult',


    'DriftBudget',


    'DriftEvent',


    'DriftEventRecord',


    'DriftReport',


    'DriftRollbackBridge',


    'DriftState',


    'DriftStateMachine',


    'DriftTrainingPattern',


    'DriftType',


    'EnvDiffReport',


    'EscalationEntry',


    'FileAttrIssue',


    'FileChange',


    'FileIntegrityRecord',


    'FixSnapshot',


    'FixtureDriftEvent',


    'ForensicsConfig',


    'ForensicsReport',


    'ForensicsTimelineEntry',


    'FunctionSignature',


    'GatePersistence',


    'GitBisector',


    'GitignoreAudit',


    'HandoffPackage',


    'HashChainEntry',


    'HeadlessDiffEntry',


    'HealthSnapshot',


    'HotfixAuditEntry',


    'HotfixBypass',


    'IncrementalScanner',


    'InjectedContext',


    'InjectionLevel',


    'InterruptLog',


    'InvalidTransitionError',


    'KnowledgeGraphSyncResult',


    'MaintenanceWindow',


    'ModuleScore',


    'MultiBaselineVote',


    'NamingMagicAlert',


    'OrphanClassification',


    'OrphanFile',


    'OrphanResource',


    'OwnerStatus',


    'PartialDeploymentRecord',


    'PythonCompatIssue',


    'QueuedScan',


    'RecoveryManager',


    'ResourceLimits',


    'ResourceSnapshot',


    'ResourceStatus',


    'ResultCache',


    'ROIEngine',


    'ROIScore',


    'Runbook',


    'ScanLevel',


    'ScanLockRecord',


    'ScanMutex',


    'ScanResult',


    'SecurityPolicyDriftResult',


    'SemanticDriftResult',


    'Severity',


    'Suggestion',


    'SuppressionLearner',


    'SuppressionRule',


    'SymlinkIssue',


    'TestCoverageDriftResult',


    'TopDriftItem',


    'TrendAlert',


    'TrendAnalyzer',


    'TrendMetrics',
    'architecture_contracts',
    'architecture_principles',
    'benchmark_integrity',
    'code_review_ai',
    'cross_env_consistency',
    'data_classification',
    'data_lifecycle',
    'data_quality',
    'data_source_reliability',
    'dependency_manager',
    'ml_engineering',
    'model_drift_monitor',
    'performance_baseline',
    'regime_detector',
    'system_topology',
]
