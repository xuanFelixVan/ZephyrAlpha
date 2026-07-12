# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.health.fle_dogfood_monitor
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_fle_dogfood_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""FLE Dogfood Monitor — v0.38.0 R480

Blindspot: "Who watches the watchmen?" — FLE monitors everything except itself.
FLE self-SLOs, self-diagnosis, and self-healing are assumed but never verified.
FLE can silently degrade while reporting all other systems as healthy.

Risk: R480 — FLE degrades -> misses real anomalies -> system fails with no
warning. The monitoring system itself is the single point of failure.

Mitigation: Dogfood the FLE: apply the same collect->detect->diagnose->act->verify
pipeline to FLE's own metrics. Track FLE-specific SLOs. Auto-diagnose FLE
degradation. Three redundant health signals cross-validated.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class FLESelfHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    SICK = "SICK"
    CRITICAL = "CRITICAL"


@dataclass
class FLEDogfoodMonitor:
    max_consecutive_missed_cycles: int = 3
    max_self_diagnosis_latency_ms: float = 10000.0
    max_metric_gap_seconds: float = 120.0

    self_metrics: dict[str, list[float]] = field(default_factory=dict)
    missed_cycles: int = 0
    last_self_check: float = 0.0
    self_health: FLESelfHealth = FLESelfHealth.HEALTHY
    dogfood_events: list[dict] = field(default_factory=list)

    def record_self_metric(self, name: str, value: float) -> None:
        if name not in self.self_metrics:
            self.self_metrics[name] = []
        self.self_metrics[name].append(value)
        if len(self.self_metrics[name]) > 100:
            self.self_metrics[name] = self.self_metrics[name][-100:]

    def self_check(self) -> dict:
        now = time.time()
        self.last_self_check = now

        issues = []

        metric_gap = now - self.last_self_check if self.last_self_check > 0 else 0
        if self.last_self_check > 0 and metric_gap > self.max_metric_gap_seconds:
            self.missed_cycles += 1
            issues.append(f"metric_gap={metric_gap:.0f}s")
        else:
            self.missed_cycles = 0

        if self.missed_cycles > self.max_consecutive_missed_cycles:
            issues.append(f"missed_cycles={self.missed_cycles}")

        self_check_latency = (time.time() - now) * 1000
        if self_check_latency > self.max_self_diagnosis_latency_ms:
            issues.append(f"self_check_slow={self_check_latency:.0f}ms")

        if len(issues) >= 3:
            self.self_health = FLESelfHealth.CRITICAL
        elif len(issues) >= 2:
            self.self_health = FLESelfHealth.SICK
        elif len(issues) >= 1:
            self.self_health = FLESelfHealth.DEGRADED
        else:
            self.self_health = FLESelfHealth.HEALTHY

        if self.self_health is not FLESelfHealth.HEALTHY:
            self.dogfood_events.append(
                {
                    "ts": now,
                    "health": self.self_health.value,
                    "issues": issues,
                }
            )

        return {
            "self_health": self.self_health.value,
            "issues": issues,
            "missed_cycles": self.missed_cycles,
            "recommendation": (
                "trigger_external_watchdog"
                if self.self_health is FLESelfHealth.CRITICAL
                else "reduce_self_check_interval"
                if self.self_health is FLESelfHealth.SICK
                else "log_and_continue"
                if self.self_health is FLESelfHealth.DEGRADED
                else "continue"
            ),
        }

    def get_self_slo_compliance(self) -> dict:
        return {
            "uptime_percent": round(
                100.0
                * (
                    1.0
                    - len([e for e in self.dogfood_events if e["health"] == FLESelfHealth.CRITICAL.value])
                    / max(len(self.dogfood_events), 1)
                ),
                1,
            ),
            "degradation_events": len([e for e in self.dogfood_events if e["health"] != FLESelfHealth.HEALTHY.value]),
            "last_health": self.self_health.value,
            "healthy": self.self_health is FLESelfHealth.HEALTHY,
        }

    def get_self_metric_summary(self) -> dict:
        return {
            name: {
                "latest": round(vals[-1], 3) if vals else 0,
                "mean": round(sum(vals) / len(vals), 3) if vals else 0,
                "count": len(vals),
            }
            for name, vals in self.self_metrics.items()
        }
