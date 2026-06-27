# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.infra_06.lock
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.infra_06.lock
# [CONSUMERS] zephyr.integration.shared_08.lock; tests.test_infra_lock
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
# Actual source: zephyr.shared.infra_06.lock
import importlib as _il

from zephyr.shared.infra_06.lock import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.infra_06.lock")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
