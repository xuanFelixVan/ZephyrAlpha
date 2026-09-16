# [A_test] module_id: MOD-L06_daban_load_producer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §test
# [MODULE] tests.ex_core.test_daban_load_producer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;零DB零时钟（fake 注入隔离 IO）
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/ex_core/test_daban_load_producer.py
# [TTL] task_bound
"""daban 四引擎应用层负载批产生产者测试（T3⑧ / 挖矿 LUE-1 治本）。

覆盖（全 fake IO / 零 DB / 零时钟）：
- seal_time_minutes_from_touch：A 股连续竞价时段折算（含一字/午休/下午扣午休/None）
- stock_change_pct：(close/pre_close−1)×100 + 昨收非正/缺→None
- events_to_load_rows：真封板家数窗口自产 + float_market_cap cap_map 注入真值 +
  缺字段 default 留痕（derived_fields JSON）+ 21 列键序
- load_rows_to_tuples：与 LOAD_INSERT_COLUMNS 同序（21 列）
- run_daily_batch：非空事件→FetchResult（table/columns/rows/last_key/elapsed_sec=0）；
  空事件→空 rows + warning（fail-visible，非静默）
- fetch_float_cap_map：TSV 解析万元→元 ×1e4 + 异常 fail-open 空 map
- ClickHouseDabanEngineLoadSource._parse_load_tsv：TSV→负载行（\\N→None、数值容错）
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from zephyr.data.implementations.daban_board_event_deriver import DabanBoardEvent
from zephyr.ex_core import daban_load_producer as P


def _evt(**kw) -> DabanBoardEvent:
    """构造最小合法 DabanBoardEvent（默认封住、有分钟/封单/昨收）。"""
    base = dict(
        trade_date="2026-09-11",
        symbol="300750.SZ",
        board="chinext",
        st_flag=0,
        pre_close=200.0,
        limit_up_price=240.0,
        open=210.0,
        high=240.0,
        low=205.0,
        close=240.0,
        touched=1,
        close_sealed=1,
        is_one_word=0,
        first_touch_time="09:41:00",
        open_board_count=0,
        seal_bid_volume=100000,
        seal_amount_proxy=2.5e8,
        consec_limit=3,
        limit_src="ch_stk_limit",
    )
    base.update(kw)
    return DabanBoardEvent(**base)


# ────────────────────────── seal_time_minutes_from_touch ──────────────────────────


@pytest.mark.parametrize(
    "touch, expected",
    [
        ("09:25:00", 0),      # 集合竞价一字 → 开盘即封最强
        ("09:30:00", 0),      # 开盘
        ("09:35:00", 5),      # 早盘 5 分钟
        ("11:30:00", 120),    # 午收
        ("12:00:00", 120),    # 午休钳到 120
        ("13:05:00", 125),    # 下午：(785-570)-90=125
        ("14:30:00", 210),
        ("15:00:00", 240),    # 封顶 240
        ("10:15", 45),        # HH:MM
        (None, None),         # 缺分钟 → default（非拍 0）
        ("", None),           # 非法 → None
    ],
)
def test_seal_time_minutes_from_touch(touch, expected):
    assert P.seal_time_minutes_from_touch(touch) == expected


# ────────────────────────── stock_change_pct ──────────────────────────


def test_stock_change_pct():
    assert P.stock_change_pct(240.0, 200.0) == pytest.approx(20.0)
    assert P.stock_change_pct(200.0, 200.0) == pytest.approx(0.0)
    assert P.stock_change_pct(None, 200.0) is None
    assert P.stock_change_pct(240.0, None) is None
    assert P.stock_change_pct(240.0, 0.0) is None      # 昨收非正 → None
    assert P.stock_change_pct(240.0, -1.0) is None


# ────────────────────────── events_to_load_rows ──────────────────────────


def test_events_to_load_rows_keys_and_order():
    rows = P.events_to_load_rows([_evt()], cap_map={("2026-09-11", "300750.SZ"): 5e9})
    assert len(rows) == 1
    assert list(rows[0].keys()) == list(P.LOAD_INSERT_COLUMNS)


def test_events_to_load_rows_real_fields():
    rows = P.events_to_load_rows(
        [_evt()],
        cap_map={("2026-09-11", "300750.SZ"): 5e9},
        market_context={"2026-09-11": {"breadth_ratio": 0.7, "change_pct": 1.2}},
    )
    r = rows[0]
    assert r["consec_limit"] == 3
    assert r["seal_amount"] == pytest.approx(2.5e8)
    assert r["float_market_cap"] == pytest.approx(5e9)        # cap_map 注入真值
    assert r["stock_change_pct"] == pytest.approx(20.0)       # 240/200-1
    assert r["seal_time_minutes"] == 11                       # 09:41 → 11
    assert r["market_breadth_ratio"] == pytest.approx(0.7)
    assert r["market_change_pct"] == pytest.approx(1.2)
    assert r["close_price"] == pytest.approx(240.0)
    derived = json.loads(r["derived_fields"])
    assert derived["float_market_cap"] == "real"
    assert derived["seal_amount"] == "real"


def test_events_to_load_rows_missing_cap_is_default():
    rows = P.events_to_load_rows([_evt()], cap_map=None)
    assert rows[0]["float_market_cap"] is None
    derived = json.loads(rows[0]["derived_fields"])
    assert derived["float_market_cap"] == "default"            # 显式缺省，非拍假值


def test_events_to_load_rows_sealed_counts_window_aggregate():
    # 两封板同 board + 一炸板（close_sealed=0，不计入家数）
    events = [
        _evt(symbol="300001.SZ"),
        _evt(symbol="300002.SZ"),
        _evt(symbol="300003.SZ", close_sealed=0),
    ]
    rows = P.events_to_load_rows(events)
    assert all(r["market_limit_up_count"] == 2 for r in rows)
    assert all(r["sector_limit_up_count"] == 2 for r in rows)  # 同 chinext


# ────────────────────────── load_rows_to_tuples ──────────────────────────


def test_load_rows_to_tuples_order():
    rows = P.events_to_load_rows([_evt()], cap_map={("2026-09-11", "300750.SZ"): 5e9})
    (tup,) = P.load_rows_to_tuples(rows)
    assert len(tup) == len(P.LOAD_INSERT_COLUMNS) == 21
    assert tup[P.LOAD_INSERT_COLUMNS.index("symbol")] == "300750.SZ"
    assert tup[P.LOAD_INSERT_COLUMNS.index("float_market_cap")] == pytest.approx(5e9)


# ────────────────────────── run_daily_batch ──────────────────────────


class _FakeEventSource:
    def __init__(self, events):
        self._events = events

    def fetch_events(self, start, end):
        return list(self._events)


def test_run_daily_batch_non_empty():
    res = P.run_daily_batch(
        dt.date(2026, 9, 11),
        event_source=_FakeEventSource([_evt()]),
        cap_source=lambda evs: {("2026-09-11", "300750.SZ"): 5e9},
    )
    assert res.table == P._TARGET_TABLE
    assert res.columns == list(P.LOAD_INSERT_COLUMNS)
    assert res.rows_fetched == 1
    assert res.elapsed_sec == 0.0                     # 零时钟（RULE-SCHEMA-TZ）
    assert res.last_key == "2026-09-11"


def test_run_daily_batch_empty_events_fail_visible(caplog):
    import logging

    with caplog.at_level(logging.WARNING):
        res = P.run_daily_batch(dt.date(2026, 9, 11), event_source=_FakeEventSource([]), cap_source=None)
    assert res.rows == []
    assert res.rows_fetched == 0
    assert "零打板事件" in caplog.text                 # 非静默


def test_run_daily_batch_cap_source_none_field_default():
    res = P.run_daily_batch(dt.date(2026, 9, 11), event_source=_FakeEventSource([_evt()]), cap_source=None)
    # rows 是 tuple；取 float_market_cap 位
    idx = P.LOAD_INSERT_COLUMNS.index("float_market_cap")
    assert res.rows[0][idx] is None


# ────────────────────────── fetch_float_cap_map (fake reader) ──────────────────────────


def test_fetch_float_cap_map_tsv_parse():
    tsv = "2026-09-11\t300750.SZ\t500000.0\n2026-09-11\t600519\t159405405.3\n"
    got = P.fetch_float_cap_map([_evt(), _evt(symbol="600519.SH")], reader=lambda sql: tsv)
    # 万元 ×1e4 → 元
    assert got[("2026-09-11", "300750.SZ")] == pytest.approx(5e9)
    assert got[("2026-09-11", "600519")] == pytest.approx(159405405.3 * 1e4)


def test_fetch_float_cap_map_skips_null_and_bad():
    tsv = "2026-09-11\t300750.SZ\t\\N\n2026-09-11\t000001\tNaNish\n2026-09-11\t600519\t1000.0\n"
    got = P.fetch_float_cap_map([_evt()], reader=lambda sql: tsv)
    assert ("2026-09-11", "300750.SZ") not in got       # NULL 跳过
    assert got.get(("2026-09-11", "600519")) == pytest.approx(1000.0 * 1e4)


def test_fetch_float_cap_map_fail_open(caplog):
    import logging

    def _boom(sql):
        raise RuntimeError("CH down")

    with caplog.at_level(logging.WARNING):
        got = P.fetch_float_cap_map([_evt()], reader=_boom)
    assert got == {}                                    # 异常降级空，非抛
    assert "float_market_cap" in caplog.text


def test_fetch_float_cap_map_empty_events():
    assert P.fetch_float_cap_map([]) == {}


# ────────────────────────── consumer PIT TSV parse ──────────────────────────


def test_parse_load_tsv_full_row():
    cols = list(P.LOAD_INSERT_COLUMNS)
    vals = {
        "trade_date": "2026-09-11",
        "symbol": "300750.SZ",
        "board": "chinext",
        "st_flag": "0",
        "consec_limit": "3",
        "open_board_count": "0",
        "first_touch_time": "09:41:00",
        "seal_time_minutes": "11",
        "seal_amount": "250000000",
        "float_market_cap": "5000000000",
        "stock_change_pct": "20",
        "close_price": "240",
        "limit_up_price": "240",
        "is_one_word": "0",
        "sector_limit_up_count": "2",
        "market_limit_up_count": "12",
        "market_breadth_ratio": "\\N",
        "market_change_pct": "\\N",
        "derived_fields": '{"float_market_cap":"real"}',
        "load_version": "v1",
        "data_source": "daban_board_event_derived",
    }
    parts = [vals[c] for c in cols]
    row = P._parse_load_tsv(parts)
    assert row["float_market_cap"] == pytest.approx(5e9)
    assert row["market_breadth_ratio"] is None          # \N → None
    assert row["seal_amount"] == pytest.approx(2.5e8)
    assert row["derived_fields"] == '{"float_market_cap":"real"}'


def test_row_to_event_from_tsv_view():
    # 12 列事件视图：trade_date symbol board st_flag consec open_board first_touch
    #               seal_amount_proxy close limit_up_price is_one_word pre_close
    r = ["2026-09-11", "300750.SZ", "chinext", "0", "3", "0", "09:41:00", "250000000", "240", "240", "0", "200"]
    e = P._row_to_event(DabanBoardEvent, r)
    assert e.symbol == "300750.SZ"
    assert e.consec_limit == 3
    assert e.seal_amount_proxy == pytest.approx(2.5e8)
    assert e.pre_close == pytest.approx(200.0)


@pytest.mark.parametrize("sentinel", ["1970-01-01", "0000-00-00", "\\N", "", "bogus"])
def test_pit_source_empty_table_sentinel_is_no_partition(monkeypatch, sentinel):
    """空表 max(trade_date) 的 CH 哨兵回值不得被读成"远古分区"——必须 None（无分区）。

    病根：ClickHouse 对空 Date 列 max() 回 1970-01-01（与 0000-00-00 随版本而异），
    只挡 0000-00-00 时 1970 会被当作合法事件日去查分区，把"今日无数据"伪装成
    "回退到 1970 分区"。下限哨兵真源=P.MIN_EVENT_DATE，消费侧共用同一真源。
    """
    from zephyr.data import ch_reader

    monkeypatch.setattr(ch_reader, "query", lambda sql, **kw: sentinel)
    src = P.ClickHouseDabanEngineLoadSource()
    assert src.resolve_event_date(dt.date(2026, 9, 16)) is None
    assert src.fetch_load(dt.date(2026, 9, 16)) == []


def test_pit_source_real_event_date_passes(monkeypatch):
    from zephyr.data import ch_reader

    monkeypatch.setattr(ch_reader, "query", lambda sql, **kw: "2026-09-15")
    src = P.ClickHouseDabanEngineLoadSource()
    assert src.resolve_event_date(dt.date(2026, 9, 16)) == dt.date(2026, 9, 15)
