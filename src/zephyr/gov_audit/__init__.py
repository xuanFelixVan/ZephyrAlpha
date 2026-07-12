# [A_module] module_id=MOD-GOV_audit_trail | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md
# [MODULE] zephyr.gov_audit
# [INVARIANTS] 所有审计模块健康检查通过才允许操作; AdmissionResult为唯一准入判定结果
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; audit-orchestrator/__init__.py __all__
# [CONSUMERS] gates; orchestrator; pipeline
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AdmissionResult.allowed=False on any check failure
# [TESTS] tests/audit-orchestrator/
# [TTL] permanent

# ============================================================================
# audit_trail 模块地图（ARCH-042 阶段4裁定：强化发现性，不建物理子目录）
# ============================================================================
# ARCH-042 阶段4裁定（2026-07-03）：本包root=62个.py文件享GOV-DOC-018 T_soft=120
# （10前缀簇+34功能名单体），62≤120合规，物理拆分非阈值强制。
# 不建物理子目录的理由（ARCH-034 + ARCH-042裁定双重支持）：
#   ① 前缀分组已提供可预测的Glob检索（audit_*/ *_bridge / trust_* / merkle_* 等）
#   ② 100+外部import改动=漂移源（含lazy import别名引用+__file__路径陷阱）
#   ③ audit_trail/__init__.py 是Safety=H对外垫片（_LAZY_IMPORTS 40+条目），拆分风险>收益
# 物理平铺 + 逻辑分类已分层：新AI通过本地图 + _LAZY_IMPORTS 字典即可定位任意符号。
#
# bridges/ 子包（8文件）：独立adapter层，提供Audit*前缀适配API（与root production实现
# 不同类名/委托目标/API）。src/zephyr/compliance/audit_trail/bridges/ 是外部消费者。
#
# 前缀簇归类（10簇，覆盖22文件）：
#   audit_*          — 审计准入/写保护（admission_controller, schema, write_failure_protector）
#   *_bridge         — 桥接适配（bridge, delegation_bridge, drift_bridge, feedback_bridge,
#                      tiered_storage_bridge, trust_bridge）
#   trust_*          — 信任引擎（trust_engine, trust_ring_manager）
#   merkle_*         — Merkle 哈希（merkle_audit, merkle_hourly）
#   supply_chain*    — 供应链安全（supply_chain, supply_chain_security）
#   finding_*        — 发现/摄入（finding_ingest, finding_model）
#   feedback_*       — 反馈策略（feedback_policy, feedback_self_audit）
#   delegation_*     — 委托审计（delegation_auditor）
#   tiered_storage*  — 分层存储（tiered_storage）
#   text_to_finding* — 适配器（text_to_finding_adapter）
#
# 功能名单体（40文件，各自独立职责，不强制前缀）：
#   orchestrator(compat层,MOD-INF-020) models contracts indexer writer query
#   cli pipeline_runner replay_engine cold_start genesis retention log_rotation
#   evidence_pack integrity integrity_verifier merkle_hourly(根canonical)
#   anomaly event_store action_history agent_signer api_lifecycle
#   changelog_manager code_archaeology compliance_map corporate_actions
#   dora_metrics external_tool_audit forensic_package glossary_matrix
#   incremental_review kb_gate observability_dashboard privacy
#   provenance_tracker resource_aware_pool sbom_generator self_monitor
#   spec_auditor wqa_scorer
#
# 命名规则约定（未来新增文件遵循，便于按名定位归簇）：
#   - audit_*           -> 审计准入/写保护簇
#   - *_bridge          -> 桥接适配簇
#   - trust_*           -> 信任引擎簇
#   - merkle_*          -> Merkle 哈希簇
#   - supply_chain*     -> 供应链安全簇
#   - finding_*         -> 发现/摄入簇
#   - feedback_*        -> 反馈策略簇
#   - 其他              -> 功能单体（需在地图中补登职责说明）
#
# 新AI使用指引（对应向内收原则④：如何发现+如何不重造）：
#   1. 定位符号：查 _LAZY_IMPORTS 字典（符号->模块路径+属性名映射），再 import 对应子模块
#   2. 定位模块：本地图按文件名前缀归位，直接 import zephyr.governance.audit_trail.<module>
#   3. 新增功能前：先 CapabilityLookup.find("<关键词>") 反查是否已有实现（防重造）
#   4. 新增文件：按命名规则命名（归对应前缀簇或功能单体），并更新 _LAZY_IMPORTS + 本地图 + 能力卡
#   5. bridges/ 子包：Audit*前缀适配层，新增需同步 src/zephyr/compliance/audit_trail/bridges/__init__.py
# ============================================================================

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
