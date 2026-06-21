# [A_module] module_id=MOD-INF__budget_telemetry_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain-infra_ops/system-telemetry/blueprint.md | §3

# [MODULE] zephyr.infrastructure.system_telemetry._budget_telemetry_bridge

# [INVARIANTS] callback must be set before first use; getter returns None if unset

# [MODIFY-GUARD] auto_bootstrap.py; budget_engine.py

# [CONSUMERS] zephyr.infrastructure.budget_enforcement.budget_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] None return when unset

# [TESTS] tests/system-telemetry/test_budget_telemetry_bridge.py

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
