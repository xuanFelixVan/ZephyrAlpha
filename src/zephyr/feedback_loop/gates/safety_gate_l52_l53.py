# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l52_l53
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

"""Safety Gates L52-L53 — Boot Integrity + OSS License

L52: boot_integrity attestation — runtime measurement validation
L53: OSS license compliance — SPDX audit pass before action

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 boot_measurement_ok / spdx_compliant
#   code: SafetyGateL52L53.evaluate
# 层: 算法
# - id: A1
#   name_zh: L52 启动完整性证明校验
#   name_en: l52_boot_integrity
#   intro: boot 运行时度量与基线不匹配 → REJECT
#   code: _l52
# - id: A2
#   name_zh: L53 OSS 许可证合规校验
#   name_en: l53_oss_license_compliance
#   intro: SPDX 许可证审计不合规 → REJECT
#   code: _l53
# 层: 输出
# - id: O1
#   name_zh: 门禁裁决列表
#   name_en: gate_results
#   intro: list[GateResult]（PASS / REJECT，HARD 门）
#   downstream: MOD-GATE_ENGINE 门禁编排聚合 → 动作授权决策
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


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
