# [A_module] module_id=MOD-GOV_audit_trail | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail
# [INVARIANTS] 所有审计模块健康检查通过才允许操作; AdmissionResult为唯一准入判定结果
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; audit-orchestrator/__init__.py __all__
# [CONSUMERS] gates; orchestrator; pipeline
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AdmissionResult.allowed=False on any check failure
# [TESTS] tests/audit-orchestrator/
# [TTL] task_bound

# ARCH-036: 子模块改为延迟导入（__getattr__ + _LAZY_IMPORTS），避免 __init__.py 直接 import 子模块
# 与外层 `import zephyr.governance.audit_trail.X` 预获取的 module lock 冲突导致 _DeadlockError。
# 根因: Python `import A.B.C` 先获取 C 的 module lock 再加载父包 A.B; A.B/__init__.py 中 import C
# 会再次请求 C 的 lock -> deadlock。延迟导入让 __init__.py 只定义 __getattr__，访问时才 import 子模块。
# 对标已有 STUB 模式(line 41-44 旧版 cli/audit_admission_controller)，统一扩展到全部子模块。
import importlib

# 名字 -> (模块路径, 属性名) 延迟导入映射表
# alias 用原名: AuditIndexerContract 实际取 contracts.AuditIndexer
_LAZY_IMPORTS = {
    "AnomalyDetector": ("zephyr.governance.audit_trail.anomaly", "AnomalyDetector"),
    "OrchestratorBridge": ("zephyr.governance.audit_trail.bridge", "OrchestratorBridge"),
    "BootstrapCache": ("zephyr.governance.audit_trail.cold_start", "BootstrapCache"),
    "AuditDiscoverer": ("zephyr.governance.audit_trail.contracts", "AuditDiscoverer"),
    "ContractViolationError": ("zephyr.governance.audit_trail.contracts", "ContractViolationError"),
    "IntegrityChecker": ("zephyr.governance.audit_trail.contracts", "IntegrityChecker"),
    "AuditIndexerContract": ("zephyr.governance.audit_trail.contracts", "AuditIndexer"),
    "AuditQueryContract": ("zephyr.governance.audit_trail.contracts", "AuditQuery"),
    "AuditWriterContract": ("zephyr.governance.audit_trail.contracts", "AuditWriter"),
    "DelegationAuditor": ("zephyr.governance.audit_trail.delegation_auditor", "DelegationAuditor"),
    "DelegationBridge": ("zephyr.governance.audit_trail.delegation_bridge", "DelegationBridge"),
    "DriftBridge": ("zephyr.governance.audit_trail.drift_bridge", "DriftBridge"),
    "ExternalToolAuditor": ("zephyr.governance.audit_trail.external_tool_audit", "ExternalToolAuditor"),
    "FeedbackBridge": ("zephyr.governance.audit_trail.feedback_bridge", "FeedbackBridge"),
    "FeedbackPolicy": ("zephyr.governance.audit_trail.feedback_policy", "FeedbackPolicy"),
    "PolicyDecision": ("zephyr.governance.audit_trail.feedback_policy", "PolicyDecision"),
    "GenesisBlock": ("zephyr.governance.audit_trail.genesis", "GenesisBlock"),
    "AuditIndexer": ("zephyr.governance.audit_trail.indexer", "AuditIndexer"),
    "LogRotation": ("zephyr.governance.audit_trail.log_rotation", "LogRotation"),
    "AuditContext": ("zephyr.governance.audit_trail.models", "AuditContext"),
    "AuditIssue": ("zephyr.governance.audit_trail.models", "AuditIssue"),
    "AuditType": ("zephyr.governance.audit_trail.models", "AuditType"),
    "ChangedFile": ("zephyr.governance.audit_trail.models", "ChangedFile"),
    "DiscoveryReport": ("zephyr.governance.audit_trail.models", "DiscoveryReport"),
    "FixLevel": ("zephyr.governance.audit_trail.models", "FixLevel"),
    "GlobalAuditReport": ("zephyr.governance.audit_trail.models", "GlobalAuditReport"),
    "OrchestratorStatus": ("zephyr.governance.audit_trail.models", "OrchestratorStatus"),
    "Priority": ("zephyr.governance.audit_trail.models", "Priority"),
    "Severity": ("zephyr.governance.audit_trail.models", "Severity"),
    "AuditQueryEngine": ("zephyr.governance.audit_trail.query", "AuditQueryEngine"),
    "ReplayEngine": ("zephyr.governance.audit_trail.replay_engine", "ReplayEngine"),
    "PoolStats": ("zephyr.governance.audit_trail.resource_aware_pool", "PoolStats"),
    "ResourceAwarePool": ("zephyr.governance.audit_trail.resource_aware_pool", "ResourceAwarePool"),
    "RetentionPolicy": ("zephyr.governance.audit_trail.retention", "RetentionPolicy"),
    "SelfMonitor": ("zephyr.governance.audit_trail.self_monitor", "SelfMonitor"),
    "TieredStorage": ("zephyr.governance.audit_trail.tiered_storage", "TieredStorage"),
    "TieredStorageBridge": ("zephyr.governance.audit_trail.tiered_storage_bridge", "TieredStorageBridge"),
    "TrustBridge": ("zephyr.governance.audit_trail.trust_bridge", "TrustBridge"),
    "TrustEngine": ("zephyr.governance.audit_trail.trust_engine", "TrustEngine"),
    "TrustLevel": ("zephyr.governance.audit_trail.trust_engine", "TrustLevel"),
    "AuditReportWriter": ("zephyr.governance.audit_trail.writer", "AuditReportWriter"),
    "TextToFindingAdapter": ("zephyr.governance.audit_trail.text_to_finding_adapter", "TextToFindingAdapter"),
    "PipelineRunner": ("zephyr.governance.audit_trail.pipeline_runner", "PipelineRunner"),
    "PipelineResult": ("zephyr.governance.audit_trail.pipeline_runner", "PipelineResult"),
    "DimensionResult": ("zephyr.governance.audit_trail.pipeline_runner", "DimensionResult"),
    "ScriptResult": ("zephyr.governance.audit_trail.pipeline_runner", "ScriptResult"),
    "AuditAdmissionController": ("zephyr.governance.audit_trail.audit_admission_controller", "AuditAdmissionController"),
    "AdmissionResult": ("zephyr.governance.audit_trail.audit_admission_controller", "AdmissionResult"),
    "cli_main": ("zephyr.governance.audit_trail.cli", "main"),
    # ARCH-031: root canonical (governance/evidence_pack.py / integrity.py / merkle_hourly.py)
    "EvidencePack": ("zephyr.governance.evidence_pack", "EvidencePack"),
    "IntegrityGuard": ("zephyr.governance.integrity", "IntegrityGuard"),
    "MerkleHourlyBridge": ("zephyr.governance.merkle_hourly", "MerkleHourlyBridge"),
}


