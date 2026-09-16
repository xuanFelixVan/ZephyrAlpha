# [A_test] module_id: MOD-L05_daban_sleeve_strategy_load | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] tests.pf_core.test_daban_sleeve_strategy_load
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_core/test_daban_sleeve_strategy_load.py
# [TTL] task_bound
"""daban-sleeve 负载真读消费面测试（T3⑧ / 挖矿 LUE-1 治本）。

覆盖：
- row_to_engine_payload：无 selector 键契约（避免机构默认→回避清零）；float_market_cap
  真实正数时喂 youzi+quant，缺/非正时省略（引擎 0.0 默认，禁拍假值）；seal_time 折算
  datetime；is_main_line 连板≥2 代理
- build_signals_from_load：键=纯数字码，非法/缺 symbol 剔除
- build_weight_panel_for_dates：PIT（fetch_load 收决策日 date() 调用）；某日无负载行→
  logger.warning 显式 skipped（禁静默零负载）；面板 schema（DatetimeIndex×纯码列×float64、
  权重和 ≤1）
- 真实四引擎回归守卫：一条真实强封板负载行（含 float_market_cap）经真策略产 **非零**
  权重（挖矿实证——补 float_market_cap 前仅 1.4% 封板事件越阈、sleeve 空转；补后 0.0945
  归位）。此断言若回退即视为治本失效。

持久化负载消费面（T3⑧ 接线，治"信号产而不消"P0；全部经 fake reader，零生产库/零 data/ 写）：
- 表名/列序真源解析（schemas DDL-as-Code × producer LOAD_INSERT_COLUMNS 同序）
- 无注入 load_source → 默认自建 DatabaseService 读源，落表行→面板候选（产而真消）
- PIT：SQL 谓词 trade_date<as_of；读源越权回未来行 → 代码级双保险下永不可见
- 无行/读库异常 → 与"引擎无输出"同一 fail-closed 分支（显式 skipped、该日全零）
- T-1 分区缺失回退更早事件日 → 恰好一条 WARNING 点名回退（禁静默陈旧消费）
- 开关 use_persisted_load=False → 不触库；注入源优先于开关
"""

from __future__ import annotations

import datetime as dt
import logging

import pytest

import zephyr.pf_core.strategies.daban_sleeve_strategy as dss
from zephyr.ex_core.daban_load_producer import LOAD_INSERT_COLUMNS
from zephyr.pf_core.strategies.daban_sleeve_strategy import (
    DabanSleeveStrategy,
    _coerce_decision_date,
    _maybe_positive,
    _persisted_load_columns,
    _persisted_load_table,
    _PersistedDabanLoadSource,
    _plain_symbol,
    _seal_datetime,
)


def _strong_row(**over):
    """真实强封板事件负载行（连板3/封单2.5亿/流通市值50亿→封流比5%/早封09:41/0开板/板块8家）。"""
    row = {
        "trade_date": "2026-09-11",
        "symbol": "300750.SZ",
        "consec_limit": 3,
        "open_board_count": 0,
        "seal_amount": 2.5e8,
        "float_market_cap": 5e9,
        "first_touch_time": "09:41:00",
        "stock_change_pct": 20.0,
        "market_change_pct": 1.2,
        "market_breadth_ratio": 0.7,
        "sector_limit_up_count": 8,
        "market_limit_up_count": 45,
    }
    row.update(over)
    return row


# ────────────────────────── module helpers ──────────────────────────


@pytest.mark.parametrize(
    "sym, expected",
    [("300750.SZ", "300750"), ("600519", "600519"), ("", ""), (None, ""), ("sh.600000", "sh")],
)
def test_plain_symbol(sym, expected):
    assert _plain_symbol(sym) == expected


def test_seal_datetime_ok_and_bad():
    got = _seal_datetime("2026-09-11", "09:41:00")
    assert got == dt.datetime(2026, 9, 11, 9, 41, 0)
    assert _seal_datetime("2026-09-11", None) is None
    assert _seal_datetime("bad", "09:41:00") is None
    assert _seal_datetime("2026-09-11", "99:99") is None


@pytest.mark.parametrize("val, exp", [(5e9, 5e9), (0.0, None), (-1.0, None), (None, None), ("", None), (float("nan"), None)])
def test_maybe_positive(val, exp):
    got = _maybe_positive(val)
    if exp is None:
        assert got is None
    else:
        assert got == pytest.approx(exp)


# ────────────────────────── row_to_engine_payload ──────────────────────────


