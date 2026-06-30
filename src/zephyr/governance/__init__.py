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

# === MOVED MODULE REDIRECT (GOV-DOC-018 split, 2026-07-01) ===
# Root-level .py files were moved to functional subdirs. This finder redirects
# old import paths (zephyr.governance.X) to new locations (zephyr.governance.subdir.X).
# Handles all import styles: import X, from X import Y, from . import X.
import sys as _sys
import importlib as _importlib
import importlib.abc as _importlib_abc
import importlib.util as _importlib_util

_MOVED_MODULES = {
    "a2a_failure": "integration",
    "account_isolator": "access_control",
    "action_history": "ops",
    "adapter": "integration",
    "adversarial_tester": "adversarial",
    "agent_cooldown": "ops",
    "aisg_sandbox": "security",
    "akshare_provider": "data_layer",
    "alerts": "observability",
    "alternative_path_blocker": "rule_bridge",
    "analytics_base": "shared",
    "annotations": "shared",
    "anti_automation_bias": "code_quality",
    "api_response_sanitizer": "integration",
    "approval": "access_control",
    "arbitrage_asymmetry_detector": "trading",
    "artifact_scanner": "security",
    "ast_comparator": "code_quality",
    "atomic_fixer": "rule_bridge",
    "atomic_transaction_manager": "data_layer",
    "audit_schema": "audit",
    "audit_write_failure_protector": "audit",
    "auditor": "audit",
    "auto_fixer": "rule_bridge",
    "auto_rollback_trigger": "rollback",
    "auto_runner": "ops",
    "auto_test_generator": "code_quality",
    "autonomy_dashboard": "observability",
    "autonomy_regressor": "code_quality",
    "backtest_engine": "trading",
    "bandwidth_optimizer": "integration",
    "bare_repo_scanner": "security",
    "base": "shared",
    "base_repo": "rule_bridge",
    "behavioral_sampler": "delegation",
    "behavioral_trust_checker": "delegation",
    "blast_radius": "resilience",
    "blind_spot_tracker": "observability",
    "blueprint_bloat_monitor": "rule_bridge",
    "blueprint_code_consistency": "code_quality",
    "blueprint_reconciler": "audit",
    "bootstrapping_calibrator": "lifecycle",
    "broker_interface": "resilience",
    "broker_resilience": "resilience",
    "budget_enforcement": "budget",
    "budget_engine": "budget",
    "budget_handler": "budget",
    "budget_models": "budget",
    "budget_profile_manager": "budget",
    "budget_tracker": "budget",
    "burn_rate_monitor": "budget",
    "cache_manager": "data_layer",
    "canary_manager": "resilience",
    "canary_register": "resilience",
    "capability_lookup": "shared",
    "checkpoint_gc": "lifecycle",
    "circuit_breaker": "resilience",
    "classifier": "code_quality",
    "cli": "shared",
    "clock_guard": "rule_bridge",
    "code_analyzer_runner": "code_quality",
    "code_simulator": "code_quality",
    "coldstart_manager": "lifecycle",
    "command_chain_length_gate": "rule_bridge",
    "commit_gate_registry": "rule_bridge",
    "commit_quality_gate": "rule_bridge",
    "complexity_budget": "budget",
    "compliance_manager": "compliance",
    "compliance_mapper": "audit",
    "compliance_rule": "compliance",
    "compositional_safety_tester": "adversarial",
    "confidence_estimator": "observability",
    "confidence_quantifier": "observability",
    "config": "shared",
    "config_scanner": "code_quality",
    "consequence_manager": "delegation",
    "consequence_tracker": "delegation",
    "construction_verifier": "ops",
    "context_budget": "budget",
    "context_manager": "context",
    "context_package": "context",
    "context_recycling": "context",
    "context_switch_governor": "context",
    "context_waste_detector": "context",
    "continuous_trust": "delegation",
    "contract": "integration",
    "contract_consistency_checker": "integration",
    "contracts": "integration",
    "conversation_tax_detector": "budget",
    "cost_attributor": "budget",
    "cost_budget": "budget",
    "cost_router": "budget",
    "credential_guard": "access_control",
    "credential_rotation_trigger": "access_control",
    "cross_agent_conflict_detector": "integration",
    "cross_assistant_adapter": "integration",
    "cross_boundary_detector": "integration",
    "cross_platform_shell": "integration",
    "cross_session_correlator": "integration",
    "daily_ops": "ops",
    "dashboard": "observability",
    "data_lifecycle": "data_layer",
    "data_pipeline_guard": "data_layer",
    "database_manager": "data_layer",
    "database_service": "data_layer",
    "dead_module_detector": "drift",
    "deadlock_detector": "resilience",
    "debt_projector": "budget",
    "decision_auditor": "ops",
    "decision_fatigue": "ops",
    "decision_fatigue_cli": "ops",
    "default_attribution_engine": "ops",
    "default_quality_gate": "rule_bridge",
    "default_security_gateway": "security",
    "default_tca_engine": "ops",
    "degradation": "budget",
    "degradation_manager": "budget",
    "delegation_engine": "delegation",
    "delegation_manager": "delegation",
    "dependency": "rule_bridge",
    "depgraph_reader": "rule_bridge",
    "depgraph_schema": "rule_bridge",
    "diff_detector": "drift",
    "dlq_retry_policy": "resilience",
    "doom_loop_guard": "resilience",
    "down_migration_generator": "drift",
    "drift_detector": "drift",
    "drift_fix": "drift",
    "engine_sandbox": "orchestrator",
    "env_watcher": "ops",
    "error_budget_burst_limiter": "budget",
    "escalation_api": "escalation",
    "escalation_engine": "escalation",
    "escalation_fatigue_manager": "escalation",
    "escalation_loop_detector": "escalation",
    "escalation_metrics": "escalation",
    "escalation_models": "escalation",
    "escalation_smoke_tests": "escalation",
    "event_store": "data_layer",
    "evidence_pack": "audit",
    "exchange_partition_detector": "trading",
    "exchange_reg_monitor": "trading",
    "exit_codes": "rule_bridge",
    "external_merkle_proof": "audit",
    "extraction_safety": "security",
    "f5_boot_integration": "lifecycle",
    "f5_event_subscriber": "lifecycle",
    "f5_shutdown_manager": "lifecycle",
    "fail_mode_manager": "resilience",
    "false_negative_auditor": "audit",
    "fault_tolerance": "resilience",
    "fifteen_dimension_auditor": "audit",
    "file_creator": "rule_bridge",
    "financial_compliance": "compliance",
    "finding_ingest": "audit",
    "flash_crash_guard": "resilience",
    "forensic": "audit",
    "forensic_package": "audit",
    "formal_verifier": "ops",
    "forward_fix_runner": "rule_bridge",
    "fsm_verifier": "ops",
    "function_discovery": "code_quality",
    "gap_analyzer": "audit",
    "gate_coordinator": "rule_bridge",
    "gate_event_adapter": "rule_bridge",
    "gate_repo": "rule_bridge",
    "ghost_scan": "drift",
    "git_commit_gateway": "rule_bridge",
    "git_hook_pre_scanner": "rule_bridge",
    "git_infra_snapshot": "rule_bridge",
    "github_api_guard": "security",
    "grandfather_manager": "rule_bridge",
    "hallucination_guard": "adversarial",
    "health_monitor": "ops",
    "hooks_integrity_guard": "rule_bridge",
    "hotspot_tracker": "observability",
    "human_factors": "compliance",
    "identity_verifier": "security",
    "import_surface_tracker": "security",
    "incident_response": "ops",
    "index_generator": "audit",
    "instruction_bloat_detector": "observability",
    "instrument": "observability",
    "integration_hub": "integration",
    "integrations": "integration",
    "integrity": "rule_bridge",
    "integrity_verifier": "rule_bridge",
    "intent_archiver": "audit",
    "interrupt_handler": "resilience",
    "ipi_defense": "security",
    "knowledge_engine": "shared",
    "knowngoodstate_ledger": "resilience",
    "last_resort_watchdog": "resilience",
    "lifecycle": "shared",
    "llm_impact_analyzer": "observability",
    "maintenance_window_adapter": "lifecycle",
    "memory_poison_guard": "context",
    "memory_provenance": "audit",
    "memory_provider": "context",
    "merkle_audit": "audit",
    "merkle_hourly": "audit",
    "meta_confidence": "observability",
    "meta_observability": "observability",
    "metadata": "shared",
    "micro_clone_detector": "drift",
    "mock_duplicate_generator": "code_quality",
    "model_provider_data": "shared",
    "model_router": "shared",
    "model_version_detector": "shared",
    "models": "shared",
    "monoculture_guard": "security",
    "multi_turn_intent_analyzer": "observability",
    "mvep_orchestrator": "orchestrator",
    "objective_tracker": "orchestrator",
    "observation_window_guard": "resilience",
    "ops_foundation": "ops",
    "output_quality_gate": "rule_bridge",
    "owner_absent": "compliance",
    "paper_live_transition": "trading",
    "parent_child_attributor": "delegation",
    "path_index_validator": "rule_bridge",
    "performance_attribution_report": "observability",
    "persuasion_detector": "adversarial",
    "phase_check_registry": "rule_bridge",
    "phase_executor": "lifecycle",
    "phase_manager": "lifecycle",
    "pipeline_base": "shared",
    "poison_cascade_detector": "adversarial",
    "policy_sandbox": "rule_bridge",
    "policy_tree_validator": "rule_bridge",
    "post_live_verification": "lifecycle",
    "post_sync_validator": "rule_bridge",
    "pre_apply_integrity_gate": "rule_bridge",
    "pre_flight_gate": "rule_bridge",
    "pricing_sync": "trading",
    "prioritizer": "orchestrator",
    "process_isolator": "resilience",
    "projection_engine": "ops",
    "protocol_self_context": "integration",
    "protocol_state_store": "integration",
    "provider_base": "integration",
    "provider_failover": "resilience",
    "quality_gate": "rule_bridge",
    "query": "observability",
    "query_metrics": "observability",
    "question_tracker": "shared",
    "rbac_bridge": "access_control",
    "realtime_streaming": "trading",
    "reconciler": "audit",
    "reconciliation_registry": "audit",
    "recovery_manifest_writer": "resilience",
    "registry_adapter": "integration",
    "report": "observability",
    "result_types": "shared",
    "reward_hacking_rebound_detector": "adversarial",
    "right_to_be_forgotten": "compliance",
    "risk_matrix": "compliance",
    "risk_mitigation_tracker": "compliance",
    "risk_mitigator": "compliance",
    "roi_calculator": "budget",
    "rollback_abuse_detector": "rollback",
    "rollback_audit_nexus": "rollback",
    "rollback_bootstrap": "rollback",
    "rollback_budget": "rollback",
    "rollback_context_restorer": "rollback",
    "rollback_dashboard": "rollback",
    "rollback_drill": "rollback",
    "rollback_executor": "rollback",
    "rollback_integration": "rollback",
    "rollback_lock": "rollback",
    "rollback_loop_detector": "rollback",
    "rollback_simulator": "rollback",
    "rollback_state_machine": "rollback",
    "rollback_target_staleness": "rollback",
    "rollback_verifier": "rollback",
    "rollback_wal": "rollback",
    "rule_canary_manager": "resilience",
    "rule_debt_auditor": "budget",
    "rule_engine": "rule_bridge",
    "rule_shadow_runner": "rule_bridge",
    "rule_watcher": "rule_bridge",
    "runbook_generator": "ops",
    "s3_snapshot_lifecycle": "data_layer",
    "sandbox_enforcer": "security",
    "sbom_guard": "audit",
    "scanner": "observability",
    "secret_rotation_aware": "security",
    "security_config_scanner": "security",
    "security_gateway_base": "security",
    "self_benchmark": "observability",
    "self_budget_tracker": "budget",
    "self_scanner": "observability",
    "self_test": "observability",
    "self_validator": "observability",
    "semantic_cache": "code_quality",
    "semantic_rollback_tag": "rollback",
    "semantic_similar_detector": "code_quality",
    "sensitivity_sweeper": "security",
    "service_registration": "integration",
    "shadow_trust_validator": "delegation",
    "shadow_verifier": "ops",
    "shared_evolver": "shared",
    "shared_lifecycle_manager": "shared",
    "signature_matcher": "security",
    "silence_detector": "resilience",
    "simplicity_auditor": "code_quality",
    "slo_contract": "observability",
    "snapshot_manager": "data_layer",
    "spiral_ews": "resilience",
    "spof_checker": "resilience",
    "sqlite_dumper": "data_layer",
    "sqlite_schema": "data_layer",
    "ssot_registrar": "rule_bridge",
    "stale_shared_detector": "drift",
    "startup_shutdown": "lifecycle",
    "startup_shutdown_cli": "lifecycle",
    "strategy_base": "trading",
    "strategy_registry": "trading",
    "strategy_scoper": "trading",
    "stream_abort_guard": "resilience",
    "subagent_hook_propagator": "integration",
    "submodule_sync": "integration",
    "success_validator": "ops",
    "symbol_index": "data_layer",
    "tamper_evident_log": "audit",
    "task_repo": "shared",
    "tco_model": "budget",
    "temporal_context_adapter": "context",
    "temporal_drift_tracker": "drift",
    "thematic_clusterer": "compliance",
    "think_time_model": "orchestrator",
    "time_sync": "lifecycle",
    "timeout_guard": "resilience",
    "token_budget": "budget",
    "topology_change_log": "rule_bridge",
    "transition": "integration",
    "triage": "shared",
    "trust_anchor": "delegation",
    "trust_ring_manager": "delegation",
    "venv_sync": "lifecycle",
    "verifier": "ops",
    "vibe_security_verify": "security",
    "vibe_verify_integration": "adversarial",
    "vigil_runtime": "adversarial",
    "vulnerability_rescanner": "security",
    "warm_standby": "resilience",
    "witness_isolation": "resilience",
    "worktree_manager": "ops",
}

class _MovedModuleFinder(_importlib_abc.MetaPathFinder):
    """Redirect old root-level module imports to new subdir locations."""

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("zephyr.governance."):
            return None
        parts = fullname.split(".")
        if len(parts) != 3:
            return None
        mod_name = parts[2]
        if mod_name not in _MOVED_MODULES:
            return None
        new_subdir = _MOVED_MODULES[mod_name]
        new_fullname = f"zephyr.governance.{new_subdir}.{mod_name}"
        real_mod = _importlib.import_module(new_fullname)
        _sys.modules[fullname] = real_mod
        return _importlib_util.spec_from_loader(fullname, loader=_AliasLoader(real_mod))


class _AliasLoader(_importlib_abc.Loader):
    """Loader returning an already-imported module."""

    def __init__(self, module):
        self._module = module

    def create_module(self, spec):
        return self._module

    def exec_module(self, module):
        pass  # Already executed


_sys.meta_path.insert(0, _MovedModuleFinder())
# === END MOVED MODULE REDIRECT ===


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
