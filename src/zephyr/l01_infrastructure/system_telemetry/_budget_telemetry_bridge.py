# [BLUEPRINT] MOD-INF-015 | docs/03_modules/l01_infrastructure/system-telemetry/blueprint.md | §3

# [MODULE] zephyr.l01_infrastructure.system_telemetry._budget_telemetry_bridge

# [INVARIANTS] callback must be set before first use; getter returns None if unset

# [MODIFY-GUARD] auto_bootstrap.py; budget_engine.py

# [CONSUMERS] zephyr.budget_enforcer.budget_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] None return when unset

# [TESTS] tests/system_telemetry/test_budget_telemetry_bridge.py

from __future__ import annotations

from typing import Any, Callable

_telemetry_getter: Callable[[], Any] | None = None


def set_telemetry_getter(getter: Callable[[], Any]) -> None:
    global _telemetry_getter
    _telemetry_getter = getter


def get_telemetry() -> Any:
    if _telemetry_getter is not None:
        return _telemetry_getter()
    return None
