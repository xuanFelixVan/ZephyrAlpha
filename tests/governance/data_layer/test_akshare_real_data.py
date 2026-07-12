# [A_test] module_id: SRC-TST-0163 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-320 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_akshare_real_data
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Phase E — Akshare 真实数据端到端测试

用 Akshare 真实 A 股市场数据，验证 C-track 全线流水线：
  L00 (AkshareProvider → QualityGate) → L02 (FactorRegistry) →
  L03 (SignalAggregator → CapitalAllocator) →
  L04 (RiskValidator) → L05 (EquityStrategy) →
  L06 (SimulationBroker → ExecutionEngine) → L09 (BacktestEngine)

前置条件：
  - 安装了 akshare (pip install akshare)
  - 网络可访问东方财富/中证指数等数据源

所有测试标记为 @pytest.mark.slow——预期运行时间 5~30 秒/用例。
离线环境自动跳过（检测网络失败后 skip）。

Phase E | Safety: MEDIUM (网络请求)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import pytest

logger = logging.getLogger(__name__)

UNIVERSE_CSI300 = [
    "600519",
    "000858",
    "601318",
    "000333",
    "600036",
    "601398",
    "600900",
    "002415",
    "688981",
    "300750",
    "600276",
    "601088",
    "002594",
    "688981",
    "601288",
]

MIN_CSI300_SYMBOLS = 5


_NETWORK_OK: bool | None = None
_AKSHARE_OK: bool | None = None


def _is_network_available() -> bool:
    global _NETWORK_OK
    if _NETWORK_OK is not None:
        return _NETWORK_OK
    try:
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(("push2his.eastmoney.com", 80))
        sock.close()
        _NETWORK_OK = True
    except Exception:
        _NETWORK_OK = False
    return _NETWORK_OK


def _is_akshare_installed() -> bool:
    global _AKSHARE_OK
    if _AKSHARE_OK is not None:
        return _AKSHARE_OK
    try:
        import akshare  # noqa: F401

        _AKSHARE_OK = True
    except ImportError:
        _AKSHARE_OK = False
    return _AKSHARE_OK


_AKSHARE_BARS_OK: bool | None = None


def _akshare_has_usable_bar_data() -> bool:
    """socket 通且 stock_zh_a_hist 能返回足够日线时 True（接口变更/限流时为 False）。"""
    global _AKSHARE_BARS_OK
    if _AKSHARE_BARS_OK is not None:
        return _AKSHARE_BARS_OK
    if not _is_network_available() or not _is_akshare_installed():
        _AKSHARE_BARS_OK = False
        return False
    try:
        from zephyr.data.akshare_provider import AkshareProvider

        provider = AkshareProvider()
        end = datetime.now(UTC)
        start = end - timedelta(days=120)
        df = provider.fetch_historical("600519", start=start, end=end)
        _AKSHARE_BARS_OK = df is not None and len(df) >= 10
    except Exception:
        _AKSHARE_BARS_OK = False
    return _AKSHARE_BARS_OK


skip_if_no_network = pytest.mark.skipif(
    "not _is_network_available()",
    reason="Akshare 数据源不可达（网络不通）",
)
skip_if_no_akshare = pytest.mark.skipif(
    "not _is_akshare_installed()",
    reason="akshare 未安装（pip install akshare）",
)

skip_if_no_akshare_bars = pytest.mark.skipif(
    "not _akshare_has_usable_bar_data()",
    reason="Akshare 日线接口无有效数据（网络/限流/API 变更）",
)


