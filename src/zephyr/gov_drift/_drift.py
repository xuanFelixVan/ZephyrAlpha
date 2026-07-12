# ============================================================================
# _drift 聚合 — 漂移检测器簇（功能域门面，ARCH-034）
# ============================================================================
# 职责：契约/DB/版本/文档/语义/安全等漂移类型检测 + 级联检测 + 基线投毒防护
# 归属规则：drift_*/contract_drift_detector/cascade_detector/baseline_poisoning_guard
# 完整模块清单见 __init__.py 顶部"模块地图"
# ============================================================================
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.gov_drift._drift
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.contract_drift_detector; zephyr.gov_drift.drift_result_types; zephyr.gov_drift.drift_training; zephyr.gov_drift.drift_infrastructure; zephyr.gov_drift.drift_hotfix_bypass; zephyr.gov_drift.cascade_detector; zephyr.gov_drift.baseline_poisoning_guard
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
# [A_module] module_id=MOD-SEC__drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.gov_drift.contract_drift_detector import DriftAlert as ContractDriftAlert
from zephyr.gov_drift.contract_drift_detector import detect_contract_drift
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

_SUBMODULES = [
    "drift_training",
]

__all__ = [
    "AITrainingLoopResult",
    "CascadeAlert",
    "CascadeConfig",
    "CascadeEvent",
    "CheckpointWriter",
    "ContractDriftAlert",
    "CrossLanguageConfig",
    "DBSchemaDriftResult",
    "DepVersionDriftResult",
    "DocCodeCoevolutionResult",
    "DriftTrainingPattern",
    "EnvDiffReport",
    "HashChainEntry",
    "HotfixAuditEntry",
    "HotfixBypass",
    "KnowledgeGraphSyncResult",
    "MaintenanceWindow",
    "MultiBaselineVote",
    "PartialDeploymentRecord",
    "RecoveryManager",
    "SecurityPolicyDriftResult",
    "SemanticDriftResult",
    "TestCoverageDriftResult",
    "build_hash_chain",
    "check_budget_for_gate",
    "check_large_diff",
    "consume_budget",
    "cross_validate_baseline",
    "declare_maintenance_window",
    "detect_ai_training_loop",
    "detect_cascade",
    "detect_concept_cardinality",
    "detect_contract_drift",
    "detect_cross_language_drift",
    "detect_db_schema_drift",
    "detect_dep_version_drift",
    "detect_doc_code_coevolution",
    "detect_enum_value_sync",
    "detect_knowledge_graph_sync",
    "detect_ownership_consistency",
    "detect_partial_deployment",
    "detect_python_dead_code",
    "detect_security_policy_drift",
    "detect_test_coverage_drift",
    "differential_detection",
    "dry_run_impact_analysis",
    "extract_training_patterns",
    "generate_integrity_manifest",
    "get_maintenance_window",
    "get_or_create_budget",
    "inject_patterns_to_prompt",
    "is_auto_fix_paused",
    "multi_baseline_vote",
    "parse_python_imports",
    "parse_python_public_api",
    "register_env_tags",
    "track_training_effectiveness",
    "verify_hash_chain",
]
