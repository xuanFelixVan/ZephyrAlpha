# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance
# [DOMAIN] D_GOVERNANCE
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
      但未注册 capability 时，三层门禁均不触发——由 AGENTS.md §4.4 + 本 docstring 提示
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: _sys_for_shim
#   code: __init__.py import L113
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AdmissionResponse, AdmissionResponseBuilder, AdmissionResponseStatus, Agent…
#   desc: __init__ import L113；__all__ 133 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（133 符号）
#   name_en: __all__
#   intro: AdmissionResponse, AdmissionResponseBuilder, AdmissionResponseStatus, AgentSign…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

try:
    import zephyr.gov_drift.drift_detector as drift_detector_mod
except (ImportError, RuntimeError):
    drift_detector_mod = None
try:
    import zephyr.governance.escalation.escalation_engine as escalation_protocol
except (ImportError, RuntimeError):
    escalation_protocol = None
try:
    from zephyr.gov_enforcement.behavioral_admission.admission_response import (
        AdmissionResponse,
        AdmissionResponseBuilder,
        AdmissionResponseStatus,
    )
    from zephyr.gov_enforcement.behavioral_admission.mcp_result_push import PushStatus, ResultPushManager
    from zephyr.gov_rule.constitutional_update.constitutional_update import (
        ConstitutionalAutoUpdate,
        Learning,
        ProposedUpdate,
    )
    from zephyr.governance.architecture_governance.path_resolver import PathResolution, PathResolver
except (ImportError, RuntimeError):
    # RuntimeError: 捕获循环 import _DeadlockError（behavioral_admission -> audit_trail 循环链）
    pass

# ARCH-031 CREATE-GUARD 适配：governance/ 根禁止新建 .py 文件，但测试和 boot_hooks
# 需要 zephyr.governance.event_hook 和 zephyr.governance.drift_fix 模块路径。
# 通过 sys.modules 注册别名指向 canonical 真源（ops_governance/infrastructure）。
import sys as _sys_for_shim

try:
    from zephyr.governance.ops_governance import event_hook as _event_hook_shim

    _sys_for_shim.modules["zephyr.governance.event_hook"] = _event_hook_shim
except (ImportError, RuntimeError):
    pass
try:
    from zephyr.infrastructure.rollback import drift_fix as _drift_fix_shim

    _sys_for_shim.modules["zephyr.governance.drift_fix"] = _drift_fix_shim
except (ImportError, RuntimeError):
    pass
try:
    from zephyr.governance.escalation import result_types as _result_types_shim

    _sys_for_shim.modules["zephyr.governance.result_types"] = _result_types_shim
