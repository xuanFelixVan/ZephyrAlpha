# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TESTS] tests/gov_code_dedup/test_self_scan_integrity.py; tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/governance/commit_gates/test_ssot_redefinition_gate.py; tests/governance/governance_e2e/test_gov_5system_integration.py; tests/governance/governance_misc/test_governance_result_types.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 5 个测试）
# [TTL] permanent
"""
Agent 治理八件套 · Governance Domain — DOM-GOV-001 v0.2.0

八模块（phase_2_complete）：
  MOD-INF-018  agent_rbac      — Agent RBAC 权限管理（七层纵深防御+六横切面）
  MOD-INF-019  agent_spec      — Agent Spec 规范约束（蓝图->可加载Skill升级引擎）
  MOD-INF-020  audit_trail     — 审计追踪（不可变+密码学Provenance+Agent签名）
  MOD-INF-021  rollback        — 回滚系统（Git-native + SQLite Checkpoint）
  MOD-INF-022  escalation      — 升级协议（规则驱动+自动委托+五层防御）引擎: v0.14.0
  MOD-INF-023  drift_detector  — 漂移检测（Git-native 运行时检测+自动对账）
  MOD-INF-024  budget_enforcer — 预算执行（Token/Cost/Time 三维强制）引擎: v0.7.0
  MOD-INF-025  a2a             — Agent-to-Agent 协议（Phase 4 Hold）引擎: v0.10.0

集成契约（8条 G-CT，与 DOM-GOV-001 蓝图 §3 对齐）：
  G-CT-001: RBAC -> Audit          G-CT-005: Drift -> Rollback
  G-CT-002: Audit -> Rollback       G-CT-006: Budget -> Escalation
  G-CT-003: Rollback -> Escalation  G-CT-007: Agent Spec -> RBAC+Audit
  G-CT-004: Escalation -> RBAC      G-CT-008: A2A -> RBAC+Escalation

桥接层架构：
  src/zephyr/governance/*  — 跨模块契约+桥接
  src/zephyr/<name>/       — 引擎实现（escalation/budget_enforcer/a2a/drift_detector）
  src/zephyr/mcp/governance_server.py — MCP统一入口（5工具）

文件归属规则（ARCH-031 命名约定，task_bound，对标 ARCH-029）：
  - 属于子模块的文件必须放在子目录（如 audit_trail/agent_signer.py）
  - 根目录仅放跨模块桥接文件（如 __init__.py, capability_lookup.py, rule_patterns.py）
  - 判定标准：文件头 [MODULE] 标注属于子模块的，禁止在根目录创建副本
  - 同名歧义消除：根目录与子目录同名文件，canonical 在 [MODULE] 标注所属位置
  - 自动门禁（ARCH-031 局限1 调研结论，2026-07-01）：
    * GATE-SSOT 第1层（check_ssot_conflicts）：检测同 [MODULE] module_path 冲突——
      新 AI 创建根目录文件且 [MODULE] 标注与子目录文件相同时硬阻断
    * GATE-SSOT 第2层（check_capability_duplicates）：检测 basename 撞 capability_id/alias——
      已注册能力的同名文件硬阻断
    * CREATE-GUARD：新建 .py 文件必须登记 creation_token，强制 AI 声明创建意图
    * 剩余缺口：新 AI 创建根目录文件、[MODULE] 标注为根目录路径、文件名与子目录文件相同
      但未注册 capability 时，三层门禁均不触发——由 RULE-CAPABILITY-LOOKUP + 本 docstring 提示
    * N-16 扩展到 src/ 不可行：src/zephyr/ 有 500 个同名 basename（含 499 个 __init__.py），
      豁免清单规模过大，维护成本高于收益
  - 历史清理：ARCH-031 步骤A+B-1 已删除 24 个根目录 STALE duplicates（2026-06-30）

施工状态（2026-05-08 审计修正）：
  蓝图文档 v0.1.0 — 100% 完成（G-CT-001~008 契约定义 + Phase 1~4 施工顺序）
  桥接层 — 8/8 模块目录创建，G-CT-001~008 桥接代码就位
  独立引擎 — RBAC 完整(68+文件) / Drift 完整(48文件) / Escalation 中等(5文件) / Budget 中等(4文件) / A2A Phase 1 核心就绪(L1发现+L2通信+L3协调 49文件, ~20文件有真实实现, 25文件为Phase 2+脚手架)
  MCP GovernanceServer — 5 工具就位
  测试 — G-CT 契约测 + 红白对抗测已通过

注意：phase_check_registry 和 phase_manager 由调用方直接导入，不从 __init__ 重导出（避免循环依赖）。

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/governance/governance__init__.yaml
"""

