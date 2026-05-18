# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.observability.token_utils

# [INVARIANTS] re-export shim only; canonical source is zephyr.context_engine.token_budget

# [MODIFY-GUARD] do not add logic here; modify zephyr.context_engine.token_budget instead

# [CONSUMERS] external packages importing from shared.observability

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from zephyr.context_engine.token_budget import *  # noqa: F401, F403