def test_row_to_engine_payload_no_selector_contract():
    payload = DabanSleeveStrategy.row_to_engine_payload(_strong_row())
    assert set(payload.keys()) == {"youzi", "quant", "fusion_context"}
    assert "selector" not in payload            # 资格门不喂（防机构默认→回避清零）


def test_row_to_engine_payload_float_cap_feeds_youzi_and_quant():
    payload = DabanSleeveStrategy.row_to_engine_payload(_strong_row())
    assert payload["youzi"]["float_market_cap"] == pytest.approx(5e9)
    assert payload["quant"]["float_market_cap"] == pytest.approx(5e9)


def test_row_to_engine_payload_missing_cap_omits_key():
    payload = DabanSleeveStrategy.row_to_engine_payload(_strong_row(float_market_cap=None))
    assert "float_market_cap" not in payload["youzi"]   # 非拍假值，交引擎 0.0 默认
    assert "float_market_cap" not in payload["quant"]


def test_row_to_engine_payload_non_positive_cap_omits_key():
    payload = DabanSleeveStrategy.row_to_engine_payload(_strong_row(float_market_cap=-3.0))
    assert "float_market_cap" not in payload["youzi"]


def test_row_to_engine_payload_seal_time_and_main_line():
    payload = DabanSleeveStrategy.row_to_engine_payload(_strong_row())
    assert payload["youzi"]["seal_time"] == dt.datetime(2026, 9, 11, 9, 41, 0)
    assert payload["quant"]["is_main_line"] is True      # consec=3 ≥2
    assert payload["fusion_context"]["is_main_line"] is True


def test_row_to_engine_payload_single_board_not_main():
    payload = DabanSleeveStrategy.row_to_engine_payload(_strong_row(consec_limit=1))
    assert payload["quant"]["is_main_line"] is False


# ────────────────────────── build_signals_from_load ──────────────────────────


def test_build_signals_from_load_plain_keys_and_drop_invalid():
    rows = [_strong_row(symbol="300750.SZ"), _strong_row(symbol=""), _strong_row(symbol="600519")]
    signals = DabanSleeveStrategy.build_signals_from_load(rows)
    assert set(signals.keys()) == {"300750", "600519"}
    assert "youzi" in signals["300750"]


# ────────────────────────── build_weight_panel_for_dates ──────────────────────────


class _FakeLoadSource:
    """duck load source：记录被请求的决策日，返回预置行。"""

    def __init__(self, mapping):
        self._mapping = mapping          # {date: list[dict]}
        self.calls: list[dt.date] = []

    def fetch_load(self, as_of):
        self.calls.append(as_of)
        return self._mapping.get(as_of, [])


def test_panel_pit_query_key_is_decision_date():
    import pandas as pd

    strat = DabanSleeveStrategy()
    src = _FakeLoadSource({})
    dates = ["2026-09-12", "2026-09-15"]
    strat.build_weight_panel_for_dates(dates, ["300750"], load_source=src)
    assert src.calls == [dt.date(2026, 9, 12), dt.date(2026, 9, 15)]   # 每决策日 PIT 读


def test_panel_schema_and_weight_sum():
    import pandas as pd

    strat = DabanSleeveStrategy()
    src = _FakeLoadSource({dt.date(2026, 9, 12): [_strong_row(), _strong_row(symbol="600519.SH", consec_limit=2)]})
    panel = strat.build_weight_panel_for_dates(["2026-09-12"], ["300750.SZ", "600519.SH"], load_source=src)
    assert isinstance(panel.index, pd.DatetimeIndex)
    assert list(panel.columns) == ["300750", "600519"]
    assert panel.dtypes.iloc[0] == "float64"
    assert panel.loc["2026-09-12"].sum() <= 1.0 + 1e-9


def test_panel_empty_day_skips_with_warning(caplog):
    strat = DabanSleeveStrategy()
    src = _FakeLoadSource({})               # 无 PIT 负载行
    with caplog.at_level(logging.WARNING):
        panel = strat.build_weight_panel_for_dates(["2026-09-12"], ["300750"], load_source=src)
    assert "显式 skipped" in caplog.text     # 禁静默零负载
    assert (panel.to_numpy() == 0).all()     # 该日全零=现金日