# ── R4 import 面削薄（st-fms-tc-20260927）：原三段 try/except 急切重导出（117 条
# import，覆盖本包全部可解析导出名）按本文件既有 PEP 562 惯例（见下方
# _LAZY_SUBMODULE_MAP + __getattr__）改为按需解析。收益实测：import zephyr.governance
# 由 1703ms 降至个位数 ms（常驻断言见 tests/library/test_lookup_import_surface.py）。
# 语义逐字等价依据：
#   * 改前实测 __all__ 132 项与下列 114 个映射名全部当前可解析（无 ImportError 级联跳过），
#     故按需解析后的可见名集合与急切版恒等；
#   * 解析失败一律收敛为 AttributeError("module 'zephyr.governance' has no attribute 'X'")，
#     与原 try/except pass 后访问未绑定名的解释器默认报错同形（from-import 亦同：先
#     AttributeError，解释器再退化为 cannot import name 的 ImportError）；
#   * drift_detector_mod/escalation_protocol 原失败语义是"绑定为 None"而非缺失，
#     由 _LAZY_NULLABLE 保留该差异；
#   * 三件套 sys.modules 别名（event_hook/drift_fix/result_types）保持急切注册，不动。
import importlib as _importlib_for_lazy
import importlib.util as _importlib_util

#: 模块别名重导出：可见名 -> 模块全路径
_LAZY_MODULE_REEXPORT: dict[str, str] = {
    "admission_response": "zephyr.gov_enforcement.behavioral_admission.admission_response",
    "agent_debate": "zephyr.governance.intelligence_governance.agent_debate",
    "agent_dispatch": "zephyr.governance.ops_governance.agent_dispatch",
    "ai_code_standards": "zephyr.gov_enforcement.behavioral_admission.ai_code_standards",
    "ai_self_diagnosis": "zephyr.governance.intelligence_governance.ai_self_diagnosis",
    "architecture_contracts": "zephyr.governance.architecture_governance.architecture_contracts",
    "architecture_principles": "zephyr.governance.architecture_governance.architecture_principles",
    "bandwidth_optimizer": "zephyr.governance.ops_governance.bandwidth_optimizer",
    "benchmark_integrity": "zephyr.gov_drift.detector_core.benchmark_integrity",
    "broker_resilience": "zephyr.governance.resilience_governance.broker_resilience",
    "bus_factor_defense": "zephyr.governance.resilience_governance.bus_factor_defense",
    "cli": "zephyr.gov_code_quality.code_dedup.cli",
    "code_review_ai": "zephyr.gov_enforcement.behavioral_admission.code_review_ai",
    "consequence_manager": "zephyr.governance.escalation.consequence_manager",
    "context_manager": "zephyr.governance.context_governance.context_manager",
    "context_recycling": "zephyr.governance.context_governance.context_recycling",
    "cross_env_consistency": "zephyr.governance.architecture_governance.cross_env_consistency",
    "data_classification": "zephyr.governance.data_governance.data_classification",
    "data_lifecycle": "zephyr.governance.data_governance.data_lifecycle",
    "data_quality": "zephyr.governance.data_governance.data_quality",
    "data_source_reliability": "zephyr.governance.data_governance.data_source_reliability",
    "decision_fatigue": "zephyr.governance.resilience_governance.decision_fatigue",
    "decision_fatigue_cli": "zephyr.governance.resilience_governance.decision_fatigue_cli",
    "dependency_manager": "zephyr.governance.architecture_governance.dependency_manager",
    "drift_detector_mod": "zephyr.gov_drift.drift_detector",
    "environment_manager": "zephyr.governance.ops_governance.environment_manager",
    "escalation_protocol": "zephyr.governance.escalation.escalation_engine",
    "fault_tolerance": "zephyr.governance.resilience_governance.fault_tolerance",
    "financial_compliance": "zephyr.governance.financial_governance.financial_compliance",
    "fsm_verifier": "zephyr.governance.financial_governance.fsm_verifier",
    "incident_response": "zephyr.governance.escalation.incident_response",
    "local_first_arch": "zephyr.governance.architecture_governance.local_first_arch",
    "mcp_result_push": "zephyr.gov_enforcement.behavioral_admission.mcp_result_push",
    "microstructure_defense": "zephyr.governance.financial_governance.microstructure_defense",
    "migration_strategy": "zephyr.governance.lifecycle_governance.migration_strategy",
    "model_drift_monitor": "zephyr.gov_drift.detector_core.model_drift_monitor",
    "multi_model_consensus": "zephyr.governance.intelligence_governance.multi_model_consensus",
    "offline_autonomy": "zephyr.governance.resilience_governance.offline_autonomy",
    "offline_resilience": "zephyr.governance.resilience_governance.offline_resilience",
    "oms_risk_engine": "zephyr.governance.financial_governance.oms_risk_engine",
    "ops_foundation": "zephyr.governance.ops_governance.ops_foundation",
    "paper_live_transition": "zephyr.governance.lifecycle_governance.paper_live_transition",
    "path_resolver": "zephyr.governance.architecture_governance.path_resolver",
    "performance_baseline": "zephyr.gov_drift.detector_core.performance_baseline",
    "phase_check_registry": "zephyr.governance.ops_governance.phase_check_registry",
    "phase_manager": "zephyr.governance.ops_governance.phase_manager",
    "post_live_verification": "zephyr.governance.lifecycle_governance.post_live_verification",
    "post_process": "zephyr.gov_enforcement.behavioral_admission.post_process",
    "prompt_lifecycle": "zephyr.governance.context_governance.prompt_lifecycle",
    "realtime_streaming": "zephyr.governance.data_governance.realtime_streaming",
    "regime_detector": "zephyr.gov_drift.detector_core.regime_detector",
    "spof_checker": "zephyr.governance.escalation.spof_checker",
    "startup_shutdown": "zephyr.infrastructure.runtime.startup_shutdown",
    "strategy_portfolio": "zephyr.governance.financial_governance.strategy_portfolio",
    "vibe_coding_enforcer": "zephyr.gov_enforcement.behavioral_admission.vibe_coding_enforcer",
}

