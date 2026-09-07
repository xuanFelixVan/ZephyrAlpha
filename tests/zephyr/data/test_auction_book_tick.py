# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""auction_book 竞价簿 tick 解析单元测试（#ARCH-DATA-020 条件②，mock miniqmt 不触库不触网）。

覆盖：
- _parse_auction_book_tick 涨跌停价：无条件按 pre_close×(1±pct) Decimal HALF_UP 到分，
  幅度=单一真源 AkshareIngestProvider._limit_pct_of（主板 ST 2026-07-06 起 10%/此前 5%
  边界、创业板/科创板 20% ST 不打折、北交所 30%）；
- stockStatus 0x04/0x08 位无关性（位推断已废弃，锁死防回归）；
- pre_close 缺失/非正、未知板块、日期缺失 → (0.0, 0.0)（本表价格列缺数据约定）；
- 返回 tuple 形状契约（33 元素/列序/data_source）；
- _fetch_auction_book 集成：ST 集加载失败 fail-open（warning+非 ST 近似，现行规则下
  数值影响=0 的强断言）。
"""

from __future__ import annotations

import datetime
import sys
from unittest.mock import MagicMock

import pytest

from zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider
from zephyr.data.provider_base import FetchPayload

D = datetime.date  # 简写


def _tick(pre: float, *, timetag: str = "20260703091503000", stock_status: int = 0) -> dict:
    """合成一条 get_full_tick tick dict（键名=provider 实证口径）。"""
    return {
        "timetag": timetag,
        "lastPrice": 10.00,
        "lastClose": pre,
        "volume": 1000.0,
        "amount": 1e6,
        "open": 9.90,
        "high": 10.10,
        "low": 9.80,
        "stockStatus": stock_status,
        "bidPrice": [9.99, 9.98, 9.97, 9.96, 9.95],
        "bidVol": [100, 200, 300, 400, 500],
        "askPrice": [10.01, 10.02, 10.03, 10.04, 10.05],
        "askVol": [110, 220, 330, 440, 550],
    }


def _parse(pre, symbol, trade_date, *, st_codes=frozenset(), limit_date=None, stock_status=0):
    p = MiniQmtIngestProvider()
    return p._parse_auction_book_tick(
        _tick(pre, stock_status=stock_status),
        symbol,
        trade_date,
        st_codes=st_codes,
        limit_date=limit_date,
    )


class TestParseAuctionBookTick:
    def test_main_board_non_st_10pct(self):
        row = _parse(10.00, "600000", "2026-09-07", limit_date=D(2026, 9, 7))
        assert (row[10], row[11]) == (11.00, 9.00)

    def test_main_board_st_date_boundary(self):
        # 主板 ST：2026-07-03（生效日前）5% → 07-06（生效日）10%（沪深交易所《交易规则（2026年修订）》）
        st = {"601398", "000651"}
        for sym in ("601398", "000651"):
            legacy = _parse(10.00, sym, "2026-07-03", st_codes=st, limit_date=D(2026, 7, 3))
            assert (legacy[10], legacy[11]) == (10.50, 9.50), sym
            current = _parse(10.00, sym, "2026-07-06", st_codes=st, limit_date=D(2026, 7, 6))
            assert (current[10], current[11]) == (11.00, 9.00), sym

    def test_chinext_and_star_20pct_st_indifferent(self):
        # 创业板/科创板 20%（ST 不打折——st_codes 含与不含同值）
        for sym in ("300001", "688001"):
            a = _parse(10.00, sym, "2026-09-07", st_codes={sym}, limit_date=D(2026, 9, 7))
            b = _parse(10.00, sym, "2026-09-07", st_codes=set(), limit_date=D(2026, 9, 7))
            assert (a[10], a[11]) == (12.00, 8.00), sym
            assert a[10] == b[10] and a[11] == b[11], sym

    def test_bse_30pct(self):
        row = _parse(10.00, "830001", "2026-09-07", limit_date=D(2026, 9, 7))
        assert (row[10], row[11]) == (13.00, 7.00)

    def test_decimal_half_up_boundary(self):
        # 10.35×1.1=11.385 → HALF_UP 11.39；×0.9=9.315 → 9.32（Decimal 域精确乘，
        # 与 stk_limit 管道逐分一致；银行家舍入会得 11.38/9.32）
        row = _parse(10.35, "600000", "2026-09-07", limit_date=D(2026, 9, 7))
        assert (row[10], row[11]) == (11.39, 9.32)

    def test_pre_close_missing_or_nonpositive(self):
        for pre in (None, 0.0, -1.0):
            row = _parse(pre, "600000", "2026-09-07", limit_date=D(2026, 9, 7))
            assert (row[10], row[11]) == (0.0, 0.0)
            assert len(row) == 33 and row[0] == "2026-09-07" and row[2] == "600000"

    def test_unknown_board_zero(self):
        row = _parse(10.00, "900001", "2026-09-07", limit_date=D(2026, 9, 7))
        assert (row[10], row[11]) == (0.0, 0.0)

    def test_limit_date_missing_via_trade_date_fallback(self):
        # limit_date 缺省时由 trade_date 字符串兜底解析（_safe_parse_iso_date）
        row = _parse(10.00, "600000", "2026-07-03")
        assert (row[10], row[11]) == (11.00, 9.00)

    def test_trade_date_unparseable_zero(self):
        row = _parse(10.00, "600000", "not-a-date")
        assert (row[10], row[11]) == (0.0, 0.0)

    def test_stock_status_bit_no_effect(self):
        # stockStatus 0x04/0x08 位推断已废弃：任意位组合下价格列恒等（锁死无条件计算）
        rows = [
            _parse(10.00, "600000", "2026-09-07", limit_date=D(2026, 9, 7), stock_status=s)
            for s in (0, 0x04, 0x08, 0xFF)
        ]
        refs = [(r[10], r[11]) for r in rows]
        assert refs == [(11.00, 9.00)] * 4

    def test_row_shape_contract(self):
        row = _parse(10.00, "600000", "2026-09-07", limit_date=D(2026, 9, 7))
        assert len(row) == 33
        assert row[0] == "2026-09-07" and row[2] == "600000"
        assert row[-1] == "miniqmt"


def _payload() -> FetchPayload:
    return FetchPayload(
        table="c1_market.market_auction_book",
        symbols=None,
        start=D(2026, 9, 7),
        end=D(2026, 9, 7),
        incremental=True,
        extra={"capability": "auction_book"},
    )


def _policy() -> MagicMock:
    return MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)


def _mock_xtdata(monkeypatch, sector_list, ticks):
    mock_xtdata = MagicMock()
    mock_xtdata.get_stock_list_in_sector.side_effect = lambda name: sector_list or []
    mock_xtdata.get_full_tick.side_effect = lambda batch: {c: ticks[c] for c in batch if c in ticks}
    mock_xt = MagicMock()
    mock_xt.xtdata = mock_xtdata
    monkeypatch.setitem(sys.modules, "xtquant", mock_xt)
    monkeypatch.setitem(sys.modules, "xtquant.xtdata", mock_xtdata)
    return mock_xtdata


class TestFetchAuctionBookDegraded:
    def test_st_load_fail_fail_open(self, monkeypatch, caplog):
        # ST 集加载失败（ok=False）→ warning + 行照常产出，按非 ST 幅度近似；
        # 现行规则下主板 ST=非 ST=10%，数值与健康路径完全一致（降级零数值影响的强断言）
        import sys

        ticks = {
            "601398.SH": _tick(10.00),
            "600000.SH": _tick(10.00),
        }
        _mock_xtdata(monkeypatch, sector_list=list(ticks), ticks=ticks)
        monkeypatch.setattr(
            "zephyr.data.market_breadth_collector.load_current_st_codes",
            lambda **kw: (set(), False),
        )
        with caplog.at_level("WARNING"):
            results = list(MiniQmtIngestProvider()._fetch_auction_book(_payload(), _policy()))
        assert len(results) == 1 and results[0].error is None
        rows = results[0].rows
        assert len(rows) == 2
        by_sym = {r[2]: r for r in rows}
        assert (by_sym["601398"][10], by_sym["601398"][11]) == (11.00, 9.00)
        assert (by_sym["600000"][10], by_sym["600000"][11]) == (11.00, 9.00)
        assert any("ST 集加载失败" in rec.getMessage() for rec in caplog.records)

    def test_st_load_ok_uses_st_codes(self, monkeypatch):
        # ST 集正常加载：现行规则下 ST 与非 ST 同 10%，但走的是正确真源链路
        import sys

        ticks = {"601398.SH": _tick(10.00)}
        _mock_xtdata(monkeypatch, sector_list=list(ticks), ticks=ticks)
        monkeypatch.setattr(
            "zephyr.data.market_breadth_collector.load_current_st_codes",
            lambda **kw: ({"601398"}, True),
        )
        results = list(MiniQmtIngestProvider()._fetch_auction_book(_payload(), _policy()))
        rows = results[0].rows
        assert len(rows) == 1 and (rows[0][10], rows[0][11]) == (11.00, 9.00)
