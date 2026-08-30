# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_negotiation
# [DOMAIN] D_INFRA_A2A
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
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
A2A 协商协议 — Agent 间资源/任务分配协商

当 Agent A 需要 Agent B 的资源(文件锁/DB表/计算资源)时触发协商:
  Agent A -> propose -> Agent B -> counter/accept/reject
  循环直到达成协议或超时

输出: NegotiationResult — 协议内容 + 妥协条款

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_rounds 参数
#   fields: 参数 max_rounds（无注解）
#   code: a2a_negotiation.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: round_timeout 参数
#   fields: 参数 round_timeout（无注解）
#   code: a2a_negotiation.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① A2ANegotiation
#   name_en: A2ANegotiation
#   intro: A2A 协商引擎.
#   desc: A2A 协商引擎. 双向提议-反提议循环: initiator propose -> responder evaluate -> accept/counter/reject ma…；公共方法（定义序）: max_rou…
#   inputs: max_rounds round_timeout
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: A2ANegotiation
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def max_rounds(self):
        """只读：max_rounds（Stage 4 公共化）。"""
        return self._max_rounds

    @max_rounds.setter
    def max_rounds(self, value):
        """写入：max_rounds（Stage 4 公共化）。"""
        self._max_rounds = value

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