#: 符号重导出：可见名 -> (宿主模块全路径, 宿主内属性名)
_LAZY_SYMBOL_SOURCES: dict[str, tuple[str, str]] = {
    "AdmissionResponse": ("zephyr.gov_enforcement.behavioral_admission.admission_response", "AdmissionResponse"),
    "AdmissionResponseBuilder": (
        "zephyr.gov_enforcement.behavioral_admission.admission_response",
        "AdmissionResponseBuilder",
    ),
    "AdmissionResponseStatus": (
        "zephyr.gov_enforcement.behavioral_admission.admission_response",
        "AdmissionResponseStatus",
    ),
    "AgentSigner": ("zephyr.gov_audit.agent_signer", "AgentSigner"),
    "AkshareQuoteProvider": ("zephyr.governance.data_governance.akshare_provider", "AkshareQuoteProvider"),
    "AssetType": ("zephyr.infrastructure.asset_inventory.models", "AssetType"),
    "BlameRecord": ("zephyr.gov_audit.code_archaeology", "BlameRecord"),
    "BlindSpotStatus": ("zephyr.gov_code_quality.code_dedup.trackers.blind_spot_tracker", "BlindSpotStatus"),
    "CanaryFile": ("zephyr.gov_code_quality.code_dedup.canary_manager", "CanaryFile"),
    "CapabilityLookup": ("zephyr.governance.capability_lookup", "CapabilityLookup"),
    "ChangeImpact": ("zephyr.gov_audit.changelog_manager", "ChangeImpact"),
    "Classifier": ("zephyr.infrastructure.asset_inventory.classifier", "Classifier"),
    "ComplexityReport": ("zephyr.infrastructure.rollback.complexity_budget", "ComplexityReport"),
    "ComplianceFramework": ("zephyr.gov_audit.compliance_map", "ComplianceFramework"),
    "ConstitutionalAutoUpdate": (
        "zephyr.gov_rule.constitutional_update.constitutional_update",
        "ConstitutionalAutoUpdate",
    ),
    "ConstructionVerifier": ("zephyr.governance.architecture_governance.construction_verifier", "ConstructionVerifier"),
    "CorporateActionType": ("zephyr.gov_audit.corporate_actions", "CorporateActionType"),
    "DORATargets": ("zephyr.gov_audit.dora_metrics", "DORATargets"),
    "Dashboard": ("zephyr.infrastructure.asset_inventory.dashboard", "Dashboard"),
    "DatabaseService": ("zephyr.governance.persistence.database_service", "DatabaseService"),
    "DependencyNode": ("zephyr.infrastructure.asset_inventory.dependency", "DependencyNode"),
    "ExperimentConfig": ("zephyr.governance.engine.pipeline_base", "ExperimentConfig"),
    "FactorMeta": ("zephyr.factor.factor_base", "FactorMeta"),
    "FeedbackNode": ("zephyr.gov_audit.feedback_self_audit", "FeedbackNode"),
    "GateEventAdapter": ("zephyr.gov_enforcement.behavioral_admission.gate_event_adapter", "GateEventAdapter"),
    "GitCommitInfo": ("zephyr.infrastructure.asset_inventory.metadata", "GitCommitInfo"),
    "GlossaryEntry": ("zephyr.gov_audit.glossary_matrix", "GlossaryEntry"),
    "HookResult": ("zephyr.gov_enforcement.behavioral_admission.post_process", "HookResult"),
    "HookStrategy": ("zephyr.gov_enforcement.behavioral_admission.post_process", "HookStrategy"),
    "IndexGenerator": ("zephyr.infrastructure.asset_inventory.index_generator", "IndexGenerator"),
    "IngestResult": ("zephyr.gov_audit.finding_ingest", "IngestResult"),
    "KBWriteCheckResult": ("zephyr.gov_audit.kb_gate", "KBWriteCheckResult"),
    "Learning": ("zephyr.gov_rule.constitutional_update.constitutional_update", "Learning"),
    "LicenseType": ("zephyr.gov_audit.sbom_generator", "LicenseType"),
    "Lifecycle": ("zephyr.infrastructure.asset_inventory.lifecycle", "Lifecycle"),
    "PIICategory": ("zephyr.gov_audit.privacy", "PIICategory"),
    "PackageRecord": ("zephyr.gov_audit.supply_chain", "PackageRecord"),
    "PathResolution": ("zephyr.governance.architecture_governance.path_resolver", "PathResolution"),
    "PathResolver": ("zephyr.governance.architecture_governance.path_resolver", "PathResolver"),
    "PhaseStatus": ("zephyr.gov_code_quality.code_dedup.phase_executor", "PhaseStatus"),
    "PipelineResult": ("zephyr.gov_enforcement.behavioral_admission.post_process", "PipelineResult"),
    "PoolLevel": ("zephyr.governance.ops_governance.token_budget", "PoolLevel"),
    "PostProcessHook": ("zephyr.gov_enforcement.behavioral_admission.post_process", "PostProcessHook"),
    "PostProcessPipeline": ("zephyr.gov_enforcement.behavioral_admission.post_process", "PostProcessPipeline"),
    "PrioritizedFixResult": ("zephyr.governance.semantic_audit.fix_result_prioritizer", "PrioritizedFixResult"),
    "ProposedUpdate": ("zephyr.gov_rule.constitutional_update.constitutional_update", "ProposedUpdate"),
    "PushStatus": ("zephyr.gov_enforcement.behavioral_admission.mcp_result_push", "PushStatus"),
    "Reconciler": ("zephyr.infrastructure.asset_inventory.reconciler", "Reconciler"),
    "RegistryParseError": ("zephyr.infrastructure.asset_inventory.registry_adapter", "RegistryParseError"),
    "ResultPushManager": ("zephyr.gov_enforcement.behavioral_admission.mcp_result_push", "ResultPushManager"),
    "RetryResult": ("zephyr.gov_enforcement.rule_enforcement.dlq_retry_policy", "RetryResult"),
    "RiskLevel": ("zephyr.governance.architecture_governance.llm_impact_analyzer", "RiskLevel"),
    "SLIResult": ("zephyr.governance.semantic_audit.self_health", "SLIResult"),
    "SelfHealError": ("zephyr.governance.semantic_audit.self_healer", "SelfHealError"),
    "SnapshotError": ("zephyr.governance.audit.snapshot_manager", "SnapshotError"),
    "TrustLevel": ("zephyr.infrastructure.asset_inventory.trust_anchor", "TrustLevel"),
    "WQAScore": ("zephyr.gov_audit.wqa_scorer", "WQAScore"),
    "main": ("zephyr.gov_code_quality.code_dedup.cli", "main"),
    "record_agent_spec": ("zephyr.gov_audit.spec_auditor", "record_agent_spec"),
}