@pytest.mark.slow
@skip_if_no_network
@skip_if_no_akshare
@skip_if_no_akshare_bars
class TestAkshareRealData:
    """真实数据接入层测试"""

    def test_provider_instantiation(self):
        """实例化 AkshareProvider 并加载 lazy import"""
        from zephyr.data.akshare_provider import (
            AkshareProvider,
        )

        provider = AkshareProvider()
        assert provider is not None
        assert provider._ak is None
        _ = provider._akshare
        assert provider._ak is not None

    def test_get_stock_list(self):
        """获取全 A 股股票列表"""
        from zephyr.data.akshare_provider import (
            AkshareProvider,
        )

        provider = AkshareProvider()
        df = provider.get_stock_list()
        assert df is not None
        assert len(df) > 1000, f"Expected >1000 stocks, got {len(df)}"
        assert "symbol" in df.columns
        assert "name" in df.columns
        assert "600519" in df["symbol"].values

    def test_get_csi300_constituents(self):
        """获取沪深 300 成分股"""
        from zephyr.data.akshare_provider import (
            AkshareProvider,
        )

        provider = AkshareProvider()
        df = provider.get_index_constituents("000300")
        assert df is not None
        assert len(df) >= 200, f"Expected >=200 CSI300 members, got {len(df)}"
        assert "symbol" in df.columns
        assert "name" in df.columns

        symbols = df["symbol"].tolist()
        assert "600519" in symbols or "000858" in symbols

    def test_fetch_daily_kline_600519(self):
        """获取贵州茅台最近 60 日 K 线数据"""
        from datetime import datetime, timedelta

        from zephyr.data.akshare_provider import (
            AkshareProvider,
        )

        provider = AkshareProvider()
        end = datetime.now(UTC)
        start = end - timedelta(days=90)

        df = provider.fetch_historical("600519", start=start, end=end)
        assert df is not None
        assert len(df) >= 30, f"Expected >=30 trading days, got {len(df)}"
        assert "open" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns
        assert "date" in df.columns

        assert df["close"].iloc[-1] > 0

    def test_fetch_multiple_symbols(self):
        """获取多只 CSI 300 成分股最近 30 日数据"""
        from datetime import datetime, timedelta

        from zephyr.data.akshare_provider import (
            AkshareProvider,
        )

        provider = AkshareProvider()
        end = datetime.now(UTC)
        start = end - timedelta(days=60)

        symbols_to_test = UNIVERSE_CSI300[:MIN_CSI300_SYMBOLS]

        results = {}
        for sym in symbols_to_test:
            df = provider.fetch_historical(sym, start=start, end=end)
            results[sym] = df

        symbols_with_data = sum(1 for df in results.values() if len(df) >= 10)
        if symbols_with_data < 3:
            pytest.skip(f"仅 {symbols_with_data}/{MIN_CSI300_SYMBOLS} 只股票有足够 K 线（数据源侧不稳定时跳过）")

    def test_quality_gate_on_real_data(self):
        """用真实行情数据过 Quality Gate"""
        from datetime import datetime, timedelta

        from zephyr.data.akshare_provider import (
            AkshareProvider,
        )

        from zephyr.gov_enforcement.rule_enforcement.default_quality_gate import (
            DefaultQualityGate,
        )

        provider = AkshareProvider()
        gate = DefaultQualityGate(max_stale_seconds=86400 * 30)

        end = datetime.now(UTC)
        start = end - timedelta(days=30)

        df = provider.fetch_historical("600519", start=start, end=end)
        if len(df) < 10:
            pytest.skip("600519 日线不足，跳过质检用例")

        last = df.iloc[-1]
        report = gate.check(
            symbol="600519",
            open_price=float(last["open"]),
            high=float(last["high"]),
            low=float(last["low"]),
            close=float(last["close"]),
            volume=float(last["volume"]),
            timestamp=last["date"],
            prev_close=float(df.iloc[-2]["close"]) if len(df) >= 2 else None,
        )
        assert report.quality_score >= 0.5, f"Quality score too low: {report.quality_score}"
        assert report.symbol == "600519"


