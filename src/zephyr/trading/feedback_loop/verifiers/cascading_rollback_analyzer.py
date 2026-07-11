# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.cascading_rollback_analyzer
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_cascading_rollback_analyzer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Cascading Rollback Analyzer — v0.38.0 R482

Blindspot: When FLE rolls back an automated repair, it only reverts the target
change. But that change may have triggered dependent changes in other subsystems
— rolling back A leaves B, C, D in inconsistent states.

Risk: R482 — Partial rollback creates worse state than the original failure.
"Fixed" system is actually more broken because rollback was incomplete.

Mitigation: Build action dependency graph. Before executing any rollback,
compute the blast radius: what other actions/state changes depend on this
one? Generate complete rollback plan covering all dependents. Verify
post-rollback consistency.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class RollbackSafety(str, Enum):
    SAFE = "SAFE"
    CASCADE_REQUIRED = "CASCADE_REQUIRED"
    UNSAFE = "UNSAFE"


@dataclass
class CascadingRollbackAnalyzer:
    max_cascade_depth: int = 5
    min_dependency_confidence: float = 0.5

    action_dependencies: dict[str, list[str]] = field(default_factory=dict)
    action_timestamps: dict[str, float] = field(default_factory=dict)
    rollback_history: list[dict] = field(default_factory=list)

    def record_action_dependency(self, action_id: str, depends_on: list[str]) -> None:
        self.action_dependencies[action_id] = depends_on
        self.action_timestamps[action_id] = time.time()

    def analyze_rollback(self, action_id: str) -> dict:
        if action_id not in self.action_dependencies:
            return {"safety": RollbackSafety.SAFE.value, "cascade": [], "depth": 0}

        cascade = []
        visited: set[str] = set()
        queue = [action_id]

        while queue and len(cascade) < self.max_cascade_depth:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            dependents = [aid for aid, deps in self.action_dependencies.items() if current in deps and aid != action_id]
            for dep in dependents:
                if dep not in visited:
                    cascade.append(dep)
                    queue.append(dep)

        safety = (
            RollbackSafety.UNSAFE
            if len(cascade) > self.max_cascade_depth
            else RollbackSafety.CASCADE_REQUIRED
            if cascade
            else RollbackSafety.SAFE
        )

        rollback_plan = {
            "action_id": action_id,
            "safety": safety.value,
            "cascade_targets": cascade,
            "depth": len(cascade),
            "requires_sequential_rollback": len(cascade) > 0,
            "estimated_actions": 1 + len(cascade),
        }

        self.rollback_history.append({**rollback_plan, "ts": time.time()})
        return rollback_plan

    def build_dependency_graph(self) -> dict:
        graph = {"nodes": list(self.action_dependencies.keys()), "edges": []}
        for aid, deps in self.action_dependencies.items():
            for dep in deps:
                graph["edges"].append({"from": aid, "to": dep, "type": "depends_on"})
        return graph

    def get_most_depended_upon(self, top_n: int = 5) -> list[dict]:
        dependency_counts: dict[str, int] = {}
        for deps in self.action_dependencies.values():
            for dep in deps:
                dependency_counts[dep] = dependency_counts.get(dep, 0) + 1

        ranked = sorted(dependency_counts.items(), key=lambda x: -x[1])[:top_n]
        return [
            {"action_id": aid, "dependent_count": count, "risk": "HIGH" if count > 3 else "MEDIUM"}
            for aid, count in ranked
        ]

    def verify_post_rollback_consistency(self, action_id: str) -> dict:
        cascade = self.analyze_rollback(action_id)
        all_targets = [action_id] + cascade.get("cascade_targets", [])

        orphaned = [
            aid
            for aid, deps in self.action_dependencies.items()
            if any(dep in all_targets for dep in deps) and aid not in all_targets
        ]

        return {
            "consistent": len(orphaned) == 0,
            "orphaned_dependents": orphaned,
            "total_rolled_back": len(all_targets),
            "recommendation": "execute_full_cascade" if orphaned else "safe_to_rollback",
        }
