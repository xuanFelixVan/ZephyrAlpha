# [A_module] module_id=MOD-SEC__analysis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.behavioral_audit._analysis
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.behavioral_audit.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py

from zephyr.behavioral_audit.correlation_engine import CorrelationReport, CorrelationEngine
from zephyr.behavioral_audit.credibility_engine import CredibilityScore, CredibilityEngine
from zephyr.behavioral_audit.cross_module_score import (
    ModuleScore,
    CrossModuleReport,
    CrossModuleScorer,
)
from zephyr.behavioral_audit.forensics_engine import (
    ForensicsTimelineEntry,
    ForensicsReport,
    ForensicsConfig,
    replay_baseline_history,
    git_checkout_snapshot,
    generate_forensics_report,
    serialize_report,
)
from zephyr.behavioral_audit.git_bisector import BisectResult, GitBisector
from zephyr.behavioral_audit.reconciler import FixSnapshot, Suggestion, AutoFixer
from zephyr.behavioral_audit.roi_engine import ROIScore, ROIEngine
from zephyr.behavioral_audit.rollback_bridge import DriftRollbackBridge
from zephyr.behavioral_audit.runbook_generator import (
    build_runbook_frontmatter,
    generate_runbook,
    generate_bulk_runbook,
)
from zephyr.behavioral_audit.self_check import (
    sha256_file,
    check_core_files,
    check_registry_parsable,
    bootstrap_self_check,
    run_self_check,
)
from zephyr.behavioral_audit.suppression_learner import SuppressionRule, SuppressionLearner
from zephyr.behavioral_audit.tamper_proof_audit import (
    AuditRecord,
    AnomalyAlert,
    setup_append_only,
    snapshot_event_hash,
    count_states,
    generate_audit_log,
    detect_anomalies,
)
from zephyr.behavioral_audit.trend_analyzer import TrendMetrics, TrendAlert, TrendAnalyzer
from zephyr.behavioral_audit.chaos_injector import (
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
from zephyr.behavioral_audit.backcompat_checker import (
    CompatBreakEvent,
    FunctionSignature,
    extract_signatures,
    compare_signatures,
    find_renamed_functions,
    scan_impact,
    detect_intentional_breaks,
    run_backcompat_check,
)
from zephyr.behavioral_audit.ai_construction_detectors import AIConstructionDetectors

_SUBMODULES = [
    "self_test_verifier",
]

__all__ = [
    "CorrelationReport",
    "CorrelationEngine",
    "CredibilityScore",
    "CredibilityEngine",
    "ModuleScore",
    "CrossModuleReport",
    "CrossModuleScorer",
    "ForensicsTimelineEntry",
    "ForensicsReport",
    "ForensicsConfig",
    "replay_baseline_history",
    "git_checkout_snapshot",
    "generate_forensics_report",
    "serialize_report",
    "BisectResult",
    "GitBisector",
    "FixSnapshot",
    "Suggestion",
    "AutoFixer",
    "ROIScore",
    "ROIEngine",
    "DriftRollbackBridge",
    "build_runbook_frontmatter",
    "generate_runbook",
    "generate_bulk_runbook",
    "sha256_file",
    "check_core_files",
    "check_registry_parsable",
    "bootstrap_self_check",
    "run_self_check",
    "SuppressionRule",
    "SuppressionLearner",
    "AuditRecord",
    "AnomalyAlert",
    "setup_append_only",
    "snapshot_event_hash",
    "count_states",
    "generate_audit_log",
    "detect_anomalies",
    "TrendMetrics",
    "TrendAlert",
    "TrendAnalyzer",
    "ChaosInjectionType",
    "ChaosPhase",
    "ChaosResult",
    "ChaosInjection",
    "ChaosMetrics",
    "inject_path_rename",
    "inject_yaml_field_flip",
    "inject_fake_todo_bomb",
    "import_hallucination",
    "run_chaos_experiment",
    "CompatBreakEvent",
    "FunctionSignature",
    "extract_signatures",
    "compare_signatures",
    "find_renamed_functions",
    "scan_impact",
    "detect_intentional_breaks",
    "run_backcompat_check",
    "AIConstructionDetectors",
]
