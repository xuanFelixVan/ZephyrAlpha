# [BLUEPRINT] DOM-GOV-001 | 03_modules/_domain-governance/blueprint.md | §
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

施工状态（2026-05-08 审计修正）：
  蓝图文档 v0.1.0 — 100% 完成（G-CT-001~008 契约定义 + Phase 1~4 施工顺序）
  桥接层 — 8/8 模块目录创建，G-CT-001~008 桥接代码就位
  独立引擎 — RBAC 完整(68+文件) / Drift 完整(48文件) / Escalation 中等(5文件) / Budget 中等(4文件) / A2A Phase 1 核心就绪(L1发现+L2通信+L3协调 49文件, ~20文件有真实实现, 25文件为Phase 2+脚手架)
  MCP GovernanceServer — 5 工具就位
  测试 — G-CT 契约测 + 红白对抗测已通过

注意：phase_check_registry 和 phase_manager 由调用方直接导入，不从 __init__ 重导出（避免循环依赖）。
"""

import zephyr.escalation_engine as escalation_protocol
import zephyr.budget_enforcer as budget_enforcer_mod
import zephyr.drift_detector as drift_detector_mod
import zephyr.rollback as rollback_mod
import zephyr.l01_infrastructure.a2a_protocol.governance as a2a_protocol

from zephyr.governance.path_resolver import PathResolver, PathResolution

from zephyr.governance.constitutional_update import (
    Learning,
    ProposedUpdate,
    ConstitutionalAutoUpdate,
)

from zephyr.governance.mcp_result_push import ResultPushManager, PushStatus

from zephyr.governance.admission_response import (
    AdmissionResponse,
    AdmissionResponseStatus,
    AdmissionResponseBuilder,
)

__all__ = [
    'agent_debate', 'agent_dispatch', 'ai_code_standards',
    'ai_self_diagnosis', 'api_lifecycle',
    'architecture_contracts', 'architecture_principles',
    'bandwidth_optimizer', 'benchmark_integrity', 'broker_resilience',
    'bus_factor_defense', 'code_review_ai',
    'consequence_manager',
    'constitutional_update',
    'mcp_result_push', 'ResultPushManager', 'PushStatus',
    'admission_response', 'AdmissionResponse', 'AdmissionResponseStatus', 'AdmissionResponseBuilder',
    'context_manager', 'context_recycling', 'cross_env_consistency',
    'data_classification',
    'data_lifecycle', 'data_quality', 'data_source_reliability',
    'decision_fatigue', 'decision_fatigue_cli',
    'dependency_manager', 'environment_manager',
    'fault_tolerance', 'financial_compliance', 'fsm_verifier',
    'incident_response', 'incremental_review',
    'knowledge_engine', 'local_first_arch', 'market_data_pipeline',
    'microstructure_defense', 'migration_strategy',
    'model_drift_monitor', 'multi_model_consensus', 'observability_dashboard',
    'offline_autonomy', 'offline_resilience', 'oms_risk_engine',
    'ops_foundation', 'paper_live_transition', 'path_resolver', 'performance_baseline',
    'phase_manager', 'PathResolution', 'PathResolver', 'ConstitutionalAutoUpdate', 'Learning', 'ProposedUpdate',
    'HookResult', 'HookStrategy', 'PipelineResult', 'PostProcessHook', 'PostProcessPipeline',
    'format_hook', 'lint_hook', 'typecheck_hook',
    'post_live_verification', 'prompt_lifecycle',
    'provenance_tracker', 'realtime_streaming', 'regime_detector',
    'session_concurrency', 'spof_checker',
    'startup_shutdown', 'startup_shutdown_cli', 'strategy_portfolio',
    'supply_chain_security', 'system_topology', 'vibe_coding_enforcer',
    'escalation_protocol',
    'budget_enforcer_mod',
    'drift_detector_mod',
    'rollback_mod',
    'a2a_protocol',
    'phase_check_registry',
    'post_process',
]

__version__ = "0.2.0"
__domain_id__ = "DOM-GOV-001"
__module_count__ = 8
__contract_count__ = 8
