# [A_module] module_id=MOD-INT_gate_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-161 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md

# [MODULE] zephyr.integration.shared_08.contracts.core.gate_types

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] backward-compat shim — canonical location is zephyr.governance.rule_enforcement.gate_types

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import importlib as _importlib
_mod = _importlib.import_module("zephyr.governance.rule_enforcement.gate_types")
for _name in getattr(_mod, '__all__', [n for n in dir(_mod) if not n.startswith('_')]):
    globals()[_name] = getattr(_mod, _name)
del _importlib, _mod, _name
