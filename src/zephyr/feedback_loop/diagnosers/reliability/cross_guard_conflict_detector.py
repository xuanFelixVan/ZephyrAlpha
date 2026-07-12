# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.cross_guard_conflict_detector
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
# [A_module] module_id=MOD-UNK_cross_guard_conflict_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R513: CrossGuardConflictDetector
守卫间矛盾建议配对冲突矩阵 — Guard A说act, Guard B说suppress
"""

from dataclasses import dataclass, field


@dataclass
class GuardDecision:
    guard_id: str
    decision: str
    confidence: float


@dataclass
class CrossGuardConflictDetector:
    decision_history: list[list[GuardDecision]] = field(default_factory=list)
    max_history: int = 100
    conflict_threshold: float = 3.0

    OPPOSING_DECISIONS = {
        ("act", "suppress"),
        ("suppress", "act"),
        ("upgrade", "downgrade"),
        ("downgrade", "upgrade"),
        ("enable", "disable"),
        ("disable", "enable"),
        ("alert", "silence"),
        ("silence", "alert"),
    }

    def record_decision_batch(self, decisions: list[GuardDecision]) -> None:
        self.decision_history.append(decisions)
        if len(self.decision_history) > self.max_history:
            self.decision_history = self.decision_history[-self.max_history :]

    def detect_conflicts(self) -> dict:
        if not self.decision_history:
            return {"conflicts": [], "conflict_matrix": {}}

        conflict_pairs = {}
        for batch in self.decision_history[-30:]:
            for i, g1 in enumerate(batch):
                for g2 in batch[i + 1 :]:
                    if (g1.decision, g2.decision) in self.OPPOSING_DECISIONS:
                        pair = tuple(sorted([g1.guard_id, g2.guard_id]))
                        if pair not in conflict_pairs:
                            conflict_pairs[pair] = 0
                        conflict_pairs[pair] += 1

        significant_conflicts = {}
        for (g1, g2), count in conflict_pairs.items():
            if count >= self.conflict_threshold:
                significant_conflicts[f"{g1}-vs-{g2}"] = {
                    "guards": [g1, g2],
                    "conflict_count": count,
                    "severity": "critical" if count >= 10 else "high" if count >= 6 else "medium",
                }

        return {
            "conflicts": list(significant_conflicts.keys()),
            "conflict_matrix": significant_conflicts,
            "total_conflict_pairs": len(conflict_pairs),
        }

    def get_top_conflicts(self, n: int = 5) -> list[dict]:
        all_conflicts = self.detect_conflicts()
        matrix = all_conflicts.get("conflict_matrix", {})
        sorted_conflicts = sorted(matrix.values(), key=lambda x: x["conflict_count"], reverse=True)
        return sorted_conflicts[:n]
