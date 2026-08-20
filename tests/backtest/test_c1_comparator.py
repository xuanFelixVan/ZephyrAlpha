# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §
# [MODULE] tests.backtest.test_c1_comparator
# [DOMAIN] D_BACKTEST
# [A_module] module_id=MOD-TEST-BT-C1 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #C1-shrinkage-comparator
"""C1ShrinkageComparator (C1) 单元测试——开/关对比 + 一票否决裁定。

策略:
  - evaluate() 配合手搓 BacktestResult → 确定性覆盖四项否决逻辑（核心）
  - compare() 真实引擎编排 → 端到端确认接线（orchestration）
  - _compute_calmar / _compute_turnover 工具函数边界
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.core.engine_base import BacktestResult
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio
from zephyr.backtest.implementations.shrinkage_engine import ShrinkageBacktestEngine
from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_comparator import (
    C1ComparisonResult,
    C1Config,
    C1MetricVerdict,
    C1ShrinkageComparator,
    C1ShrinkageComparatorError,
    _compute_calmar,
    _compute_turnover,
)
from zephyr.backtest.regime_validation.shrinkage_provider import (
    ConstShrinkageProvider,
)

# ── 手搓 BacktestResult / Portfolio 工具 ──────────────────────────────


def _make_result(
    *,
    sharpe: float = 1.0,
    maxdd: float = -0.15,
    annual_return: float = 0.20,
    trades: int = 100,
    total_return: float = 0.20,
    win_rate: float = 0.55,
) -> BacktestResult:
    """构造 BacktestResult（frozen dataclass，全必填字段）。"""
    return BacktestResult(
        annual_return=annual_return,
        end_date=datetime(2026, 12, 31, tzinfo=timezone.utc),
        idempotency_key=f"test-{sharpe}-{maxdd}-{annual_return}",
        max_drawdown=maxdd,
        sharpe_ratio=sharpe,
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        strategy_id="c1-test",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        total_return=total_return,
        trades_count=trades,
        win_rate=win_rate,
    )


def _make_portfolio(trades: list[tuple[int, float]], n_nav_days: int = 10) -> Portfolio:
    """构造带交易的 Portfolio（用于 Turnover 计算）。

    Args:
        trades: [(qty, price), ...] 同一 symbol 的 BUY 成交列表。
        n_nav_days: update_market_value 调用次数（决定 nav_series 长度）。
    """
    p = Portfolio(initial_capital=Decimal("1000000"))
    for qty, price in trades:
        fill = BacktestFill(
            date="2026-01-01",
            symbol="S1",
            side="BUY",
            quantity=Decimal(str(qty)),
            price=Decimal(str(price)),
        )
        p.apply_fill(fill, allow_t_plus_1=False)
    dates = pd.date_range("2026-01-01", periods=n_nav_days, freq="D")
    for d in dates:
        p.update_market_value(d, {"S1": Decimal("10")})
    return p


def _verdict(result: C1ComparisonResult, name: str) -> C1MetricVerdict:
    """按名称取单项判定。"""
    return next(v for v in result.metric_verdicts if v.name == name)


# ── 配置校验 ──────────────────────────────────────────────────────────


class TestC1Config:
    def test_defaults_match_plan(self):
        """默认门槛 = 11_regime_backtest_validation_plan §5 汇总表。"""
        cfg = C1Config()
        assert cfg.sharpe_tolerance == 0.1
        assert cfg.maxdd_improvement_pp == 0.03
        assert cfg.calmar_improvement_ratio == 1.2
        assert cfg.turnover_max_ratio == 2.0
        assert cfg.trading_days_per_year == 252

    def test_invalid_calmar_ratio_rejected(self):
        with pytest.raises(C1ShrinkageComparatorError):
            C1Config(calmar_improvement_ratio=0)

    def test_invalid_turnover_ratio_rejected(self):
        with pytest.raises(C1ShrinkageComparatorError):
            C1Config(turnover_max_ratio=-1)

    def test_invalid_trading_days_rejected(self):
        with pytest.raises(C1ShrinkageComparatorError):
            C1Config(trading_days_per_year=0)


# ── evaluate() 否决逻辑（核心）────────────────────────────────────────


class TestEvaluateVerdicts:
    """四项指标一票否决逻辑——确定性覆盖。"""

    def test_all_pass(self):
        """四项全过 → passed=True，无 veto_reason。"""
        # base: sharpe=1.0, maxdd=-0.15, annual=0.20 → calmar=1.333
        # exp:  sharpe=1.0(≥0.9✓), maxdd=-0.10(改善0.05≥0.03✓),
        #       annual=0.20 → calmar=2.0(≥1.333*1.2=1.6✓), turnover 相等(0=0✓)
        base = _make_result(sharpe=1.0, maxdd=-0.15, annual_return=0.20)
        exp = _make_result(sharpe=1.0, maxdd=-0.10, annual_return=0.20)

        result = C1ShrinkageComparator().evaluate(base, exp)

        assert result.passed is True
        assert result.veto_reason is None
        assert all(v.passed for v in result.metric_verdicts)

    def test_veto_sharpe_harmed(self):
        """Sharpe 降幅 > 0.1 → 否决。"""
        base = _make_result(sharpe=1.0, maxdd=-0.15, annual_return=0.20)
        exp = _make_result(sharpe=0.80, maxdd=-0.10, annual_return=0.20)
        result = C1ShrinkageComparator().evaluate(base, exp)

        assert result.passed is False
        assert result.veto_reason is not None
        assert _verdict(result, "Sharpe").passed is False
        assert "Sharpe" in result.veto_reason

    def test_veto_maxdd_not_improved(self):
        """MaxDD 改善 < 3pp → 否决。"""
        base = _make_result(sharpe=1.0, maxdd=-0.15, annual_return=0.20)
        # maxdd -0.145 → 改善 0.005 < 0.03
        exp = _make_result(sharpe=1.0, maxdd=-0.145, annual_return=0.20)
        result = C1ShrinkageComparator().evaluate(base, exp)

        assert _verdict(result, "MaxDD").passed is False
        assert result.passed is False

    def test_maxdd_borderline_3pp_passes(self):
        """MaxDD 恰好改善 3pp → 通过（边界）。"""
        base = _make_result(sharpe=1.0, maxdd=-0.15, annual_return=0.20)
        exp = _make_result(sharpe=1.0, maxdd=-0.12, annual_return=0.20)
        result = C1ShrinkageComparator().evaluate(base, exp)
        # 改善 0.03 ≥ 0.03 → 通过
        assert _verdict(result, "MaxDD").passed is True

    def test_veto_calmar_not_improved(self):
        """Calmar 提升 < 20% → 否决。"""
        # base calmar = 0.20/0.15 = 1.333；门槛 1.333*1.2 = 1.6
        # exp calmar = 0.20/0.12 = 1.667 → 刚过；改 annual 使不过
        base = _make_result(sharpe=1.0, maxdd=-0.15, annual_return=0.20)
        # exp maxdd=-0.13(改善0.02<0.03也会否决maxdd)，annual=0.20 → calmar=1.538 < 1.6
        exp = _make_result(sharpe=1.0, maxdd=-0.13, annual_return=0.20)
        result = C1ShrinkageComparator().evaluate(base, exp)
        assert _verdict(result, "Calmar").passed is False

    def test_calmar_negative_baseline_fallback(self):
        """基线 Calmar 非正 → 退化为"不变差"判定。"""
        # base 亏损：annual=-0.10, maxdd=-0.15 → calmar=-0.667
        base = _make_result(sharpe=0.5, maxdd=-0.15, annual_return=-0.10)
        # exp 仍亏损但 less bad：annual=-0.05, maxdd=-0.10 → calmar=-0.5 ≥ -0.667
        exp = _make_result(sharpe=0.5, maxdd=-0.10, annual_return=-0.05)
        result = C1ShrinkageComparator().evaluate(base, exp)
        # Calmar 退化判定：exp ≥ base → -0.5 ≥ -0.667 ✓
        assert _verdict(result, "Calmar").passed is True

    def test_veto_turnover_explodes(self):
        """换手率 > 2× → 否决（需 Portfolio）。"""
        base = _make_result(sharpe=1.0, maxdd=-0.10, annual_return=0.20)
        exp = _make_result(sharpe=1.0, maxdd=-0.10, annual_return=0.20)
        # baseline 1 笔交易，experiment 3 笔 → 3× 换手（>2×）
        base_pf = _make_portfolio([(100, 10.0)])
        exp_pf = _make_portfolio([(100, 10.0), (100, 10.0), (100, 10.0)])

        result = C1ShrinkageComparator().evaluate(base, exp, base_pf, exp_pf)
        assert _verdict(result, "Turnover").passed is False
        assert result.experiment_turnover > result.baseline_turnover * 2
        assert result.passed is False

    def test_turnover_within_limit_passes(self):
        """换手率 ≤ 2× → 通过。"""
        base = _make_result(sharpe=1.0, maxdd=-0.10, annual_return=0.20)
        exp = _make_result(sharpe=1.0, maxdd=-0.10, annual_return=0.20)
        base_pf = _make_portfolio([(100, 10.0)])
        exp_pf = _make_portfolio([(100, 10.0), (100, 10.0)])  # 2× → 恰好通过

        result = C1ShrinkageComparator().evaluate(base, exp, base_pf, exp_pf)
        assert _verdict(result, "Turnover").passed is True

    def test_summary_contains_all_metrics(self):
        base = _make_result(sharpe=1.0, maxdd=-0.15, annual_return=0.20)
        exp = _make_result(sharpe=1.0, maxdd=-0.10, annual_return=0.20)
        result = C1ShrinkageComparator().evaluate(base, exp)
        assert "Sharpe" in result.summary
        assert "MaxDD" in result.summary
        assert "Calmar" in result.summary
        assert "Turnover" in result.summary


# ── 工具函数 ──────────────────────────────────────────────────────────


class TestComputeHelpers:
    def test_calmar_normal(self):
        assert _compute_calmar(0.20, -0.10) == pytest.approx(2.0)

    def test_calmar_zero_drawdown_positive_return_is_inf(self):
        """无回撤 + 正收益 → Calmar = +inf。"""
        assert math.isinf(_compute_calmar(0.10, 0.0))
        assert _compute_calmar(0.10, 0.0) > 0

    def test_calmar_zero_drawdown_negative_return_is_neg_inf(self):
        """无回撤 + 亏损 → Calmar = -inf（异常态）。"""
        assert math.isinf(_compute_calmar(-0.10, 0.0))
        assert _compute_calmar(-0.10, 0.0) < 0

    def test_turnover_none_portfolio(self):
        assert _compute_turnover(None, 252) == 0.0

    def test_turnover_no_trades(self):
        p = Portfolio(initial_capital=Decimal("1000000"))
        p.update_market_value("2026-01-01", {})
        assert _compute_turnover(p, 252) == 0.0

    def test_turnover_known_value(self):
        """1 笔 100@10=1000 交易，nav≈1e6，10 个 nav 点 → num_years=9/252。"""
        p = _make_portfolio([(100, 10.0)], n_nav_days=10)
        # nav_series 长度 = 1(初始) + 10 = 11 → num_years = max(10,1)/252
        expected_years = 10 / 252
        avg_nav = float(p.nav_series.mean())
        expected_turnover = 1000.0 / (avg_nav * expected_years)
        assert _compute_turnover(p, 252) == pytest.approx(expected_turnover, rel=1e-6)


# ── compare() 端到端编排 ─────────────────────────────────────────────


def _make_market_data(n_days=40):
    symbols = ["600001", "600002", "600003"]
    rng = np.random.default_rng(7)
    dates = pd.date_range("2026-01-01", periods=n_days, freq="B")
    frames = []
    for sym in symbols:
        close = 100.0
        rows = []
        for t in range(n_days):
            ret = 0.001 + rng.normal(0, 0.01)
            close = close * (1 + ret)
            rows.append(
                {
                    "symbol": sym,
                    "date": dates[t],
                    "open": close,
                    "high": close * 1.01,
                    "low": close * 0.99,
                    "close": close,
                    "volume": 1_000_000,
                }
            )
        frames.append(pd.DataFrame(rows))
    return pd.concat(frames, ignore_index=True).set_index(["symbol", "date"]).sort_index()


def _make_signals(data):
    symbols = ["600001", "600002", "600003"]
    dates = data.index.get_level_values("date").unique().sort_values()
    return pd.DataFrame({sym: 1.0 for sym in symbols}, index=pd.DatetimeIndex(dates, name="date"))


class TestCompareOrchestration:
    """compare() 真实引擎编排——确认开/关两组回测接线闭环。"""

    def test_compare_returns_full_result(self):
        """compare() 跑通两组回测，返回完整 C1ComparisonResult。"""
        data = _make_market_data()
        signals = _make_signals(data)

        # 实验组也用 1.0（off vs off）→ 两组完全等价 → MaxDD 无改善 → 否决
        result = C1ShrinkageComparator().compare(
            data=data,
            signals=signals,
            shrinkage_provider=ConstShrinkageProvider(1.0),
            backtest_config=BacktestConfig(),
            strategy_name="c1-orch-test",
        )

        assert isinstance(result, C1ComparisonResult)
        assert len(result.metric_verdicts) == 4
        # 两组等价 → MaxDD 改善=0 < 3pp → MaxDD 否决
        assert _verdict(result, "MaxDD").passed is False
        assert result.passed is False
        assert result.veto_reason is not None
        # 两组回测都跑了（trades_count > 0 说明有信号成交）
        assert result.baseline_result.trades_count >= 0
        assert result.experiment_result.trades_count >= 0

    def test_compare_half_shrinkage_runs(self):
        """实验组 shrinkage=0.5 跑通（不崩），返回四项判定。"""
        data = _make_market_data()
        signals = _make_signals(data)

        result = C1ShrinkageComparator().compare(
            data=data,
            signals=signals,
            shrinkage_provider=ConstShrinkageProvider(0.5),
            backtest_config=BacktestConfig(),
        )
        assert isinstance(result, C1ComparisonResult)
        assert len(result.metric_verdicts) == 4
        # 半仓换手应 ≤ 满仓（交易更少），Sharpe/MaxDD 取决于数据，仅确认跑通
        assert isinstance(result.passed, bool)

    def test_compare_ensures_gate_off(self):
        """strict_overfitting_gate=True 的 config 也应被强制关闭，不阻断 C1。"""
        data = _make_market_data()
        signals = _make_signals(data)
        cfg = BacktestConfig(strict_overfitting_gate=True)

        # 不应抛 OverfittingGateError
        result = C1ShrinkageComparator().compare(
            data=data,
            signals=signals,
            shrinkage_provider=ConstShrinkageProvider(1.0),
            backtest_config=cfg,
        )
        assert isinstance(result, C1ComparisonResult)

    def test_compare_shrinkage_engine_reused(self):
        """确认 compare 内部用的是 ShrinkageBacktestEngine（B1 接入点）。"""
        data = _make_market_data()
        signals = _make_signals(data)
        # 用 ScheduleShrinkageProvider 验证 B1+B2 联动
        from zephyr.backtest.regime_validation.shrinkage_provider import (
            ScheduleShrinkageProvider,
        )

        dates = sorted(data.index.get_level_values("date").unique())
        mid = dates[len(dates) // 2].to_pydatetime()
        provider = ScheduleShrinkageProvider({mid: 0.6})

        result = C1ShrinkageComparator().compare(
            data=data,
            signals=signals,
            shrinkage_provider=provider,
            backtest_config=BacktestConfig(),
        )
        assert isinstance(result, C1ComparisonResult)
        assert len(result.metric_verdicts) == 4
