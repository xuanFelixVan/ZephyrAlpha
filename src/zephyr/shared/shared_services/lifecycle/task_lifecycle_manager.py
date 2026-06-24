# [BLUEPRINT] MOD-SHARED
# [MODULE] zephyr.shared.shared_services.lifecycle.task_lifecycle_manager
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.infrastructure.lifecycle.task_lifecycle_manager
# [CONSUMERS] zephyr.governance.rule_enforcement.task_completion_gate; tests.test_task_lifecycle_manager
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
# Actual source: zephyr.infrastructure.lifecycle.task_lifecycle_manager
import importlib as _il

from zephyr.infrastructure.lifecycle.task_lifecycle_manager import *  # noqa: F403

_mod = _il.import_module("zephyr.infrastructure.lifecycle.task_lifecycle_manager")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
