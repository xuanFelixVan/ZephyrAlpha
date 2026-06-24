# [BLUEPRINT] MOD-SHARED
# [MODULE] zephyr.shared.shared_services.queue.task_queue
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.infrastructure.queue.task_queue
# [CONSUMERS] zephyr.trading.auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.infrastructure.queue.task_queue
import importlib as _il

from zephyr.infrastructure.queue.task_queue import *  # noqa: F403

_mod = _il.import_module("zephyr.infrastructure.queue.task_queue")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
