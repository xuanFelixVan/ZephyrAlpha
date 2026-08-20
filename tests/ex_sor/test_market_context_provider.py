# [BLUEPRINT] MOD-XS-006 | docs/03_modules/_domain_ex_sor/market_context_provider/blueprint.md | §
# [TTL] permanent
"""MarketContextProvider 单元测试 (MOD-XS-006)。

覆盖:
    - StaticMarketContextProvider (固定上下文 + symbol 不匹配重建)
    - _to_qmt_symbol 符号格式归一化
    - RedisKlineMarketContextProvider (tick 存在 / tick 缺失降级 / 无 K线报错)
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.core.algo_trading_engine import AlgoError, MarketContext
from zephyr.ex_sor.core.market_context_provider import (
    RedisKlineMarketContextProvider,
    StaticMarketContextProvider,
    _to_qmt_symbol,
)
from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key
from zephyr.shared.contracts.market_data import NormalizedMarketData

# ── 符号归一化 ──


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("600519", "600519.SH"),
        ("000001", "000001.SZ"),
        ("300750", "300750.SZ"),
        ("688981", "688981.SH"),
        ("600519.SH", "600519.SH"),
        ("000001.SZ", "000001.SZ"),
        ("600519.sh", "600519.SH"),
    ],
)
def test_to_qmt_symbol_normalization(raw: str, expected: str) -> None:
    assert _to_qmt_symbol(raw) == expected


def test_to_qmt_symbol_empty() -> None:
    assert _to_qmt_symbol("") == ""


# ── StaticMarketContextProvider ──


def test_static_provider_returns_context() -> None:
    provider = StaticMarketContextProvider.from_values(
        symbol="600519",
        last_price=100,
        adv=100000,
        bid_price=99.9,
        ask_price=100.1,
    )
    ctx = provider.get_context("600519")
    assert isinstance(ctx, MarketContext)
    assert ctx.symbol == "600519"
    assert ctx.last_price == Decimal("100")
    assert ctx.adv == Decimal("100000")
    assert ctx.bid_price == Decimal("99.9")
    assert ctx.ask_price == Decimal("100.1")


def test_static_provider_symbol_mismatch_rebuilds() -> None:
    """请求 symbol 与 ctx.symbol 不一致时, 重建保持其余字段的 context。"""
    provider = StaticMarketContextProvider.from_values(
        symbol="600519",
        last_price=100,
        adv=100000,
    )
    ctx = provider.get_context("000001")
    assert ctx.symbol == "000001"
    assert ctx.last_price == Decimal("100")
    assert ctx.adv == Decimal("100000")


def test_static_provider_accepts_decimal_float_str() -> None:
    provider = StaticMarketContextProvider.from_values(
        symbol="600519",
        last_price=Decimal("100.5"),
        adv=100000.0,
        bid_price="99.9",
    )
    ctx = provider.get_context("600519")
    assert ctx.last_price == Decimal("100.5")
    assert ctx.adv == Decimal("100000.0")
    assert ctx.bid_price == Decimal("99.9")


# ── RedisKlineMarketContextProvider ──


class _FakeRedis:
    """最小 Redis 桩——仅实现 hgetall (decode_responses=True 返回 str)。"""

    def __init__(self, tick_data: dict[str, dict[str, str]] | None = None) -> None:
        # tick_data: {qmt_symbol: {field: str_value}}
        self._data = tick_data or {}

    def hgetall(self, key: str) -> dict[str, str]:
        return dict(self._data.get(key, {}))


def _make_kline(
    symbol: str,
    ts: datetime,
    volume: Decimal,
    close: Decimal = Decimal("100"),
) -> NormalizedMarketData:
    return NormalizedMarketData(
        close=close,
        data_source="test",
        high=close,
        idempotency_key=f"{symbol}:{ts:%Y%m%d}",
        low=close,
        open=close,
        symbol=symbol,
        timestamp=ts,
        volume=volume,
    )


def _patch_load_kline(monkeypatch, records: list[NormalizedMarketData]) -> None:
    """把 market_context_provider 模块内的 load_kline 替换为返回固定 records。"""

    def _fake_load_kline(symbols, start, end):  # noqa: ANN001 — 测试桩
        return list(records)

    monkeypatch.setattr(
        "zephyr.ex_sor.core.market_context_provider.load_kline",
        _fake_load_kline,
    )


def test_redis_provider_uses_tick_and_kline_adv(monkeypatch) -> None:
    """tick 存在 → last/bid/ask 取 tick; adv 取 K线 volume 均值。"""
    now = datetime.now(timezone.utc)
    records = [
        _make_kline("600519.SH", datetime(2026, 7, d, tzinfo=timezone.utc), Decimal(str(d * 1000)))
        for d in range(1, 21)  # 20 个交易日
    ]
    _patch_load_kline(monkeypatch, records)
    fake_redis = _FakeRedis(
        {
            tick_latest_key("600519.SH"): {"price": "100.5", "bid1": "100.4", "ask1": "100.6"},
        }
    )
    provider = RedisKlineMarketContextProvider(redis_conn=fake_redis)

    ctx = provider.get_context("600519")
    assert ctx.last_price == Decimal("100.5")
    assert ctx.bid_price == Decimal("100.4")
    assert ctx.ask_price == Decimal("100.6")
    # adv = sum(volumes)/20 = sum(1000..20000)/20
    expected_adv = sum((Decimal(str(d * 1000)) for d in range(1, 21)), Decimal("0")) / Decimal(20)
    assert ctx.adv == expected_adv


def test_redis_provider_falls_back_to_kline_close_when_tick_missing(monkeypatch) -> None:
    """tick 缺失 → last_price 用最近 K线 close, bid/ask=None (不报错)。"""
    now = datetime.now(timezone.utc)
    records = [
        _make_kline("600519.SH", datetime(2026, 7, d, tzinfo=timezone.utc), Decimal("10000"), Decimal("88.8"))
        for d in range(1, 21)
    ]
    _patch_load_kline(monkeypatch, records)
    provider = RedisKlineMarketContextProvider(redis_conn=_FakeRedis({}))

    ctx = provider.get_context("600519")
    assert ctx.last_price == Decimal("88.8")
    assert ctx.bid_price is None
    assert ctx.ask_price is None


def test_redis_provider_raises_when_no_kline(monkeypatch) -> None:
    """无任何 K线 → 无 ADV → AlgoError (即使 tick 存在)。"""
    _patch_load_kline(monkeypatch, [])
    fake_redis = _FakeRedis({tick_latest_key("600519.SH"): {"price": "100"}})
    provider = RedisKlineMarketContextProvider(redis_conn=fake_redis)

    with pytest.raises(AlgoError, match="ADV"):
        provider.get_context("600519")


def test_redis_provider_raises_when_all_suspended(monkeypatch) -> None:
    """K线全停牌 (volume=0) → 无有效 ADV → AlgoError。"""
    now = datetime.now(timezone.utc)
    records = [
        NormalizedMarketData(
            close=Decimal("100"),
            data_source="test",
            high=Decimal("100"),
            idempotency_key=f"s:{d}",
            low=Decimal("100"),
            open=Decimal("100"),
            symbol="600519.SH",
            timestamp=datetime(2026, 7, d, tzinfo=timezone.utc),
            volume=Decimal("0"),
            is_suspended=True,
        )
        for d in range(1, 10)
    ]
    _patch_load_kline(monkeypatch, records)
    provider = RedisKlineMarketContextProvider(redis_conn=_FakeRedis({}))
    with pytest.raises(AlgoError, match="ADV"):
        provider.get_context("600519")


def test_redis_provider_redis_failure_degrades_to_kline(monkeypatch) -> None:
    """Redis hgetall 抛异常 → 降级到 K线 close (best-effort, 不阻断)。"""
    now = datetime.now(timezone.utc)

    class _BoomRedis:
        def hgetall(self, key: str) -> dict[str, str]:
            raise RuntimeError("redis down")

    records = [
        _make_kline("600519.SH", datetime(2026, 7, d, tzinfo=timezone.utc), Decimal("10000"), Decimal("77.7"))
        for d in range(1, 21)
    ]
    _patch_load_kline(monkeypatch, records)
    provider = RedisKlineMarketContextProvider(redis_conn=_BoomRedis())

    ctx = provider.get_context("600519")
    assert ctx.last_price == Decimal("77.7")  # 降级到 K线 close
    assert ctx.adv > 0


def test_redis_provider_empty_symbol_raises() -> None:
    provider = RedisKlineMarketContextProvider(redis_conn=_FakeRedis({}))
    with pytest.raises(AlgoError, match="symbol"):
        provider.get_context("")
