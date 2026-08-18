# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l48_l49
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

"""Safety Gates L48-L49 — Supply Chain Integrity + Cognitive Safety

L48: dependency integrity verified + transitive trust chain intact
L49: owner cognitive budget respected + alert flooding suppressed

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 dependency_integrity_ok / transitive_trust_score / cognitive_budget_remaining_pct / alert_flood_detected
#   code: SafetyGateL48L49.evaluate
# 层: 算法
# - id: A1
#   name_zh: L48 供应链治理校验
#   name_en: l48_supply_chain_governance
#   intro: 依赖完整性破坏或传递信任分 <0.5 → REJECT
#   code: _l48_supply_chain_governance
# - id: A2
#   name_zh: L49 认知安全校验
#   name_en: l49_cognitive_safety
#   intro: 告警洪水 → REJECT 抑制；负责人认知预算 <10% → OBSERVE_ONLY（A1 未拒才执行）
#   code: _l49_cognitive_safety
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


class SafetyGateL48L49:
    def __init__(self):
        self.dependency_integrity_ok: bool = True
        self.transitive_trust_score: float = 1.0
        self.cognitive_budget_remaining_pct: float = 100.0
        self.alert_flood_detected: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l48_supply_chain_governance(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l49_cognitive_safety(ctx))
        return results

    def _l48_supply_chain_governance(self, ctx: ActionContext) -> GateResult:
        if not self.dependency_integrity_ok:
            return GateResult("L48", GateVerdict.REJECT, GateType.HARD, "Dependency integrity broken")
        if self.transitive_trust_score < 0.5:
            return GateResult(
                "L48", GateVerdict.REJECT, GateType.HARD, f"Transitive trust {self.transitive_trust_score:.2f} < 0.5"
            )
        return GateResult("L48", GateVerdict.PASS, GateType.HARD)

    def _l49_cognitive_safety(self, ctx: ActionContext) -> GateResult:
        if self.alert_flood_detected:
            return GateResult("L49", GateVerdict.REJECT, GateType.HARD, "Alert flood detected — suppressed")
        if self.cognitive_budget_remaining_pct < 10.0:
            return GateResult("L49", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Cognitive budget at capacity")
        return GateResult("L49", GateVerdict.PASS, GateType.HARD)
