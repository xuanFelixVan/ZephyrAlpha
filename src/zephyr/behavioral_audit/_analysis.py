# [A_module] module_id=MOD-SEC__analysis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from zephyr.behavioral_audit.ai_construction_detectors import AIConstructionDetectors
from zephyr.behavioral_audit.backcompat_checker import (
    CompatBreakEvent,
    FunctionSignature,
    compare_signatures,
    detect_intentional_breaks,
    extract_signatures,
    find_renamed_functions,
    run_backcompat_check,
    scan_impact,
)
from zephyr.behavioral_audit.chaos_injector import (
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
from zephyr.behavioral_audit.correlation_engine import CorrelationEngine, CorrelationReport
from zephyr.behavioral_audit.credibility_engine import CredibilityEngine, CredibilityScore
from zephyr.behavioral_audit.cross_module_score import (
    CrossModuleReport,
    CrossModuleScorer,
    ModuleScore,
)
from zephyr.behavioral_audit.forensics_engine import (
    ForensicsConfig,
    ForensicsReport,
    ForensicsTimelineEntry,
    generate_forensics_report,
    git_checkout_snapshot,
    replay_baseline_history,
    serialize_report,
)
from zephyr.behavioral_audit.git_bisector import BisectResult, GitBisector
from zephyr.behavioral_audit.reconciler import AutoFixer, FixSnapshot, Suggestion
from zephyr.behavioral_audit.roi_engine import ROIEngine, ROIScore
from zephyr.behavioral_audit.rollback_bridge import DriftRollbackBridge
from zephyr.behavioral_audit.runbook_generator import (
    build_runbook_frontmatter,
    generate_bulk_runbook,
    generate_runbook,
)
from zephyr.behavioral_audit.self_check import (
    bootstrap_self_check,
    check_core_files,
    check_registry_parsable,
    run_self_check,
    sha256_file,
)
from zephyr.behavioral_audit.suppression_learner import SuppressionLearner, SuppressionRule
from zephyr.behavioral_audit.tamper_proof_audit import (
    AnomalyAlert,
    AuditRecord,
    count_states,
    detect_anomalies,
    generate_audit_log,
    setup_append_only,
    snapshot_event_hash,
)
from zephyr.behavioral_audit.trend_analyzer import TrendAlert, TrendAnalyzer, TrendMetrics

_SUBMODULES = [
    "self_test_verifier",
]

__all__ = [
    "AIConstructionDetectors",
    "AnomalyAlert",
    "AuditRecord",
    "AutoFixer",
    "BisectResult",
    "ChaosInjection",
    "ChaosInjectionType",
    "ChaosMetrics",
    "ChaosPhase",
    "ChaosResult",
    "CompatBreakEvent",
    "CorrelationEngine",
    "CorrelationReport",
    "CredibilityEngine",
    "CredibilityScore",
    "CrossModuleReport",
    "CrossModuleScorer",
    "DriftRollbackBridge",
    "FixSnapshot",
    "ForensicsConfig",
    "ForensicsReport",
    "ForensicsTimelineEntry",
    "FunctionSignature",
    "GitBisector",
    "ModuleScore",
    "ROIEngine",
    "ROIScore",
    "Suggestion",
    "SuppressionLearner",
    "SuppressionRule",
    "TrendAlert",
    "TrendAnalyzer",
    "TrendMetrics",
    "bootstrap_self_check",
    "build_runbook_frontmatter",
    "check_core_files",
    "check_registry_parsable",
    "compare_signatures",
    "count_states",
    "detect_anomalies",
    "detect_intentional_breaks",
    "extract_signatures",
    "find_renamed_functions",
    "generate_audit_log",
    "generate_bulk_runbook",
    "generate_forensics_report",
    "generate_runbook",
    "git_checkout_snapshot",
    "import_hallucination",
    "inject_fake_todo_bomb",
    "inject_path_rename",
    "inject_yaml_field_flip",
    "replay_baseline_history",
    "run_backcompat_check",
    "run_chaos_experiment",
    "run_self_check",
    "scan_impact",
    "serialize_report",
    "setup_append_only",
    "sha256_file",
    "snapshot_event_hash",
]