def test_panel_real_engines_produce_nonzero_weight():
    """回归守卫：真实强封板负载（含 float_market_cap）→ 真四引擎产非零权重（0.0945 归位）。"""
    strat = DabanSleeveStrategy()           # 默认=真实 production 四引擎
    src = _FakeLoadSource({dt.date(2026, 9, 12): [_strong_row()]})
    panel = strat.build_weight_panel_for_dates(["2026-09-12"], ["300750"], load_source=src)
    w = float(panel.loc["2026-09-12", "300750"])
    assert w > 0.0, "补 float_market_cap 后真实强封板事件应越融合阈值产非零权重（否则治本回退）"
    assert w <= 0.15 + 1e-9                 # max_single 截顶


def test_panel_no_tradable_overlap_zero_not_silent():
    """有负载行但与 universe 无交集 → 该日全零（无越阈可投标的），非 skipped 分支。"""
    strat = DabanSleeveStrategy()
    src = _FakeLoadSource({dt.date(2026, 9, 12): [_strong_row(symbol="999999.SZ")]})
    panel = strat.build_weight_panel_for_dates(["2026-09-12"], ["300750"], load_source=src)
    assert (panel.to_numpy() == 0).all()


def test_generate_target_weights_empty_contract_preserved():
    """既有 ERROR_CONTRACT：空 universe/signals → {}（不抛），与旧测试一致。"""
    strat = DabanSleeveStrategy()
    assert strat.generate_target_weights([], {"300750": _strong_row()}) == {}
    assert strat.generate_target_weights(["300750"], {}) == {}


# ────────────────── 持久化负载消费（c1_market.daban_engine_load 真读） ──────────────────


class _FakeDbReader:
    """duck DatabaseService reader：按 SQL 形态回预置分区，零生产库/零 data/ 写。"""

    def __init__(self, event_date=None, tuples=(), explode=()):
        self.event_date = event_date          # max(trade_date) 单行返回（None=无分区）
        self.tuples = [list(t) for t in tuples]
        self.explode = set(explode)           # 命中子串则抛（模拟读库异常）
        self.sqls: list[str] = []

    def __call__(self, sql):
        self.sqls.append(sql)
        for token in self.explode:
            if token in sql:
                raise RuntimeError(f"CH 不可达：{token}")
        if "max(trade_date)" in sql:
            return [] if self.event_date is None else [(self.event_date,)]
        return self.tuples

    @property
    def row_sqls(self):
        return [s for s in self.sqls if "max(trade_date)" not in s]


def _load_tuple(**over):
    """负载行 dict → 与 LOAD_INSERT_COLUMNS 同序的 21 列 tuple（DB 回包形态）。"""
    row = dict.fromkeys(LOAD_INSERT_COLUMNS)
    row.update(_strong_row())
    row.update(over)
    return [tuple(row[col] for col in LOAD_INSERT_COLUMNS)]


def test_persisted_table_and_columns_come_from_truth_sources():
    """表名=schemas DDL-as-Code、列序=producer LOAD_INSERT_COLUMNS（禁本模块复制真源）。"""
    from schemas.categories.market.market_daban_engine_load import DATABASE, TABLE_NAME

    assert _persisted_load_table() == f"{DATABASE}.{TABLE_NAME}" == "c1_market.daban_engine_load"
    assert _persisted_load_columns() == LOAD_INSERT_COLUMNS
    assert _coerce_decision_date(dt.datetime(2026, 9, 12, 9, 30)) == dt.date(2026, 9, 12)
    assert _coerce_decision_date("2026-09-12") == dt.date(2026, 9, 12)


def test_default_source_consumes_persisted_rows(monkeypatch):
    """无注入 load_source（出厂默认）→ 自建读源真消费落表行：面板候选=持久化负载候选。"""
    reader = _FakeDbReader(event_date=dt.date(2026, 9, 11), tuples=_load_tuple())
    calls: list[str] = []
    monkeypatch.setattr(dss, "_default_load_reader", lambda sql: calls.append(sql) or reader(sql))

    panel = DabanSleeveStrategy().build_weight_panel_for_dates(["2026-09-12"], ["300750"])

    assert calls, "默认路径必须经 DatabaseService 读通道（否则持久化行仍是产而不消）"
    reference = DabanSleeveStrategy().build_weight_panel_for_dates(
        ["2026-09-12"], ["300750"], load_source=_FakeLoadSource({dt.date(2026, 9, 12): [_strong_row()]})
    )
    assert panel.to_numpy().tolist() == reference.to_numpy().tolist()
    assert float(panel.loc["2026-09-12", "300750"]) > 0.0


