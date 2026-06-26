# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.session_continuity
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.session_continuity
# [CONSUMERS] zephyr.governance.phase_check_registry; zephyr.governance.ops_governance.phase_check_registry; zephyr.infrastructure.rollback.phase_check_registry; zephyr.infrastructure.system_telemetry.auto_bootstrap; tests.test_session_continuity_core_root; tests.test_session_continuity_root; tests.test_session_continuity_session; tests.integration.test_auto_telemetry_bootstrap; tests.unit.test_session_continuity_unit; tests.unit.core.test_session_continuity_core
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
# Actual source: zephyr.shared.session_continuity
import importlib as _il

from zephyr.shared.session_continuity import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.session_continuity")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
