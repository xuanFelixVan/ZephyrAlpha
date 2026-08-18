# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §
# [MODULE] tests.backtest.test_shrinkage_engine
# [DOMAIN] D_BACKTEST
# [A_module] module_id=MOD-TEST-BT-SHRINK | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #B-shrinkage-engine
"""ShrinkageBacktestEngine (B1) 单元测试——Shrinkage 接入点。

覆盖:
  - shrinkage=1.0 与 DefaultBacktestEngine 等价（C1 可溯源对比基础）
  - shrinkage=0.5 权重减半，剩余留现金
  - shrinkage=0.0 全空仓
  - 钳制 [0,1]（只减不增不变量）
  - shrinkage_log 归因记录
  - provider 异常降级为满部署
  - ShrinkageProvider 协议 structural typing
"""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.implementations.shrinkage_engine import (
    ShrinkageBacktestEngine,
    ShrinkageProvider,
)
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.backtest.regime_validation.shrinkage_provider import (
    ConstShrinkageProvider,
    ScheduleShrinkageProvider,
)

# ── 合成数据构造 ──────────────────────────────────────────────────────

_SYMBOLS = ["600001", "600002", "600003"]
_N_DAYS = 40


def _make_market_data(symbols=_SYMBOLS, n_days=_N_DAYS, seed=7) -> pd.DataFrame:
    """合成日 K（MultiIndex symbol×date，含 OHLCV）。index level 名 "date"。"""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01", periods=n_days, freq="B")
    frames = []
    for sym in symbols:
        close = 100.0
        rows = []
        for t in range(n_days):
            ret = 0.001 + rng.normal(0, 0.01)  # 轻微正漂移
            close = close * (1 + ret)
            rows.append({
                "symbol": sym, "date": dates[t],
                "open": close, "high": close * 1.01, "low": close * 0.99,
                "close": close, "volume": 1_000_000,
            })
        frames.append(pd.DataFrame(rows))
    df = pd.concat(frames, ignore_index=True).set_index(["symbol", "date"]).sort_index()
    return df


def _make_signals(data: pd.DataFrame, symbols=_SYMBOLS) -> pd.DataFrame:
    """等权信号（index=date, columns=symbol, 值=1.0 → 归一化后 1/N）。"""
    dates = data.index.get_level_values("date").unique().sort_values()
    return pd.DataFrame(
        {sym: 1.0 for sym in symbols}, index=pd.DatetimeIndex(dates, name="date")
    )


# ── fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def market_data() -> pd.DataFrame:
    return _make_market_data()


@pytest.fixture
def signals(market_data) -> pd.DataFrame:
    return _make_signals(market_data)


# ── 等价性测试 ────────────────────────────────────────────────────────

class TestEquivalence:
    """shrinkage=1.0 必须与 DefaultBacktestEngine 完全等价。"""

    def test_off_equals_default_engine(self, market_data, signals):
        """ConstShrinkageProvider(1.0) 与 DefaultBacktestEngine 指标一致。"""
        cfg = BacktestConfig(initial_capital=__import__("decimal").Decimal("1000000"))
        default_engine = DefaultBacktestEngine(config=cfg)
        shrink_engine = ShrinkageBacktestEngine(
            config=cfg, shrinkage_provider=ConstShrinkageProvider(1.0)
        )

        r_default = default_engine.run(data=market_data, signals=signals, strategy_name="s")
        r_shrink = shrink_engine.run(data=market_data, signals=signals, strategy_name="s")

        # shrinkage=1.0 走早返回分支（权重不变），指标应 bit-identical
        assert r_shrink.sharpe_ratio == pytest.approx(r_default.sharpe_ratio)
        assert r_shrink.total_return == pytest.approx(r_default.total_return)
        assert r_shrink.max_drawdown == pytest.approx(r_default.max_drawdown)
        assert r_shrink.trades_count == r_default.trades_count

    def test_none_provider_defaults_to_full_deploy(self, market_data, signals):
        """shrinkage_provider=None 等价于满部署。"""
        engine = ShrinkageBacktestEngine(config=BacktestConfig())  # provider=None
        result = engine.run(data=market_data, signals=signals)
        assert result.sharpe_ratio == result.sharpe_ratio  # 非 NaN
        # shrinkage_log 全部应为 1.0
        assert engine.shrinkage_log, "应有 shrinkage 记录"
        assert all(v == 1.0 for _, v in engine.shrinkage_log)


