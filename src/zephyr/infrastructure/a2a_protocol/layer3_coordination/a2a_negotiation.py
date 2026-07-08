# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_negotiation
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
# [A_module] module_id=MOD-INF_a2a_negotiation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 协商协议 — Agent 间资源/任务分配协商

当 Agent A 需要 Agent B 的资源(文件锁/DB表/计算资源)时触发协商:
  Agent A -> propose -> Agent B -> counter/accept/reject
  循环直到达成协议或超时

输出: NegotiationResult — 协议内容 + 妥协条款
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NegotiationStatus(str, Enum):
    PROPOSED = "proposed"
    COUNTERED = "countered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class NegotiationOffer:
    resource: str
    proposed_by: str
    terms: dict = field(default_factory=dict)


@dataclass
class NegotiationResult:
    initiator: str
    responder: str
    status: NegotiationStatus
    final_terms: dict = field(default_factory=dict)
    rounds: int = 0


class A2ANegotiation:
    """A2A 协商引擎.

    双向提议-反提议循环:
      initiator propose -> responder evaluate -> accept/counter/reject
    max_rounds=5 防止无限协商循环.
    """

    def __init__(self, max_rounds: int = 5, round_timeout: float = 60.0):
        self._max_rounds = max_rounds
        self._round_timeout = round_timeout

    def propose(
        self,
        initiator: str,
        responder: str,
        resource: str,
        initial_terms: dict,
    ) -> NegotiationResult:
        current = NegotiationOffer(resource=resource, proposed_by=initiator, terms=initial_terms)
        result = NegotiationResult(
            initiator=initiator,
            responder=responder,
            status=NegotiationStatus.PROPOSED,
            final_terms=initial_terms,
        )

        for round_num in range(1, self._max_rounds + 1):
            response = self._evaluate_offer(responder, current)

            if response["decision"] == NegotiationStatus.ACCEPTED:
                result.status = NegotiationStatus.ACCEPTED
                result.final_terms = response["terms"]
                result.rounds = round_num
                return result
            elif response["decision"] == NegotiationStatus.REJECTED:
                result.status = NegotiationStatus.REJECTED
                result.rounds = round_num
                return result
            else:
                counter = response["terms"]
                current = NegotiationOffer(
                    resource=resource,
                    proposed_by=responder,
                    terms=counter,
                )

        result.status = NegotiationStatus.TIMEOUT
        result.rounds = self._max_rounds
        return result

    def _evaluate_offer(
        self,
        agent_id: str,
        offer: NegotiationOffer,
    ) -> dict:
        return {
            "decision": NegotiationStatus.ACCEPTED,
            "terms": offer.terms,
        }

    @staticmethod
    def is_resolved(result: NegotiationResult) -> bool:
        return result.status in (NegotiationStatus.ACCEPTED, NegotiationStatus.REJECTED)

    @staticmethod
    def needs_escalation(result: NegotiationResult) -> bool:
        return result.status in (NegotiationStatus.TIMEOUT, NegotiationStatus.REJECTED)
