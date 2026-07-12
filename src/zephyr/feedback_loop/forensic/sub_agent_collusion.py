# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.sub_agent_collusion
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_sub_agent_collusion | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Sub-Agent Collusion Detector — v0.15.0 R213

Blindspot: Multiple FLE sub-agents collude to approve each other's bad repairs.
Risk: R213 — Agent A approves Agent B's repair; Agent B reciprocates; both bad.

Mitigation: Cross-agent vote pattern analysis to detect reciprocal approval rings.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VotePair:
    from_agent: str
    to_agent: str
    action_id: str
    vote: str


@dataclass
class SubAgentCollusion:
    votes: list[VotePair] = field(default_factory=list)
    collusion_threshold: int = 3

    def record(self, from_agent: str, to_agent: str, action_id: str, vote: str) -> None:
        self.votes.append(VotePair(from_agent=from_agent, to_agent=to_agent, action_id=action_id, vote=vote))

    def detect_ring(self) -> list[str]:
        approval_counts: dict[str, int] = {}
        for v in self.votes:
            if v.vote == "APPROVE":
                pair = f"{v.from_agent}->{v.to_agent}"
                approval_counts[pair] = approval_counts.get(pair, 0) + 1
        return [pair for pair, count in approval_counts.items() if count >= self.collusion_threshold]
