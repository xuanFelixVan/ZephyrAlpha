# [A_test] module_id: MOD-GOV_skill_consensus | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_consensus
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_consensus.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.autonomy_core.skills.skill_consensus import SkillConsensus, VoteResult


class TestVoteResultInit:
    def test_instantiation(self):
        vr = VoteResult(winner="opt-a", vote_counts={"opt-a": 3}, total_voters=3)
        assert vr.winner == "opt-a"
        assert vr.vote_counts == {"opt-a": 3}
        assert vr.total_voters == 3
        assert vr.tie_broken is False
        assert vr.tiebreaker_reason == ""

    def test_with_tiebreak(self):
        vr = VoteResult(
            winner="opt-b",
            vote_counts={"opt-a": 2, "opt-b": 2},
            total_voters=4,
            tie_broken=True,
            tiebreaker_reason="freshness",
        )
        assert vr.tie_broken is True
        assert vr.tiebreaker_reason == "freshness"

    def test_to_dict(self):
        vr = VoteResult(winner="opt-a", vote_counts={"opt-a": 5}, total_voters=5)
        d = vr.to_dict()
        assert d["winner"] == "opt-a"
        assert d["vote_counts"] == {"opt-a": 5}
        assert d["total_voters"] == 5
        assert d["tie_broken"] is False


class TestReachConsensus:
    def test_consensus_reached(self):
        result = SkillConsensus.reach_consensus(["sk-a", "sk-b"], {"sk-a": "yes", "sk-b": "yes"})
        assert result["consensus_reached"] is True
        assert result["unique_opinions"] == 1

    def test_no_consensus(self):
        result = SkillConsensus.reach_consensus(["sk-a", "sk-b"], {"sk-a": "yes", "sk-b": "no"})
        assert result["consensus_reached"] is False
        assert result["unique_opinions"] == 2

    def test_empty_votes(self):
        result = SkillConsensus.reach_consensus([], {})
        assert result["consensus_reached"] is False
        assert result["unique_opinions"] == 0

    def test_single_voter(self):
        result = SkillConsensus.reach_consensus(["sk-a"], {"sk-a": "maybe"})
        assert result["consensus_reached"] is True
        assert result["unique_opinions"] == 1


class TestMajorityVote:
    def test_clear_winner(self):
        winner, result = SkillConsensus.majority_vote(
            options=["a", "b"],
            votes={"v1": "a", "v2": "a", "v3": "b"},
        )
        assert winner == "a"
        assert result.winner == "a"
        assert result.tie_broken is False

    def test_weighted_vote(self):
        winner, result = SkillConsensus.majority_vote(
            options=["a", "b"],
            votes={"v1": "a", "v2": "b"},
            weights={"v1": 3.0, "v2": 1.0},
        )
        assert winner == "a"
        assert result.vote_counts["a"] == 3

    def test_no_valid_votes(self):
        winner, result = SkillConsensus.majority_vote(
            options=["a", "b"],
            votes={"v1": "c", "v2": "d"},
        )
        assert winner is None
        assert result.winner == ""

    def test_empty_votes(self):
        winner, result = SkillConsensus.majority_vote(
            options=["a", "b"],
            votes={},
        )
        assert winner is None

    def test_vote_for_invalid_option_ignored(self):
        winner, result = SkillConsensus.majority_vote(
            options=["a", "b"],
            votes={"v1": "a", "v2": "invalid"},
        )
        assert winner == "a"
        assert result.total_voters == 2

    def test_tie_triggers_tiebreak(self):
        mock_fdm = MagicMock()
        mock_fdm.current_state.return_value = {"freshness_score": 50}
        with patch(
            "zephyr.autonomy_core.skills.skill_freshness.FreshnessDecayModel",
            return_value=mock_fdm,
        ):
            winner, result = SkillConsensus.majority_vote(
                options=["a", "b"],
                votes={"v1": "a", "v2": "b"},
            )
            assert result.tie_broken is True
            assert winner in ("a", "b")


class TestWeightedConsensus:
    def test_basic_weighted_consensus(self):
        agents = [
            {"agent_id": "ag1", "vote": "yes", "weight": 2.0},
            {"agent_id": "ag2", "vote": "no", "weight": 1.0},
        ]
        result = SkillConsensus.weighted_consensus(agents, "deploy?")
        assert result["question"] == "deploy?"
        assert result["winner"] == "yes"
        assert result["consensus_reached"] is True

    def test_agents_without_id_get_generated(self):
        agents = [
            {"vote": "a", "weight": 1.0},
            {"vote": "b", "weight": 1.0},
        ]
        result = SkillConsensus.weighted_consensus(agents, "test?")
        assert len(result["agents"]) == 2
        assert result["agents"][0] == "agent_0"
        assert result["agents"][1] == "agent_1"

    def test_empty_agents(self):
        result = SkillConsensus.weighted_consensus([], "empty?")
        assert result["winner"] is None
        assert result["consensus_reached"] is False

    def test_default_weight_is_one(self):
        agents = [
            {"agent_id": "ag1", "vote": "a"},
            {"agent_id": "ag2", "vote": "b"},
        ]
        result = SkillConsensus.weighted_consensus(agents, "tie?")
        assert result["vote_detail"]["total_voters"] == 2
