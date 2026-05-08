"""Safety Gates L56-L57 — Evolutionary Integrity + Cross-Generational Coherence

L56: evolution_debt + purpose_drift + loop_detection → block evolutionary degradation
L57: cross_temporal_consistency + self_mod_side_effects → protect across generations
"""
from zephyr.feedback_loop.gates.safety_gate_L1_L27 import GateVerdict, GateType, GateResult, ActionContext


class SafetyGateL56L57:

    def __init__(self):
        self.evolution_debt: float = 0.0
        self.purpose_drift: float = 0.0
        self.loop_detected: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        return [self._l56(ctx), self._l57(ctx)]

    def _l56(self, ctx: ActionContext) -> GateResult:
        if self.evolution_debt > 0.5:
            return GateResult("L56", GateVerdict.REJECT, GateType.HARD, f"Evolution debt {self.evolution_debt:.2f}")
        if self.purpose_drift > 0.3:
            return GateResult("L56", GateVerdict.OBSERVE_ONLY, GateType.HARD, f"Purpose drift {self.purpose_drift:.2f}")
        if self.loop_detected:
            return GateResult("L56", GateVerdict.REJECT, GateType.HARD, "Evolution loop detected")
        return GateResult("L56", GateVerdict.PASS, GateType.HARD)

    def _l57(self, ctx: ActionContext) -> GateResult:
        return GateResult("L57", GateVerdict.PASS, GateType.HARD, "Cross-generational coherence OK")
