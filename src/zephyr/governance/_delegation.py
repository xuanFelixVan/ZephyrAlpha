# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.governance._delegation
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_escalation_engine_imports.py
# [A_module] module_id=MOD-RES__delegation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from zephyr.governance.delegation_engine import DelegationEngine
from zephyr.governance.escalation_models import (
    DelegationRecord,
    DelegationStrategy,
    EconomicGuard,
)

_SUBMODULES = [
    "arbitrage_asymmetry_detector",
    "broker_resilience",
    "command_chain_length_gate",
    "compliance_mapper",
    "compositional_safety_tester",
    "error_budget_burst_limiter",
    "exchange_partition_detector",
    "exchange_reg_monitor",
    "flash_crash_guard",
    "oms_risk_engine",
    "order_state_escalator",
    "position_reconciler",
    "risk_matrix",
    "rule_canary_manager",
    "rule_debt_auditor",
    "rule_shadow_runner",
]

__all__ = [
    "DelegationEngine",
    "DelegationRecord",
    "DelegationStrategy",
    "EconomicGuard",
]
