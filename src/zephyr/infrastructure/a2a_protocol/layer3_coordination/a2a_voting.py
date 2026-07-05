# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_voting | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 加权投票协议 — 多 Agent 共识达成机制

当多个 Agent 需要集体决策同一问题时，触发加权投票:
  - 每个 Agent 有一票，权重由 AgentRole/A2AVectorReputation 决定
  - quorum (法定人数) 机制防止少部分 Agent 控制决策
  - 支持 approve/reject/abstain 三种投票动作

输出: VotingResult — 计票结果 + 是否通过
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VoteAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


@dataclass
class VotingResult:
    proposal_id: str
    total_weight: float = 0.0
    approve_weight: float = 0.0
    reject_weight: float = 0.0
    abstain_weight: float = 0.0
    quorum_required: float = 0.0
    quorum_met: bool = False
    passed: bool = False
    votes: list[dict] = field(default_factory=list)


class A2AVoting:
    """A2A 加权投票引擎.

    支持 approve/reject/abstain + quorum 检验.
    权重来源: AgentMeta.role + reputation vector.
    """

    def __init__(self, default_quorum: float = 0.5, vote_timeout_seconds: float = 300.0):
        self._default_quorum = default_quorum
        self._vote_timeout = vote_timeout_seconds
        self._boxes: dict[str, dict[str, tuple[VoteAction, float]]] = {}

    def open_proposal(self, proposal_id: str, quorum_ratio: float | None = None):
        self._boxes[proposal_id] = {}
        self._boxes[proposal_id]["_quorum"] = (VoteAction.APPROVE, quorum_ratio or self._default_quorum)

    def cast_vote(
        self,
        proposal_id: str,
        agent_id: str,
        action: VoteAction,
        weight: float = 1.0,
    ) -> bool:
        if proposal_id not in self._boxes:
            return False
        self._boxes[proposal_id][agent_id] = (action, weight)
        return True

    def tally(self, proposal_id: str, participant_count: int) -> VotingResult:
        if proposal_id not in self._boxes:
            return VotingResult(proposal_id=proposal_id)

        box = self._boxes[proposal_id]
        quorum = box.pop("_quorum", (VoteAction.APPROVE, self._default_quorum))[1]

        total = 0.0
        approve = 0.0
        reject = 0.0
        abstain = 0.0
        votes: list[dict] = []

        for agent_id, (action, weight) in box.items():
            total += weight
            votes.append({"agent_id": agent_id, "action": action.value, "weight": weight})
            if action is VoteAction.APPROVE:
                approve += weight
            elif action is VoteAction.REJECT:
                reject += weight
            else:
                abstain += weight

        voter_count = len(box)
        quorum_met = voter_count >= participant_count * quorum
        passed = approve > reject and quorum_met

        return VotingResult(
            proposal_id=proposal_id,
            total_weight=total,
            approve_weight=approve,
            reject_weight=reject,
            abstain_weight=abstain,
            quorum_required=quorum,
            quorum_met=quorum_met,
            passed=passed,
            votes=votes,
        )
