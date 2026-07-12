# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l28_l29
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
# [A_module] module_id=MOD-UNK_safety_gate_l28_l29 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L28-L29 — DR Readiness + Supply Chain (MOD-FEEDBACK_LOOP §3 L28-L41)

L28: DR Readiness — DR drill < 90d -> allow REPAIR, overdue -> block
L29: Supply Chain — active CVE -> only NOTIFY_OWNER; skill_trust < 0.5 -> block all
"""

from __future__ import annotations

import time

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL28L29:
    def __init__(self):
        self.last_drill: float = 0.0
        self.cve_active: list[str] = []
        self.skill_trust: float = 1.0

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l28_dr_readiness(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l29_supply_chain(ctx))
        return results

    def _l28_dr_readiness(self, ctx: ActionContext) -> GateResult:
        days_since = (time.time() - self.last_drill) / 86400.0 if self.last_drill > 0 else 999
        if days_since > 90 and ctx.action_type in ("REPAIR", "DEPLOY"):
            return GateResult(
                "L28", GateVerdict.REJECT, GateType.HARD, f"DR drill {days_since:.0f}d overdue > 90d limit"
            )
        return GateResult("L28", GateVerdict.PASS, GateType.HARD)

    def _l29_supply_chain(self, ctx: ActionContext) -> GateResult:
        if self.cve_active:
            return GateResult(
                "L29", GateVerdict.OBSERVE_ONLY, GateType.HARD, f"Active CVE: {', '.join(self.cve_active)}"
            )
        if self.skill_trust < 0.5:
            return GateResult("L29", GateVerdict.REJECT, GateType.HARD, f"Skill trust {self.skill_trust:.2f} < 0.5")
        return GateResult("L29", GateVerdict.PASS, GateType.HARD)
