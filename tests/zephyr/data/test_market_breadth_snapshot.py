# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""market_breadth_snapshot 采集链单元测试（92号清单 §8.2 / 44号备忘 M1-④，mock miniqmt 不触库不触网）。

覆盖：
- 合成 tick → 表行映射（aggregate_market_ticks + build_insert_row）：主板 10%/ST 5%/
  创业板 20%/北交所 30% 幅度口径；封住=涨停且卖一无量；曾涨停=high 触及（含炸板）；
  Decimal 四舍五入到分边界（10.35×1.1=11.385→11.39）；无效 tick 跳过不计 total_count；
- ST 集加载（load_current_st_codes）：注入 query_fn 往返/异常→(空集,False) fail-open；
- provider _fetch_market_breadth_snapshot：mock xtdata 全市场分批→单行落库列序；
  ST 加载失败 degraded=1；payload.table 空 fail-closed；标的清单/取数异常 error 留痕不抛；
  total_count=0 空跑不写零行；
- tasks.yaml 登记契约：任务字段/schedule 槽位存在/capability 路由+meta 一致/
  apply_market_tables_ddl 注册（DDL 真源+引擎矩阵）。
"""

from __future__ import annotations

import datetime
import pathlib
import sys
from unittest.mock import MagicMock

import pytest
import yaml

from zephyr.data.implementations.miniqmt_provider import (
    _DIRECT_ROUTES,
    MiniQmtIngestProvider,
)
from zephyr.data.market_breadth_collector import (
    INSERT_COLUMN_NAMES,
    aggregate_market_ticks,
    build_insert_row,
    load_current_st_codes,
)
from zephyr.data.provider_base import FetchPayload

D = datetime.date  # 简写
_TD = D(2026, 8, 21)  # 合成交易日

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_CONFIG = _REPO_ROOT / "src" / "zephyr" / "data" / "config"


def _tick(last, pre, *, high=None, amount=0.0, ask_p=None, ask_v=None):
    """合成一条 get_full_tick tick dict（键名=provider 实证口径）。"""
    return {
        "lastPrice": last,
        "lastClose": pre,
        "high": high if high is not None else last,
        "amount": amount,
        "askPrice": ask_p if ask_p is not None else [last, 0, 0, 0, 0],
        "askVol": ask_v if ask_v is not None else [100, 0, 0, 0, 0],
    }


class TestAggregateMarketTicks:
    def test_breadth_and_amount_mapping(self):
        ticks = {
            "600000.SH": _tick(10.50, 10.00, amount=1e6),  # 涨
            "000002.SZ": _tick(9.50, 10.00, amount=2e6),  # 跌
            "000003.SZ": _tick(10.00, 10.00, amount=3e6),  # 平
        }
        agg = aggregate_market_ticks(ticks, set(), trade_date=_TD)
        assert (agg.advancing, agg.declining, agg.flat) == (1, 1, 1)
        assert agg.total_count == 3
        assert agg.total_amount == 6e6
        assert agg.limit_up == 0 and agg.attempted == 0 and agg.limit_down == 0

    def test_main_board_limit_up_and_sealed(self):
        # 主板 10%：10.00→11.00 涨停；卖一无量（价 0/量 0）→ 封住
        ticks = {
            "600000.SH": _tick(11.00, 10.00, ask_p=[0.0], ask_v=[0]),
            "600001.SH": _tick(11.00, 10.00, ask_p=[11.00], ask_v=[100]),  # 涨停但有卖单→未封
        }
        agg = aggregate_market_ticks(ticks, set(), trade_date=_TD)
        assert agg.limit_up == 2
        assert agg.attempted == 2
        assert agg.sealed == 1

    def test_chinext_20pct(self):
        # 创业板 20%：+15% 不涨停；high 触及 20% 后回落 → 曾涨停（炸板）
        ticks = {
            "300001.SZ": _tick(11.50, 10.00),
            "300002.SZ": _tick(11.00, 10.00, high=12.00),
        }
        agg = aggregate_market_ticks(ticks, set(), trade_date=_TD)
        assert agg.limit_up == 0
        assert agg.attempted == 1

    def test_bse_30pct(self):
        # 北交所 30%：+25% 不涨停；+30% 涨停
        ticks = {
            "830001.BJ": _tick(12.50, 10.00),
            "830002.BJ": _tick(13.00, 10.00, ask_p=[0.0], ask_v=[0]),
        }
        agg = aggregate_market_ticks(ticks, set(), trade_date=_TD)
        assert agg.limit_up == 1
        assert agg.sealed == 1

    def test_st_5pct(self):
        # 主板 ST 5%：+5% 涨停（ST 集内）；同一 tick 不在 ST 集 → 非涨停
        ticks = {"601398.SH": _tick(10.50, 10.00, ask_p=[0.0], ask_v=[0])}
        agg_st = aggregate_market_ticks(ticks, {"601398"}, trade_date=_TD)
        assert agg_st.limit_up == 1
        agg_non = aggregate_market_ticks(ticks, set(), trade_date=_TD)
        assert agg_non.limit_up == 0

    def test_limit_down(self):
        ticks = {"600002.SH": _tick(9.00, 10.00)}
        agg = aggregate_market_ticks(ticks, set(), trade_date=_TD)
        assert agg.limit_down == 1
        assert agg.declining == 1

    def test_decimal_rounding_boundary(self):
        # 10.35×1.1=11.385 → 交易所四舍五入 11.39：11.38 不涨停 / 11.39 涨停
        ticks_lo = {"600000.SH": _tick(11.38, 10.35)}
        assert aggregate_market_ticks(ticks_lo, set(), trade_date=_TD).limit_up == 0
        ticks_hi = {"600000.SH": _tick(11.39, 10.35)}
        assert aggregate_market_ticks(ticks_hi, set(), trade_date=_TD).limit_up == 1

    def test_invalid_ticks_skipped(self):
        ticks = {
            "600000.SH": _tick(10.50, 10.00),
            "600001.SH": _tick(0.0, 10.00),  # 最新价 0（停牌）→ 跳过
            "600002.SH": {"lastPrice": 10.1},  # 缺昨收 → 跳过
            "600003.SH": None,  # 非 Mapping → 跳过
        }
        agg = aggregate_market_ticks(ticks, set(), trade_date=_TD)
        assert agg.total_count == 1
        assert agg.n_skipped == 3

    def test_empty_input_no_crash(self):
        agg = aggregate_market_ticks({}, set(), trade_date=_TD)
        assert agg.total_count == 0 and agg.advancing == 0

    def test_build_insert_row_column_order(self):
        agg = aggregate_market_ticks(
            {"600000.SH": _tick(11.00, 10.00, amount=123.0, ask_p=[0.0], ask_v=[0])},
            set(),
            trade_date=_TD,
        )
        row = build_insert_row(agg, "2026-08-21", "2026-08-21 10:00:00", degraded=1)
        assert len(row) == len(INSERT_COLUMN_NAMES)
        mapped = dict(zip(INSERT_COLUMN_NAMES, row, strict=True))
        assert mapped["trade_date"] == "2026-08-21"
        assert mapped["ts"] == "2026-08-21 10:00:00"
        assert mapped["advancing"] == 1 and mapped["limit_up"] == 1 and mapped["sealed"] == 1
        assert mapped["total_amount"] == 123.0
        assert mapped["data_source"] == "miniqmt" and mapped["degraded"] == 1
        # 与 schemas INSERT_COLUMNS 真源列序对账（防漂移）
        sys.path.insert(0, str(_REPO_ROOT))
        from schemas.categories.market_breadth_snapshot import INSERT_COLUMNS

        schema_cols = [c.strip() for c in INSERT_COLUMNS.strip().strip("()").split(",")]
        assert list(INSERT_COLUMN_NAMES) == schema_cols


class TestLoadCurrentStCodes:
    def test_query_fn_roundtrip(self):
        codes, ok = load_current_st_codes(query_fn=lambda sql: "601398\n000506.SH\n", as_of=_TD)
        assert ok is True
        assert codes == {"601398", "000506"}  # 裸码归一（去后缀）

    def test_failure_fail_open(self):
        def _boom(sql):
            raise RuntimeError("合成故障")

        codes, ok = load_current_st_codes(query_fn=_boom, as_of=_TD)
        assert ok is False and codes == set()

    def test_empty_is_ok(self):
        codes, ok = load_current_st_codes(query_fn=lambda sql: "", as_of=_TD)
        assert ok is True and codes == set()


def _payload(symbols=None, table="c1_market.market_breadth_snapshot") -> FetchPayload:
    return FetchPayload(
        table=table,
        symbols=symbols,
        start=_TD,
        end=_TD,
        incremental=True,
        extra={"capability": "market_breadth_snapshot"},
    )


def _policy() -> MagicMock:
    return MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)


def _mock_xtdata(monkeypatch, *, sector_list=None, ticks=None, raise_on=None):
    """构造 xtquant.xtdata 模块 mock（raise_on=('sector'|'tick') 指定故障点）。"""
    mock_xtdata = MagicMock()

    def _sector(name):
        if raise_on == "sector":
            raise RuntimeError("合成板块故障")
        return sector_list or []

    def _full_tick(batch):
        if raise_on == "tick":
            raise RuntimeError("合成取数故障")
        return {c: ticks[c] for c in batch if c in (ticks or {})}

    mock_xtdata.get_stock_list_in_sector.side_effect = _sector
    mock_xtdata.get_full_tick.side_effect = _full_tick
    mock_xt = MagicMock()
    mock_xt.xtdata = mock_xtdata
    monkeypatch.setitem(sys.modules, "xtquant", mock_xt)
    monkeypatch.setitem(sys.modules, "xtquant.xtdata", mock_xtdata)
    return mock_xtdata


class TestProviderFetch:
    def test_single_row_happy_path(self, monkeypatch):
        symbols = ["600000.SH", "000002.SZ"]
        ticks = {
            "600000.SH": _tick(11.00, 10.00, amount=1e6, ask_p=[0.0], ask_v=[0]),
            "000002.SZ": _tick(9.50, 10.00, amount=2e6),
        }
        _mock_xtdata(monkeypatch, sector_list=symbols, ticks=ticks)
        monkeypatch.setattr(
            "zephyr.data.market_breadth_collector.load_current_st_codes",
            lambda **kw: (set(), True),
        )
        results = list(MiniQmtIngestProvider()._fetch_market_breadth_snapshot(_payload(), _policy()))
        assert len(results) == 1
        res = results[0]
        assert res.error is None and len(res.rows) == 1
        assert res.table == "c1_market.market_breadth_snapshot"
        assert res.columns == list(INSERT_COLUMN_NAMES)
        row = dict(zip(res.columns, res.rows[0], strict=True))
        assert row["advancing"] == 1 and row["declining"] == 1
        assert row["limit_up"] == 1 and row["sealed"] == 1 and row["attempted"] == 1
        assert row["total_count"] == 2 and row["total_amount"] == 3e6
        assert row["degraded"] == 0 and row["data_source"] == "miniqmt"
        # ts 分钟截断形态（秒=00）
        assert row["ts"].endswith(":00")

    def test_st_load_failure_marks_degraded(self, monkeypatch):
        symbols = ["601398.SH"]
        ticks = {"601398.SH": _tick(10.50, 10.00, ask_p=[0.0], ask_v=[0])}
        _mock_xtdata(monkeypatch, sector_list=symbols, ticks=ticks)
        monkeypatch.setattr(
            "zephyr.data.market_breadth_collector.load_current_st_codes",
            lambda **kw: (set(), False),
        )
        results = list(MiniQmtIngestProvider()._fetch_market_breadth_snapshot(_payload(), _policy()))
        row = dict(zip(results[0].columns, results[0].rows[0], strict=True))
        assert row["degraded"] == 1
        assert row["limit_up"] == 0  # ST 集缺失按 10% 近似 → +5% 不计涨停（口径偏紧留痕）

    def test_empty_table_fail_closed(self):
        results = list(MiniQmtIngestProvider()._fetch_market_breadth_snapshot(_payload(table=""), _policy()))
        assert results[0].error is not None and "fail-closed" in results[0].error

    def test_sector_list_failure_fail_open(self, monkeypatch):
        _mock_xtdata(monkeypatch, raise_on="sector")
        results = list(MiniQmtIngestProvider()._fetch_market_breadth_snapshot(_payload(), _policy()))
        assert results[0].rows == [] and "标的清单失败" in results[0].error

    def test_tick_failure_fail_open(self, monkeypatch):
        _mock_xtdata(monkeypatch, sector_list=["600000.SH"], raise_on="tick")
        monkeypatch.setattr(
            "zephyr.data.market_breadth_collector.load_current_st_codes",
            lambda **kw: (set(), True),
        )
        results = list(MiniQmtIngestProvider()._fetch_market_breadth_snapshot(_payload(), _policy()))
        assert results[0].rows == [] and "抓取失败" in results[0].error

    def test_all_zero_ticks_skip_write(self, monkeypatch):
        # 非交易日/全量无效 tick：空跑不写零行（防污染时序），不留 error
        _mock_xtdata(monkeypatch, sector_list=["600000.SH"], ticks={})
        monkeypatch.setattr(
            "zephyr.data.market_breadth_collector.load_current_st_codes",
            lambda **kw: (set(), True),
        )
        results = list(MiniQmtIngestProvider()._fetch_market_breadth_snapshot(_payload(), _policy()))
        assert results[0].rows == [] and results[0].error is None


class TestRegistration:
    def test_tasks_yaml_registration(self):
        tasks = yaml.safe_load((_CONFIG / "tasks.yaml").read_text(encoding="utf-8"))["tasks"]
        task = next((t for t in tasks if t.get("task_id") == "market_breadth_snapshot_minute"), None)
        assert task is not None, "tasks.yaml 缺 market_breadth_snapshot_minute 任务"
        assert task["table"] == "c1_market.market_breadth_snapshot"
        assert task["source"] == "miniqmt"
        assert task["schedule"] == "intraday_minute"
        assert task["capability"] == "market_breadth_snapshot"
        assert task.get("symbols") is None  # null=沪深A股全市场

    def test_schedule_slot_exists(self):
        schedules = yaml.safe_load((_CONFIG / "schedule.yaml").read_text(encoding="utf-8"))["schedules"]
        assert "intraday_minute" in schedules

    def test_route_meta_consistency(self):
        # commit gate 同款口径：_DIRECT_ROUTES 与 meta.capabilities 双侧注册
        assert _DIRECT_ROUTES.get("market_breadth_snapshot") == "_fetch_market_breadth_snapshot"
        meta = MiniQmtIngestProvider.meta
        contract = meta.get_capability_contract("market_breadth_snapshot")
        assert contract is not None
        assert contract.supports_symbols_null is True

    def test_apply_script_registration(self):
        sys.path.insert(0, str(_REPO_ROOT))
        import scripts.ch.apply_market_tables_ddl as apply_mod

        tables = dict(apply_mod._ALL_DDL)
        assert "c1_market.market_breadth_snapshot" in tables
        assert (
            "CREATE TABLE IF NOT EXISTS c1_market.market_breadth_snapshot"
            in tables["c1_market.market_breadth_snapshot"]
        )
        assert apply_mod._EXPECTED_ENGINES["market_breadth_snapshot"] == "ReplacingMergeTree"

    def test_ddl_columns_match_schema(self):
        sys.path.insert(0, str(_REPO_ROOT))
        from schemas.categories.market_breadth_snapshot import (
            DATABASE,
            MARKET_BREADTH_SNAPSHOT_DDL,
            TABLE_NAME,
        )

        assert DATABASE == "c1_market" and TABLE_NAME == "market_breadth_snapshot"
        for col in INSERT_COLUMN_NAMES:
            assert col in MARKET_BREADTH_SNAPSHOT_DDL
