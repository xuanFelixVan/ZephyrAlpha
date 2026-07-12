# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l38_l39
# [DOMAIN] D_FBL_VERIFICATION [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_safety_gate_l38_l39 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L38-L39 — Deterministic Safety + Architectural Integrity

L38: HARD_BLOCK violated -> BLOCK; SOFT_BLOCK -> NEED_OVERRIDE
L39: degradation > 5%/month -> BLOCK SELF_UPGRADE; cyclical_deps > 5 -> BLOCK
"""

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL38L39:
    def __init__(self):
        self.hard_block_triggered: bool = False
        self.soft_block_triggered: bool = False
        self.monthly_degradation_pct: float = 0.0
        self.cyclical_deps: int = 0

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l38_deterministic_safety(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l39_architectural_integrity(ctx))
        return results

    def _l38_deterministic_safety(self, ctx: ActionContext) -> GateResult:
        if self.hard_block_triggered:
            return GateResult("L38", GateVerdict.REJECT, GateType.HARD, "HARD_BLOCK violated")
        if self.soft_block_triggered:
            return GateResult("L38", GateVerdict.OBSERVE_ONLY, GateType.HARD, "SOFT_BLOCK: override needed")
        return GateResult("L38", GateVerdict.PASS, GateType.HARD)

    def _l39_architectural_integrity(self, ctx: ActionContext) -> GateResult:
        if self.monthly_degradation_pct > 5.0 and ctx.action_type == "SELF_UPGRADE":
            return GateResult(
                "L39", GateVerdict.REJECT, GateType.HARD, f"Degradation {self.monthly_degradation_pct:.1f}%/month > 5%"
            )
        if self.cyclical_deps > 5:
            return GateResult(
                "L39", GateVerdict.REJECT, GateType.HARD, f"Cyclical dependencies {self.cyclical_deps} > 5"
            )
        return GateResult("L39", GateVerdict.PASS, GateType.HARD)
