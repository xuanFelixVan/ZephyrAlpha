# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.lifecycle.daemon_registry
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.lifecycle.daemon_registry
# [CONSUMERS] zephyr.behavioral_audit.drift_cron_scheduler; tests.test_daemon_registry; tests.test_resource_optimization_engine
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
# Actual source: zephyr.shared.lifecycle.daemon_registry
import importlib as _il

from zephyr.shared.lifecycle.daemon_registry import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.lifecycle.daemon_registry")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
