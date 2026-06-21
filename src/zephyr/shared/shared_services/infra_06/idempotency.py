# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.shared.infra_06.idempotency
from zephyr.shared.infra_06.idempotency import *  # noqa: F401, F403
import importlib as _il
_mod = _il.import_module("zephyr.shared.infra_06.idempotency")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
