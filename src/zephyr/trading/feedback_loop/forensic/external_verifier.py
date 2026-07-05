# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.external_verifier
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_external_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""External Verifier — v0.15.0 R203

Blindspot: FLE self-audits; no independent external validator for action correctness.
Risk: R203 — Buggy FLE approves its own bad repair; no third-party verification.

Mitigation: External verifier running in separate process/container that independently re-evaluates FLE decisions.
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
        if verdict == Verdict.DISSENT:
            self.consecutive_dissents += 1
        else:
            self.consecutive_dissents = 0
        return verdict

    @property
    def should_lockdown(self) -> bool:
        return self.consecutive_dissents >= self.dissent_threshold
