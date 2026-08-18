# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l42_l43
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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L42-L43 — Causal Integrity + Survivability

L42: counterfactual_harm_rate + decision_entropy -> severity-dependent action limit
L43: net_negative_value -> only P1; data_expired -> no action; no_checkpoints -> block upgrade

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx.action_type；门禁态 counterfactual_harm_rate / decision_entropy / net_value / data_expired / checkpoints_count
#   code: SafetyGateL42L43.evaluate
# 层: 算法
# - id: A1
#   name_zh: L42 因果完整性校验
#   name_en: l42_causal_integrity
#   intro: 反事实伤害率 >0.2 → REJECT；决策熵 >0.8 → OBSERVE_ONLY
#   code: _l42_causal_integrity
# - id: A2
#   name_zh: L43 可生存性校验
#   name_en: l43_survivability
#   intro: 净值为负仅允许 P1；数据过期禁动作；无检查点阻断 SELF_UPGRADE（A1 未拒才执行）
#   code: _l43_survivability
# 层: 输出
# - id: O1
#   name_zh: 门禁裁决列表
#   name_en: gate_results
#   intro: list[GateResult]（PASS / REJECT / OBSERVE_ONLY，HARD 门）
#   downstream: MOD-GATE_ENGINE 门禁编排聚合 → 动作授权决策
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL42L43:
    def __init__(self):
        self.counterfactual_harm_rate: float = 0.0
        self.decision_entropy: float = 0.0
        self.net_value: float = 0.0
        self.data_expired: bool = False
        self.checkpoints_count: int = 0

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l42_causal_integrity(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l43_survivability(ctx))
        return results

    def _l42_causal_integrity(self, ctx: ActionContext) -> GateResult:
        if self.counterfactual_harm_rate > 0.2:
            return GateResult(
                "L42", GateVerdict.REJECT, GateType.HARD, f"CF harm rate {self.counterfactual_harm_rate:.2f} > 0.2"
            )
        if self.decision_entropy > 0.8:
            return GateResult(
                "L42", GateVerdict.OBSERVE_ONLY, GateType.HARD, f"Decision entropy {self.decision_entropy:.2f} high"
            )
        return GateResult("L42", GateVerdict.PASS, GateType.HARD)

    def _l43_survivability(self, ctx: ActionContext) -> GateResult:
        if self.net_value < 0:
            return GateResult("L43", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Net negative value — only P1 allowed")
        if self.data_expired:
            return GateResult("L43", GateVerdict.REJECT, GateType.HARD, "Data expired — no action")
        if self.checkpoints_count == 0 and ctx.action_type == "SELF_UPGRADE":
            return GateResult("L43", GateVerdict.REJECT, GateType.HARD, "No checkpoints — upgrade blocked")
        return GateResult("L43", GateVerdict.PASS, GateType.HARD)
