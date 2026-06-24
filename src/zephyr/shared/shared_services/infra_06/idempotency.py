# [BLUEPRINT] MOD-SHARED
# [MODULE] zephyr.shared.shared_services.infra_06.idempotency
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.infra_06.idempotency
# [CONSUMERS] zephyr.integration.shared_08.idempotency; tests.test_infra_idempotency
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
# Actual source: zephyr.shared.infra_06.idempotency
import importlib as _il

from zephyr.shared.infra_06.idempotency import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.infra_06.idempotency")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
