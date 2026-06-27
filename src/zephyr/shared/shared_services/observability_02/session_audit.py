# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.observability_02.session_audit
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.session_audit
# [CONSUMERS] zephyr.governance.constitutional_update.constitutional_update; tests.unit.test_session_audit_unit; tests.unit.shared.test_adversarial_shared; tests.unit.shared.test_constitutional_update_shared; tests.unit.shared.test_session_audit_shared
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
# Actual source: zephyr.shared.session_audit
import importlib as _il

from zephyr.shared.session_audit import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.session_audit")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
