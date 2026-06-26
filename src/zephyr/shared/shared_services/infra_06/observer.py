# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.shared_services.infra_06.observer
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.infra_06.observer
# [CONSUMERS] zephyr.autonomy_core.context_budget_tracker; zephyr.autonomy_core.pipeline_orchestrator; zephyr.autonomy_core.management.context_budget_tracker; zephyr.integration.pipeline_orchestrator; zephyr.integration.shared.events.dlq; zephyr.integration.shared.events.event_schemas; zephyr.integration.shared_08.contract_versions; zephyr.integration.shared_08.observer; zephyr.integration.shared_08.foundation.constants; zephyr.trading.orchestrator.deferred_queue; zephyr.trading.orchestrator.resilience.deferred_queue; tests.test_deferred_queue; tests.test_infra_observer; tests.test_mgmt_context_budget_tracker
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
# Actual source: zephyr.shared.infra_06.observer
import importlib as _il

from zephyr.shared.infra_06.observer import *  # noqa: F403

_mod = _il.import_module("zephyr.shared.infra_06.observer")
for _n in [n for n in dir(_mod) if not n.startswith("__")]:
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
