# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_daban_board_event_deriver
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.daban_board_event_deriver
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 假数据不触网不触库（ch_client/pro 全注入）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=打板事件推导逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-daban_board_event_derive_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""daban_board_event_deriver 打板回测历史事件推导器 单元测试（假数据不触真 CH/tushare）。

覆盖：板块分类/规则涨停价（HALF_UP 边界/ST 5%/科创创业 20%/北证 30%）、日频事件推导
（触板/封住/一字/连板链/eps 容差/无涨停价跳过）、分钟级首触与开板计数（下限口径）、
tick 封单代理（尾盘买一）、tushare 涨停价拉取（mock pro）、collect 端到端
（库内 stk_limit 优先/缺失日走 tushare/限速注入/窗口过滤/开关切换）、CSV 三态。
"""

from __future__ import annotations

import datetime
import json
from dataclasses import asdict
from unittest.mock import MagicMock

import pytest

from src.zephyr.data.implementations.daban_board_event_deriver import (
    INSERT_COLUMNS,
    LIMIT_EPS,
    DabanBoardEvent,
    LimitPriceRow,
    board_of,
    collect_derived_events,
    derive_daily_events,
    enrich_intraday,
    enrich_seal_ticks,
    fetch_stk_limit_tushare,
    limit_prices_to_csv,
    rule_limit_price,
    to_csv,
)

D = datetime.date


# ---------------------------------------------------------------------------
# 合成数据工厂
# ---------------------------------------------------------------------------


def _kline(d: str, sym: str, o: float, h: float, l: float, c: float) -> dict:
    return {"trade_date": d, "symbol": sym, "open": o, "high": h, "low": l, "close": c}


def _lp(d: str, sym: str, up: float, down: float = 9.0, src: str = "ch_stk_limit") -> LimitPriceRow:
    return LimitPriceRow(
        trade_date=d,
        symbol=sym,
        pre_close=None,
        limit_up=up,
        limit_down=down,
        board=board_of(sym),
        st_flag=None,
        data_source=src,
    )


def _min_bar(d: str, sym: str, t: str, h: float, l: float) -> dict:
    return {"trade_date": d, "symbol": sym, "trade_time": f"{d} {t}", "high": h, "low": l}


def _tick(d: str, sym: str, t: str, bp: float | None, bv: int | None) -> dict:
    return {"trade_date": d, "symbol": sym, "timestamp": f"{d} {t}", "bid_price": bp, "bid_volume": bv}


# ---------------------------------------------------------------------------
# board_of / rule_limit_price
# ---------------------------------------------------------------------------


class TestBoardOf:
    def test_prefix_classification(self):
        assert board_of("600519") == "sh_main"
        assert board_of("688981") == "star"
        assert board_of("000001") == "sz_main"
        assert board_of("002594") == "sz_main"
        assert board_of("300750") == "chinext"
        assert board_of("430047") == "bj"
        assert board_of("830799") == "bj"
        assert board_of("920001") == "bj"

    def test_other(self):
        assert board_of("110000") == "other"
        assert board_of("") == "other"


class TestRuleLimitPrice:
    def test_main_board_10pct(self):
        up, down = rule_limit_price(9.68, "sh_main", False)
        assert up == pytest.approx(10.65)  # 9.68*1.1=10.648 → HALF_UP 10.65
        assert down == pytest.approx(8.71)

    def test_main_board_st_5pct(self):
        up, down = rule_limit_price(9.68, "sz_main", True)
        assert up == pytest.approx(10.16)  # 9.68*1.05=10.164 → 10.16

    def test_star_chinext_20pct(self):
        assert rule_limit_price(10.0, "star", False)[0] == pytest.approx(12.00)
        assert rule_limit_price(10.0, "chinext", True)[0] == pytest.approx(12.00)  # ST 不打折

    def test_bj_30pct(self):
        assert rule_limit_price(10.0, "bj", False)[0] == pytest.approx(13.00)

    def test_half_up_edge(self):
        # 4.55*1.1=5.005 → HALF_UP 5.01（Python round 银行家舍入会出 5.00）
        assert rule_limit_price(4.55, "sh_main", False)[0] == pytest.approx(5.01)

    def test_invalid_inputs(self):
        assert rule_limit_price(None, "sh_main", False) is None
        assert rule_limit_price(0, "sh_main", False) is None
        assert rule_limit_price(-1.0, "sh_main", False) is None
        assert rule_limit_price(10.0, "other", False) is None


# ---------------------------------------------------------------------------
# derive_daily_events
# ---------------------------------------------------------------------------


class TestDeriveDailyEvents:
    def test_basic_flags(self):
        rows = [
            _kline("2026-08-20", "600000", 9.9, 10.0, 9.8, 9.95),
            _kline("2026-08-21", "600000", 10.0, 10.65, 10.0, 10.65),  # 触板且封住
            _kline("2026-08-21", "000001", 9.0, 9.5, 8.9, 9.4),  # 未触板 → 无事件
        ]
        lps = {("2026-08-21", "600000"): _lp("2026-08-21", "600000", 10.65)}
        ev = derive_daily_events(rows, lps)
        assert len(ev) == 1
        e = ev[0]
        assert e.touched == 1 and e.close_sealed == 1 and e.is_one_word == 0
        assert e.consec_limit == 1 and e.limit_src == "ch_stk_limit"
        assert e.pre_close == pytest.approx(9.95)
        assert e.limit_up_price == pytest.approx(10.65)

    def test_one_word_board(self):
        rows = [_kline("2026-08-21", "600000", 10.65, 10.65, 10.65, 10.65)]
        lps = {("2026-08-21", "600000"): _lp("2026-08-21", "600000", 10.65)}
        (e,) = derive_daily_events(rows, lps)
        assert e.touched == 1 and e.close_sealed == 1 and e.is_one_word == 1

    def test_touched_not_sealed(self):
        rows = [_kline("2026-08-21", "600000", 10.0, 10.65, 9.9, 10.2)]  # 炸板未回封
        lps = {("2026-08-21", "600000"): _lp("2026-08-21", "600000", 10.65)}
        (e,) = derive_daily_events(rows, lps)
        assert e.touched == 1 and e.close_sealed == 0 and e.is_one_word == 0

    def test_eps_tolerance(self):
        # close 距涨停价 0.0005 < LIMIT_EPS → 判封住（Decimal(18,4) 浮点安全）
        rows = [_kline("2026-08-21", "600000", 10.0, 10.6495, 10.0, 10.6495)]
        lps = {("2026-08-21", "600000"): _lp("2026-08-21", "600000", 10.65)}
        (e,) = derive_daily_events(rows, lps)
        assert LIMIT_EPS > 0
        assert e.close_sealed == 1

    def test_missing_limit_price_skipped(self):
        rows = [_kline("2026-08-21", "600000", 10.0, 10.65, 10.0, 10.65)]
        assert derive_daily_events(rows, {}) == []

    def test_consec_chain(self):
        rows = [
            _kline("2026-08-18", "600000", 9.0, 9.0, 9.0, 9.0),
            _kline("2026-08-19", "600000", 9.5, 9.9, 9.4, 9.9),  # 封住 1 板
            _kline("2026-08-20", "600000", 10.2, 10.89, 10.1, 10.5),  # 触板未封 → 链断
            _kline("2026-08-21", "600000", 10.6, 11.0, 10.5, 11.0),  # 封住 1 板（重新计）
            _kline("2026-08-24", "600000", 11.5, 12.1, 11.4, 12.1),  # 封住 2 板
        ]
        lps = {
            ("2026-08-19", "600000"): _lp("2026-08-19", "600000", 9.90),
            ("2026-08-20", "600000"): _lp("2026-08-20", "600000", 10.89),
            ("2026-08-21", "600000"): _lp("2026-08-21", "600000", 11.00),
            ("2026-08-24", "600000"): _lp("2026-08-24", "600000", 12.10),
        }
        ev = derive_daily_events(rows, lps)
        got = {(e.trade_date): e.consec_limit for e in ev}
        assert got == {"2026-08-19": 1, "2026-08-20": 0, "2026-08-21": 1, "2026-08-24": 2}

    def test_unsorted_input_and_multi_symbol(self):
        rows = [
            _kline("2026-08-21", "000001", 11.0, 11.0, 11.0, 11.0),
            _kline("2026-08-20", "600000", 10.0, 10.65, 10.0, 10.65),
            _kline("2026-08-21", "600000", 11.0, 11.72, 11.0, 11.72),
        ]
        lps = {
            ("2026-08-20", "600000"): _lp("2026-08-20", "600000", 10.65),
            ("2026-08-21", "600000"): _lp("2026-08-21", "600000", 11.72),
            ("2026-08-21", "000001"): _lp("2026-08-21", "000001", 11.00),
        }
        ev = derive_daily_events(rows, lps)
        m = {(e.trade_date, e.symbol): e for e in ev}
        assert m[("2026-08-20", "600000")].consec_limit == 1
        assert m[("2026-08-21", "600000")].consec_limit == 2
        assert m[("2026-08-21", "000001")].consec_limit == 1
        # 输出按 (trade_date, symbol) 排序，确定性
        assert [(e.trade_date, e.symbol) for e in ev] == sorted((e.trade_date, e.symbol) for e in ev)


# ---------------------------------------------------------------------------
# enrich_intraday（分钟级首触/开板，下限口径）
# ---------------------------------------------------------------------------


def _event(d: str, sym: str, up: float, sealed: int = 1) -> DabanBoardEvent:
    return DabanBoardEvent(
        trade_date=d,
        symbol=sym,
        board=board_of(sym),
        st_flag=0,
        pre_close=9.68,
        limit_up_price=up,
        open=10.0,
        high=up,
        low=9.9,
        close=up if sealed else 10.0,
        touched=1,
        close_sealed=sealed,
        is_one_word=0,
        first_touch_time=None,
        open_board_count=None,
        seal_bid_volume=None,
        seal_amount_proxy=None,
        consec_limit=1,
        limit_src="ch_stk_limit",
    )


class TestEnrichIntraday:
    def test_first_touch_and_open_count(self):
        ev = [_event("2026-08-21", "600000", 10.65)]
        bars = [
            _min_bar("2026-08-21", "600000", "09:31:00", 10.20, 10.00),
            _min_bar("2026-08-21", "600000", "09:32:00", 10.65, 10.30),  # 首触（high 达标但 low 破）
            _min_bar("2026-08-21", "600000", "09:33:00", 10.65, 10.65),  # 封住分钟
            _min_bar("2026-08-21", "600000", "09:34:00", 10.65, 10.65),
            _min_bar("2026-08-21", "600000", "10:15:00", 10.60, 10.40),  # 开板 1
            _min_bar("2026-08-21", "600000", "10:16:00", 10.65, 10.65),  # 回封
            _min_bar("2026-08-21", "600000", "13:40:00", 10.55, 10.30),  # 开板 2
            _min_bar("2026-08-21", "600000", "13:41:00", 10.50, 10.30),  # 连续开（不重复计）
            _min_bar("2026-08-21", "600000", "14:00:00", 10.65, 10.65),  # 回封至收盘
        ]
        (e,) = enrich_intraday(ev, bars)
        assert e.first_touch_time == "09:32:00"
        assert e.open_board_count == 2

    def test_one_word_zero_open(self):
        ev = [_event("2026-08-21", "600000", 10.65)]
        bars = [
            _min_bar("2026-08-21", "600000", "09:31:00", 10.65, 10.65),
            _min_bar("2026-08-21", "600000", "09:32:00", 10.65, 10.65),
        ]
        (e,) = enrich_intraday(ev, bars)
        assert e.first_touch_time == "09:31:00"
        assert e.open_board_count == 0

    def test_touch_never_minute_sealed(self):
        ev = [_event("2026-08-21", "600000", 10.65, sealed=0)]
        bars = [
            _min_bar("2026-08-21", "600000", "10:00:00", 10.65, 10.30),  # 触板但分钟未封
            _min_bar("2026-08-21", "600000", "10:01:00", 10.50, 10.20),
        ]
        (e,) = enrich_intraday(ev, bars)
        assert e.first_touch_time == "10:00:00"
        assert e.open_board_count == 0

    def test_no_minute_rows_leaves_none(self):
        ev = [_event("2026-08-21", "600000", 10.65)]
        (e,) = enrich_intraday(ev, [])
        assert e.first_touch_time is None and e.open_board_count is None

    def test_datetime_trade_time_accepted(self):
        ev = [_event("2026-08-21", "600000", 10.65)]
        bars = [
            {
                "trade_date": "2026-08-21",
                "symbol": "600000",
                "trade_time": datetime.datetime(2026, 8, 21, 9, 45, 30),
                "high": 10.65,
                "low": 10.65,
            }
        ]
        (e,) = enrich_intraday(ev, bars)
        assert e.first_touch_time == "09:45:30"

    def test_symbol_routing_isolation(self):
        ev = [_event("2026-08-21", "600000", 10.65), _event("2026-08-21", "000001", 11.0)]
        bars = [_min_bar("2026-08-21", "000001", "09:50:00", 11.0, 11.0)]
        out = enrich_intraday(ev, bars)
        assert out[0].first_touch_time is None
        assert out[1].first_touch_time == "09:50:00"


# ---------------------------------------------------------------------------
# enrich_seal_ticks（封单代理：尾盘买一）
# ---------------------------------------------------------------------------


class TestEnrichSealTicks:
    def test_last_qualifying_tick_wins(self):
        ev = [_event("2026-08-21", "600000", 10.65)]
        ticks = [
            _tick("2026-08-21", "600000", "14:56:00", 10.65, 1000),
            _tick("2026-08-21", "600000", "15:00:00", 10.65, 55991),  # 尾盘最后达标 tick
            _tick("2026-08-21", "600000", "15:30:00", None, 0),  # 收盘价但无买一档 → 不覆盖
        ]
        (e,) = enrich_seal_ticks(ev, ticks)
        assert e.seal_bid_volume == 55991
        assert e.seal_amount_proxy == pytest.approx(55991 * 100 * 10.65, abs=0.01)

    def test_not_sealed_event_skipped(self):
        ev = [_event("2026-08-21", "600000", 10.65, sealed=0)]
        ticks = [_tick("2026-08-21", "600000", "15:00:00", 10.65, 1000)]
        (e,) = enrich_seal_ticks(ev, ticks)
        assert e.seal_bid_volume is None and e.seal_amount_proxy is None

    def test_no_qualifying_tick(self):
        ev = [_event("2026-08-21", "600000", 10.65)]
        ticks = [_tick("2026-08-21", "600000", "15:00:00", 10.50, 1000)]  # 买一低于涨停
        (e,) = enrich_seal_ticks(ev, ticks)
        assert e.seal_bid_volume is None

    def test_none_bid_volume_skipped(self):
        ev = [_event("2026-08-21", "600000", 10.65)]
        ticks = [_tick("2026-08-21", "600000", "15:00:00", 10.65, None)]
        (e,) = enrich_seal_ticks(ev, ticks)
        assert e.seal_bid_volume is None


# ---------------------------------------------------------------------------
# fetch_stk_limit_tushare（mock pro 不触网）
# ---------------------------------------------------------------------------


class TestFetchStkLimitTushare:
    def test_rows_mapped(self):
        import pandas as pd

        pro = MagicMock()
        pro.stk_limit.return_value = pd.DataFrame(
            {
                "trade_date": ["20260821", "20260821"],
                "ts_code": ["600000.SH", "000001.SZ"],
                "up_limit": [10.65, 11.0],
                "down_limit": [8.71, 9.0],
            }
        )
        rows = fetch_stk_limit_tushare("2026-08-21", pro=pro)
        assert len(rows) == 2
        r0 = rows[0]
        assert r0.symbol == "600000" and r0.limit_up == pytest.approx(10.65)
        assert r0.data_source == "tushare_stk_limit" and r0.board == "sh_main"
        pro.stk_limit.assert_called_once_with(trade_date="20260821")

    def test_empty_and_exception_tolerant(self):
        pro = MagicMock()
        pro.stk_limit.return_value = None
        assert fetch_stk_limit_tushare("2026-08-21", pro=pro) == []
        pro.stk_limit.side_effect = RuntimeError("no permission")
        assert fetch_stk_limit_tushare("2026-08-21", pro=pro) == []

    def test_bad_date_fail_closed(self):
        with pytest.raises(ValueError):
            fetch_stk_limit_tushare("2026/08/21", pro=MagicMock())


# ---------------------------------------------------------------------------
# collect_derived_events 端到端（假 ch_client SQL 路由 + mock pro）
# ---------------------------------------------------------------------------


def _fake_ch(kline_rows, stk_limit_rows, min_rows=None, tick_rows=None, st_rows=None):
    """按 SQL 子串路由的假 ch_client（对齐既有测试口径）。"""
    min_rows = min_rows or []
    tick_rows = tick_rows or []
    st_rows = st_rows or []
    client = MagicMock()

    def side_effect(sql, params=None):
        if "c1_market.kline_daily" in sql:
            return [
                (
                    r["trade_date"],
                    r["symbol"],
                    r["open"],
                    r["high"],
                    r["low"],
                    r["close"],
                    r.get("ingest_ts", "2026-08-21 18:00:00"),
                )
                for r in kline_rows
            ]
        if "c1_market.stk_limit" in sql:
            return list(stk_limit_rows)
        if "c1_market.st_stock_list" in sql:
            return list(st_rows)
        if "c1_market.kline_1min" in sql:
            d = sql.split("toDate('")[1].split("')")[0]
            return [
                (r["trade_date"], r["symbol"], r["trade_time"], r["high"], r["low"])
                for r in min_rows
                if r["trade_date"] == d
            ]
        if "c1_market.tick_data" in sql:
            d = sql.split("toDate('")[1].split("')")[0]
            return [
                (r["symbol"], r["timestamp"], r["bid_price"], r["bid_volume"])
                for r in tick_rows
                if r["trade_date"] == d
            ]
        raise AssertionError(f"unexpected SQL: {sql}")

    client.execute.side_effect = side_effect
    return client


class TestCollectDerivedEvents:
    def _stk_rows(self):
        # 库内 stk_limit 仅覆盖 08-21（验证 库内优先 + 缺失日走 tushare）
        # 列序对齐 SELECT: trade_date, symbol, pre_close, limit_up, limit_down, st_flag
        return [("2026-08-21", "600000", 9.68, 10.65, 8.71, 0)]

    def test_end_to_end_with_tushare_fallback(self):
        kline = [
            _kline("2026-08-20", "600000", 9.9, 10.65, 9.9, 10.65),  # 封住（tushare 供价）
            _kline("2026-08-21", "600000", 10.7, 11.72, 10.7, 11.72),  # 封住（库内供价）
        ]
        ch = _fake_ch(kline, self._stk_rows())
        import pandas as pd

        pro = MagicMock()
        pro.stk_limit.return_value = pd.DataFrame(
            {"trade_date": ["20260820"], "ts_code": ["600000.SH"], "up_limit": [10.65], "down_limit": [8.71]}
        )
        ev = collect_derived_events(
            "2026-08-20",
            "2026-08-21",
            ch_client=ch,
            pro=pro,
            intraday=False,
            seal_ticks=False,
            sleep=lambda s: None,
        )
        assert len(ev) == 2
        e0, e1 = ev
        assert e0.limit_src == "tushare_stk_limit" and e0.close_sealed == 1 and e0.consec_limit == 1
        assert e1.limit_src == "ch_stk_limit" and e1.consec_limit == 2
        # 库内覆盖日不调用 tushare
        called_dates = [c.kwargs.get("trade_date") for c in pro.stk_limit.call_args_list]
        assert "20260821" not in called_dates and "20260820" in called_dates

    def test_intraday_and_tick_enrichment(self):
        kline = [_kline("2026-08-21", "600000", 10.0, 10.65, 10.0, 10.65)]
        mins = [
            _min_bar("2026-08-21", "600000", "09:32:00", 10.65, 10.65),
            _min_bar("2026-08-21", "600000", "10:15:00", 10.40, 10.30),
            _min_bar("2026-08-21", "600000", "11:00:00", 10.65, 10.65),
        ]
        ticks = [_tick("2026-08-21", "600000", "15:00:00", 10.65, 8000)]
        ch = _fake_ch(kline, self._stk_rows(), min_rows=mins, tick_rows=ticks)
        ev = collect_derived_events(
            "2026-08-21",
            "2026-08-21",
            ch_client=ch,
            pro=MagicMock(),
            sleep=lambda s: None,
        )
        (e,) = ev
        assert e.first_touch_time == "09:32:00"
        assert e.open_board_count == 1
        assert e.seal_bid_volume == 8000
        assert e.seal_amount_proxy == pytest.approx(8000 * 100 * 10.65, abs=0.01)

    def test_ticks_gated_by_ticks_from(self):
        kline = [_kline("2026-06-01", "600000", 10.0, 10.65, 10.0, 10.65)]
        ch = _fake_ch(
            kline,
            [("2026-06-01", "600000", 9.68, 10.65, 8.71, 0)],
            tick_rows=[_tick("2026-06-01", "600000", "15:00:00", 10.65, 8000)],
        )
        ev = collect_derived_events(
            "2026-06-01",
            "2026-06-01",
            ch_client=ch,
            pro=MagicMock(),
            sleep=lambda s: None,
            ticks_from=D(2026, 7, 1),
        )
        (e,) = ev
        assert e.seal_bid_volume is None  # 06-01 < ticks_from → 不查 tick

    def test_symbols_filter_and_empty_window(self):
        kline = [
            _kline("2026-08-21", "600000", 10.0, 10.65, 10.0, 10.65),
            _kline("2026-08-21", "000001", 10.0, 11.0, 10.0, 11.0),
        ]
        stk = [("2026-08-21", "600000", 9.68, 10.65, 8.71, 0), ("2026-08-21", "000001", 10.0, 11.0, 9.0, 0)]
        ch = _fake_ch(kline, stk)
        ev = collect_derived_events(
            "2026-08-21",
            "2026-08-21",
            ch_client=ch,
            pro=MagicMock(),
            symbols={"000001"},
            intraday=False,
            seal_ticks=False,
            sleep=lambda s: None,
        )
        assert [(e.symbol) for e in ev] == ["000001"]
        # 空窗口（无 kline 行）
        ch2 = _fake_ch([], [])
        assert (
            collect_derived_events(
                "2026-08-21",
                "2026-08-21",
                ch_client=ch2,
                pro=MagicMock(),
                intraday=False,
                seal_ticks=False,
                sleep=lambda s: None,
            )
            == []
        )

    def test_bad_date_range_fail_closed(self):
        with pytest.raises(ValueError):
            collect_derived_events("2026-08-21", "2026-08-20", ch_client=MagicMock())
        with pytest.raises(ValueError):
            collect_derived_events("2026/08/01", "2026-08-20", ch_client=MagicMock())

    def test_kline_duplicate_rows_dedup_latest_ingest(self):
        """kline_daily 重复 (date,symbol) 行 → 按 ingest_ts 取最新，事件不重复。"""
        dup_old = _kline("2026-08-21", "600000", 10.0, 10.65, 10.0, 10.50)
        dup_old["ingest_ts"] = "2026-08-21 18:00:00"
        dup_new = _kline("2026-08-21", "600000", 10.0, 10.65, 10.0, 10.65)
        dup_new["ingest_ts"] = "2026-08-23 19:06:15"
        ch = _fake_ch([dup_old, dup_new], self._stk_rows())
        ev = collect_derived_events(
            "2026-08-21",
            "2026-08-21",
            ch_client=ch,
            pro=MagicMock(),
            intraday=False,
            seal_ticks=False,
            sleep=lambda s: None,
        )
        assert len(ev) == 1
        assert ev[0].close == pytest.approx(10.65)
        assert ev[0].close_sealed == 1


# ---------------------------------------------------------------------------
# CSV 中间层
# ---------------------------------------------------------------------------


class TestCsv:
    def test_events_csv_three_states(self, tmp_path):
        p = tmp_path / "ev.csv"
        assert to_csv([], p) == ""  # 空 → 不建文件
        e = _event("2026-08-21", "600000", 10.65)
        out = to_csv([e], p)
        assert out == str(p)
        lines = p.read_text(encoding="utf-8").splitlines()
        assert lines[0].split(",") == list(INSERT_COLUMNS)
        assert len(lines) == 2
        # append 不重复 header
        to_csv([e], p, append=True)
        lines = p.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 3 and sum(1 for x in lines if x.startswith("trade_date,")) == 1

    def test_limit_prices_csv(self, tmp_path):
        p = tmp_path / "lp.csv"
        lp = _lp("2026-08-21", "600000", 10.65)
        out = limit_prices_to_csv([lp], p)
        assert out == str(p)
        lines = p.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2 and "limit_up" in lines[0]
        assert limit_prices_to_csv([], tmp_path / "x.csv") == ""

    def test_frozen_dataclass_json_serializable(self):
        e = _event("2026-08-21", "600000", 10.65)
        json.dumps(asdict(e))
        json.dumps(asdict(_lp("2026-08-21", "600000", 10.65)))
