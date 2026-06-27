# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.observability_02.metrics
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.observability_02.metrics
# [CONSUMERS] zephyr.governance.cost_budget; zephyr.integration.shared_08.metrics
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.shared.observability_02.metrics
import importlib as _il

from zephyr.shared.observability_02.metrics import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.observability_02.metrics")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
