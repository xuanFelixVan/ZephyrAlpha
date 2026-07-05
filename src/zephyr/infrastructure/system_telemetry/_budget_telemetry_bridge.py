# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry._budget_telemetry_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.__init__
# [CONSUMERS] zephyr.infrastructure.budget_enforcement.budget_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] callback must be set before first use; getter returns None if unset
# [MODIFY-GUARD] auto_bootstrap.py; budget_engine.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None return when unset
# [TESTS] tests/system-telemetry/test_budget_telemetry_bridge.py
# [A_module] module_id=MOD-INF__budget_telemetry_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_telemetry_getter: Callable[[], Any] | None = None


def set_telemetry_getter(getter: Callable[[], Any]) -> None:
    global _telemetry_getter
    _telemetry_getter = getter


def get_telemetry() -> Any:
    if _telemetry_getter is not None:
        return _telemetry_getter()
    return None