#: 原急切块以"= None"兜底（而非留空缺失）的名——失败语义与其它名不同，必须保留
_LAZY_NULLABLE = frozenset({"drift_detector_mod", "escalation_protocol"})


def _lazy_reexport(name):
    """按需解析上方两张重导出表；未知名与解析失败同抛未绑定 AttributeError（逐字同形）。

    RuntimeError 与 ImportError 一并捕获 = 原急切 try 块同捕获口径（循环 import 的
    _DeadlockError 是 RuntimeError 子类，见下方 ARCH-036 注释）。
    """
    missing = AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path = _LAZY_MODULE_REEXPORT.get(name)
    if module_path is not None:
        try:
            return _importlib_for_lazy.import_module(module_path)
        except (ImportError, RuntimeError):
            if name in _LAZY_NULLABLE:
                return None
            raise missing from None
    source = _LAZY_SYMBOL_SOURCES.get(name)
    if source is not None:
        host, attr = source
        try:
            module = _importlib_for_lazy.import_module(host)
            try:
                return getattr(module, attr)
            except AttributeError:
                # from a.b import c 的 c 若为子模块：显式导入后即为该模块对象
                return _importlib_for_lazy.import_module(f"{host}.{attr}")
        except (ImportError, RuntimeError, AttributeError):
            raise missing from None
    # 兜底（R4）：急切版经 import 机制顺带挂载的**真实子模块**属性名（如
    # zephyr.governance.capability_lookup），惰性版按需补齐——只增不减，避免
    # "父包属性访问"这类隐式依赖被削掉。dunder 与伪名一律不试，仍报原 AttributeError。
    if name and not name.startswith("_"):
        try:
            return _importlib_for_lazy.import_module(f"{__name__}.{name}")
        except (ImportError, RuntimeError):
            raise missing from None
    raise missing