except (ImportError, RuntimeError):
    pass


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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ARCH-036: 路径漂移防御——部分模块已被重构到子目录，直接 import 可能失败。
# 用 try/except 包裹避免单个 import 失败阻塞整个包初始化（符合 __getattr__ 延迟导入设计）。
try:
    import zephyr.gov_code_quality.code_dedup.cli as cli
    from zephyr.factor.factor_base import FactorMeta
    from zephyr.gov_audit.agent_signer import AgentSigner
    from zephyr.gov_audit.changelog_manager import ChangeImpact
    from zephyr.gov_audit.code_archaeology import BlameRecord
    from zephyr.gov_audit.compliance_map import ComplianceFramework
    from zephyr.gov_audit.corporate_actions import CorporateActionType
    from zephyr.gov_audit.dora_metrics import DORATargets
    from zephyr.gov_audit.feedback_self_audit import FeedbackNode
    from zephyr.gov_audit.finding_ingest import IngestResult
    from zephyr.gov_audit.glossary_matrix import GlossaryEntry
    from zephyr.gov_audit.kb_gate import KBWriteCheckResult
    from zephyr.gov_audit.privacy import PIICategory
    from zephyr.gov_audit.sbom_generator import LicenseType
    from zephyr.gov_audit.spec_auditor import record_agent_spec
    from zephyr.gov_audit.supply_chain import PackageRecord
    from zephyr.gov_audit.wqa_scorer import WQAScore
    from zephyr.gov_code_quality.code_dedup.canary_manager import CanaryFile
    from zephyr.gov_code_quality.code_dedup.cli import main
    from zephyr.gov_code_quality.code_dedup.phase_executor import PhaseStatus
    from zephyr.gov_code_quality.code_dedup.trackers.blind_spot_tracker import BlindSpotStatus
    from zephyr.gov_enforcement.behavioral_admission.gate_event_adapter import GateEventAdapter
    from zephyr.gov_enforcement.rule_enforcement.dlq_retry_policy import RetryResult
    from zephyr.governance.architecture_governance.construction_verifier import ConstructionVerifier
    from zephyr.governance.architecture_governance.llm_impact_analyzer import RiskLevel
    from zephyr.governance.audit.snapshot_manager import SnapshotError
    from zephyr.governance.capability_lookup import CapabilityLookup
    from zephyr.governance.data_governance.akshare_quote_provider import (
        AkshareQuoteProvider,  # noqa: import-integrity  git rename staging boundary false-positive, file exists at line 69
    )
    from zephyr.governance.engine.pipeline_base import ExperimentConfig
    from zephyr.governance.ops_governance.token_budget import PoolLevel
    from zephyr.governance.persistence.database_service import DatabaseService
    from zephyr.governance.semantic_audit.fix_result_prioritizer import PrioritizedFixResult
    from zephyr.governance.semantic_audit.self_healer import SelfHealError
    from zephyr.governance.semantic_audit.self_health import SLIResult
    from zephyr.infrastructure.asset_inventory.classifier import Classifier
    from zephyr.infrastructure.asset_inventory.dashboard import Dashboard
    from zephyr.infrastructure.asset_inventory.dependency import DependencyNode
    from zephyr.infrastructure.asset_inventory.index_generator import IndexGenerator
    from zephyr.infrastructure.asset_inventory.lifecycle import Lifecycle
    from zephyr.infrastructure.asset_inventory.metadata import GitCommitInfo
    from zephyr.infrastructure.asset_inventory.models import AssetType
    from zephyr.infrastructure.asset_inventory.reconciler import Reconciler
    from zephyr.infrastructure.asset_inventory.registry_adapter import RegistryParseError
    from zephyr.infrastructure.asset_inventory.trust_anchor import TrustLevel
    from zephyr.infrastructure.rollback.complexity_budget import ComplexityReport
except (ImportError, RuntimeError):
    # RuntimeError: 捕获循环 import _DeadlockError（importlib._bootstrap._DeadlockError 是 RuntimeError 子类）
    pass

