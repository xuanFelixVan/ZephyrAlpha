# [BLUEPRINT] MOD-ORCH-004 | docs/03_modules/_domain_orchestrator/agent_coordination_skill/blueprint.md
# [MODULE] zephyr.orchestrator.agent_coordination_skill
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] 无（协调核心纯内存；cards/consensus/audit_sink/a2a_gateway/clock 全注入）
# [CONSUMERS] 运行时装配批（Agent Card 卡片库绑定 / 共识引擎回调 / 审计落库 / 真实 A2A 网关绑定）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Agent Card agent_id 唯一且能力集非空; 分工按(优先级降,agent_id升)确定性匹配; 仲裁两模式闭合(voting|priority); 投票目标须为候选 Agent; 共识回调未注入 Fail-Closed; 跨Agent调用强制 A2A 网关(未注入 Fail-Closed 不旁路); 协调记录按产生序审计留痕; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_orchestrator/agent_coordination_skill/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AgentCoordinationError(占位 ZA-ORCH-UNREGISTERED-AGENT-COORDINATION)——空卡片库/重复卡片/未知能力/未知agent/空topic/非法仲裁模式/投票非法/共识或网关未注入时抛
# [TESTS] tests/orchestrator/test_agent_coordination_skill.py
# [A_module] module_id=MOD-ORCH-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AgentCoordinationSkill — Agent 协调技能（MOD-ORCH-004）。

B11-02580（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-ORCH-004，A7）：
agent-coordination 技能封装——分工协议（按 Agent Card 能力匹配，卡片库注入）
+ 冲突仲裁（投票/优先级两模式）+ 共识触发（注入 consensus 回调）+ 协调记录
落审计 + 跨 Agent 调用走 **A2A 网关语义**（未注入 Fail-Closed 不旁路）。

查重分工（蓝图 §0）：agent_orchestrator=6角色×10域能力评分路由（本件=卡片
能力集合匹配，不做评分矩阵）；layered_command_chain=层级委托协议（本件=平
级协调/仲裁，不建指挥链）；voting_first_multi_agent=投票策略实现（本件仲
裁仅计票+优先级决胜，不实现投票策略）；A2A 网关族=协议实现（本件强制经
注入网关回调，不实现协议）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: cards 参数
#   fields: 参数 cards（无注解）
#   code: agent_coordination_skill.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: agent_coordination_skill.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: consensus 参数
#   fields: 参数 consensus（无注解）
#   code: agent_coordination_skill.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: agent_coordination_skill.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AgentCoordinationSkill
#   name_en: AgentCoordinationSkill
#   intro: Agent 协调技能（卡片库 + 分工 + 仲裁 + 共识 + A2A 网关 + 审计）。
#   desc: Agent 协调技能（卡片库 + 分工 + 仲裁 + 共识 + A2A 网关 + 审计）。；公共方法（定义序）: register_card, card_of, agents, assign, arbitrate, t…
#   inputs: cards clock consensus audit_sink a2a_gateway
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: AgentCoordinationSkill
#   downstream: 运行时装配批（Agent Card 卡片库绑定 / 共识引擎回调 / 审计落库 / 真实 A2A 网关绑定）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AgentCard",
    "AgentCoordinationError",
    "AgentCoordinationSkill",
    "ArbitrationMode",
    "Assignment",
    "ConflictResolution",
    "CoordinationKind",
    "CoordinationRecord",
]


class AgentCoordinationError(Exception):
    """Agent 协调输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ORCH-UNREGISTERED-AGENT-COORDINATION。
    """


class ArbitrationMode(str, Enum):
    """冲突仲裁模式（词表闭合）。"""

    VOTING = "voting"
    PRIORITY = "priority"


class CoordinationKind(str, Enum):
    """协调记录类别（词表闭合）。"""

    ASSIGN = "assign"
    ARBITRATE = "arbitrate"
    CONSENSUS = "consensus"
    A2A = "a2a"


@dataclass(frozen=True)
class AgentCard:
    """Agent Card（能力声明卡片，frozen；priority 大者优先）。"""

    agent_id: str
    capabilities: tuple[str, ...]
    priority: int = 0


@dataclass(frozen=True)
class Assignment:
    """分工结果（能力需求 → 受托 Agent，frozen）。"""

    requirement: str
    agent_id: str


