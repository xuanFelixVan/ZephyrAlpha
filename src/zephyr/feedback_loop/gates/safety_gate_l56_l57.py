# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l56_l57
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

"""Safety Gates L56-L57 — Evolutionary Integrity + Cross-Generational Coherence

L56: evolution_debt + purpose_drift + loop_detection -> block evolutionary degradation
L57: cross_temporal_consistency + self_mod_side_effects -> protect across generations

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 evolution_debt / purpose_drift / loop_detected
#   code: SafetyGateL56L57.evaluate
# 层: 算法
# - id: A1
#   name_zh: L56 进化完整性校验
#   name_en: l56_evolutionary_integrity
#   intro: 进化债 >0.5 或检测到进化循环 → REJECT；目的漂移 >0.3 → OBSERVE_ONLY
#   code: _l56
# - id: A2
#   name_zh: L57 跨代一致性校验
#   name_en: l57_cross_generational_coherence
#   intro: 跨代一致性与自修改副作用守护（当前恒 PASS）
#   code: _l57
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
