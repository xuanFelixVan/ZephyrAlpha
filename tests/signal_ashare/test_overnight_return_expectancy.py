# [A_test] module_id: MOD-SIG-107 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-107 | docs/03_modules/_domain_signal/overnight_return_expectancy/blueprint.md
# [MODULE] tests.signal_ashare.test_overnight_return_expectancy
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.overnight_return_expectancy

"""隔夜收益预测与开仓期望值（MOD-SIG-107，B10-01464）施工验证测试。

覆盖：期望值公式、E>0.5% 边界、盈亏比>1.5（含 E跌=0 退化）、成本优势>2ATR
（含 cost=None 降级）、踏空成本量化、多门槛归因、非法输入 fail-closed、
frozen/JSON 契约。
全程内存合成数据，无 DB。
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.overnight_return_expectancy import (
    EntryCostContext,
    ExpectancyConfig,
    ExpectancyDecision,
    OvernightForecast,
    OvernightReturnExpectancy,
)


def _eval(forecast, cost=None, **kw) -> ExpectancyDecision:
    return OvernightReturnExpectancy(ExpectancyConfig()).evaluate(forecast, cost, **kw)


class TestExpectancyFormula:
    def test_basic(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.02, e_down_pct=0.01)
        d = _eval(f)
        assert d.expectancy_pct == pytest.approx(0.7 * 0.02 - 0.3 * 0.01, abs=1e-6)

    def test_negative_expectancy(self):
        f = OvernightForecast(p_up=0.4, e_up_pct=0.01, e_down_pct=0.02)
        d = _eval(f)
        assert d.expectancy_pct < 0

    def test_zero_down(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.02, e_down_pct=0.0)
        d = _eval(f)
        assert d.expectancy_pct == pytest.approx(0.7 * 0.02, abs=1e-6)


class TestThresholds:
    def test_pass_all(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.02, e_down_pct=0.005)
        cost = EntryCostContext(entry_price=10.0, support_price=9.0, atr14=0.4)
        d = _eval(f, cost)
        assert d.passed is True
        assert d.expectancy_pct > 0.005
        assert d.profit_loss_ratio > 1.5
        assert d.cost_advantage_atr > 2.0

    def test_fail_expectancy(self):
        f = OvernightForecast(p_up=0.51, e_up_pct=0.005, e_down_pct=0.005)
        d = _eval(f)
        assert d.passed is False
        assert "expectancy" in d.reasons.lower()

    def test_fail_profit_loss(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.01, e_down_pct=0.01)
        d = _eval(f)
        assert d.passed is False
        assert "profit_loss" in d.reasons.lower()

    def test_fail_cost_advantage(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.02, e_down_pct=0.005)
        cost = EntryCostContext(entry_price=10.0, support_price=9.8, atr14=0.4)
        d = _eval(f, cost)
        assert d.passed is False
        assert "cost_advantage" in d.reasons.lower()

    def test_cost_none_degraded(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.02, e_down_pct=0.005)
        d = _eval(f, cost=None)
        assert d.passed is True
        assert d.cost_advantage_atr is None
        assert "cost_skipped" in d.notes.lower()


class TestMissedOpportunity:
    def test_quantified(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.02, e_down_pct=0.005)
        d = _eval(f, miss_probability=0.3, expected_miss_gain_pct=0.015)
        assert d.missed_opportunity_cost == pytest.approx(0.3 * 0.015, abs=1e-6)

    def test_default_zero(self):
        f = OvernightForecast(p_up=0.7, e_up_pct=0.02, e_down_pct=0.005)
        d = _eval(f)
        assert d.missed_opportunity_cost == 0.0


class TestFailClosed:
    def test_p_up_out_of_range(self):
        with pytest.raises(ValueError):
            OvernightForecast(p_up=1.1, e_up_pct=0.01, e_down_pct=0.01)

    def test_negative_e_up(self):
        with pytest.raises(ValueError):
            OvernightForecast(p_up=0.5, e_up_pct=-0.01, e_down_pct=0.01)

    def test_non_finite(self):
        with pytest.raises(ValueError):
            OvernightForecast(p_up=float("nan"), e_up_pct=0.01, e_down_pct=0.01)

    def test_zero_atr(self):
        with pytest.raises(ValueError):
            EntryCostContext(entry_price=10.0, support_price=9.0, atr14=0.0)


class TestFrozenAndJson:
    def test_frozen(self):
        f = OvernightForecast(p_up=0.5, e_up_pct=0.01, e_down_pct=0.01)
        with pytest.raises(dataclasses.FrozenInstanceError):
            f.p_up = 0.6

    def test_json(self):
        f = OvernightForecast(p_up=0.5, e_up_pct=0.01, e_down_pct=0.01)
        assert json.dumps(dataclasses.asdict(f))
