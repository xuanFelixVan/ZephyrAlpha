# [A_test] module_id: MOD-GOV_self_budget_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_self_budget_tracker
# [INVARIANTS] usage_ratio in [0,1]; remaining >= 0
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.self_budget_tracker import (
    SelfBudgetStatus,
    SelfBudgetTracker,
)


class TestSelfBudgetTracker:
    def test_instantiation_defaults(self):
        tracker = SelfBudgetTracker()
        status = tracker.status()
        assert isinstance(status, SelfBudgetStatus)
        assert status.tokens_used == 0
        assert status.budget_cap == 50000
        assert status.usage_ratio == 0.0

    def test_instantiation_custom(self):
        tracker = SelfBudgetTracker(daily_cap=100000, efficiency_threshold=0.3)
        status = tracker.status()
        assert status.budget_cap == 100000

    def test_record_usage_useful(self):
        tracker = SelfBudgetTracker()
        tracker.record_usage(tokens=1000, useful=True)
        status = tracker.status()
        assert status.tokens_used == 1000
        assert status.efficiency == 1.0

    def test_record_usage_wasted(self):
        tracker = SelfBudgetTracker()
        tracker.record_usage(tokens=1000, useful=True)
        tracker.record_usage(tokens=500, useful=False)
        status = tracker.status()
        assert status.tokens_used == 1500
        assert status.efficiency < 1.0

    def test_remaining(self):
        tracker = SelfBudgetTracker(daily_cap=10000)
        tracker.record_usage(tokens=3000)
        assert tracker.remaining() == 7000

    def test_remaining_cannot_go_negative(self):
        tracker = SelfBudgetTracker(daily_cap=1000)
        tracker.record_usage(tokens=5000)
        assert tracker.remaining() == 0

    def test_usage_ratio(self):
        tracker = SelfBudgetTracker(daily_cap=10000)
        tracker.record_usage(tokens=2500)
        status = tracker.status()
        assert status.usage_ratio == pytest.approx(0.25)

    def test_should_disable_safeguards(self):
        tracker = SelfBudgetTracker(daily_cap=100000, efficiency_threshold=0.5)
        tracker.record_usage(tokens=5000, useful=True)
        tracker.record_usage(tokens=5000, useful=False)
        tracker.record_usage(tokens=5000, useful=False)
        status = tracker.status()
        if status.efficiency < 0.5 and status.tokens_used > 1000:
            assert status.should_disable_safeguards is True

    def test_advice_high_usage(self):
        tracker = SelfBudgetTracker(daily_cap=1000)
        tracker.record_usage(tokens=900)
        status = tracker.status()
        assert "80%" in status.advice or "自预算" in status.advice

    def test_advice_normal(self):
        tracker = SelfBudgetTracker(daily_cap=10000)
        tracker.record_usage(tokens=100)
        status = tracker.status()
        assert "正常" in status.advice

    def test_reset_daily(self):
        tracker = SelfBudgetTracker()
        tracker.record_usage(tokens=5000)
        tracker.reset_daily()
        status = tracker.status()
        assert status.tokens_used == 0
        assert tracker.remaining() == 50000

    def test_zero_cap_usage_ratio(self):
        tracker = SelfBudgetTracker(daily_cap=0)
        tracker.record_usage(tokens=100)
        status = tracker.status()
        assert status.usage_ratio == 0.0


class TestBoundaryCases:
    def test_record_zero_tokens(self):
        tracker = SelfBudgetTracker()
        tracker.record_usage(tokens=0)
        status = tracker.status()
        assert status.tokens_used == 0

    def test_efficiency_with_zero_usage(self):
        tracker = SelfBudgetTracker()
        status = tracker.status()
        assert status.efficiency == 0.0

    def test_large_usage(self):
        tracker = SelfBudgetTracker(daily_cap=1000)
        tracker.record_usage(tokens=999999)
        status = tracker.status()
        assert status.usage_ratio > 1.0 or tracker.remaining() == 0
