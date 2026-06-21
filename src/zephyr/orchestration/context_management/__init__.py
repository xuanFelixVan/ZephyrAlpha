# [A_module] module_id=MOD-ORC_cm_proxy | layer=package | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] GOV-037-CONVERGENCE | docs/02_enterprise_architecture/governance_convergence_plan.md | P0
# [MODULE] zephyr.orchestration.context_management
# [INVARIANTS] 代理子包——重定向到 zephyr.autonomy_core
# [MODIFY-GUARD] OPS-2026062101
# [CONSUMERS] shared.observability_02.token_utils; shared.observability.token_utils; infra_runtime.rollback.phase_check_registry
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModuleNotFoundError if proxy target missing
# [TESTS] tests/unit/test_orchestration_proxy.py

"""
zephyr.orchestration.context_management — 代理子包

物理位置：zephyr.autonomy_core（token_budget、shadow_canary、vector_bridge 等）
"""

__all__ = ["token_budget"]

