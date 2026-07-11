# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.safety_gate_l40_l41
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
# [A_module] module_id=MOD-UNK_safety_gate_l40_l41 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L40-L41 — Self-Integrity + Container Immutability

L40: immutable core violation -> BLOCK; operational_window prohibited -> BLOCK
L41: container mutability -> OBSERVE_ONLY alert; image drift -> block deploy
"""

from zephyr.trading.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL40L41:
    def __init__(self):
        self.immutable_core_violation: bool = False
        self.operational_window_prohibited: bool = False
        self.container_mutable: bool = False
        self.image_drift_detected: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l40_self_integrity(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l41_container_immutability(ctx))
        return results

    def _l40_self_integrity(self, ctx: ActionContext) -> GateResult:
        if self.immutable_core_violation:
            return GateResult("L40", GateVerdict.REJECT, GateType.HARD, "Immutable core violated")
        if self.operational_window_prohibited:
            return GateResult("L40", GateVerdict.REJECT, GateType.HARD, "Operation window prohibited")
        return GateResult("L40", GateVerdict.PASS, GateType.HARD)

    def _l41_container_immutability(self, ctx: ActionContext) -> GateResult:
        if self.image_drift_detected:
            return GateResult("L41", GateVerdict.REJECT, GateType.HARD, "Container image drift detected")
        if self.container_mutable:
            return GateResult("L41", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Container mutability alert")
        return GateResult("L41", GateVerdict.PASS, GateType.HARD)
