# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_debate
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
# [A_module] module_id=MOD-INF_a2a_debate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 结构化辩论协议 — 多轮主张->反驳->合成

当两个 Agent 对同一决策持不同意见时，触发结构化辩论:
  Round 1: Agent A 主张 + Agent B 主张
  Round 2: Agent A 反驳B + Agent B 反驳A
  Round 3: Agent A 综合 + Agent B 综合 -> Synthesis(共识输出)

输出: DebateResult — winner/consensus/synthesis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DebatePhase(str, Enum):
    CLAIM = "claim"
    REBUTTAL = "rebuttal"
    SYNTHESIS = "synthesis"


@dataclass
class DebateRound:
    phase: DebatePhase
    agent_a_statement: str
    agent_b_statement: str
    round_number: int


@dataclass
class DebateResult:
    agent_a_id: str
    agent_b_id: str
    topic: str
    rounds: list[DebateRound] = field(default_factory=list)
    winner: str | None = None
    consensus: str = ""
    synthesis: str = ""


class A2ADebate:
    """A2A 结构化辩论协议.

    三轮递进式辩论: claim -> rebuttal -> synthesis
    max_rounds=3 为默认深度，Phase 3+ 可扩展到 N+1 模式.
    """

    def __init__(self, max_rounds: int = 3):
        self._max_rounds = max_rounds

    def debate(
        self,
        agent_a_id: str,
        agent_b_id: str,
        topic: str,
        claim_a: str,
        claim_b: str,
    ) -> DebateResult:
        result = DebateResult(agent_a_id=agent_a_id, agent_b_id=agent_b_id, topic=topic)

        result.rounds.append(
            DebateRound(
                phase=DebatePhase.CLAIM,
                agent_a_statement=claim_a,
                agent_b_statement=claim_b,
                round_number=1,
            )
        )

        rebuttal_a, rebuttal_b = self._rebut(claim_a, claim_b)
        result.rounds.append(
            DebateRound(
                phase=DebatePhase.REBUTTAL,
                agent_a_statement=rebuttal_a,
                agent_b_statement=rebuttal_b,
                round_number=2,
            )
        )

        synthesis_a, synthesis_b = self._synthesize(claim_a, claim_b, rebuttal_a, rebuttal_b)
        result.rounds.append(
            DebateRound(
                phase=DebatePhase.SYNTHESIS,
                agent_a_statement=synthesis_a,
                agent_b_statement=synthesis_b,
                round_number=3,
            )
        )

        result.synthesis = f"{agent_a_id}: {synthesis_a}\n{agent_b_id}: {synthesis_b}"
        result.consensus = self._judge(result)

        return result

    def _rebut(self, claim_a: str, claim_b: str) -> tuple[str, str]:
        rebuttal_a = f"Challenge: {claim_b} may have unintended consequences: {claim_a}"
        rebuttal_b = f"Challenge: {claim_a} needs more evidence / risk assessment: {claim_b}"
        return rebuttal_a, rebuttal_b

    def _synthesize(
        self,
        claim_a: str,
        claim_b: str,
        rebuttal_a: str,
        rebuttal_b: str,
    ) -> tuple[str, str]:
        synthesis_a = f"Integrated: best of {claim_a} with guardrails from {claim_b}"
        synthesis_b = f"Integrated: core of {claim_b} protected by {claim_a}"
        return synthesis_a, synthesis_b

    def _judge(self, result: DebateResult) -> str:
        return f"Consensus on '{result.topic}': merge proposals with safety governance overlay"