def test_default_reader_uses_database_service_reader_role(monkeypatch):
    """默认通道必须走 DatabaseService（宪法 §9.1 禁裸 duckdb/裸连接散落）。"""
    seen: dict[str, str] = {}

    class _Conn:
        def execute(self, sql):
            seen["sql"] = sql
            return []

    class _Svc:
        def get_clickhouse_conn(self, role="reader", **kw):  # noqa: ANN001, ARG002
            seen["role"] = role
            return _Conn()

    import zephyr.infrastructure.database_service as dbs

    monkeypatch.setattr(dbs, "get_db_service", lambda: _Svc())
    assert list(dss._default_load_reader("SELECT 1")) == []
    assert seen == {"sql": "SELECT 1", "role": "reader"}


def test_pit_sql_predicate_is_strictly_before_decision_date():
    """PIT：发出的每条 SQL 都只引用 <T 的分区，从不按决策日当日/未来日取数。"""
    reader = _FakeDbReader(event_date=dt.date(2026, 9, 11), tuples=_load_tuple())
    _PersistedDabanLoadSource(reader=reader).fetch_load(dt.date(2026, 9, 12))

    assert "trade_date < toDate('2026-09-12')" in reader.sqls[0]
    assert "trade_date = toDate('2026-09-11')" in reader.row_sqls[0]
    assert "FINAL" in reader.row_sqls[0]              # ReplacingMergeTree 去重口径
    assert "2026-09-12" not in reader.row_sqls[0]     # 分区查询绝不带决策日


def test_future_dated_rows_never_visible_to_decision():
    """未来行（trade_date>T-1）即使被读源越权带回，也在代码级双保险下不可见。"""
    leaked = _load_tuple(trade_date="2026-09-12") + _load_tuple(trade_date="2026-09-15", symbol="600519.SH")
    reader = _FakeDbReader(event_date=dt.date(2026, 9, 11), tuples=leaked)
    src = _PersistedDabanLoadSource(reader=reader)
    assert src.fetch_load(dt.date(2026, 9, 12)) == []          # 单行级：未来日全剔
    # max() 本身回未来日（读源撒谎）→ 视为无分区，绝不消费
    assert _PersistedDabanLoadSource(reader=_FakeDbReader(event_date=dt.date(2026, 9, 20))).resolve_event_date(
        dt.date(2026, 9, 12)
    ) is None


def test_no_persisted_rows_takes_same_fail_closed_path_as_empty_engines(caplog):
    """无分区 → 与"注入源零行"同一路径：显式 skipped 告警 + 该日全零（不造空而自信的候选集）。"""
    strat = DabanSleeveStrategy()
    with caplog.at_level(logging.WARNING):
        persisted = strat.build_weight_panel_for_dates(["2026-09-12"], ["300750"], load_reader=_FakeDbReader())
    skipped_by_persisted = [r.getMessage() for r in caplog.records if "显式 skipped" in r.getMessage()]

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        injected = strat.build_weight_panel_for_dates(["2026-09-12"], ["300750"], load_source=_FakeLoadSource({}))
    skipped_by_injected = [r.getMessage() for r in caplog.records if "显式 skipped" in r.getMessage()]

    assert skipped_by_persisted == skipped_by_injected == [
        "daban-sleeve: 决策日 2026-09-12 无 PIT 负载行（事件表未产/当日空）——显式 skipped，非静默零权重"
    ]
    assert (persisted.to_numpy() == 0).all() and (injected.to_numpy() == 0).all()
    assert persisted.equals(injected)


def test_reader_exception_degrades_to_same_fail_closed_path(caplog):
    """读库异常不崩决策链：该日回落同一 skipped 分支（该日全零，非抛异常出面板）。"""
    reader = _FakeDbReader(explode={"trade_date"})
    with caplog.at_level(logging.WARNING):
        panel = DabanSleeveStrategy().build_weight_panel_for_dates(["2026-09-12"], ["300750"], load_reader=reader)
    assert (panel.to_numpy() == 0).all()
    assert "降级空" in caplog.text and "显式 skipped" in caplog.text


def test_stale_partition_fallback_warns_exactly_once_naming_the_date(caplog):
    """T-1 分区缺失而回退更早事件日 → 恰好一条 WARNING 点名回退目标（禁静默陈旧消费）。"""
    reader = _FakeDbReader(event_date=dt.date(2026, 9, 7), tuples=_load_tuple(trade_date="2026-09-07"))
    src = _PersistedDabanLoadSource(reader=reader)
    with caplog.at_level(logging.WARNING):
        rows = src.fetch_load(dt.date(2026, 9, 12))
        assert rows and rows[0]["trade_date"] == "2026-09-07"   # 回退仍受 PIT 约束（<T）
        src.fetch_load(dt.date(2026, 9, 12))                    # 同源同日重复读
    fallbacks = [r for r in caplog.records if "fallback" in r.getMessage()]
    assert len(fallbacks) == 1, "回退必须恰有一条告警（禁静默，也禁刷屏）"
    assert "2026-09-07" in fallbacks[0].getMessage()            # 点名回退到哪一天


