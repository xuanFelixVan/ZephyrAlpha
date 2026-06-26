# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.infra_06.process_pool
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.infra.process_pool
# [CONSUMERS] zephyr.infrastructure.infra_06.process_lifecycle_gateway; zephyr.infrastructure.lifecycle.resource_optimization_engine; zephyr.trading.resource_optimization; tests.unit.resource_optimization.test_process_pool
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.shared.infra.process_pool
import importlib as _il

from zephyr.shared.infra.process_pool import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.infra.process_pool")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