def __dir__():
    """dir() 枚举面不缩：急切版曾绑定的全部名在惰性版仍可见。"""
    return sorted(
        set(globals())
        | set(_LAZY_MODULE_REEXPORT)
        | set(_LAZY_SYMBOL_SOURCES)
        | set(_LAZY_SUBMODULE_MAP)
        | {"budget_enforcer_mod", "rollback_mod", "a2a_protocol"}
    )


# ARCH-031 CREATE-GUARD 适配：governance/ 根禁止新建 .py 文件，但测试和 boot_hooks
# 需要 zephyr.governance.event_hook 和 zephyr.governance.drift_fix 模块路径。
# 别名经 sys.meta_path 解析器指向 canonical 真源（ops_governance/infrastructure/escalation）。
#
# R4（st-fms-tc-20260927）：原实现是"包初始化即 import 真源三件套再挂 sys.modules 别名"，
# 实测占本包 import 的 750ms（zephyr.infrastructure.rollback 434ms +
# zephyr.governance.escalation.result_types 316ms）——查馆等只借本包一个子模块的读侧
# 被连坐。改为按需解析后，别名语义与**模块对象身份**逐字不变：解析器 create_module 直接
# 返回真源模块对象，故 `zephyr.governance.event_hook is zephyr.governance.ops_governance
# .event_hook` 与 sys.modules 双键同值均与急切版恒等（身份断言见
# tests/library/test_lookup_import_surface.py）。唯一差异是失败时点：真源不可用时原为
# "包初始化静默跳过→后续 ModuleNotFoundError"，现为"首次导入别名即抛"，两条腿都是硬失败，
# 不存在被吞后降级服务的路径。
import sys as _sys_for_shim

#: 历史别名模块路径 -> canonical 真源模块路径
_ALIAS_MODULE_TARGETS: dict[str, str] = {
    "zephyr.governance.event_hook": "zephyr.governance.ops_governance.event_hook",
    "zephyr.governance.drift_fix": "zephyr.infrastructure.rollback.drift_fix",
    "zephyr.governance.result_types": "zephyr.governance.escalation.result_types",
}


