# [A_module] module_id=MOD-SEC_access_control | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §
# [MODULE] zephyr.security.access_control
# [INVARIANTS] access_control 包——七层纵深防御权限强制执行器的根包；子模块按后缀簇归位 guards/verifiers/detectors/
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.governance.git_commit_gateway; zephyr.security.access_control.guards.rbac_guard; tests.unit.agent_rbac
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac/; tests/unit/agent_rbac/
# [TTL] task_bound
"""zephyr.security.access_control — Agent RBAC 权限强制执行器根包.

依据蓝图 MOD-INF-018（Agent RBAC 七层纵深防御）：
- guards/        — *_guard.py 权限守卫簇（rbac_guard/abac_guard/input_guard 等）
- verifiers/     — *_verifier.py 验证器簇
- detectors/     — *_detector.py 检测器簇
- 根目录        — 其他横切组件（contracts/identity/kill_switch 等）

子模块导入范式: from zephyr.security.access_control.guards.rbac_guard import RBACGuard
"""
# submodules are stubs pending implementation (ARCH-036) — 不在此处 re-export，按需显式 import

__all__ = [
    "a2a_check",
    "abac_guard",
    "adversarial_resilience",
    "agent_creation_policy",
    "anomaly_detector",
    "anti_pattern_guard",
    "approver_check",
    "asymmetric_audit",
    "audit_log_guard",
    "auto_maintenance",
    "blind_spot_tracker",
    "blueprint_fidelity",
    "bootstrap_superadmin",
    "bootstrap_verifier",
    "build_sanitizer",
    "cache_invalidation",
    "canary_rollout_manager",
    "capability_check",
    "cascading_failure_isolator",
    "cold_start_lock",
    "compliance_matrix",
    "context_drift_detector",
    "continuous_verifier",
    "contract_verifier",
    "contracts",
    "cross_cutting",
    "cross_session_detector",
    "cybersec_2026_guard",
    "decision_explainer",
    "decision_registry",
    "defense_depth",
    "dependency_auditor",
    "derive_rbac_roles",
    "dry_run",
    "emergency_override",
    "engine_degradation",
    "environment_manager",
    "escalation_handler",
    "exceptions",
    "false_completion_detector",
    "genesis_bootstrap",
    "governance_bridges",
    "guard_layers",
    "identity",
    "immutable_core",
    "input_guard",
    "integration",
    "integrity_self_check",
    "intent_binder",
    "key_hierarchy",
    "kill_switch",
    "legal_audit_chain",
    "memory_guard",
    "memory_provenance_guard",
    "micro_verifier",
    "microstructure_defense",
    "monotonic_clock",
    "multi_agent_collusion_detector",
    "native_api_guard",
    "non_repudiation",
    "novel_attack_guard",
    "observability",
    "output_guard",
    "path_guard",
    "permission_guard",
    "permission_hooks",
    "permission_mode_manager",
    "phase_executor",
    "post_action_verifier",
    "rbac_guard",
    "replay_attack_guard",
    "risk_mitigation",
    "rollback_sandbox",
    "rule_injection_guard",
    "secrets_lifecycle",
    "sequence_guard",
    "session_concurrency",
    "session_lifecycle",
    "shell_dialect_detector",
    "toctou_guard",
    "vibe_coding_guard",
]
