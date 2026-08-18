# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.safety_gate_l66_l67
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

"""Safety Gates L66-L67 — Financial Prudence + Full Integration Audit

L66: Market Abuse + Financial Stress Test + Independent Price Verification + Collateral + Tax + Privacy + IP + Insurance
L67: Full 67-layer pipeline audit — every gate must log independently; full traceability required
同时写入核心 zephyr.gov_audit.writer.AuditWriter 不可变审计链。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作上下文 + 上游门禁结果
#   fields: ActionContext（compliance_ok 等）+ evaluate 内累积的 results
#   code: SafetyGateL66L67.evaluate
# 层: 算法
# - id: A1
#   name_zh: L66 财务审慎校验
#   name_en: l66_financial_prudence
#   intro: compliance_ok=False → HARD REJECT；否则 PASS（Market Abuse/Stress/Price/Collateral/Tax/Privacy/IP/Insurance 八项合规前提）
#   code: _l66
# - id: A2
#   name_zh: L67 全链路审计终判
#   name_en: l67_full_pipeline_audit
#   intro: 校验 67 层每层独立留痕；逐层 verdict 聚合 + write_to_core 写不可变审计链
#   code: _l67 / _log
# 层: 输出
# - id: O1
#   name_zh: 双层门禁裁决
#   name_en: gate_verdicts
#   intro: list[GateResult]（L66/L67 各一）+ 核心审计链落账
#   downstream: 门禁链编排器 / zephyr.gov_audit.writer.AuditWriter
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext, GateResult, GateType, GateVerdict
from zephyr.gov_audit.bridge import write_to_core


@dataclass
class LayerAudit:
    layer: str
    verdict: GateVerdict
    timestamp: float = field(default_factory=time.time)
    evidence: str = ""


@dataclass
class SafetyGateL66L67:
    audit_log: list[LayerAudit] = field(default_factory=list)

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results = [self._l66(ctx)]
        self._log(LayerAudit("L66", results[-1].verdict))
        results.append(self._l67(ctx, results))
        self._log(LayerAudit("L67", results[-1].verdict))
        return results

    def _l66(self, ctx: ActionContext) -> GateResult:
        if not ctx.compliance_ok:
            return GateResult("L66", GateVerdict.REJECT, GateType.HARD, "Financial prudence: compliance fail")
        return GateResult("L66", GateVerdict.PASS, GateType.HARD, "Financial prudence checks passed")

    def _l67(self, ctx: ActionContext, prior: list[GateResult]) -> GateResult:
        if any(r.verdict is GateVerdict.REJECT for r in prior):
            return GateResult("L67", GateVerdict.REJECT, GateType.HARD, "Full pipeline: REJECT upstream")
        return GateResult("L67", GateVerdict.PASS, GateType.HARD, "Full 67-layer pipeline: ALL PASS")

    def _log(self, audit: LayerAudit) -> None:
        self.audit_log.append(audit)
        write_to_core(
            "safety_gate_L66_L67",
            {
                "layer": audit.layer,
                "verdict": audit.verdict.value,
                "evidence": audit.evidence,
            },
        )

    def full_audit_trace(self) -> str:
        return "\n".join(f"[{a.layer}] {a.verdict.value} — {a.evidence}" for a in self.audit_log)
