# [A_module] module_id=MOD-SEC__drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.behavioral_audit._drift
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.behavioral_audit.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py

from zephyr.behavioral_audit.contract_drift_detector import DriftAlert as ContractDriftAlert, detect_contract_drift
from zephyr.behavioral_audit.drift_result_types import (
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
from zephyr.behavioral_audit.drift_training import (
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
from zephyr.behavioral_audit.drift_infrastructure import (
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
from zephyr.behavioral_audit.drift_hotfix_bypass import HotfixAuditEntry, HotfixBypass
from zephyr.behavioral_audit.cascade_detector import (
    CascadeEvent,
    CascadeAlert,
    CascadeConfig,
    detect_cascade,
    dry_run_impact_analysis,
    is_auto_fix_paused,
)
from zephyr.behavioral_audit.baseline_poisoning_guard import (
    BaselineSnapshot as BPGBaselineSnapshot,
    MultiBaselineVote,
    HashChainEntry,
    cross_validate_baseline,
    multi_baseline_vote,
    build_hash_chain,
    verify_hash_chain,
    generate_integrity_manifest,
)

_SUBMODULES = [
    "drift_training",
]

__all__ = [
    "ContractDriftAlert",
    "detect_contract_drift",
    "SemanticDriftResult",
    "detect_concept_cardinality",
    "detect_enum_value_sync",
    "detect_ownership_consistency",
    "DBSchemaDriftResult",
    "detect_db_schema_drift",
    "DepVersionDriftResult",
    "detect_dep_version_drift",
    "SecurityPolicyDriftResult",
    "detect_security_policy_drift",
    "DocCodeCoevolutionResult",
    "detect_doc_code_coevolution",
    "TestCoverageDriftResult",
    "detect_test_coverage_drift",
    "KnowledgeGraphSyncResult",
    "detect_knowledge_graph_sync",
    "DriftTrainingPattern",
    "AITrainingLoopResult",
    "extract_training_patterns",
    "inject_patterns_to_prompt",
    "track_training_effectiveness",
    "detect_ai_training_loop",
    "CrossLanguageConfig",
    "parse_python_imports",
    "parse_python_public_api",
    "detect_python_dead_code",
    "detect_cross_language_drift",
    "MaintenanceWindow",
    "get_maintenance_window",
    "declare_maintenance_window",
    "check_large_diff",
    "get_or_create_budget",
    "consume_budget",
    "check_budget_for_gate",
    "CheckpointWriter",
    "RecoveryManager",
    "register_env_tags",
    "EnvDiffReport",
    "differential_detection",
    "PartialDeploymentRecord",
    "detect_partial_deployment",
    "HotfixAuditEntry",
    "HotfixBypass",
    "CascadeEvent",
    "CascadeAlert",
    "CascadeConfig",
    "detect_cascade",
    "dry_run_impact_analysis",
    "is_auto_fix_paused",
    "MultiBaselineVote",
    "HashChainEntry",
    "cross_validate_baseline",
    "multi_baseline_vote",
    "build_hash_chain",
    "verify_hash_chain",
    "generate_integrity_manifest",
]
