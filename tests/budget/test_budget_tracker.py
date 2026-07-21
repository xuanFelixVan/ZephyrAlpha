# [A_test] module_id: MOD-GOV_budget_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_budget_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_budget_tracker.py
# [TTL] task_bound

from __future__ import annotations

import json
import time

import pytest

from zephyr.governance.ops_governance.budget_models import BudgetDimension
from zephyr.governance.ops_governance.budget_tracker import (
    BudgetSnapshot,
    BudgetTracker,
    TrackerScope,
    TrackerSummary,
)


class TestTrackerScope:
    def test_all_members(self):
        assert TrackerScope.GLOBAL.value == "global"
        assert TrackerScope.SESSION.value == "session"
        assert TrackerScope.TASK.value == "task"
        assert TrackerScope.TURN.value == "turn"
        assert TrackerScope.REQUEST.value == "request"

    def test_member_count(self):
        assert len(TrackerScope) == 5


class TestBudgetSnapshot:
    def test_defaults(self):
        snap = BudgetSnapshot(scope=TrackerScope.SESSION, scope_id="s-1")
        assert snap.tokens_in == 0
        assert snap.tokens_out == 0
        assert snap.cost_usd == 0.0
        assert snap.wall_time_seconds == 0.0
        assert snap.ttl is None

    def test_total_tokens(self):
        snap = BudgetSnapshot(
            scope=TrackerScope.REQUEST,
            scope_id="r-1",
            tokens_in=100,
            tokens_out=50,
        )
        assert snap.total_tokens == 150

    def test_is_expired_no_ttl(self):
        snap = BudgetSnapshot(scope=TrackerScope.SESSION, scope_id="s-1")
        assert snap.is_expired() is False

    def test_is_expired_with_ttl(self):
        snap = BudgetSnapshot(
            scope=TrackerScope.REQUEST,
            scope_id="r-1",
            created_at=time.time() - 600,
            ttl=300,
        )
        assert snap.is_expired() is True

    def test_is_expired_not_yet(self):
        snap = BudgetSnapshot(
            scope=TrackerScope.REQUEST,
            scope_id="r-1",
            created_at=time.time(),
            ttl=300,
        )
        assert snap.is_expired() is False

    def test_to_dict(self):
        snap = BudgetSnapshot(
            scope=TrackerScope.SESSION,
            scope_id="s-1",
            tokens_in=100,
            tokens_out=50,
            cost_usd=0.05,
        )
        d = snap.to_dict()
        assert d["scope"] == "session"
        assert d["scope_id"] == "s-1"
        assert d["total_tokens"] == 150
        assert d["cost_usd"] == pytest.approx(0.05)


class TestTrackerSummary:
    def test_defaults(self):
        ts = TrackerSummary()
        assert ts.total_tokens == 0
        assert ts.total_cost_usd == 0.0
        assert ts.request_count == 0
        assert ts.active_sessions == 0

    def test_usage_ratio_zero_limit(self):
        ts = TrackerSummary()
        assert ts.usage_ratio(BudgetDimension.TOKEN, 0) == 1.0

    def test_usage_ratio_normal(self):
        ts = TrackerSummary(dimension_usage={BudgetDimension.TOKEN.value: 50.0})
        assert ts.usage_ratio(BudgetDimension.TOKEN, 100) == pytest.approx(0.5)

    def test_usage_ratio_capped(self):
        ts = TrackerSummary(dimension_usage={BudgetDimension.TOKEN.value: 200.0})
        assert ts.usage_ratio(BudgetDimension.TOKEN, 100) == 1.0


