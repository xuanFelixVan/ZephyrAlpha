# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.ops.observability.token_utils
# [DOMAIN] D-OPS
# [DEPENDENCIES]
# [CONSUMERS] external packages importing from shared.observability
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; canonical source is zephyr.autonomy_core.token_budget
# [MODIFY-GUARD] do not add logic here; modify zephyr.autonomy_core.token_budget instead
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_token_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

import importlib

# Re-export shim — canonical source is zephyr.autonomy_core.token_budget
_mod = importlib.import_module("zephyr.autonomy_core.token_budget")
for _name in getattr(_mod, "__all__", [n for n in dir(_mod) if not n.startswith("_")]):
    globals()[_name] = getattr(_mod, _name)
del _mod, _name
