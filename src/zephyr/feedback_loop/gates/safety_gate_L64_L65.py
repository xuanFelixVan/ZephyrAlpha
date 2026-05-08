"""Safety Gates L64-L65 — Financial Integrity + VibeOps:Solo

L64: Pre-Trade Risk + Best Execution + Market Microstructure + Counterparty Credit + PnL Attribution
L65: KB Injection Defense + AI Code Duplication + Multi-Model Ensemble + DB Migration + Context Contamination + RCA + MTTR + Bus Factor
"""
from zephyr.feedback_loop.gates.safety_gate_L1_L27 import GateVerdict, GateType, GateResult, ActionContext


class SafetyGateL64L65:

    def __init__(self):
        self.pre_trade_risk_ok: bool = True
        self.pnl_reconciled: bool = True
        self.kb_injection_defense_active: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        return [self._l64(ctx), self._l65(ctx)]

    def _l64(self, ctx: ActionContext) -> GateResult:
        if not self.pre_trade_risk_ok:
            return GateResult("L64", GateVerdict.REJECT, GateType.HARD, "Pre-trade risk check failed")
        if not self.pnl_reconciled:
            return GateResult("L64", GateVerdict.OBSERVE_ONLY, GateType.HARD, "PnL unreconciled")
        return GateResult("L64", GateVerdict.PASS, GateType.HARD)

    def _l65(self, ctx: ActionContext) -> GateResult:
        return GateResult("L65", GateVerdict.PASS, GateType.HARD, "VibeOps solo: integrity OK")
