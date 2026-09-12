# [BLUEPRINT] MOD-DATA_ENG | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""CryptoProvider 最小单测——纯函数与路由（不依赖网络/CH，FAIL-FAST）。"""
import datetime

import pytest

from zephyr.data.implementations.crypto_provider import (
    _STABLE_BASES,
    CryptoProvider,
)


@pytest.fixture(scope="module")
def provider():
    return CryptoProvider()


def test_unsupported_capability_yields_error(provider):
    from zephyr.data.provider_base import FetchPayload

    payload = FetchPayload(
        table="c1_market.crypto_kline_daily", symbols=None,
        start=datetime.date(2026, 9, 1), end=datetime.date(2026, 9, 11),
        incremental=True, extra={"capability": "nope"},
    )
    results = list(provider.fetch(payload, policy=None))
    assert len(results) == 1 and results[0].error and "unsupported capability" in results[0].error


def test_judge_day_trend_when_above_rising_ma200():
    """BTC 站上上行 MA200 且山寨季比率未达阈值 → trend。"""
    end = datetime.date(2026, 9, 11)
    n = 220
    btc = [(end - datetime.timedelta(days=n - 1 - i), 100.0 + i * 0.5) for i in range(n)]
    # 宇宙成员 30 对：90 日收益均低于 BTC（非山寨季）
    series = {"BTCUSDT": btc}
    for i in range(30):
        sym = f"ALT{i:02d}USDT"
        series[sym] = [(end - datetime.timedelta(days=n - 1 - j), 50.0 + j * 0.1) for j in range(n)]
    r = CryptoProvider.judge_day(end, btc, series, fng_value=56)
    assert r["tier"] == "trend", r["reason"]
    assert r["metrics"]["fng_value"] == 56 and r["metrics"]["altseason_ratio"] == 0.0


def test_judge_day_tighten_when_below_ma200():
    """BTC 收盘跌破 MA200 → tighten（破位收紧优先于趋势/山寨季）。"""
    end = datetime.date(2026, 9, 11)
    n = 220
    btc = [(end - datetime.timedelta(days=n - 1 - i), 200.0 - i * 0.5) for i in range(n)]
    r = CryptoProvider.judge_day(end, btc, {}, fng_value=None)
    assert r["tier"] == "tighten", r["reason"]


def test_judge_day_insufficient_history():
    """MA200 未满 200 根 → insufficient_history（FAIL-VISIBLE 不硬判）。"""
    end = datetime.date(2026, 9, 11)
    n = 100
    btc = [(end - datetime.timedelta(days=n - 1 - i), 100.0 + i) for i in range(n)]
    r = CryptoProvider.judge_day(end, btc, {}, fng_value=None)
    assert r["tier"] == "insufficient_history"


def test_mark_universe_ranks_by_daily_quote_volume():
    provider = CryptoProvider()
    rows = [
        {"symbol": "AAAUSDT", "trade_date": "2026-09-11", "quote_volume": "100"},
        {"symbol": "BBBUSDT", "trade_date": "2026-09-11", "quote_volume": "300"},
        {"symbol": "ETHBTC", "trade_date": "2026-09-11", "quote_volume": "999"},
    ]
    km = provider.mark_universe(rows, {"AAAUSDT", "BBBUSDT", "ETHBTC"})
    assert km[("BBBUSDT", "2026-09-11")] == (1, 1)  # 量最大 rank 1
    assert km[("AAAUSDT", "2026-09-11")] == (1, 2)
    # 汇率对恒非成员：不进 key_map，下游 INSERT 用 .get(key, (0, 0)) 默认
    assert km.get(("ETHBTC", "2026-09-11"), (0, 0)) == (0, 0)


def test_stable_bases_block_list():
    """稳定币 base 必须在剔除清单（防污染 altseason 比率）。"""
    for s in ("USDC", "FDUSD", "RLUSD"):
        assert s in _STABLE_BASES
