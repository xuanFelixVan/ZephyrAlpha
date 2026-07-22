# [A_test] module_id: MOD-GOV_think_time_model | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_think_time_model
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_think_time_model.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.context_governance.think_time_model import ThinkTimeModel, ThinkTimeSnapshot


class TestThinkTimeModelInit:
    def test_default_init(self):
        model = ThinkTimeModel()
        assert model.average_tps() == 0.0
        assert model.average_chunk_latency() == 0.0

    def test_recent_snapshots_empty(self):
        model = ThinkTimeModel()
        assert model.recent_snapshots() == []


class TestRecordThinkSegment:
    def test_record_returns_snapshot(self):
        model = ThinkTimeModel()
        snap = model.record_think_segment(elapsed=2.0, tokens=100, tier="premium")
        assert isinstance(snap, ThinkTimeSnapshot)
        assert snap.tokens_per_second == pytest.approx(50.0)
        assert snap.tier == "premium"

    def test_record_zero_elapsed(self):
        model = ThinkTimeModel()
        snap = model.record_think_segment(elapsed=0.0, tokens=100, tier="basic")
        assert snap.tokens_per_second == 0.0

    def test_record_accumulates_thinking_time(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=1.0, tokens=50, tier="a")
        model.record_think_segment(elapsed=2.0, tokens=100, tier="b")
        assert model.average_tps() == pytest.approx(50.0)


class TestRecordChunkLatency:
    def test_record_chunk_latency(self):
        model = ThinkTimeModel()
        model.record_chunk_latency(0.1)
        model.record_chunk_latency(0.3)
        assert model.average_chunk_latency() == pytest.approx(0.2)

    def test_record_chunk_latency_empty(self):
        model = ThinkTimeModel()
        assert model.average_chunk_latency() == 0.0


class TestEstimateNextDuration:
    def test_estimate_with_history(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=1.0, tokens=100, tier="a")
        model.record_think_segment(elapsed=1.0, tokens=100, tier="a")
        est = model.estimate_next_duration(expected_tokens=500)
        assert est == pytest.approx(5.0)

    def test_estimate_without_history(self):
        model = ThinkTimeModel()
        est = model.estimate_next_duration(expected_tokens=500)
        assert est == pytest.approx(50.0)

    def test_estimate_zero_expected_tokens(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=1.0, tokens=100, tier="a")
        est = model.estimate_next_duration(expected_tokens=0)
        assert est == 0.0


class TestAverageTps:
    def test_average_tps_multiple_segments(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=1.0, tokens=100, tier="a")
        model.record_think_segment(elapsed=2.0, tokens=100, tier="b")
        assert model.average_tps() == pytest.approx(75.0)

    def test_average_tps_empty(self):
        model = ThinkTimeModel()
        assert model.average_tps() == 0.0


class TestTotalThinkingCost:
    def test_total_thinking_cost(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=5.0, tokens=100, tier="a")
        cost = model.total_thinking_cost(cost_per_second=0.02)
        assert cost == pytest.approx(0.1)

    def test_total_thinking_cost_zero_rate(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=5.0, tokens=100, tier="a")
        assert model.total_thinking_cost(cost_per_second=0.0) == 0.0


class TestThinkingRatio:
    def test_thinking_ratio(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=3.0, tokens=100, tier="a")
        ratio = model.thinking_ratio(total_wall_time=10.0)
        assert ratio == pytest.approx(0.3)

    def test_thinking_ratio_capped_at_one(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=20.0, tokens=100, tier="a")
        ratio = model.thinking_ratio(total_wall_time=10.0)
        assert ratio == 1.0

    def test_thinking_ratio_zero_wall_time(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=5.0, tokens=100, tier="a")
        assert model.thinking_ratio(total_wall_time=0.0) == 0.0


class TestRecentSnapshots:
    def test_recent_snapshots_returns_last_n(self):
        model = ThinkTimeModel()
        for i in range(15):
            model.record_think_segment(elapsed=1.0, tokens=100, tier="a")
        snaps = model.recent_snapshots(n=5)
        assert len(snaps) == 5

    def test_recent_snapshots_fewer_than_n(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=1.0, tokens=100, tier="a")
        snaps = model.recent_snapshots(n=10)
        assert len(snaps) == 1


class TestReset:
    def test_reset_clears_all(self):
        model = ThinkTimeModel()
        model.record_think_segment(elapsed=1.0, tokens=100, tier="a")
        model.record_chunk_latency(0.5)
        model.reset()
        assert model.average_tps() == 0.0
        assert model.average_chunk_latency() == 0.0
        assert model.recent_snapshots() == []
