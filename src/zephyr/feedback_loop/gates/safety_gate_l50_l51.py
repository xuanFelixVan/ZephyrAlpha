# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l50_l51
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

"""Safety Gates L50-L55 — Coherence + Integrity Ladder (double-pair pattern)

L50-L51: knowledge coherence, cross-subsystem consistency
L52-L53: run-time integrity, boot-time attestation
L54-L55: end-to-end validation, final integrity gate

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文与门禁状态
#   fields: ctx；门禁态 coherence_score / runtime_integrity / boot_attestation_ok / e2e_validation
#   code: SafetyGateL50L55.evaluate
# 层: 算法
# - id: A1
#   name_zh: L50-L54 五层链式校验
#   name_en: l50_l54_staged_checks
#   intro: 一致性 <0.6 → REJECT；运行时完整性/启动证明/E2E 校验失败 → REJECT（L51 恒 PASS）
#   code: _l50_coherence / _l51_consistency / _l52_runtime / _l53_boot / _l54_e2e
# - id: A2
#   name_zh: L55 完整性终判聚合
#   name_en: l55_final_aggregation
#   intro: L52-L54 任一 REJECT → L55 REJECT（上游完整性链断裂）
#   code: _l55_final
# 层: 输出
# - id: O1
#   name_zh: 门禁裁决列表
#   name_en: gate_results
#   intro: list[GateResult]（六层各一条，PASS / REJECT）
#   downstream: MOD-GATE_ENGINE 门禁编排聚合 → 动作授权决策
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict


class SafetyGateL50L55:
    def __init__(self):
        self.coherence_score: float = 1.0
        self.runtime_integrity: bool = True
        self.boot_attestation_ok: bool = True
        self.e2e_validation: bool = True

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = [
            self._l50_coherence(ctx),
            self._l51_consistency(ctx),
            self._l52_runtime(ctx),
            self._l53_boot(ctx),
            self._l54_e2e(ctx),
        ]
        results.append(self._l55_final(ctx, results))
        return results

    def _l50_coherence(self, ctx: ActionContext) -> GateResult:
        if self.coherence_score < 0.6:
            return GateResult("L50", GateVerdict.REJECT, GateType.HARD, f"Coherence {self.coherence_score:.2f}")
        return GateResult("L50", GateVerdict.PASS, GateType.SOFT)

    def _l51_consistency(self, ctx: ActionContext) -> GateResult:
        return GateResult("L51", GateVerdict.PASS, GateType.SOFT)

    def _l52_runtime(self, ctx: ActionContext) -> GateResult:
        if not self.runtime_integrity:
            return GateResult("L52", GateVerdict.REJECT, GateType.HARD, "Runtime integrity compromised")
        return GateResult("L52", GateVerdict.PASS, GateType.HARD)

    def _l53_boot(self, ctx: ActionContext) -> GateResult:
        if not self.boot_attestation_ok:
            return GateResult("L53", GateVerdict.REJECT, GateType.HARD, "Boot attestation failed")
        return GateResult("L53", GateVerdict.PASS, GateType.HARD)

    def _l54_e2e(self, ctx: ActionContext) -> GateResult:
        if not self.e2e_validation:
            return GateResult("L54", GateVerdict.REJECT, GateType.HARD, "E2E validation failed")
        return GateResult("L54", GateVerdict.PASS, GateType.HARD)

    def _l55_final(self, ctx: ActionContext, prior: list[GateResult]) -> GateResult:
        if any(r.verdict is GateVerdict.REJECT and r.layer in ("L52", "L53", "L54") for r in prior):
            return GateResult("L55", GateVerdict.REJECT, GateType.HARD, "Integrity chain broken upstream")
        return GateResult("L55", GateVerdict.PASS, GateType.HARD)
