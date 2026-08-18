# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l40_l41
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

"""Safety Gates L40-L41 — Self-Integrity + Container Immutability

L40: immutable core violation -> BLOCK; operational_window prohibited -> BLOCK
L41: container mutability -> OBSERVE_ONLY alert; image drift -> block deploy

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 immutable_core_violation / operational_window_prohibited / container_mutable / image_drift_detected
#   code: SafetyGateL40L41.evaluate
# 层: 算法
# - id: A1
#   name_zh: L40 自身完整性校验
#   name_en: l40_self_integrity
#   intro: 不可变核心被篡改或处于禁用操作窗口 → REJECT
#   code: _l40_self_integrity
# - id: A2
#   name_zh: L41 容器不可变性校验
#   name_en: l41_container_immutability
#   intro: 镜像漂移 → REJECT 阻断部署；容器可变 → OBSERVE_ONLY 告警（A1 未拒才执行）
#   code: _l41_container_immutability
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


class SafetyGateL40L41:
    def __init__(self):
        self.immutable_core_violation: bool = False
        self.operational_window_prohibited: bool = False
        self.container_mutable: bool = False
        self.image_drift_detected: bool = False

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        results.append(self._l40_self_integrity(ctx))
        if results[-1].verdict is not GateVerdict.REJECT:
            results.append(self._l41_container_immutability(ctx))
        return results

    def _l40_self_integrity(self, ctx: ActionContext) -> GateResult:
        if self.immutable_core_violation:
            return GateResult("L40", GateVerdict.REJECT, GateType.HARD, "Immutable core violated")
        if self.operational_window_prohibited:
            return GateResult("L40", GateVerdict.REJECT, GateType.HARD, "Operation window prohibited")
        return GateResult("L40", GateVerdict.PASS, GateType.HARD)

    def _l41_container_immutability(self, ctx: ActionContext) -> GateResult:
        if self.image_drift_detected:
            return GateResult("L41", GateVerdict.REJECT, GateType.HARD, "Container image drift detected")
        if self.container_mutable:
            return GateResult("L41", GateVerdict.OBSERVE_ONLY, GateType.HARD, "Container mutability alert")
        return GateResult("L41", GateVerdict.PASS, GateType.HARD)
