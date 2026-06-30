# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain_governance/blueprint.md | §
# [TTL] task_bound
"""
Agent 治理八件套 · Governance Domain — DOM-GOV-001 v0.2.0

八模块（phase_2_complete）：
  MOD-INF-018  agent_rbac      — Agent RBAC 权限管理（七层纵深防御+六横切面）
  MOD-INF-019  agent_spec      — Agent Spec 规范约束（蓝图→可加载Skill升级引擎）
  MOD-INF-020  audit_trail     — 审计追踪（不可变+密码学Provenance+Agent签名）
  MOD-INF-021  rollback        — 回滚系统（Git-native + SQLite Checkpoint）
  MOD-INF-022  escalation      — 升级协议（规则驱动+自动委托+五层防御）引擎: v0.14.0
  MOD-INF-023  drift_detector  — 漂移检测（Git-native 运行时检测+自动对账）
  MOD-INF-024  budget_enforcer — 预算执行（Token/Cost/Time 三维强制）引擎: v0.7.0
  MOD-INF-025  a2a             — Agent-to-Agent 协议（Phase 4 Hold）引擎: v0.10.0

集成契约（8条 G-CT，与 DOM-GOV-001 蓝图 §3 对齐）：
  G-CT-001: RBAC → Audit          G-CT-005: Drift → Rollback
  G-CT-002: Audit → Rollback       G-CT-006: Budget → Escalation
  G-CT-003: Rollback → Escalation  G-CT-007: Agent Spec → RBAC+Audit
  G-CT-004: Escalation → RBAC      G-CT-008: A2A → RBAC+Escalation

桥接层架构：
  src/zephyr/governance/*  — 跨模块契约+桥接
  src/zephyr/<name>/       — 引擎实现（escalation/budget_enforcer/a2a/drift_detector）
  src/zephyr/mcp/governance_server.py — MCP统一入口（5工具）

文件归属规则（ARCH-031 命名约定，task_bound，对标 ARCH-029）：
  - 属于子模块的文件必须放在子目录（如 audit_trail/agent_signer.py）
  - 根目录仅放跨模块桥接文件（如 __init__.py, capability_lookup.py, base.py）
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
"""


try:
    import zephyr.governance.drift_detector as drift_detector_mod
except ImportError:
    drift_detector_mod = None
try:
    import zephyr.governance.escalation_engine as escalation_protocol
except ImportError:
    escalation_protocol = None
from zephyr.governance.architecture_governance.path_resolver import PathResolution, PathResolver
from zephyr.governance.behavioral_admission.admission_response import (
    AdmissionResponse,
    AdmissionResponseBuilder,
    AdmissionResponseStatus,
)
from zephyr.governance.behavioral_admission.mcp_result_push import PushStatus, ResultPushManager
from zephyr.governance.constitutional_update.constitutional_update import (
    ConstitutionalAutoUpdate,
    Learning,
    ProposedUpdate,
)


def __getattr__(name):
    """延迟导入避免缺失模块阻塞整个包初始化."""
    if name == "budget_enforcer_mod":
        import zephyr.governance.budget_enforcement as _mod

        return _mod
    if name == "rollback_mod":
        import zephyr.governance.rollback as _mod

        return _mod
    if name == "a2a_protocol":
        import zephyr.l01_infrastructure.a2a_protocol.governance as _mod

        return _mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ARCH-036: 路径漂移防御——部分模块已被重构到子目录，直接 import 可能失败。
# 用 try/except 包裹避免单个 import 失败阻塞整个包初始化（符合 __getattr__ 延迟导入设计）。
try:
    from zephyr.governance.audit_trail.agent_signer import AgentSigner
    from zephyr.governance.akshare_provider import AkshareProvider
    from zephyr.governance.base import FactorMeta
    from zephyr.governance.blind_spot_tracker import BlindSpotStatus
    from zephyr.governance.capability_lookup import CapabilityLookup
    from zephyr.governance.canary_manager import CanaryFile
    from zephyr.governance.audit_trail.changelog_manager import ChangeImpact
    from zephyr.governance.classifier import Classifier
    from zephyr.governance.cli import main
    from zephyr.governance.audit_trail.code_archaeology import BlameRecord
    from zephyr.governance.complexity_budget import ComplexityReport
    from zephyr.governance.audit_trail.compliance_map import ComplianceFramework
    from zephyr.governance.construction_verifier import ConstructionVerifier
    from zephyr.governance.audit_trail.corporate_actions import CorporateActionType
    from zephyr.governance.dashboard import Dashboard
    from zephyr.governance.database_service import DatabaseService
    from zephyr.governance.dependency import DependencyNode
    from zephyr.governance.dlq_retry_policy import RetryResult
    from zephyr.governance.audit_trail.dora_metrics import DORATargets
    from zephyr.governance.audit_trail.feedback_self_audit import FeedbackNode
    from zephyr.governance.finding_ingest import IngestResult
    from zephyr.governance.semantic_audit.fix_result_prioritizer import PrioritizedFixResult
    from zephyr.governance.gate_event_adapter import GateEventAdapter
    from zephyr.governance.audit_trail.glossary_matrix import GlossaryEntry
    from zephyr.governance.index_generator import IndexGenerator
    from zephyr.governance.audit_trail.kb_gate import KBWriteCheckResult
    from zephyr.governance.lifecycle import Lifecycle
    from zephyr.governance.llm_impact_analyzer import RiskLevel
    from zephyr.governance.metadata import GitCommitInfo
    from zephyr.governance.models import AssetType
    from zephyr.governance.phase_executor import PhaseStatus
    from zephyr.governance.pipeline_base import ExperimentConfig
    from zephyr.governance.audit_trail.privacy import PIICategory
    from zephyr.governance.reconciler import Reconciler
    from zephyr.governance.registry_adapter import RegistryParseError
    from zephyr.governance.audit_trail.sbom_generator import LicenseType
    from zephyr.governance.semantic_audit.self_healer import SelfHealError
    from zephyr.governance.semantic_audit.self_health import SLIResult
    from zephyr.governance.snapshot_manager import SnapshotError
    from zephyr.governance.audit_trail.spec_auditor import record_agent_spec
    from zephyr.governance.audit_trail.supply_chain import PackageRecord
    from zephyr.governance.token_budget import PoolLevel
    from zephyr.governance.trust_anchor import TrustLevel
    from zephyr.governance.audit_trail.wqa_scorer import WQAScore
except ImportError:
    pass

__all__ = [
    "AdmissionResponse",
    "AdmissionResponseBuilder",
    "AdmissionResponseStatus",
    "AgentSigner",
    "AkshareProvider",
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
    "Momentum20d",
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
    "format_hook",
    "fsm_verifier",
    "incident_response",
    "knowledge_engine",
    "lint_hook",
    "local_first_arch",
    "main",
    "market_data_pipeline",
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
    "session_concurrency",
    "spof_checker",
    "startup_shutdown",
    "startup_shutdown_cli",
    "strategy_portfolio",
    "system_topology",
    "typecheck_hook",
    "vibe_coding_enforcer",
]

__version__ = "0.2.0"
__domain_id__ = "DOM-GOV-001"
__module_count__ = 8
__contract_count__ = 8
