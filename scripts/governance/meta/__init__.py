# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/__init__.py | §
# [TTL] permanent
"""
meta/ — 脚本系统自我审计维度（第 13 维度）

对标 MOD-INF-005 §13.1（系统健康自检）+ B16（关键阈值变更审计）。
本目录下的脚本负责审计脚本系统自身——"审计的审计"。
"""

__all__ = [
    "arbitrate_findings",
    "backup_runtime_state",
    "compute_sla_metrics",
    "create_task_from_finding",
    "detect_config_deviation",
    "detect_fix_oscillation",
    "detect_hallucinated_packages",
    "detect_script_divergence",
    "detect_script_rot",
    "false_negative_cases",
    "finding_state_machine",
    "manage_baseline",
    "manage_error_budget",
    "manage_finding_timeseries",
    "manage_kill_switch",
    "manage_script_ab_test",
    "manage_script_retirement",
    "manage_shadow_mode",
    "phase_e_context_check",
    "score_script_effectiveness",
    "trace_finding_lifecycle",
    "track_script_costs",
    "validate_automation_boundary",
    "validate_cross_model_consensus",
    "validate_dependency_chain",
    "validate_emergency_bypass_log",
    "validate_end_to_end_benchmark",
    "validate_environment_health",
    "validate_false_negatives",
    "validate_gate_engine_external",
    "validate_mutation_testing",
    "validate_rule_freshness",
    "validate_rules_file_backdoor",
    "validate_rules_integrity",
    "validate_script_onboarding",
    "validate_script_provenance",
    "validate_script_system_health",
    "validate_threshold_changes",
    "validate_trust_tier",
]