def test_on_time_t1_partition_does_not_warn_fallback(caplog):
    """未回退（分区恰为前一交易日）不得误报陈旧——告警只属于真回退。"""
    src = _PersistedDabanLoadSource(reader=_FakeDbReader(event_date=dt.date(2026, 9, 11), tuples=_load_tuple()))
    with caplog.at_level(logging.WARNING):
        assert src.fetch_load(dt.date(2026, 9, 12))
    assert not [r for r in caplog.records if "fallback" in r.getMessage()]


def test_switch_off_never_touches_the_database(caplog, monkeypatch):
    """use_persisted_load=False → 消费路径整体关闭（零 SQL），逐日仍走 fail-closed。"""

    def _boom(sql):
        raise AssertionError(f"开关关闭后不得触库: {sql}")

    monkeypatch.setattr(dss, "_default_load_reader", _boom)
    with caplog.at_level(logging.WARNING):
        panel = DabanSleeveStrategy().build_weight_panel_for_dates(
            ["2026-09-12", "2026-09-15"], ["300750"], use_persisted_load=False
        )
    assert (panel.to_numpy() == 0).all()
    assert panel.shape == (2, 1)
    assert "use_persisted_load=False" in caplog.text          # 关闭本身也留痕（禁静默）
    assert caplog.text.count("显式 skipped") == 2              # 每个决策日各自 fail-closed


def test_injected_source_takes_precedence_over_switch():
    """注入源优先于开关：use_persisted_load=False 也不改变显式注入的语义（行为向后兼容）。"""
    src = _FakeLoadSource({dt.date(2026, 9, 12): [_strong_row()]})
    panel = DabanSleeveStrategy().build_weight_panel_for_dates(
        ["2026-09-12"], ["300750"], load_source=src, use_persisted_load=False
    )
    assert float(panel.loc["2026-09-12", "300750"]) > 0.0
    assert src.calls == [dt.date(2026, 9, 12)]


def test_decimal_db_values_reach_engine_payload():
    """CH Decimal 回包（封单/市值）经消费面进 payload——量纲不在读侧丢失。"""
    from decimal import Decimal

    tuples = _load_tuple(seal_amount=Decimal("250000000.00"), float_market_cap=Decimal("5000000000.00"))
    src = _PersistedDabanLoadSource(reader=_FakeDbReader(event_date=dt.date(2026, 9, 11), tuples=tuples))
    rows = src.fetch_load(dt.date(2026, 9, 12))
    payload = DabanSleeveStrategy.build_signals_from_load(rows)["300750"]
    assert payload["youzi"]["seal_amount"] == pytest.approx(2.5e8)
    assert payload["youzi"]["float_market_cap"] == pytest.approx(5e9)


def test_illegal_decision_date_rejected_before_sql():
    """非日期决策日 → ValueError（禁裸串入 SQL），且一条 SQL 都不发出。"""
    reader = _FakeDbReader()
    with pytest.raises(ValueError, match="决策日"):
        _PersistedDabanLoadSource(reader=reader).fetch_load("not-a-date")
    assert reader.sqls == []


@pytest.mark.parametrize("sentinel", [dt.date(1970, 1, 1), "0000-00-00", ""])
def test_empty_table_sentinel_is_no_partition_not_stale_fallback(sentinel, caplog):
    """空表 max(trade_date) 回 1970-01-01/0000-00-00 → 判"无分区"走 fail-closed，禁误报陈旧回退。"""
    src = _PersistedDabanLoadSource(reader=_FakeDbReader(event_date=sentinel))
    with caplog.at_level(logging.WARNING):
        assert src.resolve_event_date(dt.date(2026, 9, 12)) is None
        assert src.fetch_load(dt.date(2026, 9, 12)) == []
    assert not [r for r in caplog.records if "fallback" in r.getMessage()]
    assert (
        DabanSleeveStrategy()
        .build_weight_panel_for_dates(["2026-09-12"], ["300750"], load_reader=_FakeDbReader(event_date=sentinel))
        .to_numpy() == 0
    ).all()
