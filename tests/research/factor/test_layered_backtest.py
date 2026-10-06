# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""D-FACTOR-ANA-06 分层回测测试——纯函数模块（无 IO 依赖）。

覆盖：
- layered_returns: 空输入 / 单截面分层 / 层间收益单调 / 数据不足
- compute_layer_spread: 多空收益差计算 / 数据不足截面跳过 / 全部不足返回空
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

layered_backtest = pytest.importorskip("zephyr.factor.analysis.layered_backtest")

layered_returns = layered_backtest.layered_returns
compute_layer_spread = layered_backtest.compute_layer_spread


class TestLayeredReturns:
    def test_empty_input(self):
        result = layered_returns(
            pd.Series([], dtype=float),
            pd.Series([], dtype=float),
            n_layers=5,
        )
        assert result.empty

    def test_single_cross_section_layering(self):
        # 5 symbols, 5 layers → each layer has 1 symbol
        fv = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], index=list("ABCDE"))
        fr = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], index=list("ABCDE"))
        result = layered_returns(fv, fr, n_layers=5)
        assert len(result) == 5
        assert list(result.columns) == ["avg_return", "count"]
        # layer 0 = 最低因子值 (A), layer 4 = 最高 (E)
        assert result.loc[0, "avg_return"] == 10.0
        assert result.loc[4, "avg_return"] == 50.0
        # 每层 1 个标的
        assert (result["count"] == 1).all()

    def test_monotonic_returns(self):
        # 因子值与收益同向递增 → 各层平均收益单调递增
        fv = pd.Series(
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            index=list("ABCDEFGHIJ"),
        )
        fr = pd.Series(
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            index=list("ABCDEFGHIJ"),
        )
        result = layered_returns(fv, fr, n_layers=5)
        # 10 symbols, 5 layers → 2 per layer
        assert len(result) == 5
        avg_returns = result["avg_return"].tolist()
        assert avg_returns == sorted(avg_returns)
        # layer 0 = A,B → mean(1,2)=1.5; layer 4 = I,J → mean(9,10)=9.5
        assert abs(avg_returns[0] - 1.5) < 1e-10
        assert abs(avg_returns[-1] - 9.5) < 1e-10

    def test_insufficient_data_returns_empty(self):
        # 标的数 < n_layers → 数据不足返回空
        fv = pd.Series([1.0, 2.0, 3.0], index=list("ABC"))
        fr = pd.Series([10.0, 20.0, 30.0], index=list("ABC"))
        result = layered_returns(fv, fr, n_layers=5)
        assert result.empty

    def test_nan_dropped(self):
        # 含 NaN 的标的被剔除
        fv = pd.Series([1.0, 2.0, float("nan"), 4.0, 5.0], index=list("ABCDE"))
        fr = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], index=list("ABCDE"))
        result = layered_returns(fv, fr, n_layers=4)
        # 去掉 NaN 后 4 个标的，4 层各 1 个
        assert len(result) == 4

    def test_count_column(self):
        fv = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], index=list("ABCDEF"))
        fr = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, 60.0], index=list("ABCDEF"))
        result = layered_returns(fv, fr, n_layers=3)
        # 6 symbols, 3 layers → 2 per layer
        assert len(result) == 3
        assert (result["count"] == 2).all()


class TestComputeLayerSpread:
    def test_normal_spread(self):
        # 2 个日期，每日期 5 标的 5 层
        dates = [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-02")]
        factor_panel = pd.DataFrame(
            {
                "A": [1.0, 1.0],
                "B": [2.0, 2.0],
                "C": [3.0, 3.0],
                "D": [4.0, 4.0],
                "E": [5.0, 5.0],
            },
            index=dates,
        )
        return_panel = pd.DataFrame(
            {
                "A": [10.0, 5.0],
                "B": [20.0, 10.0],
                "C": [30.0, 15.0],
                "D": [40.0, 20.0],
                "E": [50.0, 25.0],
            },
            index=dates,
        )
        spreads = compute_layer_spread(factor_panel, return_panel, n_layers=5)
        assert len(spreads) == 2
        assert spreads.name == "layer_spread"
        # 日期1: 最高层50 - 最低层10 = 40
        assert abs(spreads.iloc[0] - 40.0) < 1e-10
        # 日期2: 最高层25 - 最低层5 = 20
        assert abs(spreads.iloc[1] - 20.0) < 1e-10

    def test_insufficient_dates_skipped(self):
        # 日期1 有足够标的，日期2 标的不足 → 只返回日期1
        dates = [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-02")]
        factor_panel = pd.DataFrame(
            {
                "A": [1.0, 1.0],
                "B": [2.0, 2.0],
                "C": [3.0, 3.0],
                "D": [4.0, 4.0],
                "E": [5.0, 5.0],
            },
            index=dates,
        )
        return_panel = pd.DataFrame(
            {
                "A": [10.0, 10.0],
                "B": [20.0, 20.0],
                "C": [30.0, 30.0],
                "D": [40.0, float("nan")],
                "E": [50.0, float("nan")],
            },
            index=dates,
        )
        # 日期2: 去掉 NaN 后只剩 A,B,C 3 个标的 < 5 层 → 跳过
        spreads = compute_layer_spread(factor_panel, return_panel, n_layers=5)
        assert len(spreads) == 1
        assert spreads.index[0] == pd.Timestamp("2026-01-01")

    def test_all_insufficient_returns_empty(self):
        # 所有日期标的都不足 → 空 Series
        dates = [pd.Timestamp("2026-01-01")]
        factor_panel = pd.DataFrame(
            {"A": [1.0], "B": [2.0], "C": [3.0]},
            index=dates,
        )
        return_panel = pd.DataFrame(
            {"A": [10.0], "B": [20.0], "C": [30.0]},
            index=dates,
        )
        spreads = compute_layer_spread(factor_panel, return_panel, n_layers=5)
        assert spreads.empty

    def test_empty_panels(self):
        spreads = compute_layer_spread(
            pd.DataFrame(),
            pd.DataFrame(),
            n_layers=5,
        )
        assert spreads.empty
        assert spreads.name == "layer_spread"
