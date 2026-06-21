# [A_module] module_id=MOD-ORC_rc_proxy | layer=package | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] GOV-037-CONVERGENCE | docs/02_enterprise_architecture/governance_convergence_plan.md | P0
# [MODULE] zephyr.orchestration.runtime_core
# [INVARIANTS] 代理子包——重定向到 zephyr.trading
# [MODIFY-GUARD] OPS-2026062101
# [CONSUMERS] 16处运行时调用（staging_area/resource_optimization/ide_health_daemon/capability_registry/orchestrator.*）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModuleNotFoundError if proxy target missing
# [TESTS] tests/unit/test_orchestration_proxy.py

"""
zephyr.orchestration.runtime_core — 代理子包

物理位置：zephyr.trading（autopilot、staging_area、orchestrator/ 等）
"""
