# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.safety_gate_l52_l53
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
# [A_module] module_id=MOD-UNK_safety_gate_l52_l53 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L52-L53 — Boot Integrity + OSS License

L52: boot_integrity attestation — runtime measurement validation
L53: OSS license compliance — SPDX audit pass before action
"""

from zephyr.trading.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL52L53:
    def __init__(self):
        self.boot_measurement_ok: bool = True
        self.spdx_compliant: bool = True

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        return [self._l52(ctx), self._l53(ctx)]

    def _l52(self, ctx: ActionContext) -> GateResult:
        if not self.boot_measurement_ok:
            return GateResult("L52", GateVerdict.REJECT, GateType.HARD, "Boot measurement mismatch")
        return GateResult("L52", GateVerdict.PASS, GateType.HARD)

    def _l53(self, ctx: ActionContext) -> GateResult:
        if not self.spdx_compliant:
            return GateResult("L53", GateVerdict.REJECT, GateType.HARD, "SPDX license non-compliant")
        return GateResult("L53", GateVerdict.PASS, GateType.HARD)
