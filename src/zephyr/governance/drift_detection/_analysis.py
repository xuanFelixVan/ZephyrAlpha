# ============================================================================
# _analysis 聚合 — 分析与报告簇（功能域门面，ARCH-034）
# ============================================================================
# 职责：相关性/可信度/跨模块评分/取证/ROI/趋势分析/混沌注入/回滚/自检/抑制学习等
# 归属规则：*_engine/*_analyzer/forensics_*/reconciler/runbook_*/self_check/
#   suppression_learner/tamper_proof_audit/chaos_injector/backcompat_checker/
#   ai_construction_detectors/self_test_verifier/cross_module_score/git_bisector
# 完整模块清单见 __init__.py 顶部"模块地图"
# ============================================================================
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection._analysis
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.governance.drift_detection.correlation_engine; zephyr.governance.drift_detection.credibility_engine; zephyr.governance.drift_detection.cross_module_score; zephyr.governance.drift_detection.forensics_engine; zephyr.governance.drift_detection.git_bisector; zephyr.governance.drift_detection.reconciler; zephyr.governance.drift_detection.roi_engine; zephyr.governance.drift_detection.rollback_bridge; zephyr.governance.drift_detection.runbook_generator; zephyr.governance.drift_detection.self_check; zephyr.governance.drift_detection.suppression_learner; zephyr.governance.drift_detection.tamper_proof_audit; zephyr.governance.drift_detection.trend_analyzer; zephyr.governance.drift_detection.chaos_injector; zephyr.governance.drift_detection.backcompat_checker; zephyr.governance.drift_detection.ai_construction_detectors
# [CONSUMERS] zephyr.governance.drift_detection.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py
# [A_module] module_id=MOD-SEC__analysis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.governance.drift_detection.correlation_engine import CorrelationEngine, CorrelationReport
from zephyr.governance.drift_detection.credibility_engine import CredibilityEngine, CredibilityScore
from zephyr.governance.drift_detection.cross_module_score import (
    CrossModuleReport,
    CrossModuleScorer,
    ModuleScore,
)
from zephyr.governance.drift_detection.forensics_engine import (
    ForensicsConfig,
    ForensicsReport,
    ForensicsTimelineEntry,
    generate_forensics_report,
    git_checkout_snapshot,
    replay_baseline_history,
    serialize_report,
)
from zephyr.governance.drift_detection.git_bisector import BisectResult, GitBisector
from zephyr.governance.drift_detection.reconciler import AutoFixer, FixSnapshot, Suggestion
from zephyr.governance.drift_detection.roi_engine import ROIEngine, ROIScore
from zephyr.governance.drift_detection.rollback_bridge import DriftRollbackBridge
from zephyr.governance.drift_detection.runbook_generator import (
    build_runbook_frontmatter,
    generate_bulk_runbook,
    generate_runbook,
)
from zephyr.governance.drift_detection.self_check import (
    bootstrap_self_check,
    check_core_files,
    check_registry_parsable,
    run_self_check,
    sha256_file,
)
from zephyr.governance.drift_detection.suppression_learner import SuppressionLearner, SuppressionRule
from zephyr.governance.drift_detection.tamper_proof_audit import (
    AnomalyAlert,
    AuditRecord,
    count_states,
    detect_anomalies,
    generate_audit_log,
    setup_append_only,
    snapshot_event_hash,
)
from zephyr.governance.drift_detection.trend_analyzer import TrendAlert, TrendAnalyzer, TrendMetrics

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
