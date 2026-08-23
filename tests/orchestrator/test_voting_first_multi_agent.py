# [BLUEPRINT] MOD-INF-048 | docs/03_modules/MOD-INF-048/
# [MODULE] tests.orchestrator.test_voting_first_multi_agent
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/orchestrator/test_voting_first_multi_agent.py -q
# [TTL] permanent

"""投票优先多智能体编排（MOD-INF-048）单元测试——纯函数投票/容错/无提案 fail-closed。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.voting_first_multi_agent import (
    VoteConfigError,
    VotingFirstMultiAgent,
    VotingResult,
    tally_votes,
)


class TestTallyVotesPure:
    def test_plurality_winner(self):
        out = tally_votes({"a1": "X", "a2": "X", "a3": "Y"})
        assert out.winner == "X"
        assert out.tally == {"X": 2.0, "Y": 1.0}
        assert out.tie_broken is False

    def test_weighted_winner(self):
        out = tally_votes({"a1": "X", "a2": "Y"}, weights={"a1": 1.0, "a2": 3.0})
        assert out.winner == "Y"
        assert out.tally["Y"] == 3.0

    def test_tie_broken_deterministic(self):
        r1 = tally_votes({"a1": "X", "a2": "Y"})
        r2 = tally_votes({"a2": "Y", "a1": "X"})
        assert r1.tie_broken is True
        assert r1.winner == r2.winner  # 字典序小者胜（确定性）

    def test_empty_votes_winner_none(self):
        out = tally_votes({})
        assert out.winner is None
        assert out.tally == {}

    def test_negative_weight_rejected(self):
        with pytest.raises(VoteConfigError):
            tally_votes({"a1": "X"}, weights={"a1": -1.0})


def _agent(answer: str):
    return lambda task: answer


def _failing_agent(task: str) -> str:
    raise RuntimeError("agent boom")


class TestOrchestrator:
    def test_no_agents_rejected(self):
        with pytest.raises(VoteConfigError):
            VotingFirstMultiAgent().run("task")

    def test_empty_task_rejected(self):
        orch = VotingFirstMultiAgent()
        orch.register_agent("a1", _agent("X"))
        with pytest.raises(VoteConfigError):
            orch.run("")

    def test_register_validation(self):
        orch = VotingFirstMultiAgent()
        with pytest.raises(VoteConfigError):
            orch.register_agent("", _agent("X"))
        with pytest.raises(VoteConfigError):
            orch.register_agent("a1", _agent("X"), weight=0.0)
        with pytest.raises(VoteConfigError):
            orch.register_agent("a1", "not-callable")

    def test_voting_decides_winner(self):
        orch = VotingFirstMultiAgent()
        orch.register_agent("a1", _agent("买入"))
        orch.register_agent("a2", _agent("买入"))
        orch.register_agent("a3", _agent("观望"))
        result = orch.run("明日操作?")
        assert isinstance(result, VotingResult)
        assert result.winner == "买入"
        assert result.proposals == {"a1": "买入", "a2": "买入", "a3": "观望"}
        assert result.failed_agents == []

    def test_agent_failure_tolerated(self):
        orch = VotingFirstMultiAgent()
        orch.register_agent("good", _agent("X"))
        orch.register_agent("bad", _failing_agent)
        result = orch.run("t")
        assert result.winner == "X"
        assert result.failed_agents == ["bad"]
        assert "bad" not in result.proposals

    def test_all_agents_failed_fail_closed(self):
        orch = VotingFirstMultiAgent()
        orch.register_agent("bad1", _failing_agent)
        orch.register_agent("bad2", _failing_agent)
        result = orch.run("t")
        assert result.winner is None
        assert result.vote.winner is None
        assert len(result.failed_agents) == 2

    def test_error_code(self):
        assert VoteConfigError.error_code == "ZA-TR-0022"