def __getattr__(name):
    # 1. 类名/函数名延迟导入
    entry = _LAZY_IMPORTS.get(name)
    if entry is not None:
        module_path, attr = entry
        mod = importlib.import_module(module_path)
        val = getattr(mod, attr)
        globals()[name] = val  # 缓存到模块全局，后续直接命中
        return val
    # 2. 尝试作为子模块导入（__all__ 里的子模块名: anomaly, bridge, models, query 等）
    try:
        mod = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = mod
        return mod
    except ModuleNotFoundError:
        pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AdmissionResult",
    "AnomalyDetector",
    "AuditAdmissionController",
    "AuditContext",
    "AuditDiscoverer",
    "AuditIndexer",
    "AuditIndexerContract",
    "AuditIssue",
    "AuditQueryContract",
    "AuditQueryEngine",
    "AuditReportWriter",
    "AuditType",
    "AuditWriterContract",
    "BootstrapCache",
    "ChangedFile",
    "ContractViolationError",
    "DelegationAuditor",
    "DelegationBridge",
    "DimensionResult",
    "DiscoveryReport",
    "DriftBridge",
    "EvidencePack",
    "ExternalToolAuditor",
    "FeedbackBridge",
    "FeedbackPolicy",
    "FixLevel",
    "GenesisBlock",
    "GlobalAuditReport",
    "IntegrityChecker",
    "IntegrityGuard",
    "LogRotation",
    "MerkleHourlyBridge",
    "OrchestratorBridge",
    "OrchestratorStatus",
    "PipelineResult",
    "PipelineRunner",
    "PolicyDecision",
    "PoolStats",
    "Priority",
    "ReplayEngine",
    "ResourceAwarePool",
    "RetentionPolicy",
    "ScriptResult",
    "SelfMonitor",
    "Severity",
    "TextToFindingAdapter",
    "TieredStorage",
    "TieredStorageBridge",
    "TrustBridge",
    "TrustEngine",
    "TrustLevel",
    "agent_signer",
    "anomaly",
    "api_lifecycle",
    "audit_admission_controller",
    "bridge",
    "changelog_manager",
    "cli",
    "cli_main",
    "code_archaeology",
    "cold_start",
    "compliance_map",
    "contracts",
    "corporate_actions",
    "delegation_auditor",
    "delegation_bridge",
    "dora_metrics",
    "drift_bridge",
    "evidence_pack",
    "external_tool_audit",
    "feedback_bridge",
    "feedback_policy",
    "feedback_self_audit",
    "finding_model",
    "genesis",
    "glossary_matrix",
    "incremental_review",
    "indexer",
    "integrity",
    "kb_gate",
    "log_rotation",
    "merkle_hourly",
    "models",
    "observability_dashboard",
    "orchestrator",
    "pipeline_runner",
    "privacy",
    "provenance_tracker",
    "query",
    "replay_engine",
    "resource_aware_pool",
    "retention",
    "sbom_generator",
    "self_monitor",
    "spec_auditor",
    "supply_chain",
    "supply_chain_security",
    "tiered_storage",
    "tiered_storage_bridge",
    "trust_bridge",
    "trust_engine",
    "wqa_scorer",
    "writer",
'action_history', 'audit_schema', 'audit_write_failure_protector', 'event_store', 'finding_ingest', 'forensic_package', 'integrity_verifier', 'merkle_audit', 'trust_ring_manager']
