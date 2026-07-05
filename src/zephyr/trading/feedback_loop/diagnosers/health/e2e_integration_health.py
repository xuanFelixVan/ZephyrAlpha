# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.health.e2e_integration_health
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_e2e_integration_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""E2E Integration Health Monitor — v0.39.0 R489

Blindspot: FLE monitors individual components but not their integration. Component
A and Component B both report GREEN, but A→B communication is silently broken.
The system as a whole can be DEGRADED while every part reports HEALTHY.

Risk: R489 — False sense of security: all dashboards green but the end-to-end
user experience is broken. Integration failures hide between component boundaries.

Mitigation: Monitor cross-component integration points as first-class health
signals. Define integration contracts (latency SLA, error rate, throughput).
Detect when integration health diverges from component health.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class IntegrationHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BROKEN = "BROKEN"
    UNKNOWN = "UNKNOWN"


@dataclass
class E2EIntegrationHealth:
    max_integration_latency_ms: float = 10000.0
    max_integration_error_rate: float = 0.05
    min_sample_count: int = 10

    integrations: dict[str, dict] = field(default_factory=dict)
    health_history: list[dict] = field(default_factory=list)

    def register_integration(
        self, name: str, source: str, target: str, sla_latency_ms: float, sla_error_rate: float
    ) -> None:
        self.integrations[name] = {
            "source": source,
            "target": target,
            "sla_latency_ms": sla_latency_ms,
            "sla_error_rate": sla_error_rate,
            "latency_samples": [],
            "success_count": 0,
            "failure_count": 0,
            "total_samples": 0,
        }

    def record_call(self, integration_name: str, latency_ms: float, success: bool) -> None:
        integration = self.integrations.get(integration_name)
        if not integration:
            return
        integration["latency_samples"].append(latency_ms)
        if len(integration["latency_samples"]) > 200:
            integration["latency_samples"] = integration["latency_samples"][-200:]
        if success:
            integration["success_count"] += 1
        else:
            integration["failure_count"] += 1
        integration["total_samples"] += 1

    def check_integration_health(self, integration_name: str) -> dict:
        integration = self.integrations.get(integration_name)
        if not integration:
            return {"health": IntegrationHealth.UNKNOWN.value, "reason": "not_registered"}

        total = integration["total_samples"]
        if total < self.min_sample_count:
            return {"health": IntegrationHealth.UNKNOWN.value, "reason": f"insufficient_samples:{total}"}

        lats = sorted(integration["latency_samples"])
        p95 = lats[int(len(lats) * 0.95)] if lats else 0
        error_rate = integration["failure_count"] / max(total, 1)

        violations = []
        if p95 > integration["sla_latency_ms"]:
            violations.append(f"p95_latency={p95:.0f}ms > sla={integration['sla_latency_ms']}ms")
        if error_rate > integration["sla_error_rate"]:
            violations.append(f"error_rate={error_rate:.3f} > sla={integration['sla_error_rate']}")

        if len(violations) >= 2:
            health = IntegrationHealth.BROKEN
        elif len(violations) == 1:
            health = IntegrationHealth.DEGRADED
        else:
            health = IntegrationHealth.HEALTHY

        return {
            "integration": integration_name,
            "health": health.value,
            "source": integration["source"],
            "target": integration["target"],
            "p95_latency_ms": round(p95, 1),
            "error_rate": round(error_rate, 4),
            "violations": violations,
            "total_samples": total,
        }

    def check_all_integrations(self) -> dict:
        results = {}
        broken = 0
        degraded = 0
        for name in self.integrations:
            result = self.check_integration_health(name)
            results[name] = result
            if result["health"] == IntegrationHealth.BROKEN.value:
                broken += 1
            elif result["health"] == IntegrationHealth.DEGRADED.value:
                degraded += 1

        overall = (
            IntegrationHealth.BROKEN
            if broken > 0
            else IntegrationHealth.DEGRADED
            if degraded > 1
            else IntegrationHealth.HEALTHY
        )

        self.health_history.append(
            {
                "ts": time.time(),
                "overall": overall.value,
                "broken_count": broken,
                "degraded_count": degraded,
                "total": len(self.integrations),
            }
        )
        if len(self.health_history) > 500:
            self.health_history = self.health_history[-500:]

        return {
            "overall_health": overall.value,
            "broken_integrations": broken,
            "degraded_integrations": degraded,
            "healthy_integrations": len(self.integrations) - broken - degraded,
            "details": results,
        }

    def get_degradation_trend(self) -> dict:
        if len(self.health_history) < 2:
            return {"trend": "stable", "reason": "insufficient_history"}

        recent = self.health_history[-10:]
        older = self.health_history[-20:-10] if len(self.health_history) >= 20 else self.health_history[:-10]
        if not older:
            return {"trend": "stable"}

        recent_broken = sum(1 for h in recent if h["overall"] == IntegrationHealth.BROKEN.value)
        older_broken = sum(1 for h in older if h["overall"] == IntegrationHealth.BROKEN.value)

        if recent_broken > older_broken:
            return {"trend": "degrading", "recent_broken": recent_broken, "older_broken": older_broken}
        elif recent_broken < older_broken:
            return {"trend": "improving", "recent_broken": recent_broken, "older_broken": older_broken}
        return {"trend": "stable", "broken_ratio": recent_broken / max(len(recent), 1)}

    def overall_integration_score(self) -> float:
        if not self.integrations:
            return 1.0
        healthy = sum(
            1
            for name in self.integrations
            if self.check_integration_health(name)["health"] == IntegrationHealth.HEALTHY.value
        )
        return round(healthy / len(self.integrations), 3)
