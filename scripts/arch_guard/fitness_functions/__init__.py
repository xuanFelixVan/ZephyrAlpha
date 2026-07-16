# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/__init__.py | §
# [TTL] permanent
"""Architecture Guard — 不变量适应度函数集

每个文件对应 invariants.yaml 中的一条不变量。
执行方式：python scripts/arch_guard/fitness_functions/<name>.py
exit 0 = 不变量未被违反，exit 1 = 违反。

桩文件（manifest.yaml 中 status=stub）可作为模板扩展。
"""

__all__ = [
    "check_aisg_gateway",
    "check_audit_log_immutability",
    "check_capacity_slo_ssot",
    "check_daily_loss_limit",
    "check_hot_warm_ipc",
    "check_idempotency_key",
    "check_kill_switch_latency",
    "check_log_secret_leak",
    "check_no_cross_plane_mutable_state",
    "check_ocp_signatures",
    "check_pit_compliance",
    "check_position_limit",
    "check_risk_params_consistency",
    "check_survivorship_bias",
    "check_warm_cold_async",
]
