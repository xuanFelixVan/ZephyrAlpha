# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.lifecycle.health_discovery
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.health
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
# [A_module] module_id=MOD-INF_health_discovery | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""CT-HEALTH-001: System-wide Health Discovery Registration.

Registers AggregateHealth for all 12 infrastructure systems and provides
a unified healthz endpoint consumable by external monitoring.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final
import logging
from typing import Any

__all__ = [
    "ALL_SYSTEM_NAMES",
    "HealthDiscovery",
    "register_system_health",
]

_logger = logging.getLogger(__name__)

ALL_SYSTEM_NAMES: Final[tuple[str, ...]] = (
    "orchestrator",
    "script_system",
    "knowledge_base",
    "gate_engine",
    "context-engine",
    "pipeline",
    "feedback-loop",
    "vector-memory",
    "database",
    "mcp_gateway",
    "llm-security",
    "telemetry",
)


class HealthDiscovery:
    def __init__(self) -> None:
        self._registered: dict[str, dict[str, Any]] = {}
        for name in ALL_SYSTEM_NAMES:
            self._registered[name] = {"status": "unknown", "last_check": "", "details": {}}

    def register(self, system_name: str, check_fn: Callable[[], bool], **metadata: Any) -> None:
        if system_name not in self._registered:
            _logger.warning("HealthDiscovery.register: unknown system '%s'", system_name)
            self._registered[system_name] = {}
        self._registered[system_name].update(
            {
                "status": "registered",
                "check_fn": check_fn,
                "metadata": metadata,
            }
        )

    def get_status(self) -> dict[str, Any]:
        result: dict[str, Any] = {"systems": {}, "overall": "unknown"}
        healthy = 0
        unhealthy = 0
        for name, entry in self._registered.items():
            status = entry.get("status", "unknown")
            result["systems"][name] = {
                "status": status,
                "last_check": entry.get("last_check", ""),
                "details": entry.get("details", {}),
            }
            if status == "healthy":
                healthy += 1
            elif status in ("degraded", "unhealthy", "failed"):
                unhealthy += 1
        if unhealthy > 0:
            result["overall"] = "degraded"
        elif healthy == len(ALL_SYSTEM_NAMES):
            result["overall"] = "healthy"
        else:
            result["overall"] = "partial"
        return result

    @property
    def all_registered(self) -> bool:
        return all(e.get("status") not in ("unknown",) for e in self._registered.values())


_discovery = HealthDiscovery()


def register_system_health(system_name: str, check_fn: Callable[[], bool], **metadata: Any) -> None:
    _discovery.register(system_name, check_fn, **metadata)
    _logger.info(
        "CT-HEALTH-001 registered: %s status=%s",
        system_name,
        _discovery.get_status()["systems"].get(system_name, {}).get("status"),
    )
