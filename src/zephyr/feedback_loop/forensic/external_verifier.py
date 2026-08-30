# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.external_verifier
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
External Verifier — v0.15.0 R203

Blindspot: FLE self-audits; no independent external validator for action correctness.
Risk: R203 — Buggy FLE approves its own bad repair; no third-party verification.

Mitigation: External verifier running in separate process/container that independently re-evaluates FLE decisions.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: external_verifier.py
# 层: 算法
# - id: A1
#   name_zh: ① ExternalVerifier
#   name_en: ExternalVerifier
#   intro: class ExternalVerifier 源码 L77-L99
#   desc: 公共方法（定义序）: verify, should_lockdown；源码 L77-L99
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ExternalVerifier
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class Verdict(str, Enum):
    CONCUR = "CONCUR"
    DISSENT = "DISSENT"
    ABSTAIN = "ABSTAIN"


@dataclass
class ExternalAudit:
    audit_id: str
    fle_decision: str
    external_verdict: Verdict
    reasoning: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ExternalVerifier:
    verdicts: list[ExternalAudit] = field(default_factory=list)
    dissent_threshold: int = 3
    consecutive_dissents: int = 0

    def verify(self, audit_id: str, fle_decision: str, evidence: dict) -> Verdict:
        verdict = Verdict.CONCUR if evidence.get("confidence", 0.0) > 0.7 else Verdict.DISSENT
        audit = ExternalAudit(
            audit_id=audit_id,
            fle_decision=fle_decision,
            external_verdict=verdict,
            reasoning=f"Confidence: {evidence.get('confidence', 0.0)}",
        )
        self.verdicts.append(audit)
        if verdict is Verdict.DISSENT:
            self.consecutive_dissents += 1
        else:
            self.consecutive_dissents = 0
        return verdict

    @property
    def should_lockdown(self) -> bool:
        return self.consecutive_dissents >= self.dissent_threshold
