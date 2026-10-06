# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""D-FACTOR-ANA-11 因子优化测试——纯函数模块（无 IO 依赖）。

覆盖：
- optimize_weights: 空输入 / 单因子 / 权重非负且和为1 / 优化失败退化为等权
- evaluate_portfolio: 用权重合成 / 空输入 / 权重归一化
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

factor_optimization = pytest.importorskip("zephyr.factor.analysis.factor_optimization")

optimize_weights = factor_optimization.optimize_weights
evaluate_portfolio = factor_optimization.evaluate_portfolio


def _make_factor_panel(n_dates: int = 6) -> tuple[dict, pd.DataFrame]:
    """构造合成因子面板与前向收益面板。

    factor_values: factor_id → pd.Series(index=date)
    forward_returns: DataFrame(index=date, columns=symbol)
    """
    dates = list(range(n_dates))
    factor_values = {
        "f1": pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0][:n_dates], index=dates),
        "f2": pd.Series([6.0, 5.0, 4.0, 3.0, 2.0, 1.0][:n_dates], index=dates),
    }
    forward_returns = pd.DataFrame(
        {
            "f1": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6][:n_dates],
            "f2": [0.6, 0.5, 0.4, 0.3, 0.2, 0.1][:n_dates],
        },
        index=dates,
    )
    return factor_values, forward_returns


class TestOptimizeWeights:
    def test_empty_input(self):
        result = optimize_weights({}, pd.DataFrame())
        assert result == {}

    def test_single_factor(self):
        fv = {
            "f1": pd.Series([1.0, 2.0, 3.0], index=[0, 1, 2]),
        }
        fr = pd.DataFrame({"f1": [0.1, 0.2, 0.3]}, index=[0, 1, 2])
        result = optimize_weights(fv, fr)
        assert result == {"f1": 1.0}

    def test_weights_non_negative_and_sum_to_one(self):
        fv, fr = _make_factor_panel(n_dates=6)
        result = optimize_weights(fv, fr, objective="max_ir")
        assert set(result.keys()) == {"f1", "f2"}
        # 非负
        for fid, w in result.items():
            assert w >= -1e-6, f"{fid} 权重为负: {w}"
        # 和为 1（允许浮点误差）
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-4

    def test_min_variance_weights_valid(self):
        fv, fr = _make_factor_panel(n_dates=6)
        result = optimize_weights(fv, fr, objective="min_variance")
        assert set(result.keys()) == {"f1", "f2"}
        for fid, w in result.items():
            assert w >= -1e-6, f"{fid} 权重为负: {w}"
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-4

    def test_unknown_objective_degrades_to_equal_weight(self):
        # 未知目标 → 等权兜底
        fv, fr = _make_factor_panel(n_dates=6)
        result = optimize_weights(fv, fr, objective="bogus_objective")
        assert set(result.keys()) == {"f1", "f2"}
        # 等权：各 0.5
        assert abs(result["f1"] - 0.5) < 1e-10
        assert abs(result["f2"] - 0.5) < 1e-10

    def test_three_factors_weights_valid(self):
        dates = list(range(6))
        fv = {
            "f1": pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], index=dates),
            "f2": pd.Series([6.0, 5.0, 4.0, 3.0, 2.0, 1.0], index=dates),
            "f3": pd.Series([2.0, 4.0, 1.0, 5.0, 3.0, 6.0], index=dates),
        }
        fr = pd.DataFrame(
            {
                "f1": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                "f2": [0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
                "f3": [0.3, 0.4, 0.5, 0.6, 0.1, 0.2],
            },
            index=dates,
        )
        result = optimize_weights(fv, fr, objective="max_ir")
        assert set(result.keys()) == {"f1", "f2", "f3"}
        for fid, w in result.items():
            assert w >= -1e-6, f"{fid} 权重为负: {w}"
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-4

    def test_default_objective_from_config(self):
        # 不传 objective → 从配置读取默认 "max_ir"
        fv, fr = _make_factor_panel(n_dates=6)
        result = optimize_weights(fv, fr)
        assert set(result.keys()) == {"f1", "f2"}
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-4


class TestEvaluatePortfolio:
    def test_normal_synthesis(self):
        weights = {"f1": 0.3, "f2": 0.7}
        factor_values = {
            "f1": pd.Series([1.0, 2.0], index=["A", "B"]),
            "f2": pd.Series([3.0, 4.0], index=["A", "B"]),
        }
        result = evaluate_portfolio(weights, factor_values)
        # A: 1*0.3 + 3*0.7 = 2.4; B: 2*0.3 + 4*0.7 = 3.4
        assert len(result) == 2
        assert abs(result.loc["A"] - 2.4) < 1e-10
        assert abs(result.loc["B"] - 3.4) < 1e-10

    def test_empty_weights(self):
        factor_values = {
            "f1": pd.Series([1.0, 2.0], index=["A", "B"]),
        }
        result = evaluate_portfolio({}, factor_values)
        assert result.empty

    def test_empty_factor_values(self):
        result = evaluate_portfolio({"f1": 1.0}, {})
        assert result.empty

    def test_weights_normalized(self):
        # 权重未归一化（和=2）→ 内部归一化后结果与归一化权重一致
        weights = {"f1": 0.6, "f2": 1.4}  # 和 = 2
        factor_values = {
            "f1": pd.Series([1.0, 2.0], index=["A", "B"]),
            "f2": pd.Series([3.0, 4.0], index=["A", "B"]),
        }
        result = evaluate_portfolio(weights, factor_values)
        # 归一化后 f1=0.3, f2=0.7 → 同 test_normal_synthesis
        assert abs(result.loc["A"] - 2.4) < 1e-10
        assert abs(result.loc["B"] - 3.4) < 1e-10

    def test_filter_valid_factors(self):
        # weights 只覆盖部分因子 → 只用有权重的因子
        weights = {"f1": 1.0}
        factor_values = {
            "f1": pd.Series([1.0, 2.0], index=["A", "B"]),
            "f2": pd.Series([3.0, 4.0], index=["A", "B"]),
        }
        result = evaluate_portfolio(weights, factor_values)
        # 仅 f1 有效 → 结果 = f1
        assert abs(result.loc["A"] - 1.0) < 1e-10
        assert abs(result.loc["B"] - 2.0) < 1e-10

    def test_zero_total_weights_degrades_to_equal_weight(self):
        # 权重全 0 → total≈0 → 等权兜底
        weights = {"f1": 0.0, "f2": 0.0}
        factor_values = {
            "f1": pd.Series([1.0, 2.0], index=["A", "B"]),
            "f2": pd.Series([3.0, 4.0], index=["A", "B"]),
        }
        result = evaluate_portfolio(weights, factor_values)
        # 等权 = [(1+3)/2, (2+4)/2] = [2.0, 3.0]
        assert abs(result.loc["A"] - 2.0) < 1e-10
        assert abs(result.loc["B"] - 3.0) < 1e-10

    def test_roundtrip_with_optimize(self):
        # optimize_weights 的结果可传入 evaluate_portfolio
        fv, fr = _make_factor_panel(n_dates=6)
        weights = optimize_weights(fv, fr, objective="min_variance")
        result = evaluate_portfolio(weights, fv)
        assert len(result) == 6
        assert not result.isna().all()
