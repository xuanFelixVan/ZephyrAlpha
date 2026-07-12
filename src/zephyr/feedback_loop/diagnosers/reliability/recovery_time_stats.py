# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.recovery_time_stats
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
# [A_module] module_id=MOD-UNK_recovery_time_stats | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Recovery Time Statistics — v0.37.0 R454

Blindspot: FLE repairs issues but doesn't track recovery velocity;
silent MTTR degradation means system fragility is invisible.

Risk: R454 — Escalating recovery times undetected; compounding fragility.

Mitigation: Per-component MTTR tracking with EWMA. Detect upward trend in recovery
time (p95). Alert when MTTR doubles from baseline. Feed into Error Budget calc.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RecoveryTimeStats:
    alpha: float = 0.2
    mttr_warning_multiplier: float = 2.0

    per_component: dict[str, dict] = field(default_factory=dict)
    global_ewma_mttr: float = 0.0

    def record_incident(self, component: str, started_at: float, resolved_at: float) -> dict:
        recovery_time = max(0.0, resolved_at - started_at)

        if component not in self.per_component:
            self.per_component[component] = {
                "ewma": recovery_time,
                "count": 0,
                "total": 0.0,
                "max": recovery_time,
                "last": recovery_time,
            }

        stats = self.per_component[component]
        stats["ewma"] = self.alpha * recovery_time + (1 - self.alpha) * stats["ewma"]
        stats["count"] += 1
        stats["total"] += recovery_time
        stats["max"] = max(stats["max"], recovery_time)
        stats["last"] = recovery_time

        self.global_ewma_mttr = self.alpha * recovery_time + (1 - self.alpha) * self.global_ewma_mttr

        baseline = stats["total"] / stats["count"] if stats["count"] > 0 else recovery_time
        is_degraded = stats["ewma"] > baseline * self.mttr_warning_multiplier and stats["count"] > 5

        return {
            "component": component,
            "recovery_time": recovery_time,
            "ewma": stats["ewma"],
            "baseline": baseline,
            "degraded": is_degraded,
        }

    def get_global_mttr(self) -> float:
        return self.global_ewma_mttr