class TestBudgetTracker:
    def test_instantiation(self):
        bt = BudgetTracker()
        s = bt.summarize()
        assert s.total_tokens == 0

    def test_open_scope(self):
        bt = BudgetTracker()
        snap = bt.open_scope(TrackerScope.SESSION, "sess-1")
        assert snap.scope == TrackerScope.SESSION
        assert snap.scope_id == "sess-1"

    def test_open_scope_idempotent(self):
        bt = BudgetTracker()
        snap1 = bt.open_scope(TrackerScope.SESSION, "sess-1")
        snap2 = bt.open_scope(TrackerScope.SESSION, "sess-1")
        assert snap1 is snap2

    def test_record_request(self):
        bt = BudgetTracker()
        snap = bt.record_request(
            TrackerScope.SESSION,
            "sess-1",
            tokens_in=100,
            tokens_out=50,
            cost_usd=0.05,
            wall_time=1.5,
        )
        assert snap.tokens_in == 100
        assert snap.tokens_out == 50
        assert snap.cost_usd == pytest.approx(0.05)

    def test_record_request_accumulates(self):
        bt = BudgetTracker()
        bt.record_request(TrackerScope.SESSION, "sess-1", tokens_in=100, tokens_out=50)
        snap = bt.record_request(TrackerScope.SESSION, "sess-1", tokens_in=200, tokens_out=100)
        assert snap.tokens_in == 300
        assert snap.tokens_out == 150

    def test_record_turn(self):
        bt = BudgetTracker()
        s1 = BudgetSnapshot(
            scope=TrackerScope.REQUEST,
            scope_id="r-1",
            tokens_in=100,
            tokens_out=50,
            cost_usd=0.01,
            wall_time_seconds=1.0,
        )
        s2 = BudgetSnapshot(
            scope=TrackerScope.REQUEST,
            scope_id="r-2",
            tokens_in=200,
            tokens_out=100,
            cost_usd=0.02,
            wall_time_seconds=2.0,
        )
        turn = bt.record_turn("turn-1", [s1, s2])
        assert turn.tokens_in == 300
        assert turn.tokens_out == 150
        assert turn.cost_usd == pytest.approx(0.03)

    def test_record_turn_empty_snapshots(self):
        bt = BudgetTracker()
        turn = bt.record_turn("turn-empty", [])
        assert turn.tokens_in == 0
        assert turn.tokens_out == 0

    def test_get_snapshot(self):
        bt = BudgetTracker()
        bt.open_scope(TrackerScope.SESSION, "sess-1")
        snap = bt.get_snapshot(TrackerScope.SESSION, "sess-1")
        assert snap is not None
        assert snap.scope_id == "sess-1"

    def test_get_snapshot_nonexistent(self):
        bt = BudgetTracker()
        assert bt.get_snapshot(TrackerScope.SESSION, "nope") is None

    def test_summarize(self):
        bt = BudgetTracker()
        bt.record_request(TrackerScope.SESSION, "sess-1", tokens_in=100, tokens_out=50, cost_usd=0.05)
        s = bt.summarize()
        assert s.total_tokens == 150
        assert s.total_cost_usd == pytest.approx(0.05)
        assert s.active_sessions == 1

    def test_dimension_usage(self):
        bt = BudgetTracker()
        bt.record_request(TrackerScope.SESSION, "sess-1", tokens_in=100, tokens_out=50, cost_usd=0.05)
        assert bt.dimension_usage(BudgetDimension.TOKEN) == 150
        assert bt.dimension_usage(BudgetDimension.COST) == pytest.approx(0.05)

    def test_elapsed(self):
        bt = BudgetTracker()
        e = bt.elapsed()
        assert e >= 0

    def test_dump(self):
        bt = BudgetTracker()
        bt.record_request(TrackerScope.SESSION, "sess-1", tokens_in=100, tokens_out=50)
        data = json.loads(bt.dump())
        assert "summary" in data
        assert "snapshots" in data
        assert "elapsed" in data

    def test_clear(self):
        bt = BudgetTracker()
        bt.record_request(TrackerScope.SESSION, "sess-1", tokens_in=100, tokens_out=50)
        bt.clear()
        s = bt.summarize()
        assert s.total_tokens == 0

    def test_ttl_assignment(self):
        bt = BudgetTracker()
        snap = bt.open_scope(TrackerScope.REQUEST, "r-1")
        assert snap.ttl == 300
        snap2 = bt.open_scope(TrackerScope.SESSION, "s-1")
        assert snap2.ttl == 86400

    def test_global_scope_no_ttl(self):
        bt = BudgetTracker()
        snap = bt.open_scope(TrackerScope.GLOBAL, "g-1")
        assert snap.ttl is None
