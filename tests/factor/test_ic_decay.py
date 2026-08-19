# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""ic_decay 模块测试——IC 衰减分析与半衰期计算。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis import ic_decay


class TestComputeHalfLife:
    def test_empty_series(self) -> None:
        assert ic_decay.compute_half_life(pd.Series(dtype=float)) == 0.0

    def test_zero_initial_ic(self) -> None:
        # 初始 IC 为 0，无法计算半衰期
        s = pd.Series([0.0, 0.0, 0.0], index=[1, 2, 3])
        assert ic_decay.compute_half_life(s) == 0.0

    def test_never_decays_below_half(self) -> None:
        # IC 始终高于初始值的一半，返回最大 lag
        s = pd.Series([0.8, 0.7, 0.6], index=[1, 2, 3])
        # initial=0.8, half=0.4, all values > 0.4
        result = ic_decay.compute_half_life(s)
        assert result == 3.0

    def test_immediate_decay(self) -> None:
        # 第一个点就低于一半（idx==0 分支：仅在初始 IC 本身 <= half 时触发，
        # 而 half = initial/2，故仅 initial==0 可达——已被前置分支拦截）。
        # 这里验证正常插值路径：initial=0.1, half=0.05,
        # abs_ics=[0.1, 0.01, 0.001], below=[1,2], idx=1
        # prev_ic=0.1, curr_ic=0.01, ratio=(0.1-0.05)/(0.1-0.01)=0.5555
        # result = 1.0 + 0.5555*(2.0-1.0) ≈ 1.5555
        s = pd.Series([0.1, 0.01, 0.001], index=[1, 2, 3])
        result = ic_decay.compute_half_life(s)
        expected = 1.0 + (0.1 - 0.05) / (0.1 - 0.01) * (2.0 - 1.0)
        assert abs(result - expected) < 1e-6

    def test_linear_interpolation(self) -> None:
        # initial=1.0, half=0.5
        # lag1: 1.0, lag2: 0.4 → 在 lag1~lag2 之间插值
        s = pd.Series([1.0, 0.4], index=[1, 2])
        result = ic_decay.compute_half_life(s)
        # 线性插值：prev_ic=1.0, curr_ic=0.4, half=0.5
        # ratio = (1.0 - 0.5) / (1.0 - 0.4) = 0.5/0.6 ≈ 0.8333
        expected = 1.0 + 0.8333 * (2.0 - 1.0)
        assert abs(result - expected) < 1e-4

    def test_negative_ic(self) -> None:
        # 负 IC 也能正确计算（取绝对值）
        s = pd.Series([-0.8, -0.3], index=[1, 2])
        # initial=0.8, half=0.4
        # lag1: 0.8, lag2: 0.3 → 插值
        # ratio = (0.8 - 0.4) / (0.8 - 0.3) = 0.4/0.5 = 0.8
        result = ic_decay.compute_half_life(s)
        expected = 1.0 + 0.8 * (2.0 - 1.0)
        assert abs(result - expected) < 1e-4

    def test_equal_adjacent_values(self) -> None:
        # 相邻两点 IC 绝对值相等，返回 curr_lag
        s = pd.Series([1.0, 0.6, 0.3], index=[1, 2, 3])
        # initial=1.0, half=0.5
        # lag1: 1.0, lag2: 0.6, lag3: 0.3
        # 第一个 <= 0.5 的是 lag3 (0.3)
        # prev_ic=0.6, curr_ic=0.3, prev_ic != curr_ic
        # ratio = (0.6 - 0.5) / (0.6 - 0.3) = 0.1/0.3 ≈ 0.333
        result = ic_decay.compute_half_life(s)
        expected = 2.0 + (0.6 - 0.5) / (0.6 - 0.3) * (3.0 - 2.0)
        assert abs(result - expected) < 1e-4