# ── 节流行为测试 ──────────────────────────────────────────────────────

class TestThrottling:
    """Shrinkage 缩放仓位，剩余留现金。"""

    def test_half_shrinkage_leaves_cash(self, market_data, signals):
        """shrinkage=0.5 → 持仓约为满部署一半，现金更多。"""
        cfg = BacktestConfig()
        full_engine = ShrinkageBacktestEngine(cfg, ConstShrinkageProvider(1.0))
        half_engine = ShrinkageBacktestEngine(cfg, ConstShrinkageProvider(0.5))

        full_engine.run(data=market_data, signals=signals)
        half_engine.run(data=market_data, signals=signals)

        full_cash = float(full_engine.last_portfolio.cash)
        half_cash = float(half_engine.last_portfolio.cash)
        # 半仓应保留更多现金
        assert half_cash > full_cash, (
            f"半仓现金 {half_cash} 应 > 满仓现金 {full_cash}"
        )

        # shrinkage_log 全部 0.5
        assert all(abs(v - 0.5) < 1e-9 for _, v in half_engine.shrinkage_log)

    def test_zero_shrinkage_full_cash(self, market_data, signals):
        """shrinkage=0.0 → 全空仓（权重返回空 dict）。"""
        engine = ShrinkageBacktestEngine(
            BacktestConfig(), ConstShrinkageProvider(0.0)
        )
        result = engine.run(data=market_data, signals=signals)

        # 无交易
        assert result.trades_count == 0
        # 持仓为空，现金 = 初始资金（扣手续费前；无 fills 故无扣减）
        assert float(engine.last_portfolio.cash) == float(
            engine.last_portfolio.initial_capital
        )
        # shrinkage_log 记录 0.0
        assert all(v == 0.0 for _, v in engine.shrinkage_log)

    def test_shrinkage_reduces_market_value_ratio(self, market_data, signals):
        """shrinkage=0.5 → 市值/NAV 比例约为满部署的一半。"""
        cfg = BacktestConfig()
        full = ShrinkageBacktestEngine(cfg, ConstShrinkageProvider(1.0))
        half = ShrinkageBacktestEngine(cfg, ConstShrinkageProvider(0.5))
        full.run(data=market_data, signals=signals)
        half.run(data=market_data, signals=signals)

        fp = full.last_portfolio
        hp = half.last_portfolio
        # 取最后一日价格估算市值比例
        last_date = market_data.index.get_level_values("date").unique()[-1]
        prices = market_data.xs(last_date, level="date")["close"]
        price_dict = {s: __import__("decimal").Decimal(str(p)) for s, p in prices.items()}

        full_mv = float(fp.total_market_value(price_dict))
        half_mv = float(hp.total_market_value(price_dict))
        full_nav = float(fp.total_nav(price_dict))
        half_nav = float(hp.total_nav(price_dict))

        # 半仓市值比例应明显低于满仓
        assert half_mv / half_nav < full_mv / full_nav


# ── 钳制与不变量 ──────────────────────────────────────────────────────

