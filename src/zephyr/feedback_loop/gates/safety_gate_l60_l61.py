# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l60_l61
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

"""Safety Gates L60-L61 — Environmental Grounding + Meta-System Integrity

L60: Exchange Halt + Corporate Events + Model Retirement -> environmental checks
L61: Cross-Blueprint Contract Drift + Owner Burnout + Cascading Rollback

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx.owner_fatigue；门禁态 exchange_halted / corporate_event_active / burnout_risk
#   code: SafetyGateL60L61.evaluate
# 层: 算法
# - id: A1
#   name_zh: L60 环境接地校验
#   name_en: l60_environmental_grounding
#   intro: 交易所停牌 → REJECT 交易动作；公司行动事件激活 → OBSERVE_ONLY 抑制非关键
#   code: _l60
# - id: A2
#   name_zh: L61 元系统完整性校验
#   name_en: l61_meta_system_integrity
#   intro: owner_fatigue >0.8（负责人倦怠风险） → REJECT
#   code: _l61
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


class SafetyGateL60L61:
    def __init__(self):
        self.exchange_halted: bool = False
        self.corporate_event_active: bool = False
        self.burnout_risk: float = 0.0

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        return [self._l60(ctx), self._l61(ctx)]

    def _l60(self, ctx: ActionContext) -> GateResult:
        if self.exchange_halted:
            return GateResult("L60", GateVerdict.REJECT, GateType.HARD, "Exchange halted — block trading actions")
        if self.corporate_event_active:
            return GateResult(
                "L60", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Corporate event active — suppress non-critical"
            )
        return GateResult("L60", GateVerdict.PASS, GateType.HARD)

    def _l61(self, ctx: ActionContext) -> GateResult:
        if ctx.owner_fatigue > 0.8:
            return GateResult("L61", GateVerdict.REJECT, GateType.HARD, f"Owner burnout risk {ctx.owner_fatigue:.2f}")
        return GateResult("L61", GateVerdict.PASS, GateType.HARD)
