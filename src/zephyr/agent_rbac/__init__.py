"""
Agent 身份与权限系统 — 七层纵深防御 + 六横切面 Runtime RBAC 11.3

module_id: MOD-INF-018 | version: 0.14.0 | layer: cross_layer | status: construction

核心职责: 判定"这个 Agent 能不能做这件事"——运行时权限强制执行。单次检查 < 1ms。

架构模式: 七层纵深防御 + 六横切面 (Defense-in-Depth + Cross-Cutting)
  垂直层 L0-L7: 不可变核心 → 六层增量护栏
  横切面 A-F: 权限钩子 / 权限拓扑 / 自动维护 / 意图绑定与连续验证(IBAC) / 对抗韧性&激励对齐 / 取证级安全保障

对标: Grantex State of Agent Security 2026 + Google Antigravity P0 + VibeGuard + SecureVibes +
  Sherlock + SUSVIBES + STRIDE + OWASP Agentic Top 10 + OWASP MCP Top 10 + NVIDIA Morpheus +
  MCPSHIELD + CSA/COSAiS + NIST CAISI + HexagonalRodent + ETDI +
  CVE-2026-26268 + LiteLLM TeamPCP + PocketOS全链路 + Claude Code预执行CVE +
  Unit 42 MCP Sampling + SymbioticSec 80% + OX Security MCP STDIO 200K +
  Azure Agent Identity + AWS Agent IAM + PraisonAI CVE-2026-39890 +
  Awesome AI Agent Attacks全时间线(2024-2026)

209项盲点全覆盖。

运行场景约束:
  - 100% AI 开发，多 IDE 并发 (TRAE / Cursor / RooCode)
  - 同时开启 10+ 对话 — 阻塞式审批绝对不可接受
  - 1 人 + AI，99% AI 维护 — 人工审批最小化
  - 权限层核心必须不可变 — AI 不能修改自己的护栏
  - Owner 缺席时自治保守模式 — 超时未审阅→自动降权
  - Vibe Coding AI 零记忆重启 — 权限规则必须自解释

DOM-GOV-001 集成契约:
  G-CT-001: 产出方 — RBAC 判定后写入 Audit (MOD-INF-020)
  G-CT-004: 消费方 — 承接 Escalation 的权限策略 (MOD-INF-022)
  G-CT-007: 消费方 — Agent Spec 与权限绑定 (MOD-INF-019)
  G-CT-008: 消费方 — A2A 身份与隔离 (MOD-INF-025)

垂直层结构:
  L0: 不可变核心 — PermissionGuard 基础判定 + rbac_roles.yaml SSoT
  L1: 信任默认 — Cold-Start Lock + 渐进信任建立
  L2: 边界拦截 — Agent身份认证 + 会话Token签名校验
  L3: 序列阻断 — 操作序列追踪 + 危险序列检测 + 跨Session关联
  L4: 先干后验 — auto_guard 模式 + 后验失败→auto-rollback
  L5: 自动回滚 — 异常行为检测 + 权限变更自动回退
  L6: 全局熔断 — Kill Switch + Engine降级策略 + 降级攻击防护

横切面结构:
  A: 权限钩子系统 — pre/post/on_blocked/on_kill_switch 四类钩子
  B: 权限拓扑 — 权限依赖图 + 权限变更影响分析
  C: 自动维护 — 规则自我修剪 + 僵尸规则检测 + 权限复杂度预算
  D: 意图绑定与连续验证(IBAC) — 意图声明 + 行为预期 + 偏差检测
  E: 对抗韧性&激励对齐 — 对抗样本检测 + Agent间合谋检测 + 激励对齐
  F: 取证级安全保障 — 非对称审计 + 不可否认性 + MCP工具完整性证明

管什么:
  - Agent 身份注册与识别 + Agent 成熟度分级
  - 权限声明式配置 (GOV-AI-001 → rbac_roles.yaml 自动派生)
  - 七层+六横切面运行时 Permission Guard (L0→L5 + 横切面 A/B/C/D/E/F)
  - auto_guard 后验失败 → auto-rollback
  - 全局 Kill Switch + Engine 降级策略 + 降级攻击防护
  - 操作序列追踪 + 危险序列阻断 + 跨 Session 关联 + Agent间隐式通信检测
  - 权限模拟 (Dry-Run) + 影响分析 + 对抗性测试
  - 横向越权防护 — Agent身份防伪 + session_token签名校验
  - 冷启动锁 — 系统启动时全局拒绝直到权限配置加载校验通过
  - 权限钩子系统 — pre/post/on_blocked/on_kill_switch 四类钩子
  - Agent 创建权与权限遗传 — Agent 派生/复制的权限衰减继承
  - 紧急覆盖令牌 — Owner签发的JIT临时越权令牌 (<5分钟有效)
  - Owner缺席策略 — 超时未审阅→自动进入保守模式
  - 规则自我修剪 — 僵尸规则检测 + 权限复杂度预算
  - 第三方依赖管控 — package_install 白名单
  - 网络边界管控 — Agent工具调用的network_target白名单
  - 环境变量保护 — .env/pyproject.toml 等纳入保护路径

不管什么 (→ 去哪):
  - Agent 的具体执行逻辑 → Orchestrator (MOD-INF-006)
  - 权限判定的触发时机 → Gate Engine (MOD-INF-007)
  - 权限审计日志的存储 → Audit Trail (MOD-INF-020)
  - 回滚的具体执行 → Rollback System (MOD-INF-021)
  - 熔断器的底层实现 → Circuit Breaker (MOD-INF-022)
  - 具体的 Prompt Injection 检测 → Input Sanitizer / LSG (MOD-INF-014)
  - 生产环境的实际部署 → CI/CD
  - Agent 会话管理 → Session Continuity
"""