class TestClamping:
    """Shrinkage 钳制到 [0,1]（只减不增）。"""

    def test_clamps_above_one(self, market_data, signals):
        """provider 返回 1.5 → 钳制为 1.0（满部署）。"""

        class _OverProvider:
            def get_shrinkage(self, date):  # noqa: ARG002
                return 1.5

        engine = ShrinkageBacktestEngine(BacktestConfig(), _OverProvider())
        engine.run(data=market_data, signals=signals)
        assert all(v == 1.0 for _, v in engine.shrinkage_log)

    def test_clamps_negative(self, market_data, signals):
        """provider 返回 -0.1 → 钳制为 0.0（全空仓）。"""

        class _NegProvider:
            def get_shrinkage(self, date):  # noqa: ARG002
                return -0.1

        engine = ShrinkageBacktestEngine(BacktestConfig(), _NegProvider())
        result = engine.run(data=market_data, signals=signals)
        assert result.trades_count == 0
        assert all(v == 0.0 for _, v in engine.shrinkage_log)

    def test_clamps_nan_to_full_deploy(self, market_data, signals):
        """provider 返回 NaN → 钳制为 1.0。"""
        import math

        class _NaNProvider:
            def get_shrinkage(self, date):  # noqa: ARG002
                return math.nan

        engine = ShrinkageBacktestEngine(BacktestConfig(), _NaNProvider())
        engine.run(data=market_data, signals=signals)
        assert all(v == 1.0 for _, v in engine.shrinkage_log)


# ── 健壮性 ────────────────────────────────────────────────────────────

class TestRobustness:
    """provider 异常降级，不阻断回测。"""

    def test_provider_exception_fallback(self, market_data, signals):
        """provider 抛异常 → 当日退化为 1.0。"""

        class _BoomProvider:
            def get_shrinkage(self, date):  # noqa: ARG002
                raise RuntimeError("boom")

        engine = ShrinkageBacktestEngine(BacktestConfig(), _BoomProvider())
        result = engine.run(data=market_data, signals=signals)
        # 不应抛异常，且全部降级为 1.0
        assert all(v == 1.0 for _, v in engine.shrinkage_log)
        assert result.trades_count >= 0  # 跑通即可

    def test_schedule_provider_as_of_join(self, market_data, signals):
        """ScheduleShrinkageProvider PIT as-of join：前段 1.0，后段 0.5。"""
        dates = sorted(market_data.index.get_level_values("date").unique())
        mid = dates[len(dates) // 2].to_pydatetime()
        schedule = {mid: 0.5}  # mid 起切换到 0.5
        provider = ScheduleShrinkageProvider(schedule)

        engine = ShrinkageBacktestEngine(BacktestConfig(), provider)
        engine.run(data=market_data, signals=signals)

        log = engine.shrinkage_log
        # mid 之前（不含）应为 1.0，mid 及之后应为 0.5
        before = [v for d, v in log if d < mid]
        after = [v for d, v in log if d >= mid]
        assert before, "应有 mid 前记录"
        assert after, "应有 mid 后记录"
        assert all(v == 1.0 for v in before)
        assert all(v == 0.5 for v in after)

    def test_no_signals_no_shrinkage_log(self, market_data):
        """无信号的日期不记录 shrinkage（与父类早返回语义一致）。"""
        # 全空信号
        empty_signals = _make_signals(market_data) * 0.0
        engine = ShrinkageBacktestEngine(BacktestConfig(), ConstShrinkageProvider(0.5))
        engine.run(data=market_data, signals=empty_signals)
        # 无信号 → 不进入缩放分支 → shrinkage_log 为空
        assert engine.shrinkage_log == []


# ── 协议 ──────────────────────────────────────────────────────────────

class TestProtocol:
    """ShrinkageProvider 协议 structural typing（runtime_checkable）。"""

    def test_const_provider_satisfies_protocol(self):
        provider = ConstShrinkageProvider(0.8)
        assert isinstance(provider, ShrinkageProvider)

    def test_custom_object_satisfies_protocol(self):
        class _Custom:
            def get_shrinkage(self, date):  # noqa: ARG002
                return 0.7

        assert isinstance(_Custom(), ShrinkageProvider)

    def test_object_without_method_fails_protocol(self):
        class _NotAProvider:
            pass

        assert not isinstance(_NotAProvider(), ShrinkageProvider)