class _AliasModuleLoader:
    """把别名请求转发给 canonical 真源（落进 sys.modules 的仍是真源模块对象本身）。"""

    def __init__(self, target: str) -> None:
        self._target = target

    def create_module(self, spec):
        return _importlib_for_lazy.import_module(self._target)

    def exec_module(self, module) -> None:  # noqa: ARG002 — 真源在 create_module 已执行完毕
        return None


class _AliasModuleFinder:
    """只服务 _ALIAS_MODULE_TARGETS 三个历史别名路径；其余 import 一律放行返回 None。

    挂在 sys.meta_path **末尾**：真实模块由标准 PathFinder 命中即短路，本解析器只在
    "文件形态不存在"时才被问一次（一次 dict.get），非别名 import 零成本。
    """

    def find_spec(self, fullname, path=None, target=None):  # noqa: ARG002 — 协议形参
        alias_target = _ALIAS_MODULE_TARGETS.get(fullname)
        if alias_target is None:
            return None
        return _importlib_util.spec_from_loader(fullname, _AliasModuleLoader(alias_target))


if not any(isinstance(finder, _AliasModuleFinder) for finder in _sys_for_shim.meta_path):
    _sys_for_shim.meta_path.append(_AliasModuleFinder())


# __all__ 尾部声明的子目录模块 basename -> canonical 子目录模块路径（PEP 562 惰性加载）。
# 治本（2026-08-17 AI-AUDIT13）：原 __all__ 声明 11 个子目录 basename 但 __getattr__
# 未覆盖——from zephyr.governance import auto_runner 等全部 ImportError（悬空声明）。
# 此处补齐 lazy loader（注释原承诺"保留供 lazy loader 反查"），使 __all__ 声明为真。
_LAZY_SUBMODULE_MAP: dict[str, str] = {
    # 根目录核心模块 basename（ARCH-031 六核心之三；__all__ 声明但惰性未覆盖——
    # depgraph_schema 原仅靠他模块传递 import 的副作用挂载，try 块失败即不可达；
    # evidence_pack/integrity 属性不可达。2026-08-17 AI-AUDIT13 复检治本）
    "depgraph_schema": "zephyr.governance.depgraph_schema",
    "evidence_pack": "zephyr.governance.evidence_pack",
    "integrity": "zephyr.governance.integrity",
    "auto_runner": "zephyr.governance.ops_governance.auto_runner",
    "budget_enforcement": "zephyr.governance.financial_governance.budget_enforcement",
    "constitutional_update": "zephyr.gov_rule.constitutional_update.constitutional_update",
    "database_manager": "zephyr.governance.persistence.database_manager",
    "default_attribution_engine": "zephyr.governance.audit.default_attribution_engine",
    "default_tca_engine": "zephyr.governance.audit.default_tca_engine",
    "f5_boot_integration": "zephyr.governance.resilience_governance.f5_boot_integration",
    "f5_event_subscriber": "zephyr.governance.resilience_governance.f5_event_subscriber",
    "f5_shutdown_manager": "zephyr.governance.resilience_governance.f5_shutdown_manager",
    "pipeline_base": "zephyr.governance.engine.pipeline_base",
    "strategy_base": "zephyr.governance.strategies.strategy_base",
    "strategy_registry": "zephyr.governance.strategies.strategy_registry",
}


def __getattr__(name):
    """延迟导入避免缺失模块阻塞整个包初始化."""
    if name == "budget_enforcer_mod":
        import zephyr.governance.financial_governance.budget_enforcement as _mod

        return _mod
    if name == "rollback_mod":
        import zephyr.infrastructure.rollback as _mod

        return _mod
    if name == "a2a_protocol":
        import zephyr.infrastructure.a2a_protocol as _mod

        return _mod
    if name in _LAZY_SUBMODULE_MAP:
        import importlib

        return importlib.import_module(_LAZY_SUBMODULE_MAP[name])
    if name in _LAZY_SUBMODULE_MAP:
        import importlib

        return importlib.import_module(_LAZY_SUBMODULE_MAP[name])
    return _lazy_reexport(name)  # R4：原三段急切重导出块的按需解析（含未知名报错）


