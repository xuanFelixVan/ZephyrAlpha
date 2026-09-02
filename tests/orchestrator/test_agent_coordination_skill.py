# [BLUEPRINT] MOD-ORCH-004 | docs/03_modules/_domain_orchestrator/agent_coordination_skill/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ORCH-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.orchestrator.test_agent_coordination_skill
# [TESTS] src/zephyr/orchestrator/agent_coordination_skill.py
"""MOD-ORCH-004 单元测试：agent_coordination_skill Agent 协调技能。

蓝图验收（B11-02580/CAND-ORCH-004，A7）：分工协议（Agent Card 能力匹配，
卡片库注入）+ 冲突仲裁（投票/优先级两模式）+ 共识触发（注入回调，未注入
Fail-Closed）+ 协调记录审计 + 跨 Agent 调用强制 A2A 网关语义。共识/审计/
网关/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.orchestrator.agent_coordination_skill",
    reason="agent_coordination_skill not importable",
)

from zephyr.orchestrator.agent_coordination_skill import (  # noqa: E402
    AgentCard,
    AgentCoordinationError,
    AgentCoordinationSkill,
    ArbitrationMode,
    CoordinationKind,
    CoordinationRecord,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

_CARDS = (
    AgentCard(agent_id="analyst", capabilities=("signal", "timing"), priority=5),
    AgentCard(agent_id="trader", capabilities=("execution",), priority=8),
    AgentCard(agent_id="risk", capabilities=("signal", "risk_control"), priority=3),
)


def _skill(
    audits: list | None = None,
    consensus=None,
    gateway=None,
    gateway_ok: bool = True,
) -> AgentCoordinationSkill:
    return AgentCoordinationSkill(
        cards=_CARDS,
        clock=lambda: _T0,
        consensus=consensus,
        audit_sink=(lambda r: audits.append(r)) if audits is not None else None,
        a2a_gateway=gateway if gateway is not None else (lambda s, r, m: gateway_ok),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 卡片库
# ──────────────────────────────────────────────────────────────────────────────


class TestCards:
    def test_init_ok_agents_sorted(self) -> None:
        assert _skill().agents() == ("analyst", "risk", "trader")

    def test_empty_cards_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            AgentCoordinationSkill(cards=[], clock=lambda: _T0)

    def test_duplicate_card_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            AgentCoordinationSkill(
                cards=(
                    AgentCard(agent_id="a", capabilities=("x",)),
                    AgentCard(agent_id="a", capabilities=("y",)),
                ),
                clock=lambda: _T0,
            )

    def test_invalid_card_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            AgentCoordinationSkill(cards=(AgentCard(agent_id="", capabilities=("x",)),), clock=lambda: _T0)
        with pytest.raises(AgentCoordinationError):
            AgentCoordinationSkill(cards=(AgentCard(agent_id="a", capabilities=()),), clock=lambda: _T0)

    def test_register_card_late_and_duplicate(self) -> None:
        skill = _skill()
        skill.register_card(AgentCard(agent_id="ops", capabilities=("deploy",)))
        assert skill.card_of("ops").capabilities == ("deploy",)
        with pytest.raises(AgentCoordinationError):
            skill.register_card(AgentCard(agent_id="ops", capabilities=("deploy",)))

    def test_card_of_unknown_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            _skill().card_of("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 分工协议（能力匹配）
# ──────────────────────────────────────────────────────────────────────────────


class TestAssign:
    def test_assign_priority_wins(self) -> None:
        out = _skill().assign(["signal", "execution"])
        assert [(a.requirement, a.agent_id) for a in out] == [
            ("signal", "analyst"),  # analyst(5) > risk(3)
            ("execution", "trader"),
        ]

    def test_assign_tie_break_by_agent_id(self) -> None:
        skill = AgentCoordinationSkill(
            cards=(
                AgentCard(agent_id="beta", capabilities=("x",), priority=1),
                AgentCard(agent_id="alpha", capabilities=("x",), priority=1),
            ),
            clock=lambda: _T0,
        )
        assert skill.assign(["x"])[0].agent_id == "alpha"  # 平优先级→字典序

    def test_assign_unknown_capability_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            _skill().assign(["ghost_capability"])

    def test_assign_empty_requirements_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            _skill().assign([])
        with pytest.raises(AgentCoordinationError):
            _skill().assign([""])

    def test_assign_audit_record(self) -> None:
        audits: list[CoordinationRecord] = []
        _skill(audits).assign(["signal"])
        assert len(audits) == 1
        assert audits[0].kind is CoordinationKind.ASSIGN
        assert audits[0].detail["assignments"] == (("signal", "analyst"),)
        assert audits[0].recorded_at == _T0


# ──────────────────────────────────────────────────────────────────────────────
# 冲突仲裁（投票/优先级）
# ──────────────────────────────────────────────────────────────────────────────


class TestArbitrate:
    def test_priority_mode(self) -> None:
        res = _skill().arbitrate("信号分歧", ["analyst", "risk"], ArbitrationMode.PRIORITY)
        assert res.winner == "analyst"  # priority 5 > 3
        assert res.mode is ArbitrationMode.PRIORITY
        assert res.candidates == ("analyst", "risk")  # 确定性排序

    def test_voting_mode_count_wins(self) -> None:
        res = _skill().arbitrate(
            "方向冲突",
            ["analyst", "trader"],
            ArbitrationMode.VOTING,
            votes={"v1": "trader", "v2": "analyst", "v3": "trader"},
        )
        assert res.winner == "trader"
        assert res.votes == {"trader": 2, "analyst": 1}

    def test_voting_tie_break_by_priority(self) -> None:
        res = _skill().arbitrate(
            "平票",
            ["analyst", "trader"],
            ArbitrationMode.VOTING,
            votes={"v1": "analyst", "v2": "trader"},
        )
        assert res.winner == "trader"  # 平票 → priority 8 > 5

    def test_voting_empty_votes_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            _skill().arbitrate("t", ["analyst"], ArbitrationMode.VOTING, votes={})

    def test_voting_non_candidate_raises(self) -> None:
        with pytest.raises(AgentCoordinationError):
            _skill().arbitrate("t", ["analyst"], ArbitrationMode.VOTING, votes={"v1": "trader"})

    def test_arbitrate_invalid_input_raises(self) -> None:
        skill = _skill()
        with pytest.raises(AgentCoordinationError):
            skill.arbitrate("", ["analyst"], ArbitrationMode.PRIORITY)  # 空 topic
        with pytest.raises(AgentCoordinationError):
            skill.arbitrate("t", ["analyst"], "majority")  # 非法模式
        with pytest.raises(AgentCoordinationError):
            skill.arbitrate("t", [], ArbitrationMode.PRIORITY)  # 空候选
        with pytest.raises(AgentCoordinationError):
            skill.arbitrate("t", ["analyst", "ghost"], ArbitrationMode.PRIORITY)  # 未知
        with pytest.raises(AgentCoordinationError):
            skill.arbitrate("t", ["analyst", "analyst"], ArbitrationMode.PRIORITY)  # 重复

    def test_arbitrate_audit_record(self) -> None:
        audits: list[CoordinationRecord] = []
        _skill(audits).arbitrate("信号分歧", ["analyst", "risk"], ArbitrationMode.PRIORITY)
        assert audits[0].kind is CoordinationKind.ARBITRATE
        assert audits[0].detail["winner"] == "analyst"


# ──────────────────────────────────────────────────────────────────────────────
# 共识触发
# ──────────────────────────────────────────────────────────────────────────────


class TestConsensus:
    def test_consensus_reached(self) -> None:
        seen: list = []
        skill = _skill(consensus=lambda t, p: seen.append((t, p)) or True)
        assert skill.trigger_consensus("调仓提案", {"delta": 0.1}) is True
        assert seen == [("调仓提案", {"delta": 0.1})]

    def test_consensus_not_injected_fail_closed(self) -> None:
        with pytest.raises(AgentCoordinationError):
            _skill().trigger_consensus("t", {})

    def test_consensus_exception_as_not_reached(self) -> None:
        def _boom(t, p):
            raise RuntimeError("共识引擎故障")

        assert _skill(consensus=_boom).trigger_consensus("t", {}) is False

    def test_consensus_invalid_input_raises(self) -> None:
        skill = _skill(consensus=lambda t, p: True)
        with pytest.raises(AgentCoordinationError):
            skill.trigger_consensus("", {})
        with pytest.raises(AgentCoordinationError):
            skill.trigger_consensus("t", "not-a-mapping")

    def test_consensus_audit_record(self) -> None:
        audits: list[CoordinationRecord] = []
        _skill(audits, consensus=lambda t, p: False).trigger_consensus("t", {"x": 1})
        assert audits[0].kind is CoordinationKind.CONSENSUS
        assert audits[0].detail["reached"] is False


# ──────────────────────────────────────────────────────────────────────────────
# 跨 Agent 调用（A2A 网关）与审计
# ──────────────────────────────────────────────────────────────────────────────


class TestA2AAndAudit:
    def test_send_via_gateway(self) -> None:
        sent: list = []
        skill = _skill(gateway=lambda s, r, m: sent.append((s, r, m)) or True)
        assert skill.send("analyst", "trader", {"order": "buy"}) is True
        assert sent == [("analyst", "trader", {"order": "buy"})]

    def test_send_gateway_not_injected_fail_closed(self) -> None:
        skill = AgentCoordinationSkill(cards=_CARDS, clock=lambda: _T0)
        with pytest.raises(AgentCoordinationError):
            skill.send("analyst", "trader", {})

    def test_send_nack_and_exception(self) -> None:
        assert _skill(gateway_ok=False).send("analyst", "trader", {}) is False

        def _boom(s, r, m):
            raise RuntimeError("网关超时")

        assert _skill(gateway=_boom).send("analyst", "trader", {}) is False

    def test_send_invalid_input_raises(self) -> None:
        skill = _skill()
        with pytest.raises(AgentCoordinationError):
            skill.send("ghost", "trader", {})
        with pytest.raises(AgentCoordinationError):
            skill.send("analyst", "analyst", {})  # 自调用
        with pytest.raises(AgentCoordinationError):
            skill.send("analyst", "trader", "not-a-mapping")

    def test_records_order_deterministic(self) -> None:
        audits: list[CoordinationRecord] = []
        skill = _skill(audits, consensus=lambda t, p: True)
        skill.assign(["signal"])
        skill.arbitrate("t", ["analyst", "risk"], ArbitrationMode.PRIORITY)
        skill.trigger_consensus("t", {})
        skill.send("analyst", "trader", {})
        records = skill.records()
        assert [r.kind for r in records] == [
            CoordinationKind.ASSIGN,
            CoordinationKind.ARBITRATE,
            CoordinationKind.CONSENSUS,
            CoordinationKind.A2A,
        ]
        assert audits == list(records)  # 审计回调与内部记录一致
        assert all(r.recorded_at == _T0 for r in records)
