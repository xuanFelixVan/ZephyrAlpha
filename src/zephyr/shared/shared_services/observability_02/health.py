# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.observability_02.health
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.observability_02.health
# [CONSUMERS] zephyr.integration.shared_08.health
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.shared.observability_02.health
import importlib as _il

from zephyr.shared.observability_02.health import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.observability_02.health")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
