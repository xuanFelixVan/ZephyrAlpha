# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.feedback_loop.gates.safety_gate_L62_L63

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Safety Gates L62-L63 — Infrastructure Reality + Market Reality

L62: Strategy Isolation + Network Partition + Immutable Infra + LLM Cost + Kernel Anomaly
L63: Cross-Venue Arbitrage + E2E Health + Self-API Throttle + Schema Registry + Intraday Season + News Sentiment
"""
from zephyr.feedback_loop.gates.safety_gate_L1_L27 import GateVerdict, GateType, GateResult, ActionContext


class SafetyGateL62L63:

    def __init__(self):
        self.network_partition: bool = False
        self.immutable_infra_ok: bool = True
        self.self_api_throttled: bool = False
        self.intraday_anomaly: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        return [self._l62(ctx), self._l63(ctx)]

    def _l62(self, ctx: ActionContext) -> GateResult:
        if self.network_partition:
            return GateResult("L62", GateVerdict.REJECT, GateType.HARD, "Network partition detected")
        if not self.immutable_infra_ok:
            return GateResult("L62", GateVerdict.REJECT, GateType.HARD, "Immutable infrastructure violated")
        return GateResult("L62", GateVerdict.PASS, GateType.HARD)

    def _l63(self, ctx: ActionContext) -> GateResult:
        if self.self_api_throttled:
            return GateResult("L63", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Self-API throttling active")
        return GateResult("L63", GateVerdict.PASS, GateType.HARD)