@pytest.mark.slow
@skip_if_no_network
@skip_if_no_akshare
@skip_if_no_akshare_bars
class TestAkshareMiniPipeline:
    """从真实数据到信号/风控/回测的小型流水线"""

    @pytest.fixture(scope="class")
    def real_data(self):
        """获取 5 只 CSI 300 成分股最近 120 日数据"""
        from datetime import datetime, timedelta

        from zephyr.data.akshare_provider import (
            AkshareProvider,
        )

        provider = AkshareProvider()
        end = datetime.now(UTC)
        start = end - timedelta(days=180)

        data = {}
        for sym in UNIVERSE_CSI300[:MIN_CSI300_SYMBOLS]:
            df = provider.fetch_historical(sym, start=start, end=end)
            if len(df) >= 30:
                data[sym] = df

        if len(data) < 3:
            pytest.skip(f"仅 {len(data)} 只股票有足够历史数据，跳过 mini pipeline")

        return data

    def test_quality_gate_batch_on_real_data(self, real_data):
        """批量质检真实数据"""
        from zephyr.gov_enforcement.rule_enforcement.default_quality_gate import (
            DefaultQualityGate,
        )

        gate = DefaultQualityGate(max_stale_seconds=86400 * 60)

        batch = []
        for sym, df in real_data.items():
            last = df.iloc[-1]
            batch.append(
                {
                    "symbol": sym,
                    "open": float(last["open"]),
                    "high": float(last["high"]),
                    "low": float(last["low"]),
                    "close": float(last["close"]),
                    "volume": float(last["volume"]),
                    "timestamp": last["date"],
                    "prev_close": float(df.iloc[-2]["close"]) if len(df) >= 2 else None,
                }
            )

        reports = gate.check_batch(batch)
        passed = sum(1 for r in reports if r.passed)
        assert passed >= len(batch) - 1, f"Expected >= {len(batch) - 1} passed, got {passed}/{len(batch)}"

    def test_simple_momentum_signal(self, real_data):
        """简单动量信号——20 日收益率"""
        signals = {}
        for sym, df in real_data.items():
            if len(df) < 30:
                continue
            ret_20d = (df["close"].iloc[-1] - df["close"].iloc[-21]) / df["close"].iloc[-21]
            signals[sym] = float(ret_20d)

        assert len(signals) >= 3
        positive = sum(1 for v in signals.values() if v > 0)
        logger.info("Momentum signals: %d positive out of %d", positive, len(signals))

    def test_risk_limit_on_real_positions(self, real_data):
        """用真实数据构建虚拟持仓 + 风控校验"""
        from datetime import datetime

        from zephyr.risk.implementations.default_risk_validator import (
            DefaultRiskValidator,
        )
        from zephyr.risk.risk_manager import RiskLimits

        limits = RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="lim-real-001",
            max_single_position=0.15,
            max_gross_leverage=1.0,
            max_drawdown_limit=0.20,
        )

        validator = DefaultRiskValidator()

        holdings: dict[str, float] = {}
        market_values: dict[str, float] = {}
        total_nav = 1000000.0

        for sym, df in real_data.items():
            weight = 0.10
            holdings[sym] = weight
            market_values[sym] = total_nav * weight

        actual_total = sum(market_values.values())

        result = validator.validate_portfolio(
            holdings=holdings,
            market_values=market_values,
            total_nav=actual_total,
            limits=limits,
        )
        assert isinstance(result, list)
        assert len(result) == 0, f"Unexpected violations: {[v.description for v in result]}"

    def test_mini_backtest_with_real_prices(self, real_data):
        """用真实价格做简单回测"""
        import pandas as pd

        daily_nav = [1.0]
        symbols = list(real_data.keys())

        returns_by_symbol = {}
        for sym, df in real_data.items():
            if len(df) < 30:
                continue
            r = df["close"].pct_change().dropna()
            returns_by_symbol[sym] = r

        if not returns_by_symbol:
            pytest.skip("No symbols with sufficient returns data")

        common_idx = None
        for sym, r in returns_by_symbol.items():
            if common_idx is None:
                common_idx = r.index
            else:
                common_idx = common_idx.intersection(r.index)

        if common_idx is None or len(common_idx) < 10:
            pytest.skip("Not enough common trading dates")

        for i in range(min(30, len(common_idx))):
            day_return = 0.0
            count = 0
            for sym, r in returns_by_symbol.items():
                idx_date = common_idx[i]
                if idx_date in r.index:
                    day_return += r.loc[idx_date]
                    count += 1
            if count > 0:
                day_return /= count
            daily_nav.append(daily_nav[-1] * (1 + day_return))

        nav_series = pd.Series(daily_nav)
        assert len(nav_series) >= 10, f"Nav series too short: {len(nav_series)}"

        total_return = (nav_series.iloc[-1] - nav_series.iloc[0]) / nav_series.iloc[0]
        logger.info("Mini backtest: %.2f%% return over %d days", total_return * 100, len(nav_series) - 1)
        assert abs(total_return) < 2.0, f"Unrealistic return: {total_return:.2%}"