__all__ = ['AdversarialResilience', 'AgentIdentity', 'AgentMaturity', 'AgentRbacError', 'AutoGuard', 'AutoMaintenance', 'ColdStartLock', 'ColdStartLockedError', 'EscalationHandler', 'ForensicAssurance', 'IntentBinder', 'KillSwitch', 'OverrideTokenExpiredError', 'PermissionDeniedError', 'PermissionGuard', 'PermissionHookRegistry', 'PermissionRequest', 'PermissionTopology', 'PermissionVerdict', 'RbacConfig', 'SequenceGuard', 'abac_guard', 'adversarial_resilience', 'agent_creation_policy', 'anomaly_detector', 'asymmetric_audit', 'audit_log_guard', 'auto_maintenance', 'blind_spot_tracker', 'blueprint_fidelity', 'bootstrap_verifier', 'build_sanitizer', 'cache_invalidation', 'canary_rollout_manager', 'cascading_failure_isolator', 'cold_start_lock', 'get_cold_start_lock', 'context_drift_detector', 'continuous_verifier', 'contract_verifier', 'cross_cutting', 'cross_session_detector', 'cybersec_2026_guard', 'decision_explainer', 'decision_registry', 'dependency_auditor', 'derive_rbac_roles', 'dry_run', 'emergency_override', 'engine_degradation', 'escalation_handler', 'exceptions', 'false_completion_detector', 'genesis_bootstrap', 'guard_layers', 'identity', 'immutable_core', 'input_guard', 'integration', 'integrity_self_check', 'intent_binder', 'key_hierarchy', 'kill_switch', 'legal_audit_chain', 'memory_guard', 'memory_provenance_guard', 'micro_verifier', 'monotonic_clock', 'multi_agent_collusion_detector', 'native_api_guard', 'non_repudiation', 'novel_attack_guard', 'observability', 'output_guard', 'path_guard', 'permission_guard', 'permission_hooks', 'permission_mode_manager', 'phase_executor', 'post_action_verifier', 'rbac_guard', 'replay_attack_guard', 'risk_mitigation', 'rollback_sandbox', 'rule_injection_guard', 'sequence_guard', 'shell_dialect_detector', 'toctou_guard', 'vibe_coding_guard']

_COREMODULES: dict[str, tuple[str, ...]] = {
    "permission_guard": ("PermissionGuard", "GuardDecision", "GuardResult"),
    "identity": ("AgentIdentity", "AgentMaturity"),
    "rbac_guard": ("PermissionVerdict", "PermissionRequest", "PermissionDecision", "PermissionResult", "RBACGuard"),
    "immutable_core": ("ImmutableCore", "RbacConfig"),
    "guard_layers": ("ColdStartLock", "AutoGuard", "EscalationHandler"),
    "sequence_guard": ("SequenceGuard",),
    "kill_switch": ("KillSwitch",),
    "cross_cutting": ("PermissionHookRegistry", "PermissionTopology", "AutoMaintenance", "ForensicAssurance"),
    "intent_binder": ("IntentBinder",),
    "adversarial_resilience": ("AdversarialResilience",),
    "exceptions": ("AgentRbacError", "PermissionDeniedError", "ColdStartLockedError", "OverrideTokenExpiredError"),
}


def __getattr__(name: str):
    for mod_name, symbols in _COREMODULES.items():
        if name in symbols:
            mod = __import__(f"zephyr.agent_rbac.{mod_name}", fromlist=[name])
            try:
                return getattr(mod, name)
            except AttributeError:
                pass
    raise AttributeError(f"module 'zephyr.agent_rbac' has no attribute '{name}'")
