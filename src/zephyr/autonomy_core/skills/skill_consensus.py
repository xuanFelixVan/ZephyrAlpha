# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_consensus
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Consensus
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 共识 —— Multi-Agent 投票/协商/冲突裁决.
当多个 Agent 对同一 Skill 输出产生分歧时提供收敛机制.
支持: majority_vote / weighted_vote / tiebreaker_by_freshness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class VoteResult:
    winner: str
    vote_counts: dict[str, int]
    total_voters: int
    tie_broken: bool = False
    tiebreaker_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "winner": self.winner,
            "vote_counts": self.vote_counts,
            "total_voters": self.total_voters,
            "tie_broken": self.tie_broken,
            "tiebreaker_reason": self.tiebreaker_reason,
        }


class SkillConsensus:
    """Skill 共识 —— Multi-Agent 分歧收敛."""

    @staticmethod
    def reach_consensus(skill_ids: list[str], votes: dict[str, int]) -> dict[str, Any]:
        unique = set(votes.values())
        return {
            "participants": skill_ids,
            "votes": votes,
            "consensus_reached": len(unique) == 1,
            "unique_opinions": len(unique),
        }

    @staticmethod
    def majority_vote(
        options: list[str],
        votes: dict[str, str],
        weights: dict[str, float] | None = None,
    ) -> tuple[str | None, VoteResult]:
        tally: dict[str, float] = {}
        for voter, choice in votes.items():
            if choice not in options:
                continue
            w = (weights or {}).get(voter, 1.0)
            tally[choice] = tally.get(choice, 0.0) + w

        if not tally:
            return None, VoteResult(winner="", vote_counts={}, total_voters=len(votes))

        max_votes = max(tally.values())
        winners = [k for k, v in tally.items() if v == max_votes]

        if len(winners) == 1:
            return winners[0], VoteResult(
                winner=winners[0],
                vote_counts={k: int(v) for k, v in tally.items()},
                total_voters=len(votes),
            )

        result = SkillConsensus._tiebreak(winners, tally)
        return result.winner, result

    @staticmethod
    def weighted_consensus(
        agents: list[dict[str, Any]],
        question: str,
    ) -> dict[str, Any]:
        agent_ids = [a.get("agent_id", f"agent_{i}") for i, a in enumerate(agents)]
        agent_votes = {}
        agent_weights = {}
        for i, a in enumerate(agents):
            aid = a.get("agent_id", f"agent_{i}")
            agent_votes[aid] = a.get("vote", "abstain")
            agent_weights[aid] = a.get("weight", 1.0)

        winner, result = SkillConsensus.majority_vote(
            options=list(set(agent_votes.values())),
            votes=agent_votes,
            weights=agent_weights,
        )

        return {
            "question": question,
            "agents": agent_ids,
            "winner": winner,
            "vote_detail": result.to_dict(),
            "consensus_reached": result.winner != "",
        }

    @staticmethod
    def _tiebreak(winners: list[str], tally: dict[str, float]) -> VoteResult:
        from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel

        fdm = FreshnessDecayModel()
        best_skill = winners[0]
        best_score = -1.0
        for w in winners:
            state = fdm.current_state(w.split(":")[0])
            score = float(state.get("freshness_score", 0))
            if score > best_score:
                best_score = score
                best_skill = w

        return VoteResult(
            winner=best_skill,
            vote_counts={k: int(v) for k, v in tally.items()},
            total_voters=sum(int(v) for v in tally.values()),
            tie_broken=True,
            tiebreaker_reason=f"Freshness-tiebreak: '{best_skill}' score={best_score:.1f}",
        )


__all__ = ["SkillConsensus", "VoteResult"]