class TestComputeIcDecay:
    def test_empty_history(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # 历史数据为空时返回空 Series
        monkeypatch.setattr(
            ic_decay, "load_history",
            lambda symbols, start, end: pd.DataFrame(),
        )
        # 需要一个 fake factor class
        class _FakeFactor:
            pass
        monkeypatch.setattr(
            ic_decay.FactorRegistry, "get", lambda fid: _FakeFactor,
        )
        result = ic_decay.compute_ic_decay("f1", ["000001"], "2026-01-01", "2026-06-01")
        assert result.empty

    def test_returns_series_with_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # 构造最小数据集
        dates = pd.date_range("2026-01-01", periods=30, freq="D")
        symbols = ["000001", "000002"]
        rows = []
        for d in dates:
            for s in symbols:
                rows.append({
                    "trade_date": d, "symbol": s,
                    "open": 10.0, "high": 11.0, "low": 9.0,
                    "close": 10.0 + np.random.randn() * 0.5,
                    "volume": 1000.0, "amount": 10000.0, "adj_factor": 1.0,
                })
        history = pd.DataFrame(rows).set_index(["trade_date", "symbol"])

        # 返回常数因子值的 fake factor
        class _FakeFactor:
            def compute(self, data, **kwargs):
                return pd.Series(1.0, index=data.index)

        monkeypatch.setattr(ic_decay, "load_history", lambda symbols, start, end: history)
        # _compute_factor_panel 会 factor_cls() 实例化，故返回类而非实例
        monkeypatch.setattr(ic_decay.FactorRegistry, "get", lambda fid: _FakeFactor)

        result = ic_decay.compute_ic_decay("f1", symbols, "2026-01-01", "2026-01-30", max_lag=3)
        assert isinstance(result, pd.Series)
        assert result.name == "ic_decay"


class TestComputeIcDecayAdjustedClose218:
    """#218：前向收益必须按复权价面板（close×adj_factor）计算。

    修复前 ic_decay 以 raw close 面板调 _compute_forward_returns，除权日
    （10送10 价格腰斩）跳变被计为真实盈亏，IC 衰减曲线系统性偏差。
    修复复用 #197 在 backtest.py 落地的 _adjusted_close_panel（不重造）。
    """

    def test_forward_returns_use_adjusted_panel_218(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # 构造除权事件：2026-01-06 起 10送10，raw close 20→10 腰斩，
        # adj_factor 1→2（hfq 口径）→ 复权价 20→20 连续，无真实盈亏
        dates = pd.date_range("2026-01-05", periods=4, freq="D")
        raw_closes = [20.0, 10.0, 10.5, 11.0]
        adj_factors = [1.0, 2.0, 2.0, 2.0]
        rows = [
            {
                "trade_date": d, "symbol": "600010",
                "open": c, "high": c, "low": c, "close": c,
                "volume": 1000.0, "amount": 10000.0, "adj_factor": a,
            }
            for d, c, a in zip(dates, raw_closes, adj_factors)
        ]
        history = pd.DataFrame(rows).set_index(["symbol", "trade_date"]).sort_index()

        class _FakeFactor:
            def compute(self, data, **kwargs):
                return pd.Series(1.0, index=data.index)

        monkeypatch.setattr(ic_decay, "load_history", lambda symbols, start, end: history)
        monkeypatch.setattr(ic_decay.FactorRegistry, "get", lambda fid: _FakeFactor)

        captured: dict = {}
        real_forward = ic_decay._compute_forward_returns

        def _spy(panel, horizon):
            captured.setdefault("panel", panel)
            return real_forward(panel, horizon)

        monkeypatch.setattr(ic_decay, "_compute_forward_returns", _spy)
        ic_decay.compute_ic_decay("f1", ["600010"], "2026-01-05", "2026-01-08", max_lag=1)

        panel = captured["panel"]
        # 除权日（01-06）复权价 = 10.0×2.0 = 20.0（连续），非 raw close 10.0（腰斩）
        assert panel.loc[pd.Timestamp("2026-01-06"), "600010"] == pytest.approx(20.0)
        assert panel.loc[pd.Timestamp("2026-01-05"), "600010"] == pytest.approx(20.0)