@dataclass(frozen=True)
class ConflictResolution:
    """冲突仲裁结果（frozen）。"""

    topic: str
    mode: ArbitrationMode
    winner: str
    candidates: tuple[str, ...]
    votes: Mapping
    resolved_at: datetime.datetime


@dataclass(frozen=True)
class CoordinationRecord:
    """协调记录（审计载荷，frozen）。"""

    kind: CoordinationKind
    detail: Mapping
    recorded_at: datetime.datetime


class AgentCoordinationSkill:
    """Agent 协调技能（卡片库 + 分工 + 仲裁 + 共识 + A2A 网关 + 审计）。"""

    def __init__(
        self,
        *,
        cards: Iterable[AgentCard],
        clock: Callable[[], datetime.datetime] | None = None,
        consensus: Callable[[str, Mapping], bool] | None = None,
        audit_sink: Callable[[CoordinationRecord], None] | None = None,
        a2a_gateway: Callable[[str, str, Mapping], bool] | None = None,
    ) -> None:
        cards = tuple(cards)
        if not cards:
            raise AgentCoordinationError("cards 为空（Agent Card 卡片库须注入）")
        self._cards: dict[str, AgentCard] = {}
        for card in cards:
            self._validate_card(card)
            self._cards[card.agent_id] = card
        self._clock = clock or datetime.datetime.now
        self._consensus = consensus
        self._audit_sink = audit_sink
        self._gateway = a2a_gateway
        self._records: list[CoordinationRecord] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _validate_card(self, card: AgentCard) -> None:
        if not isinstance(card, AgentCard):
            raise AgentCoordinationError(f"非法卡片: {card!r}")
        if not card.agent_id:
            raise AgentCoordinationError("agent_id 为空")
        if not card.capabilities or not all(isinstance(c, str) and c for c in card.capabilities):
            raise AgentCoordinationError(f"能力集非法: {card.agent_id!r}（须非空字符串元组）")
        if card.agent_id in self._cards:
            raise AgentCoordinationError(f"卡片重复登记: {card.agent_id!r}")

    def _card_of(self, agent_id: str) -> AgentCard:
        card = self._cards.get(agent_id)
        if card is None:
            raise AgentCoordinationError(f"未知 agent: {agent_id!r}（未在卡片库中）")
        return card

    def _record(self, kind: CoordinationKind, detail: Mapping) -> None:
        record = CoordinationRecord(kind=kind, detail=dict(detail), recorded_at=self._clock())
        self._records.append(record)
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — 审计回调异常不阻断协调
                _log.exception("audit_sink 回调失败: %s", kind.value)

    # ── 卡片库 ────────────────────────────────────────────────────────────

    def register_card(self, card: AgentCard) -> None:
        """补登记 Agent Card（重复/非法 → Fail-Closed）。"""
        self._validate_card(card)
        self._cards[card.agent_id] = card

    def card_of(self, agent_id: str) -> AgentCard:
        """卡片查询（未知 agent → Fail-Closed）。"""
        return self._card_of(agent_id)

    def agents(self) -> tuple[str, ...]:
        """已登记 Agent 视图（字典序确定性排列）。"""
        return tuple(sorted(self._cards))

    # ── 分工协议（能力匹配） ───────────────────────────────────────────────

    def assign(self, requirements: Iterable[str]) -> tuple[Assignment, ...]:
        """分工：逐项能力需求匹配受托 Agent（优先级降 → agent_id 升决胜）。"""
        requirements = tuple(requirements)
        if not requirements:
            raise AgentCoordinationError("requirements 为空（无分工需求）")
        out: list[Assignment] = []
        for req in requirements:
            if not req:
                raise AgentCoordinationError("能力需求为空串")
            candidates = [c for c in self._cards.values() if req in c.capabilities]
            if not candidates:
                raise AgentCoordinationError(f"未知能力: {req!r}（无 Agent 覆盖）")
            candidates.sort(key=lambda c: (-c.priority, c.agent_id))
            out.append(Assignment(requirement=req, agent_id=candidates[0].agent_id))
        self._record(
            CoordinationKind.ASSIGN,
            {
                "assignments": tuple((a.requirement, a.agent_id) for a in out),
            },
        )
        return tuple(out)

    # ── 冲突仲裁（投票/优先级） ───────────────────────────────────────────

    def arbitrate(
        self,
        topic: str,
        candidates: Iterable[str],
        mode: ArbitrationMode,
        votes: Mapping[str, str] | None = None,
    ) -> ConflictResolution:
        """仲裁：PRIORITY=优先级决胜；VOTING=计票决胜（平票→优先级→agent_id）。"""
        if not topic:
            raise AgentCoordinationError("topic 为空")
        if not isinstance(mode, ArbitrationMode):
            raise AgentCoordinationError(f"非法仲裁模式: {mode!r}（词表闭合）")
        candidates = tuple(candidates)
        if not candidates:
            raise AgentCoordinationError("candidates 为空（无仲裁候选）")
        for agent_id in candidates:
            self._card_of(agent_id)
        if len(set(candidates)) != len(candidates):
            raise AgentCoordinationError("candidates 含重复 agent")

        if mode is ArbitrationMode.PRIORITY:
            winner = self._by_priority(candidates)
            tally: dict[str, int] = {}
        else:
            if not votes:
                raise AgentCoordinationError("投票模式须注入非空 votes")
            tally = {}
            for voter, target in votes.items():
                if target not in candidates:
                    raise AgentCoordinationError(f"非法投票: {voter!r} 投给非候选 {target!r}")
                tally[target] = tally.get(target, 0) + 1
            # 计票降序 → 优先级降序 → agent_id 字典序升（确定性决胜）
            ranked = sorted(tally, key=lambda a: (-tally[a], -self._cards[a].priority, a))
            winner = ranked[0]
        resolution = ConflictResolution(
            topic=topic,
            mode=mode,
            winner=winner,
            candidates=tuple(sorted(candidates)),
            votes=dict(tally),
            resolved_at=self._clock(),
        )
        self._record(
            CoordinationKind.ARBITRATE,
            {
                "topic": topic,
                "mode": mode.value,
                "winner": winner,
                "votes": dict(tally),
            },
        )
        return resolution

    def _by_priority(self, candidates: tuple[str, ...]) -> str:
        ranked = sorted(candidates, key=lambda a: (-self._cards[a].priority, a))
        return ranked[0]

    # ── 共识触发（注入回调） ───────────────────────────────────────────────

    def trigger_consensus(self, topic: str, proposal: Mapping) -> bool:
        """共识触发：回调未注入 Fail-Closed；异常按未达成收敛不抛。"""
        if not topic:
            raise AgentCoordinationError("topic 为空")
        if not isinstance(proposal, Mapping):
            raise AgentCoordinationError("proposal 非法（须为 Mapping）")
        if self._consensus is None:
            raise AgentCoordinationError("consensus 未注入（Fail-Closed 不旁路）")
        try:
            reached = bool(self._consensus(topic, proposal))
        except Exception:  # noqa: BLE001 — 共识异常按未达成处理不抛
            _log.exception("consensus 回调异常: %s", topic)
            reached = False
        self._record(
            CoordinationKind.CONSENSUS,
            {
                "topic": topic,
                "reached": reached,
                "proposal": dict(proposal),
            },
        )
        return reached

    # ── 跨 Agent 调用（强制 A2A 网关） ────────────────────────────────────

    def send(self, sender: str, recipient: str, message: Mapping) -> bool:
        """跨 Agent 调用：双方须已登记；强制经 A2A 网关（未注入 Fail-Closed）。"""
        self._card_of(sender)
        self._card_of(recipient)
        if sender == recipient:
            raise AgentCoordinationError(f"自调用非法: {sender!r}")
        if not isinstance(message, Mapping):
            raise AgentCoordinationError("message 非法（须为 Mapping）")
        if self._gateway is None:
            raise AgentCoordinationError("a2a_gateway 未注入（跨Agent调用强制 A2A 网关，禁止旁路）")
        try:
            ok = bool(self._gateway(sender, recipient, message))
        except Exception:  # noqa: BLE001 — 网关异常按 NACK 处理不抛
            _log.exception("a2a_gateway 传递异常: %s -> %s", sender, recipient)
            ok = False
        self._record(
            CoordinationKind.A2A,
            {
                "sender": sender,
                "recipient": recipient,
                "delivered": ok,
            },
        )
        return ok

    # ── 审计查询 ──────────────────────────────────────────────────────────

    def records(self) -> tuple[CoordinationRecord, ...]:
        """协调记录视图（按产生序确定性排列）。"""
        return tuple(self._records)
