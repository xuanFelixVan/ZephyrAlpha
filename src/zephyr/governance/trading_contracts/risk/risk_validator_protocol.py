# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.governance.trading_contracts.risk.risk_validator_protocol
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] ex_core.execution_engine; risk.risk_validator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.risk.risk_validator_protocol
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.risk.risk_validator_protocol
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError on negative limit_value
# [TESTS] tests/risk/test_risk_validator.py; tests/ex_core/
# [A_module] module_id=MOD-EXE_risk_validator_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.risk.risk_validator_protocol。"""
from zephyr.trading.trading_contracts.risk.risk_validator_protocol import *  # noqa: F401,F403
