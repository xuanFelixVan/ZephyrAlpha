# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.safety_gate_l48_l49
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_safety_gate_l48_l49 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L48-L49 — Supply Chain Integrity + Cognitive Safety

L48: dependency integrity verified + transitive trust chain intact
L49: owner cognitive budget respected + alert flooding suppressed
"""

from zephyr.trading.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL48L49:
    def __init__(self):
        self.dependency_integrity_ok: bool = True
        self.transitive_trust_score: float = 1.0
        self.cognitive_budget_remaining_pct: float = 100.0
        self.alert_flood_detected: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l48_supply_chain_governance(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l49_cognitive_safety(ctx))
        return results

    def _l48_supply_chain_governance(self, ctx: ActionContext) -> GateResult:
        if not self.dependency_integrity_ok:
            return GateResult("L48", GateVerdict.REJECT, GateType.HARD, "Dependency integrity broken")
        if self.transitive_trust_score < 0.5:
            return GateResult(
                "L48", GateVerdict.REJECT, GateType.HARD, f"Transitive trust {self.transitive_trust_score:.2f} < 0.5"
            )
        return GateResult("L48", GateVerdict.PASS, GateType.HARD)

    def _l49_cognitive_safety(self, ctx: ActionContext) -> GateResult:
        if self.alert_flood_detected:
            return GateResult("L49", GateVerdict.REJECT, GateType.HARD, "Alert flood detected — suppressed")
        if self.cognitive_budget_remaining_pct < 10.0:
            return GateResult("L49", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Cognitive budget at capacity")
        return GateResult("L49", GateVerdict.PASS, GateType.HARD)
