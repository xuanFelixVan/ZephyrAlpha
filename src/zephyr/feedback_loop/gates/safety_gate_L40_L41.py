"""Safety Gates L40-L41 — Self-Integrity + Container Immutability

L40: immutable core violation → BLOCK; operational_window prohibited → BLOCK
L41: container mutability → OBSERVE_ONLY alert; image drift → block deploy
"""
from zephyr.feedback_loop.gates.safety_gate_L1_L27 import GateVerdict, GateType, GateResult, ActionContext


class SafetyGateL40L41:

    def __init__(self):
        self.immutable_core_violation: bool = False
        self.operational_window_prohibited: bool = False
        self.container_mutable: bool = False
        self.image_drift_detected: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l40_self_integrity(ctx))
        if results[-1].verdict != GateVerdict.REJECT:
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
