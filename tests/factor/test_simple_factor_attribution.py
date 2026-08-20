# [BLUEPRINT] MOD-E2E-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""25号memo §3.7#4 SimpleFactorAttribution 测试。

覆盖：Brinson 分解公式 / 基准暴露扣减 / 残差与 explained_ratio /
低贡献标记与排序 / 空输入退化 / 总PnL为0退化。
"""

from __future__ import annotations

import pandas as pd
import pytest

mod = pytest.importorskip("zephyr.factor.analysis.simple_factor_attribution")

attribute = mod.attribute


class TestAttributionFormula:
    def test_basic_pnl_decomposition(self):
        idx = pd.RangeIndex(3)
        exposures = {"f1": pd.Series([0.10, 0.10, 0.10], index=idx)}
        returns = {"f1": pd.Series([0.02, -0.01, 0.03], index=idx)}
        rep = attribute(exposures, returns, total_pnl=0.004)
        # PnL = 0.1*(0.02-0.01+0.03) = 0.004
        assert rep.rows[0].pnl == pytest.approx(0.004)
        assert rep.residual == pytest.approx(0.0)
        assert rep.explained_ratio == pytest.approx(1.0)
        assert rep.rows[0].contribution_ratio == pytest.approx(1.0)

    def test_benchmark_exposure_deducted(self):
        idx = pd.RangeIndex(2)
        exposures = {"f1": pd.Series([0.10, 0.10], index=idx)}
        returns = {"f1": pd.Series([0.05, 0.05], index=idx)}
        bench = {"f1": 0.06}
        rep = attribute(exposures, returns, total_pnl=0.004, benchmark_exposures=bench)
        # active = 0.04 → PnL = 0.04*0.05*2 = 0.004
        assert rep.rows[0].pnl == pytest.approx(0.004)
        assert rep.rows[0].avg_active_exposure == pytest.approx(0.04)

    def test_multi_factor_sorted_and_flagged(self):
        idx = pd.RangeIndex(10)
        exposures = {
            "big": pd.Series([0.20] * 10, index=idx),
            "small": pd.Series([0.01] * 10, index=idx),
        }
        returns = {
            "big": pd.Series([0.05] * 10, index=idx),  # pnl=0.1
            "small": pd.Series([0.01] * 10, index=idx),  # pnl=0.001
        }
        rep = attribute(exposures, returns, total_pnl=0.101)
        assert rep.rows[0].factor_id == "big"  # 按 pnl 降序
        assert rep.rows[1].factor_id == "small"
        assert "small" in rep.low_contribution_factors
        assert "big" not in rep.low_contribution_factors
        assert rep.explained_ratio == pytest.approx(1.0)

    def test_residual_when_unexplained(self):
        idx = pd.RangeIndex(5)
        exposures = {"f1": pd.Series([0.1] * 5, index=idx)}
        returns = {"f1": pd.Series([0.01] * 5, index=idx)}  # pnl=0.005
        rep = attribute(exposures, returns, total_pnl=0.02)
        assert rep.residual == pytest.approx(0.015)
        assert rep.explained_ratio == pytest.approx(0.25)


class TestEdgeCases:
    def test_empty_input(self):
        rep = attribute({}, {}, total_pnl=0.0)
        assert rep.rows == ()
        assert rep.residual == 0.0
        assert rep.explained_ratio == 0.0

    def test_zero_total_pnl_no_division_error(self):
        idx = pd.RangeIndex(2)
        exposures = {"f1": pd.Series([0.1, 0.1], index=idx)}
        returns = {"f1": pd.Series([0.01, -0.01], index=idx)}  # pnl=0
        rep = attribute(exposures, returns, total_pnl=0.0)
        assert rep.rows[0].contribution_ratio == 0.0
        assert rep.explained_ratio == 0.0

    def test_missing_factor_returns_skipped(self):
        idx = pd.RangeIndex(2)
        exposures = {"f1": pd.Series([0.1, 0.1], index=idx), "f2": pd.Series([0.1, 0.1], index=idx)}
        returns = {"f1": pd.Series([0.01, 0.01], index=idx)}
        rep = attribute(exposures, returns, total_pnl=0.002)
        assert len(rep.rows) == 1
        assert rep.rows[0].factor_id == "f1"

    def test_misaligned_index_intersection(self):
        exposures = {"f1": pd.Series([0.1, 0.1, 0.1], index=[0, 1, 2])}
        returns = {"f1": pd.Series([0.02, 0.02], index=[1, 2])}  # 只有 2 期交集
        rep = attribute(exposures, returns, total_pnl=0.004)
        assert rep.rows[0].pnl == pytest.approx(0.004)
