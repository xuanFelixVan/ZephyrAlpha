# [A_module] module_id=MOD-INF_token_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.infrastructure.shared_services.observability_02.token_utils

# [INVARIANTS] re-export shim only; canonical source is zephyr.autonomy_core.token_budget

# [MODIFY-GUARD] do not add logic here; modify zephyr.autonomy_core.token_budget instead

# [CONSUMERS] external packages importing from shared.observability

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import importlib as _il
_mod = _il.import_module("zephyr.autonomy_core.token_budget")
for _n in getattr(_mod, "__all__", [n for n in dir(_mod) if not n.startswith("_")]):
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
