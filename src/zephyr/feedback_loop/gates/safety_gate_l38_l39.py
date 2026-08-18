# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l38_l39
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

"""Safety Gates L38-L39 — Deterministic Safety + Architectural Integrity

L38: HARD_BLOCK violated -> BLOCK; SOFT_BLOCK -> NEED_OVERRIDE
L39: degradation > 5%/month -> BLOCK SELF_UPGRADE; cyclical_deps > 5 -> BLOCK

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx.action_type；门禁态 hard_block_triggered / soft_block_triggered / monthly_degradation_pct / cyclical_deps
#   code: SafetyGateL38L39.evaluate
# 层: 算法
# - id: A1
#   name_zh: L38 确定性安全校验
#   name_en: l38_deterministic_safety
#   intro: HARD_BLOCK 触发 → REJECT；SOFT_BLOCK 触发 → OBSERVE_ONLY 需人工覆盖
#   code: _l38_deterministic_safety
# - id: A2
#   name_zh: L39 架构完整性校验
#   name_en: l39_architectural_integrity
#   intro: 月退化 >5% 阻断 SELF_UPGRADE；循环依赖 >5 → REJECT（A1 未拒才执行）
#   code: _l39_architectural_integrity
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


class SafetyGateL38L39:
    def __init__(self):
        self.hard_block_triggered: bool = False
        self.soft_block_triggered: bool = False
        self.monthly_degradation_pct: float = 0.0
        self.cyclical_deps: int = 0

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l38_deterministic_safety(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l39_architectural_integrity(ctx))
        return results

    def _l38_deterministic_safety(self, ctx: ActionContext) -> GateResult:
        if self.hard_block_triggered:
            return GateResult("L38", GateVerdict.REJECT, GateType.HARD, "HARD_BLOCK violated")
        if self.soft_block_triggered:
            return GateResult("L38", GateVerdict.OBSERVE_ONLY, GateType.HARD, "SOFT_BLOCK: override needed")
        return GateResult("L38", GateVerdict.PASS, GateType.HARD)

    def _l39_architectural_integrity(self, ctx: ActionContext) -> GateResult:
        if self.monthly_degradation_pct > 5.0 and ctx.action_type == "SELF_UPGRADE":
            return GateResult(
                "L39", GateVerdict.REJECT, GateType.HARD, f"Degradation {self.monthly_degradation_pct:.1f}%/month > 5%"
            )
        if self.cyclical_deps > 5:
            return GateResult(
                "L39", GateVerdict.REJECT, GateType.HARD, f"Cyclical dependencies {self.cyclical_deps} > 5"
            )
        return GateResult("L39", GateVerdict.PASS, GateType.HARD)
