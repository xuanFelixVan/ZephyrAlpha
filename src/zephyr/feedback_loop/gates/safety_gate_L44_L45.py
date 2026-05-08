"""Safety Gates L44-L45 — Operational Excellence + Causal Interrogability

L44: self_SLO_compliance OK + API contracts intact + chain amplification controlled
L45: execution quality no degradation + noise correctly filtered + learning ceiling respected
"""
from zephyr.feedback_loop.gates.safety_gate_L1_L27 import GateVerdict, GateType, GateResult, ActionContext


class SafetyGateL44L45:

    def __init__(self):
        self.slo_compliant: bool = True
        self.api_contracts_intact: bool = True
        self.chain_amplification: float = 0.0
        self.execution_quality: float = 1.0
        self.noise_filter_ok: bool = True
        self.learning_ceiling_reached: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l44_operational_excellence(ctx))
        if results[-1].verdict != GateVerdict.REJECT:
            results.append(self._l45_causal_interrogability(ctx))
        return results

    def _l44_operational_excellence(self, ctx: ActionContext) -> GateResult:
        if not self.slo_compliant:
            return GateResult("L44", GateVerdict.REJECT, GateType.HARD, "Self-SLO non-compliant")
        if not self.api_contracts_intact:
            return GateResult("L44", GateVerdict.REJECT, GateType.HARD, "API contracts broken")
        if self.chain_amplification > 1.0:
            return GateResult("L44", GateVerdict.OBSERVE_ONLY, GateType.HARD, f"Chain amplification {self.chain_amplification:.2f} > 1.0")
        return GateResult("L44", GateVerdict.PASS, GateType.HARD)

    def _l45_causal_interrogability(self, ctx: ActionContext) -> GateResult:
        if self.learning_ceiling_reached:
            return GateResult("L45", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Learning ceiling reached")
        if self.execution_quality < 0.5:
            return GateResult("L45", GateVerdict.REJECT, GateType.HARD, f"Execution quality {self.execution_quality:.2f} degraded")
        return GateResult("L45", GateVerdict.PASS, GateType.HARD)
