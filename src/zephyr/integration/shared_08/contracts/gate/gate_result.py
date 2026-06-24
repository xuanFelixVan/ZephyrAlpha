# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.governance.rule_enforcement.gate_types
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.governance.rule_enforcement.gate_types.__init__
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.governance.rule_enforcement.gate_types
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.governance.rule_enforcement.gate_types
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.governance.rule_enforcement.gate_types"
# [A_module] module_id=MOD-INT_gate_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Re-export shim — 真源已合并至 zephyr.governance.rule_enforcement.gate_types。"""

from zephyr.governance.rule_enforcement.gate_types import *  # noqa: F401,F403
