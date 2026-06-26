# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.blueprint_decomposer
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.blueprint_decomposer
# [CONSUMERS] zephyr.infrastructure.file_watcher; zephyr.infrastructure.task_manager_server; zephyr.integration.mcp.task_manager_server; tests.test_blueprint_decomposer; tests.adversarial.test_cross_layer_systems_red_team; tests.adversarial.test_task_system_red_team; tests.unit.test_blueprint_decomposer_depends_unit; tests.unit.test_task_manager_mcp; tests.unit.core.test_blueprint_decomposer_depends_core
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
# Actual source: zephyr.shared.blueprint_decomposer
import importlib as _il

from zephyr.shared.blueprint_decomposer import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.blueprint_decomposer")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
