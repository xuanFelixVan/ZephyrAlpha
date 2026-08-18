# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l44_l45
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

"""Safety Gates L44-L45 — Operational Excellence + Causal Interrogability

L44: self_SLO_compliance OK + API contracts intact + chain amplification controlled
L45: execution quality no degradation + noise correctly filtered + learning ceiling respected

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 slo_compliant / api_contracts_intact / chain_amplification / execution_quality / learning_ceiling_reached
#   code: SafetyGateL44L45.evaluate
# 层: 算法
# - id: A1
#   name_zh: L44 运营卓越校验
#   name_en: l44_operational_excellence
#   intro: 自 SLO 违约或 API 契约破坏 → REJECT；链式放大 >1.0 → OBSERVE_ONLY
#   code: _l44_operational_excellence
# - id: A2
#   name_zh: L45 因果可质询性校验
#   name_en: l45_causal_interrogability
#   intro: 学习触顶 → OBSERVE_ONLY；执行质量 <0.5 → REJECT（A1 未拒才执行）
#   code: _l45_causal_interrogability
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
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l45_causal_interrogability(ctx))
        return results

    def _l44_operational_excellence(self, ctx: ActionContext) -> GateResult:
        if not self.slo_compliant:
            return GateResult("L44", GateVerdict.REJECT, GateType.HARD, "Self-SLO non-compliant")
        if not self.api_contracts_intact:
            return GateResult("L44", GateVerdict.REJECT, GateType.HARD, "API contracts broken")
        if self.chain_amplification > 1.0:
            return GateResult(
                "L44",
                GateVerdict.OBSERVE_ONLY,
                GateType.HARD,
                f"Chain amplification {self.chain_amplification:.2f} > 1.0",
            )
        return GateResult("L44", GateVerdict.PASS, GateType.HARD)

    def _l45_causal_interrogability(self, ctx: ActionContext) -> GateResult:
        if self.learning_ceiling_reached:
            return GateResult("L45", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Learning ceiling reached")
        if self.execution_quality < 0.5:
            return GateResult(
                "L45", GateVerdict.REJECT, GateType.HARD, f"Execution quality {self.execution_quality:.2f} degraded"
            )
        return GateResult("L45", GateVerdict.PASS, GateType.HARD)
