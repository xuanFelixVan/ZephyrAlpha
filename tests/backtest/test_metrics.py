# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_metrics
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_metrics.py
# [TTL] permanent
"""metrics 单元测试（52号 四核心模块零单测清偿，AI-WAVE2C-001）。

覆盖: calculate_metrics 收益/回撤/Sharpe/Sortino/胜率黄金数、样本量<60 不计算
Sharpe 防线、异常输入（空/单点/全NaN/初始净值非正）、calculate_ic_ir 因子评估
黄金数（Spearman IC/标准误/t统计量/年化IR）、calculate_full_metrics 字段合并。
DSR 专项已由 tests/backtest/test_metrics_dsr.py 覆盖，本文件仅测 full_metrics 集成。
纯内存合成净值夹具，不触网不触库。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.core.metrics import (
    DEFAULT_RISK_FREE_RATE,
    MIN_SAMPLES_FOR_SHARPE,
    TRADING_DAYS_PER_YEAR,
    MetricsError,
    calculate_full_metrics,
    calculate_ic_ir,
    calculate_metrics,
)


def _nav_from_returns(returns: np.ndarray, initial: float = 100.0) -> pd.Series:
    """由日收益率序列构造净值序列（首值为 initial）。"""
    return pd.Series(np.concatenate([[initial], initial * np.cumprod(1.0 + returns)]))


class TestConstants:
    """常量契约（中国10年期国债/252交易日/Sharpe最小样本量）。"""

    def test_golden_constants(self):
        assert DEFAULT_RISK_FREE_RATE == 0.025
        assert TRADING_DAYS_PER_YEAR == 252
        assert MIN_SAMPLES_FOR_SHARPE == 60


class TestCalculateMetricsErrors:
    """异常输入防线。"""

    def test_none_raises(self):
        with pytest.raises(MetricsError):
            calculate_metrics(None)  # type: ignore[arg-type]

    def test_empty_series_raises(self):
        with pytest.raises(MetricsError):
            calculate_metrics(pd.Series([], dtype=float))

    def test_single_point_raises(self):
        with pytest.raises(MetricsError):
            calculate_metrics(pd.Series([100.0]))

    def test_all_nan_raises(self):
        with pytest.raises(MetricsError):
            calculate_metrics(pd.Series([np.nan, np.nan, np.nan]))

    def test_zero_initial_nav_raises(self):
        with pytest.raises(MetricsError):
            calculate_metrics(pd.Series([0.0, 100.0]))

    def test_negative_initial_nav_raises(self):
        with pytest.raises(MetricsError):
            calculate_metrics(pd.Series([-100.0, 100.0]))

    def test_error_code(self):
        err = MetricsError("boom")
        assert err.error_code == "ZA-BT-0006"
        err2 = MetricsError("boom", error_code="ZA-CUSTOM-1")
        assert err2.error_code == "ZA-CUSTOM-1"


class TestCalculateMetricsGolden:
    """收益/回撤/胜率黄金数。"""

    def test_total_return_and_win_rate(self):
        """净值 100→110: 总收益 10%, 1 个正收益日 → 胜率 1.0。"""
        m = calculate_metrics(pd.Series([100.0, 110.0]))
        assert m["total_return"] == pytest.approx(0.1)
        assert m["win_rate"] == pytest.approx(1.0)
        assert m["max_drawdown"] == pytest.approx(0.0)

    def test_annual_return_golden(self):
        """2 点净值年化: (1+0.1)^(252/2) - 1。"""
        m = calculate_metrics(pd.Series([100.0, 110.0]))
        expected = (1.1) ** (TRADING_DAYS_PER_YEAR / 2) - 1
        assert m["annual_return"] == pytest.approx(expected)

    def test_negative_total_return(self):
        m = calculate_metrics(pd.Series([100.0, 90.0]))
        assert m["total_return"] == pytest.approx(-0.1)

    def test_max_drawdown_golden(self):
        """100→120→90→110: 峰值120, 谷底90 → MaxDD = 30/120 = 0.25。"""
        m = calculate_metrics(pd.Series([100.0, 120.0, 90.0, 110.0]))
        assert m["max_drawdown"] == pytest.approx(0.25)

    def test_max_drawdown_monotonic_rising_is_zero(self):
        m = calculate_metrics(pd.Series([100.0, 101.0, 102.0, 103.0]))
        assert m["max_drawdown"] == pytest.approx(0.0)

    def test_max_drawdown_partial_recovery(self):
        """100→90→95: 最大回撤取谷底 0.10。"""
        m = calculate_metrics(pd.Series([100.0, 90.0, 95.0]))
        assert m["max_drawdown"] == pytest.approx(0.1)

    def test_win_rate_golden(self):
        """4 个收益日 3 正 1 负 → 胜率 0.75。"""
        m = calculate_metrics(pd.Series([100.0, 101.0, 100.0, 102.0, 103.0]))
        assert m["win_rate"] == pytest.approx(0.75)

    def test_nan_dropped(self):
        """NaN 值剔除后计算: [100, NaN, 110] → 总收益 10%。"""
        m = calculate_metrics(pd.Series([100.0, np.nan, 110.0]))
        assert m["total_return"] == pytest.approx(0.1)

    def test_trades_count_passthrough(self):
        m = calculate_metrics(pd.Series([100.0, 110.0]), trades_count=42)
        assert m["trades_count"] == 42

    def test_return_keys_complete(self):
        m = calculate_metrics(pd.Series([100.0, 110.0]))
        assert set(m.keys()) == {
            "total_return",
            "annual_return",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown",
            "win_rate",
            "trades_count",
        }


class TestSharpeSortino:
    """Sharpe/Sortino 统计显著性防线 + 黄金数。"""

    def test_below_min_samples_sharpe_zero(self):
        """59 个收益样本 < 60 → Sharpe/Sortino 不计算(0.0)。"""
        returns = np.full(MIN_SAMPLES_FOR_SHARPE - 1, 0.01)
        m = calculate_metrics(_nav_from_returns(returns))
        assert m["sharpe_ratio"] == 0.0
        assert m["sortino_ratio"] == 0.0

    def test_sharpe_golden_at_min_samples(self):
        """60 个精确 +100%/-50% 交替日收益(1↔2 净值): Sharpe=(mean-rf/252)/std×√252。"""
        # 净值在 1.0/2.0 间交替 → pct_change 精确为 +1.0/-0.5（2 的幂比率浮点无损）
        nav = pd.Series([1.0 + float(i % 2) for i in range(MIN_SAMPLES_FOR_SHARPE + 1)])
        returns = nav.pct_change().dropna().to_numpy()
        m = calculate_metrics(nav)
        rf_per_period = DEFAULT_RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
        excess = returns - rf_per_period
        expected = excess.mean() / returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
        assert m["sharpe_ratio"] == pytest.approx(expected, rel=1e-9)
        assert m["sharpe_ratio"] > 0.0
        # 下行收益全为精确 -0.5 → 下行波动率精确 0 → Sortino 0.0
        assert m["sortino_ratio"] == 0.0
        # 30 正 30 负 → 胜率 0.5
        assert m["win_rate"] == pytest.approx(0.5)

    def test_sharpe_zero_when_std_zero(self):
        """60 个精确 +100% 日收益(2 的幂净值): 波动率精确 0 → Sharpe 0.0（防除零）。"""
        nav = pd.Series([2.0**i for i in range(MIN_SAMPLES_FOR_SHARPE + 1)])
        m = calculate_metrics(nav)
        assert m["sharpe_ratio"] == 0.0

    def test_sortino_golden(self):
        """60 样本含两类下行(-1%/-2%): Sortino 仅用下行波动率。"""
        returns = np.tile([0.03, -0.01, 0.02, -0.02], MIN_SAMPLES_FOR_SHARPE // 4).astype(float)
        m = calculate_metrics(_nav_from_returns(returns))
        rf_per_period = DEFAULT_RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
        excess_mean = returns.mean() - rf_per_period
        downside = returns[returns < 0]
        expected = excess_mean / downside.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
        assert m["sortino_ratio"] == pytest.approx(expected, rel=1e-9)
        # Sortino 分母更小 → 绝对值大于 Sharpe（同号均值下）
        assert abs(m["sortino_ratio"]) > abs(m["sharpe_ratio"])

    def test_sortino_zero_when_no_downside(self):
        """60 样本全正收益 → 无下行 → Sortino 0.0。"""
        returns = np.linspace(0.001, 0.01, MIN_SAMPLES_FOR_SHARPE)
        m = calculate_metrics(_nav_from_returns(returns))
        assert m["sortino_ratio"] == 0.0
        assert m["win_rate"] == pytest.approx(1.0)


class TestCalculateIcIr:
    """因子 IC/IR 黄金数（Spearman 秩相关）。"""

    def test_length_mismatch_raises(self):
        with pytest.raises(MetricsError):
            calculate_ic_ir(pd.Series([1.0, 2.0]), pd.Series([0.1]))

    def test_insufficient_length_returns_zeros(self):
        r = calculate_ic_ir(pd.Series([1.0]), pd.Series([0.1]))
        assert r == {
            "ic_mean": 0.0,
            "ic_std": 0.0,
            "ic_ir": 0.0,
            "t_stat": 0.0,
            "ic_positive_ratio": 0.0,
        }

    def test_golden_values(self):
        """factor=[1,2,3,4,5] vs fwd=[0.5,-0.3,0.8,-0.2,0.9]:
        秩 [1,2,3,4,5] vs [3,1,4,2,5] → Spearman IC=0.5,
        ic_std=√((1-0.25)/3)=0.5, t=1.0, ic_ir=√252, 正收益占比3/5=0.6。"""
        r = calculate_ic_ir(
            pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]),
            pd.Series([0.5, -0.3, 0.8, -0.2, 0.9]),
        )
        assert r["ic_mean"] == pytest.approx(0.5)
        assert r["ic_std"] == pytest.approx(0.5)
        assert r["t_stat"] == pytest.approx(1.0)
        assert r["ic_ir"] == pytest.approx(np.sqrt(TRADING_DAYS_PER_YEAR))
        assert r["ic_positive_ratio"] == pytest.approx(0.6)

    def test_perfect_monotone_near_degenerate(self):
        """完全单调 → IC≈1, ic_std→0, t/ic_ir 公式一致（t=ic/ic_std, ic_ir=t×√252）。"""
        r = calculate_ic_ir(
            pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]),
            pd.Series([2.0, 4.0, 6.0, 8.0, 10.0]),
        )
        assert r["ic_mean"] == pytest.approx(1.0)
        assert r["ic_std"] == pytest.approx(0.0, abs=1e-6)
        # 近完全相关 → t 统计量极大, 且与 ic_ir 保持 √252 年化关系
        assert r["t_stat"] > 1e6
        assert r["ic_ir"] == pytest.approx(r["t_stat"] * np.sqrt(TRADING_DAYS_PER_YEAR), rel=1e-9)

    def test_negative_correlation(self):
        """反向因子: IC 为负。"""
        r = calculate_ic_ir(
            pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]),
            pd.Series([-0.5, 0.3, -0.8, 0.2, -0.9]),
        )
        assert r["ic_mean"] == pytest.approx(-0.5)


class TestCalculateFullMetrics:
    """完整指标（基础 + DSR 合并字段）。"""

    def test_merged_keys(self):
        m = calculate_full_metrics(pd.Series([100.0, 110.0]))
        for key in (
            "total_return",
            "annual_return",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown",
            "win_rate",
            "trades_count",
            "dsr",
            "adjusted_sharpe",
            "expected_max_sharpe",
            "is_overfitting",
        ):
            assert key in m, key

    def test_small_sample_overfitting_degenerate(self):
        """小样本 → n_samples<60 → dsr=0.0, is_overfitting=True, adjusted=原始Sharpe。"""
        m = calculate_full_metrics(pd.Series([100.0, 105.0, 103.0, 108.0]))
        assert m["dsr"] == 0.0
        assert m["is_overfitting"] is True
        assert m["adjusted_sharpe"] == m["sharpe_ratio"]

    def test_large_sample_dsr_computed(self):
        """60+ 样本 → DSR 正常计算, adjusted_sharpe == sharpe_ratio（#14 裁定口径）。"""
        returns = np.tile([0.02, -0.01], MIN_SAMPLES_FOR_SHARPE // 2).astype(float)
        m = calculate_full_metrics(_nav_from_returns(returns))
        assert 0.0 <= m["dsr"] <= 1.0
        assert m["adjusted_sharpe"] == m["sharpe_ratio"]
        assert isinstance(m["is_overfitting"], bool)

    def test_base_metrics_consistent_with_calculate_metrics(self):
        """full_metrics 基础字段与 calculate_metrics 完全一致（复用契约）。"""
        nav = pd.Series([100.0, 101.0, 99.0, 102.0, 105.0])
        base = calculate_metrics(nav, trades_count=7)
        full = calculate_full_metrics(nav, trades_count=7)
        for key in (
            "total_return",
            "annual_return",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown",
            "win_rate",
            "trades_count",
        ):
            assert full[key] == base[key], key
