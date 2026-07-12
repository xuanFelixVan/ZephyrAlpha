# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.meta_guard_latency_budget
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_meta_guard_latency_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R516: MetaGuardLatencyBudget
累计Guard开销监控+超限降级 — >poll_interval的X%则降级低价值Guard
"""

import time
from dataclasses import dataclass, field


@dataclass
class MetaGuardLatencyBudget:
    guard_latencies: dict[str, list[float]] = field(default_factory=dict)
    max_samples_per_guard: int = 50
    poll_interval_seconds: float = 60.0
    budget_ratio: float = 0.2
    max_total_latency_ms: float = 5000.0
    downgraded_guards: set[str] = field(default_factory=set)
    priority_ranking: dict[str, float] = field(default_factory=dict)

    def record_latency(self, guard_id: str, latency_ms: float) -> None:
        if guard_id not in self.guard_latencies:
            self.guard_latencies[guard_id] = []
        self.guard_latencies[guard_id].append(latency_ms)
        if len(self.guard_latencies[guard_id]) > self.max_samples_per_guard:
            self.guard_latencies[guard_id] = self.guard_latencies[guard_id][-self.max_samples_per_guard :]

    def set_priority(self, guard_id: str, priority: float) -> None:
        self.priority_ranking[guard_id] = priority

    def check_budget(self) -> dict:
        avg_latencies = {}
        for guard_id, latencies in self.guard_latencies.items():
            if latencies:
                avg_latencies[guard_id] = sum(latencies) / len(latencies)

        total_avg = sum(avg_latencies.values())
        budget_used = total_avg / (self.poll_interval_seconds * 1000.0)

        over_budget = total_avg > self.max_total_latency_ms or budget_used > self.budget_ratio

        if over_budget and not self.downgraded_guards:
            self._downgrade_low_priority_guards(avg_latencies)

        return {
            "over_budget": over_budget,
            "total_avg_latency_ms": round(total_avg, 1),
            "budget_used_ratio": round(budget_used, 3),
            "max_total_latency_ms": self.max_total_latency_ms,
            "guard_count": len(avg_latencies),
            "downgraded_guards": list(self.downgraded_guards),
            "per_guard_avg": {k: round(v, 1) for k, v in avg_latencies.items()},
        }

    def _downgrade_low_priority_guards(self, avg_latencies: dict[str, float]) -> None:
        if not self.priority_ranking:
            return

        sorted_guards = sorted(
            avg_latencies.keys(),
            key=lambda g: self.priority_ranking.get(g, 0.5),
        )

        freed = 0.0
        for guard_id in sorted_guards:
            if guard_id in self.downgraded_guards:
                continue
            self.downgraded_guards.add(guard_id)
            freed += avg_latencies.get(guard_id, 0)
            remaining = sum(v for g, v in avg_latencies.items() if g not in self.downgraded_guards)
            if remaining < self.max_total_latency_ms * 0.8:
                break

        if freed > 0:
            entry = {
                "timestamp": time.time(),
                "freed_ms": round(freed, 1),
                "downgraded_count": len(self.downgraded_guards),
            }

    def is_active(self, guard_id: str) -> bool:
        return guard_id not in self.downgraded_guards

    def restore_all(self) -> None:
        self.downgraded_guards.clear()
