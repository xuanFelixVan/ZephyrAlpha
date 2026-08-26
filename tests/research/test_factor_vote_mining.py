# [BLUEPRINT] MOD-FAC-004 | docs/03_modules/_domain_factor/factor_vote_mining/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FAC-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.research.test_factor_vote_mining
# [TESTS] src/zephyr/research/factor_vote_mining.py
"""MOD-FAC-004 单元测试：factor_vote_mining FactorMAD 多智能体投票因子挖掘。

蓝图验收（B10-01845/CAND-FAC-020，A1 §29.14-3.5）：
3-5 Agent 独立产出（回调全注入）+ 多数投票严格过半入选 + 性能不足升级辩论
（轮次护栏）+ IC 验证 + 样本外测试（注入验证器）+ <1分钟/因子时延预算标记。
Agent/验证器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.research.factor_vote_mining",
    reason="factor_vote_mining not importable",
)

from zephyr.research.factor_vote_mining import (  # noqa: E402
    FactorVoteError,
    FactorVoteMiner,
    VoteAgent,
)

_IC = {"f_alpha": 0.10, "f_beta": 0.06, "f_weak": 0.005}
_OOS_PASS = {"f_alpha", "f_beta"}


def _ic(expr: str) -> float:
    return _IC.get(expr, 0.0)


def _oos(expr: str) -> bool:
    return expr in _OOS_PASS


def _agent(aid: str, proposals, yes_for=frozenset()) -> VoteAgent:
    """proposals: list[str] 或 {round: list[str]}；yes_for: 该 Agent 赞成的表达式集。"""
    def propose(topic: str, r: int):
        if isinstance(proposals, dict):
            return proposals.get(r, [])
        return proposals if r == 0 else []

    return VoteAgent(agent_id=aid, propose=propose, vote=lambda e: e in yes_for)


def _miner(agents, **kw) -> FactorVoteMiner:
    kw.setdefault("ic_validator", _ic)
    kw.setdefault("oos_validator", _oos)
    kw.setdefault("clock", iter([0.0] * 200).__next__)
    return FactorVoteMiner(agents=agents, **kw)


def _three_agents(voters=("a1", "a2")) -> list[VoteAgent]:
    """a1 提案 f_alpha；a2 提案 f_beta；a3 空提案；voters 中 Agent 全票赞成。"""
    yes = frozenset(voters)
    return [
        _agent("a1", ["f_alpha"], yes_for={"f_alpha", "f_beta"} if "a1" in yes else set()),
        _agent("a2", ["f_beta"], yes_for={"f_alpha", "f_beta"} if "a2" in yes else set()),
        _agent("a3", [], yes_for={"f_alpha", "f_beta"} if "a3" in yes else set()),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_agent_count_guard(self) -> None:
        two = _three_agents()[:2]
        with pytest.raises(FactorVoteError):
            _miner(two)
        six = [_agent(f"a{i}", []) for i in range(6)]
        with pytest.raises(FactorVoteError):
            _miner(six)

    def test_duplicate_agent_id(self) -> None:
        agents = [_agent("a1", []), _agent("a1", []), _agent("a3", [])]
        with pytest.raises(FactorVoteError):
            _miner(agents)

    def test_blank_agent_id(self) -> None:
        agents = [_agent(" ", []), _agent("a2", []), _agent("a3", [])]
        with pytest.raises(FactorVoteError):
            _miner(agents)

    def test_missing_validators(self) -> None:
        with pytest.raises(FactorVoteError):
            FactorVoteMiner(agents=_three_agents(), ic_validator=None, oos_validator=_oos)
        with pytest.raises(FactorVoteError):
            FactorVoteMiner(agents=_three_agents(), ic_validator=_ic, oos_validator=None)

    def test_min_ic_range(self) -> None:
        with pytest.raises(FactorVoteError):
            _miner(_three_agents(), min_ic=1.0)

    def test_debate_rounds_guard(self) -> None:
        with pytest.raises(FactorVoteError):
            _miner(_three_agents(), max_debate_rounds=6)

    def test_latency_budget_positive(self) -> None:
        with pytest.raises(FactorVoteError):
            _miner(_three_agents(), latency_budget_s=0.0)


# ──────────────────────────────────────────────────────────────────────────────
# 提案 → IC/OOS 验证 → 多数投票
# ──────────────────────────────────────────────────────────────────────────────


class TestMine:
    def test_blank_topic_raises(self) -> None:
        with pytest.raises(FactorVoteError):
            _miner(_three_agents()).mine("  ")

    def test_majority_elected(self) -> None:
        # 3 Agent，a1/a2 赞成 → 2/3 严格过半
        result = _miner(_three_agents(voters=("a1", "a2"))).mine("动量")
        exprs = {e.expression for e in result.elected}
        assert "f_alpha" in exprs and "f_beta" in exprs
        alpha = next(e for e in result.elected if e.expression == "f_alpha")
        assert alpha.votes == 2
        assert alpha.vote_share == pytest.approx(round(2 / 3, 6))
        assert alpha.ic == pytest.approx(0.10)
        assert alpha.within_latency_budget is True

    def test_exactly_half_not_elected(self) -> None:
        # 4 Agent 仅 2 票 → 2 > 4/2 不成立 → 落选
        agents = [
            _agent("a1", ["f_alpha"], yes_for={"f_alpha"}),
            _agent("a2", [], yes_for={"f_alpha"}),
            _agent("a3", [], yes_for=set()),
            _agent("a4", [], yes_for=set()),
        ]
        result = _miner(agents).mine("动量")
        assert result.elected == ()
        assert any("票数未过半" in n for n in result.notes)

    def test_ic_filter_blocks(self) -> None:
        agents = [
            _agent("a1", ["f_weak"], yes_for={"f_weak"}),
            _agent("a2", [], yes_for={"f_weak"}),
            _agent("a3", [], yes_for={"f_weak"}),
        ]
        result = _miner(agents).mine("动量")
        assert result.elected == ()
        assert any("IC 不足" in n for n in result.notes)

    def test_oos_filter_blocks(self) -> None:
        agents = [
            _agent("a1", ["f_alpha"], yes_for={"f_alpha"}),
            _agent("a2", [], yes_for={"f_alpha"}),
            _agent("a3", [], yes_for={"f_alpha"}),
        ]
        result = _miner(agents, oos_validator=lambda e: False).mine("动量")
        assert result.elected == ()
        assert any("样本外未过" in n for n in result.notes)

    def test_proposals_recorded_with_round(self) -> None:
        result = _miner(_three_agents()).mine("动量")
        assert [(p.agent_id, p.expression, p.debate_round) for p in result.proposals] == [
            ("a1", "f_alpha", 0),
            ("a2", "f_beta", 0),
        ]

    def test_elected_sorted_by_votes_then_ic(self) -> None:
        # f_alpha 3 票，f_beta 2 票 → f_alpha 居首
        agents = [
            _agent("a1", ["f_alpha"], yes_for={"f_alpha", "f_beta"}),
            _agent("a2", ["f_beta"], yes_for={"f_alpha", "f_beta"}),
            _agent("a3", [], yes_for={"f_alpha"}),
        ]
        result = _miner(agents).mine("动量")
        assert [e.expression for e in result.elected] == ["f_alpha", "f_beta"]
        assert result.elected[0].votes == 3

    def test_validator_exception_fail_closed(self) -> None:
        def boom(expr: str) -> float:
            raise RuntimeError("IC 后端故障")

        with pytest.raises(FactorVoteError):
            _miner(_three_agents(), ic_validator=boom).mine("动量")

    def test_ic_validator_bad_return_fail_closed(self) -> None:
        with pytest.raises(FactorVoteError):
            _miner(_three_agents(), ic_validator=lambda e: "bad").mine("动量")

    def test_propose_exception_fail_closed(self) -> None:
        def bad_propose(topic: str, r: int):
            raise RuntimeError("Agent 故障")

        agents = _three_agents()
        agents[0] = VoteAgent(agent_id="a1", propose=bad_propose, vote=lambda e: True)
        with pytest.raises(FactorVoteError):
            _miner(agents).mine("动量")


# ──────────────────────────────────────────────────────────────────────────────
# 升级辩论（轮次护栏）+ 时延预算标记
# ──────────────────────────────────────────────────────────────────────────────


class TestDebateAndLatency:
    def test_debate_escalation_success(self) -> None:
        # 第 0 轮提案 IC 不足，辩论第 1 轮提案 f_alpha → 入选
        agents = [
            _agent("a1", {0: ["f_weak"], 1: ["f_alpha"]}, yes_for={"f_alpha"}),
            _agent("a2", {0: [], 1: []}, yes_for={"f_alpha"}),
            _agent("a3", {0: [], 1: []}, yes_for=set()),
        ]
        result = _miner(agents, max_debate_rounds=2).mine("动量")
        assert [e.expression for e in result.elected] == ["f_alpha"]
        assert result.debate_rounds == 1
        assert result.elected[0].debate_round == 1
        assert any("升级辩论" in n for n in result.notes)

    def test_debate_rounds_capped(self) -> None:
        # 全程 IC 不足 → 用尽辩论轮次护栏，零入选
        agents = [
            _agent("a1", {0: ["f_weak"], 1: ["f_weak"]}, yes_for=set()),
            _agent("a2", {}, yes_for=set()),
            _agent("a3", {}, yes_for=set()),
        ]
        result = _miner(agents, max_debate_rounds=1).mine("动量")
        assert result.elected == ()
        assert result.debate_rounds == 1  # 护栏封顶

    def test_no_debate_when_first_round_elects(self) -> None:
        result = _miner(_three_agents(), max_debate_rounds=3).mine("动量")
        assert result.debate_rounds == 0

    def test_latency_budget_flag(self) -> None:
        # f_alpha 验证耗时 30s（预算内），f_beta 耗时 90s（超预算）
        ticks = iter([0.0, 30.0, 0.0, 90.0])
        result = _miner(_three_agents(), clock=ticks.__next__).mine("动量")
        flags = {e.expression: e.within_latency_budget for e in result.elected}
        assert flags == {"f_alpha": True, "f_beta": False}

    def test_full_determinism(self) -> None:
        def run() -> tuple:
            r = _miner(_three_agents()).mine("动量")
            return tuple((e.expression, e.votes, e.ic) for e in r.elected)

        assert run() == run()  # 同输入必同输出
