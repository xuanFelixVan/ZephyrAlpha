# Proxy module - redirects to actual location
# Created by create_shared_services_proxies.py
# Actual source: zephyr.shared.infra_06.observer
import importlib as _il

from zephyr.shared.infra_06.observer import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.infra_06.observer")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
