# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infra_ops/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.health_probes
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.__init__
# [CONSUMERS] zephyr.security.access_control
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 12-system triple-state probes; liveness/readiness/degraded contract; ProbeStatus enum stability
# [MODIFY-GUARD] health_aggregator.py; watchdog.py; health.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError; RuntimeError
# [TESTS] tests/system-telemetry/test_health_probes.py
# [A_module] module_id=MOD-INF_health_probes | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
三态健康探针协议（Health Probes — CT-HEALTH-001）

依据：MOD-MASTER-002 蓝图 §十四 标准化 HealthCheck
实现 12 系统 liveness/readiness/degraded 三态探针。
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProbeStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class LivenessProbe(BaseModel):
    status: str = "alive"
    pid: int = 0
    uptime_s: float = 0.0


class ReadinessProbe(BaseModel):
    status: str = "ready"
    dependencies: dict[str, str] = Field(default_factory=dict)


class HealthzProbe(BaseModel):
    status: ProbeStatus = ProbeStatus.HEALTHY
    degraded_details: str = ""


SYSTEMS: tuple[str, ...] = (
    "orchestrator",
    "script_system",
    "knowledge_base",
    "context-engine",
    "gate_engine",
    "pipeline",
    "feedback-loop",
    "vector-memory",
    "database",
    "llm-security",
    "system-telemetry",
    "mcp_servers",
)

SPECIAL_RULES: dict[str, dict] = {
    "orchestrator": {"degraded_when": "pending_queue > 100"},
    "context-engine": {"degraded_when": "token_budget > 7200"},
    "llm-security": {"no_degraded": True},
    "database": {"degraded_when": "wal_checkpoint_lag > 5s"},
}


class HealthProbeManager:
    def __init__(self):
        self._start_time = time.monotonic()
        self._states: dict[str, dict[str, Any]] = {}

    def liveness(self, system: str) -> dict:
        return {
            "status": "alive",
            "pid": 0,
            "uptime_s": round(time.monotonic() - self._start_time, 2),
            "system": system,
        }

    def readiness(self, system: str, deps_ok: bool = True) -> dict:
        return {
            "status": "ready" if deps_ok else "not_ready",
            "dependencies": {"db": "ok" if deps_ok else "down"},
            "system": system,
        }

    def healthz(self, system: str, metrics: dict[str, Any] | None = None) -> dict:
        rules = SPECIAL_RULES.get(system, {})
        degraded = False
        reason = ""

        if metrics:
            if system == "orchestrator" and metrics.get("pending_queue", 0) > 100:
                degraded = True
                reason = "pending_queue > 100"
            elif system == "context-engine" and metrics.get("token_budget", 0) > 7200:
                degraded = True
                reason = "token_budget > 7200"
            elif system == "database" and metrics.get("wal_checkpoint_lag", 0) > 5.0:
                degraded = True
                reason = "wal_checkpoint_lag > 5s"

        if rules.get("no_degraded") and degraded:
            degraded = False
            reason = ""

        return {
            "status": "degraded" if degraded else "healthy",
            "system": system,
            "degraded_details": reason,
        }

    def list_systems(self) -> list[str]:
        return list(SYSTEMS)
