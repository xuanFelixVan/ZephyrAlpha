# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.safety_gate_l36_l37
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
# [A_module] module_id=MOD-UNK_safety_gate_l36_l37 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L36-L37 — AI Code Integrity + Vibe Maintainability

L36: context_rot > 35% + dilution > 0.3 → context refresh before action
L37: worsening > 0.4 → only NOTIFY_OWNER; trust_decay > baseline*1.5 → force L0
"""

from zephyr.trading.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL36L37:
    def __init__(self):
        self.context_rot: float = 0.0
        self.dilution: float = 0.0
        self.worsening: float = 0.0
        self.trust_decay: float = 0.0
        self.baseline_decay: float = 0.05

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l36_ai_code_integrity(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l37_vibe_maintainability(ctx))
        return results

    def _l36_ai_code_integrity(self, ctx: ActionContext) -> GateResult:
        if self.context_rot > 0.35 and self.dilution > 0.3:
            return GateResult("L36", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Context refresh required")
        return GateResult("L36", GateVerdict.PASS, GateType.HARD)

    def _l37_vibe_maintainability(self, ctx: ActionContext) -> GateResult:
        if self.worsening > 0.4:
            return GateResult(
                "L37", GateVerdict.OBSERVE_ONLY, GateType.HARD, f"Vibe worsening {self.worsening:.2f} > 0.4"
            )
        if self.trust_decay > self.baseline_decay * 1.5:
            return GateResult(
                "L37", GateVerdict.REJECT, GateType.HARD, f"Trust decay {self.trust_decay:.3f} — force L0"
            )
        return GateResult("L37", GateVerdict.PASS, GateType.HARD)
