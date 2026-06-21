# [A_module] module_id=MOD-ORC_rc_orch_proxy | layer=package | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] GOV-037-CONVERGENCE | docs/02_enterprise_architecture/governance_convergence_plan.md | P0
# [MODULE] zephyr.trading.orchestrator
# [INVARIANTS] 代理子包——重定向到 zephyr.trading.orchestrator
# [MODIFY-GUARD] OPS-2026062101
# [CONSUMERS] blueprint_scorer/agent_orchestrator/trigger_router 等
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModuleNotFoundError if proxy target missing
# [TESTS] tests/unit/test_orchestration_proxy.py

"""
zephyr.trading.orchestrator — 代理子包

物理位置：zephyr.trading.orchestrator
"""

__all__ = ["blueprint_scorer"]