__all__ = [
    "AdmissionResponse",
    "AdmissionResponseBuilder",
    "AdmissionResponseStatus",
    "AgentSigner",
    "AkshareQuoteProvider",
    "AssetType",
    "BlameRecord",
    "BlindSpotStatus",
    "CanaryFile",
    "CapabilityLookup",
    "ChangeImpact",
    "Classifier",
    "ComplexityReport",
    "ComplianceFramework",
    "ConstitutionalAutoUpdate",
    "ConstructionVerifier",
    "CorporateActionType",
    "cli",
    "DORATargets",
    "Dashboard",
    "DatabaseService",
    "DependencyNode",
    "ExperimentConfig",
    "FactorMeta",
    "FeedbackNode",
    "GateEventAdapter",
    "GitCommitInfo",
    "GlossaryEntry",
    "HookResult",
    "HookStrategy",
    "IndexGenerator",
    "IngestResult",
    "KBWriteCheckResult",
    "Learning",
    "LicenseType",
    "Lifecycle",
    "PIICategory",
    "PackageRecord",
    "PathResolution",
    "PathResolver",
    "PhaseStatus",
    "PipelineResult",
    "PoolLevel",
    "PostProcessHook",
    "PostProcessPipeline",
    "PrioritizedFixResult",
    "ProposedUpdate",
    "PushStatus",
    "Reconciler",
    "RegistryParseError",
    "ResultPushManager",
    "RetryResult",
    "RiskLevel",
    "SLIResult",
    "SelfHealError",
    "SnapshotError",
    "TrustLevel",
    "WQAScore",
    "a2a_protocol",
    "admission_response",
    "agent_debate",
    "agent_dispatch",
    "ai_code_standards",
    "ai_self_diagnosis",
    "architecture_contracts",
    "architecture_principles",
    "bandwidth_optimizer",
    "benchmark_integrity",
    "broker_resilience",
    "budget_enforcer_mod",
    "bus_factor_defense",
    "code_review_ai",
    "consequence_manager",
    "constitutional_update",
    "context_manager",
    "context_recycling",
    "cross_env_consistency",
    "data_classification",
    "data_lifecycle",
    "data_quality",
    "data_source_reliability",
    "decision_fatigue",
    "decision_fatigue_cli",
    "dependency_manager",
    "drift_detector_mod",
    "environment_manager",
    "escalation_protocol",
    "fault_tolerance",
    "financial_compliance",
    "fsm_verifier",
    "incident_response",
    "local_first_arch",
    "main",
    "mcp_result_push",
    "microstructure_defense",
    "migration_strategy",
    "model_drift_monitor",
    "multi_model_consensus",
    "offline_autonomy",
    "offline_resilience",
    "oms_risk_engine",
    "ops_foundation",
    "paper_live_transition",
    "path_resolver",
    "performance_baseline",
    "phase_check_registry",
    "phase_manager",
    "post_live_verification",
    "post_process",
    "prompt_lifecycle",
    "realtime_streaming",
    "record_agent_spec",
    "regime_detector",
    "rollback_mod",
    "spof_checker",
    "startup_shutdown",
    "strategy_portfolio",
    "vibe_coding_enforcer",
    # ARCH-031 残留模块名（2026-07-17 清理：删除 7 个失效条目 base/broker_interface/
    # compliance_rule/market_schema/merkle_hourly/performance_attribution_report/gate_repo，
    # 其中 base/merkle_hourly/performance_attribution_report/market_schema 已被 commit
    # 213be2b5a3 删除，broker_interface/compliance_rule 是 capability 名非模块符号，
    # gate_repo 从未存在）。剩余 14 项 = 11 个子目录模块 basename（经 _LAZY_SUBMODULE_MAP
    # 惰性加载，2026-08-17 AI-AUDIT13 补齐）+ 3 个根目录模块（depgraph_schema/evidence_pack/
    # integrity，Python 子模块导入机制天然可解析）。
    "auto_runner",
    "budget_enforcement",
    "database_manager",
    "default_attribution_engine",
    "default_tca_engine",
    "depgraph_schema",
    "evidence_pack",
    "f5_boot_integration",
    "f5_event_subscriber",
    "f5_shutdown_manager",
    "integrity",
    "pipeline_base",
    "strategy_base",
    "strategy_registry",
]

__version__ = "0.15.0"
__module_id__ = "MOD-INF-017"
__domain_id__ = "DOM-GOV-001"
__module_count__ = 8
__contract_count__ = 8
