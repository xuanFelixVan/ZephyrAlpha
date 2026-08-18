# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l36_l37
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

"""Safety Gates L36-L37 — AI Code Integrity + Vibe Maintainability

L36: context_rot > 35% + dilution > 0.3 -> context refresh before action
L37: worsening > 0.4 -> only NOTIFY_OWNER; trust_decay > baseline*1.5 -> force L0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 context_rot / dilution / worsening / trust_decay / baseline_decay
#   code: SafetyGateL36L37.evaluate
# 层: 算法
# - id: A1
#   name_zh: L36 AI 代码完整性校验
#   name_en: l36_ai_code_integrity
#   intro: context_rot>35% 且 dilution>0.3 → OBSERVE_ONLY，要求动作前刷新上下文
#   code: _l36_ai_code_integrity
# - id: A2
#   name_zh: L37 氛围可维护性校验
#   name_en: l37_vibe_maintainability
#   intro: worsening>0.4 → OBSERVE_ONLY；trust_decay>baseline*1.5 → REJECT 强制 L0（A1 未拒才执行）
#   code: _l37_vibe_maintainability
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


class SafetyGateL36L37:
    def __init__(self):
        self.context_rot: float = 0.0
        self.dilution: float = 0.0
        self.worsening: float = 0.0
        self.trust_decay: float = 0.0
        self.baseline_decay: float = 0.05

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l36_ai_code_integrity(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l37_vibe_maintainability(ctx))
        return results

    def _l36_ai_code_integrity(self, ctx: ActionContext) -> GateResult:
        if self.context_rot > 0.35 and self.dilution > 0.3:
            return GateResult("L36", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Context refresh required")
        return GateResult("L36", GateVerdict.PASS, GateType.HARD)

    def _l37_vibe_maintainability(self, ctx: ActionContext) -> GateResult:
        if self.worsening > 0.4:
            return GateResult(
                "L37", GateVerdict.OBSERVE_ONLY, GateType.HARD, f"Vibe worsening {self.worsening:.2f} > 0.4"
            )
        if self.trust_decay > self.baseline_decay * 1.5:
            return GateResult(
                "L37", GateVerdict.REJECT, GateType.HARD, f"Trust decay {self.trust_decay:.3f} — force L0"
            )
        return GateResult("L37", GateVerdict.PASS, GateType.HARD)
