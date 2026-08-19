# [TTL] permanent
"""25号memo §3.7#6 RebalanceTrigger（含 Inaction Cost）测试。

覆盖：WAIT/TIME/DRIFT/SIGNAL/HOLD 五分支 + 成本门控通过/拦截 +
Inaction Cost 公式 + 优先级（最短间隔>保底>漂移>信号）。
"""
from __future__ import annotations

import pytest

mod = pytest.importorskip("zephyr.pf_core.core.multifactor_rebalance_trigger")

RebalanceTriggerParams = mod.RebalanceTriggerParams
RebalanceTriggerType = mod.RebalanceTriggerType
should_rebalance = mod.should_rebalance


class TestTimeWindow:
    def test_wait_below_min_interval(self):
        d = should_rebalance(days_since_last=2, weight_drift=0.5, top30_rank_change=30)
        assert d.trigger is RebalanceTriggerType.WAIT
        assert not d.should_rebalance

    def test_time_forced_at_max_window(self):
        d = should_rebalance(days_since_last=5)
        assert d.trigger is RebalanceTriggerType.TIME
        assert d.should_rebalance
        assert not d.cost_gate_applied  # 保底不受成本门控

    def test_time_forced_beyond_max_window(self):
        d = should_rebalance(days_since_last=9)
        assert d.trigger is RebalanceTriggerType.TIME


class TestDriftTrigger:
    def test_drift_triggered_when_worthwhile(self):
        # days=3, drift=0.20: inaction=0.20*0.0005*2=0.0002, action=0.004*0.20=0.0008
        # → inaction<action → HOLD（等保底）
        d = should_rebalance(days_since_last=3, weight_drift=0.20)
        assert d.trigger is RebalanceTriggerType.HOLD
        assert not d.should_rebalance
        assert d.inaction_cost == pytest.approx(0.0002)
        assert d.action_cost == pytest.approx(0.0008)

    def test_drift_blocked_near_window_end(self):
        # days=4, drift=0.20: inaction=0.20*0.0005*1=0.0001 < action 0.0008 → 等保底
        d = should_rebalance(days_since_last=4, weight_drift=0.20)
        assert d.trigger is RebalanceTriggerType.HOLD
        assert "保底" in d.reason

    def test_drift_triggered_cost_unaware(self):
        p = RebalanceTriggerParams(cost_aware=False)
        d = should_rebalance(days_since_last=3, weight_drift=0.20, params=p)
        assert d.trigger is RebalanceTriggerType.DRIFT
        assert d.should_rebalance

    def test_drift_below_threshold_no_trigger(self):
        d = should_rebalance(days_since_last=3, weight_drift=0.14)
        assert d.trigger is RebalanceTriggerType.HOLD


class TestSignalTrigger:
    def test_signal_triggered(self):
        p = RebalanceTriggerParams(cost_aware=False)
        d = should_rebalance(days_since_last=3, weight_drift=0.0,
                             top30_rank_change=12.0, params=p)
        assert d.trigger is RebalanceTriggerType.SIGNAL
        assert d.rank_change_score == pytest.approx(360.0)  # 12×30 归一化

    def test_signal_below_threshold(self):
        d = should_rebalance(days_since_last=3, top30_rank_change=9.0)
        assert d.trigger is RebalanceTriggerType.HOLD

    def test_signal_cost_gate_blocks(self):
        # days=4: expected_days=1 → inaction=0 漂移 → 成本门控拦截
        d = should_rebalance(days_since_last=4, weight_drift=0.0,
                             top30_rank_change=15.0)
        assert d.trigger is RebalanceTriggerType.HOLD
        assert "成本门控" in d.reason


class TestPriorityAndEdge:
    def test_hold_default(self):
        d = should_rebalance(days_since_last=3)
        assert d.trigger is RebalanceTriggerType.HOLD
        assert not d.should_rebalance

    def test_none_inputs_treated_as_zero(self):
        d = should_rebalance(days_since_last=3, weight_drift=None, top30_rank_change=None)
        assert d.trigger is RebalanceTriggerType.HOLD

    def test_min_interval_overrides_everything(self):
        # 漂移/排名双超阈仍 WAIT
        d = should_rebalance(days_since_last=1, weight_drift=0.9, top30_rank_change=99)
        assert d.trigger is RebalanceTriggerType.WAIT

    def test_inaction_cost_formula(self):
        # 单元公式验证：drift×daily_alpha×expected_days vs 0.4%×drift
        p = RebalanceTriggerParams()
        ok, ina, act = mod._is_rebalance_worthwhile(0.30, 3, p)
        assert ina == pytest.approx(0.30 * 0.0005 * 2)
        assert act == pytest.approx(0.004 * 0.30)
        assert not ok  # 0.0003 < 0.0012
