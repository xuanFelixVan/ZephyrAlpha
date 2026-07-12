# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience.graceful_degradation_planner
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_graceful_degradation_planner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Graceful Degradation Planner — v0.40.0 R496

Blindspot: When FLE is overloaded or resource-constrained, it has no pre-planned
degradation strategy. It either runs everything (causing more overload) or crashes
entirely — no middle ground. Without a tiered degradation plan, overload -> crash
-> no monitoring at all.

Risk: R496 — FLE disappears during peak load exactly when monitoring is most needed.
System runs blind during crisis because the watchdog died from exhaustion.

Mitigation: Four-tier degradation model:
  P0: CRITICAL — keep at full frequency (core anomaly detection, safety gates)
  P1: IMPORTANT — reduce frequency to 50% (diagnosis, non-critical verifiers)
  P2: NICE_TO_HAVE — pause entirely (forensic archiving, evolution/training)
  P3: COSMETIC — drop (detailed reporting, historical replay)
Auto-degrade on resource pressure, auto-restore when pressure subsides.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class DegradationTier(str, Enum):
    P0_CRITICAL = "P0"
    P1_IMPORTANT = "P1"
    P2_NICE_TO_HAVE = "P2"
    P3_COSMETIC = "P3"


class DegradationLevel(str, Enum):
    FULL = "FULL"
    REDUCED = "REDUCED"
    MINIMAL = "MINIMAL"
    OBSERVE_ONLY = "OBSERVE_ONLY"


@dataclass
class GracefulDegradationPlanner:
    cpu_threshold_pct: float = 85.0
    memory_threshold_pct: float = 85.0
    cooldown_seconds: float = 300.0

    services: dict[str, dict] = field(default_factory=dict)
    current_level: DegradationLevel = DegradationLevel.FULL
    degradation_history: list[dict] = field(default_factory=list)
    last_degradation: float = 0.0

    def register_service(self, name: str, tier: DegradationTier, frequency_hz: float) -> None:
        self.services[name] = {
            "tier": tier,
            "base_frequency_hz": frequency_hz,
            "current_frequency_hz": frequency_hz,
            "active": True,
        }

    def evaluate_degradation(self, cpu_pct: float, memory_pct: float) -> dict:
        now = time.time()

        if cpu_pct > self.cpu_threshold_pct or memory_pct > self.memory_threshold_pct:
            new_level = self._next_degradation_level()
        elif cpu_pct < self.cpu_threshold_pct * 0.5 and memory_pct < self.memory_threshold_pct * 0.5:
            new_level = self._next_restoration_level()
        else:
            new_level = self.current_level

        if new_level != self.current_level and (now - self.last_degradation) > self.cooldown_seconds:
            self.last_degradation = now
            self.current_level = new_level
            self._apply_degradation()
            self.degradation_history.append(
                {
                    "ts": now,
                    "level": new_level.value,
                    "cpu_pct": round(cpu_pct, 1),
                    "memory_pct": round(memory_pct, 1),
                }
            )

        active_services = sum(1 for s in self.services.values() if s["active"])
        return {
            "level": self.current_level.value,
            "cpu_pct": round(cpu_pct, 1),
            "memory_pct": round(memory_pct, 1),
            "active_services": active_services,
            "total_services": len(self.services),
            "recommendation": (
                "scale_up_or_increase_thresholds" if self.current_level != DegradationLevel.FULL else "continue"
            ),
        }

    def _next_degradation_level(self) -> DegradationLevel:
        order = [
            DegradationLevel.FULL,
            DegradationLevel.REDUCED,
            DegradationLevel.MINIMAL,
            DegradationLevel.OBSERVE_ONLY,
        ]
        idx = order.index(self.current_level) if self.current_level in order else 0
        return order[min(idx + 1, len(order) - 1)]

    def _next_restoration_level(self) -> DegradationLevel:
        order = [
            DegradationLevel.OBSERVE_ONLY,
            DegradationLevel.MINIMAL,
            DegradationLevel.REDUCED,
            DegradationLevel.FULL,
        ]
        idx = order.index(self.current_level) if self.current_level in order else 0
        return order[min(idx + 1, len(order) - 1)]

    def _apply_degradation(self) -> None:
        tier_cutoff = {
            DegradationLevel.FULL: None,
            DegradationLevel.REDUCED: DegradationTier.P3_COSMETIC,
            DegradationLevel.MINIMAL: DegradationTier.P2_NICE_TO_HAVE,
            DegradationLevel.OBSERVE_ONLY: DegradationTier.P1_IMPORTANT,
        }

        cutoff = tier_cutoff.get(self.current_level)
        for name, svc in self.services.items():
            if cutoff is None:
                svc["active"] = True
                svc["current_frequency_hz"] = svc["base_frequency_hz"]
            elif svc["tier"].value >= cutoff.value:
                svc["active"] = True
                if svc["tier"] == DegradationTier.P1_IMPORTANT:
                    svc["current_frequency_hz"] = svc["base_frequency_hz"] * 0.5
                else:
                    svc["current_frequency_hz"] = svc["base_frequency_hz"]
            else:
                svc["active"] = False
                svc["current_frequency_hz"] = 0.0

    def get_service_status(self) -> dict:
        return {
            name: {
                "tier": svc["tier"].value,
                "active": svc["active"],
                "frequency_hz": round(svc["current_frequency_hz"], 2),
            }
            for name, svc in self.services.items()
        }

    def force_degradation(self, target: DegradationLevel) -> None:
        self.current_level = target
        self._apply_degradation()
        self.degradation_history.append(
            {
                "ts": time.time(),
                "level": target.value,
                "reason": "manual_override",
            }
        )
