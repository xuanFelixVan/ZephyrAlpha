# [BLUEPRINT] MOD-E2E-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""25号memo §3.7#7 MultifactorPITBacktestFramework（注入式骨架）测试。

覆盖：5 层 PIT 断言（通过/违规抛错各层）+ 主循环（INIT→HOLD→TIME 保底/
DRIFT_CRITICAL 强制换仓/数据缺失 skip/合成方法记录）。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

mod = pytest.importorskip("zephyr.factor.analysis.multifactor_pit_backtest")

BacktestDayRecord = mod.BacktestDayRecord
MultifactorPITBacktestFramework = mod.MultifactorPITBacktestFramework
PITViolationError = mod.PITViolationError
assert_covariance_pit = mod.assert_covariance_pit
assert_factor_pit = mod.assert_factor_pit
assert_ic_weight_pit = mod.assert_ic_weight_pit
assert_industry_pit = mod.assert_industry_pit

D0 = pd.Timestamp("2026-08-20")


class TestPITAssertions:
    def test_factor_pit_pass_and_fail(self):
        assert_factor_pit(D0, D0)  # AS OF JOIN 允许同日
        assert_factor_pit(D0 - pd.Timedelta(days=1), D0)
        with pytest.raises(PITViolationError):
            assert_factor_pit(D0 + pd.Timedelta(days=1), D0)

    def test_ic_weight_pit_strict_t_minus_1(self):
        assert_ic_weight_pit(D0 - pd.Timedelta(days=1), D0)
        with pytest.raises(PITViolationError):
            assert_ic_weight_pit(D0, D0)  # t 日 IC 算 t 日权重=未来函数

    def test_covariance_pit_strict(self):
        assert_covariance_pit(D0 - pd.Timedelta(days=1), D0)
        with pytest.raises(PITViolationError):
            assert_covariance_pit(D0, D0)

    def test_industry_pit_as_of_join(self):
        assert_industry_pit(D0, D0)
        with pytest.raises(PITViolationError):
            assert_industry_pit(D0 + pd.Timedelta(days=1), D0)


def _framework(dates, **overrides):
    """构造全注入最小可用框架。"""
    idx = pd.RangeIndex(5)
    defaults = dict(
        load_factors=lambda d: (
            {"f1": pd.Series(np.arange(5.0), index=idx), "f2": pd.Series(np.arange(5.0) * 2, index=idx)},
            d,
        ),
        load_ic_history=lambda d, w: (
            {"f1": [0.05] * 30, "f2": [0.03] * 30},
            d - pd.Timedelta(days=1),
        ),
        load_covariance=lambda d, w: (np.eye(2), d - pd.Timedelta(days=1)),
        load_industry=lambda d: ({"A": "银行"}, d),
        optimize_fn=lambda signal, cov, ind: {"A": 0.5, "B": 0.5},
        rebalance_fn=lambda days, drift, rank: "TIME" if days >= 5 else "HOLD",
        drift_monitor_fn=lambda cur, tgt: ([], 0),
    )
    defaults.update(overrides)
    return MultifactorPITBacktestFramework(**defaults)


class TestRunBacktest:
    def test_init_then_hold_then_time(self):
        dates = pd.date_range("2026-08-10", periods=7, freq="D")
        recs = _framework(dates).run_backtest(list(dates))
        assert recs[0].trigger == "INIT"  # 首次建仓
        assert recs[1].trigger == "HOLD"
        assert all(r.method == "ic_weighted" for r in recs)
        # INIT 后 days_since_last 累积到 5 → TIME 保底
        assert any(r.trigger == "TIME" for r in recs)

    def test_pit_violation_propagates(self):
        dates = pd.date_range("2026-08-10", periods=3, freq="D")
        fw = _framework(dates, load_factors=lambda d: ({"f1": pd.Series([1.0])}, d + pd.Timedelta(days=1)))  # 未来因子
        with pytest.raises(PITViolationError):
            fw.run_backtest(list(dates))

    def test_ic_lookahead_propagates(self):
        dates = pd.date_range("2026-08-10", periods=3, freq="D")
        fw = _framework(dates, load_ic_history=lambda d, w: ({"f1": [0.05] * 30}, d))
        with pytest.raises(PITViolationError):
            fw.run_backtest(list(dates))

    def test_missing_factors_skipped(self):
        dates = pd.date_range("2026-08-10", periods=3, freq="D")
        fw = _framework(dates, load_factors=lambda d: ({}, d))
        recs = fw.run_backtest(list(dates))
        assert all(r.skipped for r in recs)

    def test_drift_critical_forces_rebalance(self):
        dates = pd.date_range("2026-08-10", periods=3, freq="D")
        fw = _framework(dates, drift_monitor_fn=lambda cur, tgt: (["x"], 1))
        recs = fw.run_backtest(list(dates))
        assert recs[1].trigger == "DRIFT_CRITICAL"  # HOLD 日 critical→强制换仓
        assert recs[1].drift_alerts == 1

    def test_no_optional_callbacks(self):
        # 最小骨架：仅因子+IC 两回调（协方差/行业/优化/触发/监控全缺省）
        dates = pd.date_range("2026-08-10", periods=7, freq="D")
        idx = pd.RangeIndex(3)
        fw = MultifactorPITBacktestFramework(
            load_factors=lambda d: ({"f1": pd.Series([1.0, 2.0, 3.0], index=idx)}, d),
            load_ic_history=lambda d, w: ({"f1": [0.05] * 30}, d - pd.Timedelta(days=1)),
        )
        recs = fw.run_backtest(list(dates))
        assert recs[0].trigger == "INIT"
        assert any(r.trigger == "TIME" for r in recs)  # 缺省 5 日保底
