# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.infra_06.cache
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.infra.cache
# [CONSUMERS] zephyr.integration.shared_08.cache; tests.test_infra_cache; zephyr.shared.shared_services.infra_06.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.shared.infra.cache
import importlib as _il

from zephyr.shared.infra.cache import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.infra.cache")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
