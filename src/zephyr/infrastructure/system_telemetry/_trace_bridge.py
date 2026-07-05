# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry._trace_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF__trace_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
from typing import Any

_span_context_getter: Callable[[], Any] | None = None
_record_writer: Callable[[dict[str, Any], dict[str, Any] | None], bool] | None = None


def set_span_context_getter(fn: Callable[[], Any]) -> None:
    global _span_context_getter
    _span_context_getter = fn


def set_record_writer(fn: Callable[[dict[str, Any], dict[str, Any] | None], bool]) -> None:
    global _record_writer
    _record_writer = fn


def get_current_span() -> Any:
    if _span_context_getter is not None:
        return _span_context_getter()
    return None


def write_record(data: dict[str, Any], labels: dict[str, Any] | None = None) -> bool:
    if _record_writer is not None:
        return _record_writer(data, labels)
    return False