# ARCH-031 #6残余: 补齐 __all__ 中声明的悬空符号 import，使 __all__ 与实际 import 一致
# 5 个大写符号（HookResult 等）定义在 behavioral_admission/post_process.py
# 55 个小写模块名（22 根目录 + 33 子目录）此前只在 __all__ 声明但从未 import
try:
    import zephyr.gov_drift.detector_core.benchmark_integrity as benchmark_integrity
    import zephyr.gov_drift.detector_core.model_drift_monitor as model_drift_monitor
    import zephyr.gov_drift.detector_core.performance_baseline as performance_baseline
    import zephyr.gov_drift.detector_core.regime_detector as regime_detector

    # 子目录桥接模块（gov_drift/behavioral_admission/architecture/context/data/escalation/financial/intelligence/lifecycle/ops）
    import zephyr.gov_enforcement.behavioral_admission.admission_response as admission_response
    import zephyr.gov_enforcement.behavioral_admission.ai_code_standards as ai_code_standards
    import zephyr.gov_enforcement.behavioral_admission.code_review_ai as code_review_ai
    import zephyr.gov_enforcement.behavioral_admission.mcp_result_push as mcp_result_push
    import zephyr.gov_enforcement.behavioral_admission.post_process as post_process
    import zephyr.gov_enforcement.behavioral_admission.vibe_coding_enforcer as vibe_coding_enforcer
    import zephyr.governance.architecture_governance.architecture_contracts as architecture_contracts
    import zephyr.governance.architecture_governance.architecture_principles as architecture_principles
    import zephyr.governance.architecture_governance.cross_env_consistency as cross_env_consistency
    import zephyr.governance.architecture_governance.dependency_manager as dependency_manager
    import zephyr.governance.architecture_governance.local_first_arch as local_first_arch
    import zephyr.governance.architecture_governance.path_resolver as path_resolver
    import zephyr.governance.context_governance.context_manager as context_manager
    import zephyr.governance.context_governance.context_recycling as context_recycling
    import zephyr.governance.context_governance.prompt_lifecycle as prompt_lifecycle
    import zephyr.governance.data_governance.data_classification as data_classification
    import zephyr.governance.data_governance.data_lifecycle as data_lifecycle
    import zephyr.governance.data_governance.data_quality as data_quality
    import zephyr.governance.data_governance.data_source_reliability as data_source_reliability
    import zephyr.governance.data_governance.realtime_streaming as realtime_streaming
    import zephyr.governance.escalation.consequence_manager as consequence_manager
    import zephyr.governance.escalation.incident_response as incident_response
    import zephyr.governance.escalation.spof_checker as spof_checker
    import zephyr.governance.financial_governance.financial_compliance as financial_compliance
    import zephyr.governance.financial_governance.fsm_verifier as fsm_verifier
    import zephyr.governance.financial_governance.microstructure_defense as microstructure_defense
    import zephyr.governance.financial_governance.oms_risk_engine as oms_risk_engine
    import zephyr.governance.financial_governance.strategy_portfolio as strategy_portfolio
    import zephyr.governance.intelligence_governance.agent_debate as agent_debate
    import zephyr.governance.intelligence_governance.ai_self_diagnosis as ai_self_diagnosis
    import zephyr.governance.intelligence_governance.multi_model_consensus as multi_model_consensus
    import zephyr.governance.lifecycle_governance.migration_strategy as migration_strategy
    import zephyr.governance.lifecycle_governance.paper_live_transition as paper_live_transition
    import zephyr.governance.lifecycle_governance.post_live_verification as post_live_verification
    import zephyr.governance.ops_governance.agent_dispatch as agent_dispatch

    # 子目录桥接模块（续：ops/resilience/infrastructure.runtime）
    import zephyr.governance.ops_governance.bandwidth_optimizer as bandwidth_optimizer
    import zephyr.governance.ops_governance.environment_manager as environment_manager
    import zephyr.governance.ops_governance.ops_foundation as ops_foundation
    import zephyr.governance.ops_governance.phase_check_registry as phase_check_registry
    import zephyr.governance.ops_governance.phase_manager as phase_manager
    import zephyr.governance.ops_governance.startup_shutdown_cli as startup_shutdown_cli
    import zephyr.governance.resilience_governance.broker_resilience as broker_resilience
    import zephyr.governance.resilience_governance.bus_factor_defense as bus_factor_defense
    import zephyr.governance.resilience_governance.decision_fatigue as decision_fatigue
    import zephyr.governance.resilience_governance.decision_fatigue_cli as decision_fatigue_cli
    import zephyr.governance.resilience_governance.fault_tolerance as fault_tolerance
    import zephyr.governance.resilience_governance.offline_autonomy as offline_autonomy
    import zephyr.governance.resilience_governance.offline_resilience as offline_resilience
    import zephyr.infrastructure.runtime.startup_shutdown as startup_shutdown
    from zephyr.gov_enforcement.behavioral_admission.post_process import (
        HookResult,
        HookStrategy,
        PipelineResult,
        PostProcessHook,
        PostProcessPipeline,
    )
except (ImportError, RuntimeError):
    # RuntimeError: 捕获循环 import _DeadlockError（同上）
    pass

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
    "startup_shutdown_cli",
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
