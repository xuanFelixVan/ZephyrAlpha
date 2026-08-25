# [A_test] module_id: MOD-SIG-109 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-109 | docs/03_modules/_domain_signal/strategy_cross_vote_funnel/blueprint.md
# [MODULE] tests.signal_ashare.test_strategy_cross_vote_funnel
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.strategy_cross_vote_funnel

"""筛选漏斗第五层多策略交叉投票（MOD-SIG-109，B10-01504）施工验证测试。

覆盖：三席+额外投票方权重封闭集、加权投票通过与否决、弃权口径（含全弃权）、
C-021 否决门（含降级直通）、容量截断排序（~30）、无投票剔除、非法输入 fail-closed、
frozen/JSON 契约。
全程内存合成数据，无 DB。
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.strategy_cross_vote_funnel import (
    CORE_SEAT_WEIGHTS,
    EXTRA_VOTER_WEIGHTS,
    CrossVoteConfig,
    MarketStateClearance,
    StrategyCrossVoteFunnel,
    StrategyVote,
)


def _fn(cfg=None) -> StrategyCrossVoteFunnel:
    return StrategyCrossVoteFunnel(cfg or CrossVoteConfig())


def _v(voter, vote):
    return StrategyVote(voter=voter, vote=vote)


class TestWeightsRegistry:
    def test_core_seats(self):
        assert CORE_SEAT_WEIGHTS["value"] == pytest.approx(0.30, abs=1e-9)
        assert CORE_SEAT_WEIGHTS["momentum"] == pytest.approx(0.25, abs=1e-9)
        assert CORE_SEAT_WEIGHTS["event"] == pytest.approx(0.20, abs=1e-9)

    def test_extra_voters(self):
        assert EXTRA_VOTER_WEIGHTS["c034_inference"] == pytest.approx(0.10, abs=1e-9)
        assert EXTRA_VOTER_WEIGHTS["c036_synergy"] == pytest.approx(0.10, abs=1e-9)


class TestEvaluateSymbol:
    def test_approve(self):
        fn = _fn()
        votes = [_v("value", 1), _v("momentum", 1), _v("event", 1)]
        r = fn.evaluate_symbol("000001", votes)
        assert r.approved is True
        assert r.vote_score > 0

    def test_reject(self):
        fn = _fn()
        votes = [_v("value", -1), _v("momentum", -1), _v("event", -1)]
        r = fn.evaluate_symbol("000001", votes)
        assert r.approved is False
        assert r.vote_score < 0

    def test_abstain_excluded(self):
        fn = _fn()
        votes = [_v("value", 1), _v("momentum", 0), _v("event", 0)]
        r = fn.evaluate_symbol("000001", votes)
        assert r.approved is True
        assert r.vote_score == pytest.approx(1.0, abs=1e-9)

    def test_all_abstain_reject(self):
        fn = _fn()
        votes = [_v("value", 0), _v("momentum", 0), _v("event", 0)]
        r = fn.evaluate_symbol("000001", votes)
        assert r.approved is False
        assert r.vote_score == 0.0

    def test_weighted_majority(self):
        fn = _fn()
        votes = [_v("value", -1), _v("momentum", 1), _v("event", 1),
                 _v("c034_inference", 1), _v("c036_synergy", 1)]
        r = fn.evaluate_symbol("000001", votes)
        # -0.30 + 0.25 + 0.20 + 0.10 + 0.10 = +0.35 > 0
        assert r.approved is True
        assert r.vote_score > 0

    def test_veto_market_state(self):
        fn = _fn()
        votes = [_v("value", 1), _v("momentum", 1), _v("event", 1)]
        ms = MarketStateClearance(allow_buy=False, state_label="extreme")
        r = fn.evaluate_symbol("000001", votes, market_state=ms)
        assert r.vetoed is True
        assert r.approved is False

    def test_veto_none_degraded(self):
        fn = _fn()
        votes = [_v("value", 1), _v("momentum", 1), _v("event", 1)]
        r = fn.evaluate_symbol("000001", votes, market_state=None)
        assert r.vetoed is False
        assert r.degraded is True


class TestRunFunnel:
    def test_kept_subset(self):
        fn = _fn()
        votes = {
            "000001": [_v("value", 1), _v("momentum", 1), _v("event", 1)],
            "000002": [_v("value", -1), _v("momentum", -1), _v("event", -1)],
        }
        r = fn.run(["000001", "000002"], votes)
        assert set(r.kept) == {"000001"}
        assert "000002" in r.excluded

    def test_no_votes_excluded(self):
        fn = _fn()
        r = fn.run(["000001"], {})
        assert "000001" in r.excluded
        assert r.excluded["000001"] == "no_votes"

    def test_capacity_truncation(self):
        fn = _fn(CrossVoteConfig(capacity_target=2))
        votes = {
            "a": [_v("value", 1), _v("momentum", 1), _v("event", 1)],
            "b": [_v("value", 1), _v("momentum", 1), _v("event", 0)],
            "c": [_v("value", 1), _v("momentum", 0), _v("event", 0)],
        }
        r = fn.run(["a", "b", "c"], votes)
        assert len(r.kept) == 2
        assert r.kept[0] == "a"

    def test_capacity_sorted_desc(self):
        fn = _fn(CrossVoteConfig(capacity_target=10))
        votes = {
            "low": [_v("value", 1), _v("momentum", -1), _v("event", -1)],
            "high": [_v("value", 1), _v("momentum", 1), _v("event", 1)],
        }
        r = fn.run(["low", "high"], votes)
        assert r.kept[0] == "high"


class TestFailClosed:
    def test_unknown_voter(self):
        with pytest.raises(ValueError):
            _v("no_such_voter", 1)

    def test_duplicate_voter(self):
        fn = _fn()
        votes = [_v("value", 1), _v("value", -1)]
        with pytest.raises(ValueError):
            fn.evaluate_symbol("000001", votes)

    def test_invalid_vote_value(self):
        with pytest.raises(ValueError):
            _v("value", 2)

    def test_zero_capacity(self):
        with pytest.raises(ValueError):
            CrossVoteConfig(capacity_target=0)

    def test_empty_symbol(self):
        fn = _fn()
        with pytest.raises(ValueError):
            fn.evaluate_symbol("", [_v("value", 1)])


class TestFrozenAndJson:
    def test_frozen(self):
        v = _v("value", 1)
        with pytest.raises(dataclasses.FrozenInstanceError):
            v.vote = -1

    def test_json(self):
        v = _v("value", 1)
        assert json.dumps(dataclasses.asdict(v))
