"""Provider 实现的单测（MOD-L00-004 阶段1）。

测试 3 个 Provider 的辅助方法（纯函数，不依赖真实 SDK）和 fetch 路由。
不测试真实 SDK 调用（需 iFind/QMT/AKShare 环境）。
"""
import datetime
import math
import pytest

from src.zephyr.data.provider_base import FetchPayload, FetchResult
from src.zephyr.data.policy_registry import SourcePolicy
from src.zephyr.data.implementations.ifind_provider import IFindProvider
from src.zephyr.data.implementations.akshare_provider import (
    AKShareProvider,
    safe_float as ak_safe_float,
)
from src.zephyr.data.implementations.miniqmt_provider import MiniQMTProvider


# ============== IFindProvider 测试 ==============

class TestIFindHelpers:
    def test_ts_code_to_symbol_sz(self):
        assert IFindProvider._ts_code_to_symbol("000001.SZ") == "000001"

    def test_ts_code_to_symbol_sh(self):
        assert IFindProvider._ts_code_to_symbol("600000.SH") == "600000"

    def test_ts_code_to_symbol_no_suffix(self):
        assert IFindProvider._ts_code_to_symbol("000001") == "000001"

    def test_safe_float_normal(self):
        assert IFindProvider.safe_float(1.5) == 1.5
        assert IFindProvider.safe_float("2.3") == 2.3
        assert IFindProvider.safe_float(0) == 0.0

    def test_safe_float_none(self):
        assert IFindProvider.safe_float(None) is None

    def test_safe_float_nan(self):
        assert IFindProvider.safe_float(float("nan")) is None

    def test_safe_float_invalid(self):
        assert IFindProvider.safe_float("abc") is None
        assert IFindProvider.safe_float("") is None

    def test_check_ifind_error_non_dict(self):
        p = IFindProvider()
        assert p._check_ifind_error(None) == (False, None, "")
        assert p._check_ifind_error("string") == (False, None, "")

    def test_check_ifind_error_quota_exceeded(self):
        p = IFindProvider()
        raw = {"errorcode": -4318, "errmsg": "月度配额耗尽"}
        is_err, code, msg = p._check_ifind_error(raw)
        assert is_err is True
        assert code == -4318
        assert "配额" in msg

    def test_check_ifind_error_negative_201(self):
        p = IFindProvider()
        raw = {"errcode": -201, "errormsg": "通用失败"}
        is_err, code, _ = p._check_ifind_error(raw)
        assert is_err is True
        assert code == -201

    def test_check_ifind_error_no_code(self):
        p = IFindProvider()
        raw = {"data": "some data"}
        assert p._check_ifind_error(raw) == (False, None, "")

    def test_check_ifind_error_alt_key(self):
        """兼容 error_code / code 等键名。"""
        p = IFindProvider()
        raw = {"code": -4309, "message": "quota"}
        is_err, code, msg = p._check_ifind_error(raw)
        assert is_err is True
        assert code == -4309


class TestIFindFetchRoute:
    def test_unknown_capability_yields_error(self):
        p = IFindProvider()
        payload = FetchPayload(
            table="t", symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 2),
            extra={"capability": "nonexistent"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "nonexistent" in results[0].error or "未知" in results[0].error

    def test_no_capability_yields_error(self):
        p = IFindProvider()
        payload = FetchPayload(
            table="t", symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 2),
            extra={},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_meta(self):
        assert IFindProvider.meta.name == "ifind"
        assert IFindProvider.source_name == "ifind"
        assert "月度配额" in IFindProvider.meta.known_issues[0]


# ============== AKShareProvider 测试 ==============

class TestAKShareHelpers:
    def test_quarter_to_date_q1(self):
        assert AKShareProvider._quarter_to_date("2025年第1季度") == "2025-03-31"

    def test_quarter_to_date_q4(self):
        assert AKShareProvider._quarter_to_date("2024年第4季度") == "2024-12-31"

    def test_quarter_to_date_q2(self):
        assert AKShareProvider._quarter_to_date("2025年第2季度") == "2025-06-30"

    def test_quarter_to_date_q3(self):
        assert AKShareProvider._quarter_to_date("2025年第3季度") == "2025-09-30"

    def test_month_to_date_june(self):
        assert AKShareProvider._month_to_date("2025年6月") == "2025-06-30"

    def test_month_to_date_december(self):
        assert AKShareProvider._month_to_date("2025年12月") == "2025-12-31"

    def test_month_to_date_february_leap(self):
        """闰年 2 月末。"""
        assert AKShareProvider._month_to_date("2024年2月") == "2024-02-29"

    def test_month_to_date_february_nonleap(self):
        assert AKShareProvider._month_to_date("2025年2月") == "2025-02-28"

    def test_module_safe_float(self):
        assert ak_safe_float(1.5) == 1.5
        assert ak_safe_float(None) is None
        assert ak_safe_float("abc") is None


class TestAKShareFetchRoute:
    def test_unknown_capability_yields_error(self):
        p = AKShareProvider()
        payload = FetchPayload(
            table="t", symbols=None,
            start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 2),
            extra={"capability": "nonexistent"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_meta(self):
        assert AKShareProvider.meta.name == "akshare"
        assert AKShareProvider.source_name == "akshare"
        assert "VPN" in AKShareProvider.meta.known_issues[0] or "vpn" in AKShareProvider.meta.known_issues[0].lower()


# ============== MiniQMTProvider 测试 ==============

class TestMiniQMTHelpers:
    def test_date_to_str(self):
        assert MiniQMTProvider._date_to_str(datetime.date(2024, 1, 9)) == "20240109"
        assert MiniQMTProvider._date_to_str(datetime.date(2024, 12, 31)) == "20241231"

    def test_ts_to_date(self):
        """毫秒时间戳 → YYYY-MM-DD。1704067200000 = 2024-01-01 00:00:00 UTC。"""
        result = MiniQMTProvider._ts_to_date(1704067200000)
        assert result == "2024-01-01"

    def test_ts_to_date_end_of_day(self):
        """2024-01-01 23:59:59 UTC → 2024-01-01。"""
        result = MiniQMTProvider._ts_to_date(1704153599000)
        assert result == "2024-01-01"

    def test_stock_to_symbol_sz(self):
        assert MiniQMTProvider._stock_to_symbol("000001.SZ") == "000001"

    def test_stock_to_symbol_sh(self):
        assert MiniQMTProvider._stock_to_symbol("600000.SH") == "600000"

    def test_safe_float_normal(self):
        assert MiniQMTProvider.safe_float(1.5) == 1.5
        assert MiniQMTProvider.safe_float("2.3") == 2.3

    def test_safe_float_none(self):
        assert MiniQMTProvider.safe_float(None) is None

    def test_safe_float_nan(self):
        assert MiniQMTProvider.safe_float(float("nan")) is None

    def test_safe_float_invalid(self):
        assert MiniQMTProvider.safe_float("abc") is None


class TestMiniQMTFetchRoute:
    def test_unknown_capability_yields_error(self):
        p = MiniQMTProvider()
        payload = FetchPayload(
            table="t", symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 2),
            extra={"capability": "nonexistent"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_meta(self):
        assert MiniQMTProvider.meta.name == "miniqmt"
        assert MiniQMTProvider.source_name == "miniqmt"
        assert MiniQMTProvider.meta.requires_process is True
        assert MiniQMTProvider.meta.thread_safety == "single_thread"


# ============== 新能力测试（阶段4） ==============

class TestIFindNewCapabilities:
    """IFindProvider 新增能力（kline_daily/index_kline/money_flow）的单元测试。"""

    def test_ts_code_to_money_flow_symbol_sh(self):
        """600000.SH → sh600000。"""
        assert IFindProvider._ts_code_to_money_flow_symbol("600000.SH") == "sh600000"

    def test_ts_code_to_money_flow_symbol_sz(self):
        """000001.SZ → sz000001。"""
        assert IFindProvider._ts_code_to_money_flow_symbol("000001.SZ") == "sz000001"

    def test_ts_code_to_money_flow_symbol_bj(self):
        """830001.BJ → bj830001。"""
        assert IFindProvider._ts_code_to_money_flow_symbol("830001.BJ") == "bj830001"

    def test_ts_code_to_money_flow_symbol_invalid(self):
        """无后缀或未知后缀 → 空串。"""
        assert IFindProvider._ts_code_to_money_flow_symbol("600000") == ""
        assert IFindProvider._ts_code_to_money_flow_symbol("600000.US") == ""
        assert IFindProvider._ts_code_to_money_flow_symbol("") == ""

    def test_extract_date_from_string(self):
        """字符串日期 '2025-06-01' → '2025-06-01'。"""
        result = IFindProvider._extract_date("2025-06-01", {})
        assert result == "2025-06-01"

    def test_extract_date_from_timestamp(self):
        """pandas Timestamp 日期提取（用 datetime.date 模拟）。"""
        import datetime as dt
        result = IFindProvider._extract_date(dt.date(2025, 6, 1), {})
        assert result == "2025-06-01"

    def test_extract_date_from_row_time(self):
        """从 row 的 time 列提取日期。"""
        class FakeRow:
            def get(self, key):
                if key == "time":
                    return "2025-06-15"
                return None
        result = IFindProvider._extract_date(None, FakeRow())
        assert result == "2025-06-15"

    def test_extract_date_empty(self):
        """无法提取时返回空串。"""
        assert IFindProvider._extract_date(None, {}) == ""

    def test_find_column_exact(self):
        """精确匹配列名。"""
        data = {"主力净流入-净额": [1.0, 2.0]}
        result = IFindProvider._find_column(data, ["主力净流入-净额", "主力净流入"])
        assert result == [1.0, 2.0]

    def test_find_column_fallback(self):
        """第一个候选不存在时回退到第二个。"""
        data = {"主力净流入": [3.0, 4.0]}
        result = IFindProvider._find_column(data, ["主力净流入-净额", "主力净流入"])
        assert result == [3.0, 4.0]

    def test_find_column_not_found(self):
        """所有候选都不存在时返回 None。"""
        data = {"other": [1.0]}
        result = IFindProvider._find_column(data, ["主力净流入-净额", "主力净流入"])
        assert result is None

    def test_kline_daily_route(self, monkeypatch):
        """fetch(capability=kline_daily) 路由到 _fetch_kline_daily。"""
        p = IFindProvider()
        called = []

        def fake_fetch(self, payload, policy):
            called.append("kline_daily")
            yield FetchResult(
                table="c1_market.kline_daily", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(IFindProvider, "_fetch_kline_daily", fake_fetch)
        payload = FetchPayload(
            table="c1_market.kline_daily", symbols=["600000.SH"],
            start=datetime.date(2025, 6, 1), end=datetime.date(2025, 6, 30),
            extra={"capability": "kline_daily"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["kline_daily"]

    def test_index_kline_route(self, monkeypatch):
        """fetch(capability=index_kline) 路由到 _fetch_index_kline。"""
        p = IFindProvider()
        called = []

        def fake_fetch(self, payload, policy):
            called.append("index_kline")
            yield FetchResult(
                table="c1_market.index_kline", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(IFindProvider, "_fetch_index_kline", fake_fetch)
        payload = FetchPayload(
            table="c1_market.index_kline", symbols=["000300.SH"],
            start=datetime.date(2025, 6, 1), end=datetime.date(2025, 6, 30),
            extra={"capability": "index_kline"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["index_kline"]

    def test_money_flow_route(self, monkeypatch):
        """fetch(capability=money_flow) 路由到 _fetch_money_flow。"""
        p = IFindProvider()
        called = []

        def fake_fetch(self, payload, policy):
            called.append("money_flow")
            yield FetchResult(
                table="c1_market.money_flow", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(IFindProvider, "_fetch_money_flow", fake_fetch)
        payload = FetchPayload(
            table="c1_market.money_flow", symbols=None,
            start=datetime.date(2025, 6, 1), end=datetime.date(2025, 6, 1),
            extra={"capability": "money_flow"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["money_flow"]

    def test_parse_iwencai_money_flow_normal(self):
        """解析 i问财资金流向返回（正常情况）。"""
        p = IFindProvider()
        raw = {
            "tables": [{
                "table": {
                    "股票代码": ["600000.SH", "000001.SZ"],
                    "收盘价": [10.5, 15.3],
                    "涨跌幅": [1.2, -0.5],
                    "主力净流入-净额": [1000000.0, -500000.0],
                    "主力净流入-净占比": [5.0, -2.5],
                    "超大单净流入-净额": [500000.0, -200000.0],
                    "超大单净流入-净占比": [2.5, -1.0],
                    "大单净流入-净额": [300000.0, -150000.0],
                    "大单净流入-净占比": [1.5, -0.8],
                    "中单净流入-净额": [-200000.0, 100000.0],
                    "中单净流入-净占比": [-1.0, 0.5],
                    "小单净流入-净额": [-800000.0, 400000.0],
                    "小单净流入-净占比": [-4.0, 2.0],
                }
            }]
        }
        rows = p._parse_iwencai_money_flow(raw, "2025-06-30")
        assert len(rows) == 2
        assert rows[0][0] == "2025-06-30"  # trade_date
        assert rows[0][1] == "sh600000"     # symbol
        assert rows[0][2] == 10.5           # close
        assert rows[0][4] == 1000000.0      # main_net_inflow
        assert rows[0][14] == "ifind_iwencai"  # data_source
        assert rows[1][1] == "sz000001"
        assert rows[1][4] == -500000.0

    def test_parse_iwencai_money_flow_empty(self):
        """i问财返回无 table 数据 → 空列表。"""
        p = IFindProvider()
        assert p._parse_iwencai_money_flow({}, "2025-06-30") == []
        assert p._parse_iwencai_money_flow({"tables": []}, "2025-06-30") == []
        assert p._parse_iwencai_money_flow("not dict", "2025-06-30") == []

    def test_parse_iwencai_money_flow_no_codes(self):
        """i问财返回无股票代码列 → 空列表。"""
        p = IFindProvider()
        raw = {"tables": [{"table": {"其他字段": [1.0]}}]}
        assert p._parse_iwencai_money_flow(raw, "2025-06-30") == []

    def test_kline_columns_match_schema(self):
        """kline_daily 列顺序与 ClickHouse schema 一致。"""
        expected = ["trade_date", "symbol", "open", "close", "high", "low",
                    "volume", "amount", "amplitude", "pct_change", "change",
                    "turnover", "data_source"]
        assert IFindProvider._KLINE_COLUMNS == expected

    def test_index_kline_columns_match_schema(self):
        """index_kline 列顺序与 ClickHouse schema 一致。"""
        expected = ["trade_date", "symbol", "name", "open", "high", "low",
                    "close", "volume", "amount", "advance_count",
                    "decline_count", "data_source", "quality_flag"]
        assert IFindProvider._INDEX_KLINE_COLUMNS == expected

    def test_money_flow_columns_match_schema(self):
        """money_flow 列顺序与 ClickHouse schema 一致。"""
        expected = ["trade_date", "symbol", "close", "pct_change",
                    "main_net_inflow", "main_net_inflow_pct",
                    "super_large_net_inflow", "super_large_net_inflow_pct",
                    "large_net_inflow", "large_net_inflow_pct",
                    "medium_net_inflow", "medium_net_inflow_pct",
                    "small_net_inflow", "small_net_inflow_pct",
                    "data_source"]
        assert IFindProvider._MONEY_FLOW_COLUMNS == expected

    # ---- concept_sector 能力测试 ----

    def test_concept_sector_route(self, monkeypatch):
        """fetch(capability=concept_sector) 路由到 _fetch_concept_sector。"""
        p = IFindProvider()
        called = []

        def fake_fetch(self, payload, policy):
            called.append("concept_sector")
            yield FetchResult(
                table="c1_market.concept_sector", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(IFindProvider, "_fetch_concept_sector", fake_fetch)
        payload = FetchPayload(
            table="c1_market.concept_sector", symbols=None,
            start=datetime.date(2025, 7, 1), end=datetime.date(2025, 7, 1),
            extra={"capability": "concept_sector"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["concept_sector"]

    def test_concept_sector_columns_match_schema(self):
        """concept_sector 列顺序与 ClickHouse schema 一致。"""
        expected = ["sector_code", "sector_name", "data_source"]
        assert IFindProvider._CONCEPT_SECTOR_COLUMNS == expected

    def test_parse_concept_sectors_normal(self):
        """解析 i问财概念板块返回（正常情况）。"""
        p = IFindProvider()
        raw = {
            "tables": [{
                "table": {
                    "股票代码": ["600000.SH", "000001.SZ"],
                    "所属概念": ["融资融券;深股通;小金属概念", "融资融券;黄金概念"],
                }
            }]
        }
        rows = p._parse_concept_sectors(raw)
        # 唯一概念板块：融资融券、深股通、小金属概念、黄金概念
        # sorted() 按 Unicode 码点排序：小(U+5C0F) < 深(U+6DF1) < 融(U+878D) < 黄(U+9EC4)
        assert len(rows) == 4
        assert rows[0] == ("小金属概念", "小金属概念", "ifind_iwencai")
        assert rows[1] == ("深股通", "深股通", "ifind_iwencai")
        assert rows[2] == ("融资融券", "融资融券", "ifind_iwencai")
        assert rows[3] == ("黄金概念", "黄金概念", "ifind_iwencai")

    def test_parse_concept_sectors_empty(self):
        """i问财返回无 table 数据 → 空列表。"""
        p = IFindProvider()
        assert p._parse_concept_sectors({}) == []
        assert p._parse_concept_sectors({"tables": []}) == []
        assert p._parse_concept_sectors("not dict") == []

    def test_parse_concept_sectors_no_concept_col(self):
        """i问财返回无'所属概念'列 → 空列表。"""
        p = IFindProvider()
        raw = {"tables": [{"table": {"其他字段": [1.0]}}]}
        assert p._parse_concept_sectors(raw) == []

    def test_parse_concept_sectors_dedup(self):
        """重复的概念板块名称去重。"""
        p = IFindProvider()
        raw = {
            "tables": [{
                "table": {
                    "股票代码": ["600000.SH", "000001.SZ", "000002.SZ"],
                    "所属概念": ["融资融券;深股通", "融资融券;黄金概念", "深股通;黄金概念"],
                }
            }]
        }
        rows = p._parse_concept_sectors(raw)
        # 唯一概念板块：融资融券、深股通、黄金概念
        assert len(rows) == 3

    def test_parse_concept_sectors_skips_empty(self):
        """空字符串和非字符串条目被跳过。"""
        p = IFindProvider()
        raw = {
            "tables": [{
                "table": {
                    "股票代码": ["600000.SH", "000001.SZ"],
                    "所属概念": ["", None, "融资融券"],
                }
            }]
        }
        rows = p._parse_concept_sectors(raw)
        assert len(rows) == 1
        assert rows[0][1] == "融资融券"

    # ---- realtime_snapshot 能力测试 ----

    def test_realtime_snapshot_route(self, monkeypatch):
        """fetch(capability=realtime_snapshot) 路由到 _fetch_realtime_snapshot。"""
        p = IFindProvider()
        called = []

        def fake_fetch(self, payload, policy):
            called.append("realtime_snapshot")
            yield FetchResult(
                table="c1_market.realtime_snapshot", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(IFindProvider, "_fetch_realtime_snapshot", fake_fetch)
        payload = FetchPayload(
            table="c1_market.realtime_snapshot", symbols=["000001.SZ"],
            start=datetime.date(2025, 7, 1), end=datetime.date(2025, 7, 1),
            extra={"capability": "realtime_snapshot"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["realtime_snapshot"]

    def test_realtime_snapshot_columns_match_schema(self):
        """realtime_snapshot 列顺序与 ClickHouse schema 一致。"""
        expected = [
            "snapshot_time", "symbol", "open", "high", "low",
            "close", "volume", "amount", "data_source",
        ]
        assert IFindProvider._REALTIME_SNAPSHOT_COLUMNS == expected

    def test_get_list_val_normal(self):
        """_get_list_val 正常取值并转 float。"""
        col_data = {"open": [10.5, 11.0]}
        assert IFindProvider._get_list_val(col_data, "open", 0) == 10.5
        assert IFindProvider._get_list_val(col_data, "open", 1) == 11.0

    def test_get_list_val_missing_key(self):
        """键不存在返回 None。"""
        assert IFindProvider._get_list_val({}, "open", 0) is None

    def test_get_list_val_idx_out_of_range(self):
        """索引越界返回 None。"""
        col_data = {"open": [10.5]}
        assert IFindProvider._get_list_val(col_data, "open", 5) is None

    def test_get_list_val_invalid_value(self):
        """非法值转 float 失败返回 None。"""
        col_data = {"open": ["abc"]}
        assert IFindProvider._get_list_val(col_data, "open", 0) is None

    def test_parse_realtime_quotes_normal(self):
        """解析 THS_RealtimeQuotes 返回（正常情况）。"""
        p = IFindProvider()
        raw = {
            "tables": [{
                "table": {
                    "thscode": ["000001.SZ", "600000.SH"],
                    "ths_open": [10.5, 5.2],
                    "ths_high": [11.0, 5.5],
                    "ths_low": [10.2, 5.0],
                    "ths_close": [10.8, 5.3],
                    "ths_volume": [1000000, 2000000],
                    "ths_amount": [10800000.0, 10600000.0],
                }
            }]
        }
        rows = p._parse_realtime_quotes(raw, "2025-07-11 15:00:00", "000001.SZ,600000.SH")
        assert len(rows) == 2
        # 第一行
        assert rows[0][0] == "2025-07-11 15:00:00"  # snapshot_time
        assert rows[0][1] == "000001"               # symbol
        assert rows[0][2] == 10.5                   # open
        assert rows[0][3] == 11.0                   # high
        assert rows[0][4] == 10.2                   # low
        assert rows[0][5] == 10.8                   # close
        assert rows[0][6] == 1000000                # volume (int)
        assert rows[0][7] == 10800000.0             # amount
        assert rows[0][8] == "ifind_realtime"       # data_source
        # 第二行
        assert rows[1][1] == "600000"
        assert rows[1][6] == 2000000

    def test_parse_realtime_quotes_empty(self):
        """返回无 table 数据 → 空列表。"""
        p = IFindProvider()
        assert p._parse_realtime_quotes({}, "2025-07-11 15:00:00", "000001.SZ") == []
        assert p._parse_realtime_quotes({"tables": []}, "2025-07-11 15:00:00", "000001.SZ") == []
        assert p._parse_realtime_quotes("not dict", "2025-07-11 15:00:00", "000001.SZ") == []

    def test_parse_realtime_quotes_fallback_codes(self):
        """无 thscode 列时用 codes_str 回退。"""
        p = IFindProvider()
        raw = {
            "tables": [{
                "table": {
                    "ths_open": [10.5],
                    "ths_high": [11.0],
                    "ths_low": [10.2],
                    "ths_close": [10.8],
                    "ths_volume": [1000000],
                    "ths_amount": [10800000.0],
                }
            }]
        }
        rows = p._parse_realtime_quotes(raw, "2025-07-11 15:00:00", "000001.SZ")
        assert len(rows) == 1
        assert rows[0][1] == "000001"  # symbol 来自 codes_str 回退

    def test_query_realtime_chunk_quota_error(self, monkeypatch):
        """_query_realtime_chunk 配额耗尽返回 fatal_error。"""
        p = IFindProvider()

        def fake_call_with_policy(func, policy, *args, **kwargs):
            return {"errorcode": -4318, "errmsg": "月度配额耗尽"}

        monkeypatch.setattr(IFindProvider, "_call_with_policy", fake_call_with_policy)
        monkeypatch.setattr(IFindProvider, "_check_ifind_error",
                            lambda self, raw: (True, -4318, "月度配额耗尽"))
        rows, fatal = p._query_realtime_chunk("000001.SZ", SourcePolicy())
        assert rows == []
        assert fatal is not None
        assert "配额" in fatal

    def test_query_realtime_chunk_no_data(self, monkeypatch):
        """_query_realtime_chunk -4001 非交易时段不视为致命错误。"""
        p = IFindProvider()

        def fake_call_with_policy(func, policy, *args, **kwargs):
            return {"errorcode": -4001, "errmsg": "无数据"}

        monkeypatch.setattr(IFindProvider, "_call_with_policy", fake_call_with_policy)
        monkeypatch.setattr(IFindProvider, "_check_ifind_error",
                            lambda self, raw: (True, -4001, "无数据"))
        rows, fatal = p._query_realtime_chunk("000001.SZ", SourcePolicy())
        assert rows == []
        assert fatal is None  # -4001 不视为致命错误


class TestMiniQMTNewCapabilities:
    """MiniQMTProvider 新增能力（kline_1min/financial_statement/index_constituent）的单元测试。"""

    def test_ts_to_datetime(self):
        """毫秒时间戳 → YYYY-MM-DD HH:MM:SS。1704067200000 = 2024-01-01 00:00:00 UTC。"""
        result = MiniQMTProvider._ts_to_datetime(1704067200000)
        assert result == "2024-01-01 00:00:00"

    def test_ts_to_datetime_end_of_day(self):
        """2024-01-01 23:59:59 UTC。"""
        result = MiniQMTProvider._ts_to_datetime(1704153599000)
        assert result == "2024-01-01 23:59:59"

    def test_kline_1min_route(self, monkeypatch):
        """fetch(capability=kline_1min) 路由到 _fetch_kline(period=1m)。"""
        p = MiniQMTProvider()
        called = {}

        def fake_fetch_kline(self, payload, policy, period):
            called["period"] = period
            yield FetchResult(
                table="c1_market.kline_1min", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQMTProvider, "_fetch_kline", fake_fetch_kline)
        payload = FetchPayload(
            table="c1_market.kline_1min", symbols=["000001.SZ"],
            start=datetime.date(2025, 6, 30), end=datetime.date(2025, 6, 30),
            extra={"capability": "kline_1min"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("period") == "1m"

    def test_kline_5min_route(self, monkeypatch):
        """fetch(capability=kline_5min) 路由到 _fetch_kline(period=5m)。"""
        p = MiniQMTProvider()
        called = {}

        def fake_fetch_kline(self, payload, policy, period):
            called["period"] = period
            yield FetchResult(
                table="c1_market.kline_5min", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQMTProvider, "_fetch_kline", fake_fetch_kline)
        payload = FetchPayload(
            table="c1_market.kline_5min", symbols=["000001.SZ"],
            start=datetime.date(2025, 6, 30), end=datetime.date(2025, 6, 30),
            extra={"capability": "kline_5min"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("period") == "5m"

    def test_kline_daily_route(self, monkeypatch):
        """fetch(capability=kline_daily) 路由到 _fetch_kline(period=1d)。"""
        p = MiniQMTProvider()
        called = {}

        def fake_fetch_kline(self, payload, policy, period):
            called["period"] = period
            yield FetchResult(
                table="c1_market.kline_daily", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQMTProvider, "_fetch_kline", fake_fetch_kline)
        payload = FetchPayload(
            table="c1_market.kline_daily", symbols=["000001.SZ"],
            start=datetime.date(2025, 6, 1), end=datetime.date(2025, 6, 30),
            extra={"capability": "kline_daily"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("period") == "1d"

    def test_balance_sheet_route(self, monkeypatch):
        """fetch(capability=balance_sheet) 路由到 _fetch_financial_statement(Balance)。"""
        p = MiniQMTProvider()
        called = {}

        def fake_fetch(self, payload, policy, table_list):
            called["table_list"] = table_list
            yield FetchResult(
                table="c3_fundamental.balance", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQMTProvider, "_fetch_financial_statement", fake_fetch)
        payload = FetchPayload(
            table="c3_fundamental.balance", symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1), end=datetime.date(2025, 6, 30),
            extra={"capability": "balance_sheet"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("table_list") == "Balance"

    def test_index_constituent_route(self, monkeypatch):
        """fetch(capability=index_constituent) 路由到 _fetch_index_constituent。"""
        p = MiniQMTProvider()
        called = []

        def fake_fetch(self, payload, policy):
            called.append("index_constituent")
            yield FetchResult(
                table="c1_market.index_constituent", columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQMTProvider, "_fetch_index_constituent", fake_fetch)
        payload = FetchPayload(
            table="c1_market.index_constituent", symbols=None,
            start=datetime.date(2025, 6, 30), end=datetime.date(2025, 6, 30),
            extra={"capability": "index_constituent"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["index_constituent"]

    def test_financial_capabilities_map(self):
        """验证财务能力映射完整性。"""
        from src.zephyr.data.implementations.miniqmt_provider import MiniQMTProvider as M
        # 检查 fetch 方法中的映射字典
        # 由于 _FINANCIAL_CAPABILITIES 是方法内局部变量，这里通过路由测试间接验证
        # 已在 test_balance_sheet_route 中验证 Balance 映射
        assert hasattr(M, "_fetch_financial_statement")
        assert hasattr(M, "_fetch_index_constituent")
        assert hasattr(M, "_fetch_kline")


# ============== 第二批新增能力测试（15 个数据下载能力）==============

class TestMiniQMTBatch2Capabilities:
    """MiniQMTProvider 第二批新增能力（15 个数据下载）的单元测试。"""

    def test_all_15_capabilities_registered(self):
        """验证 15 个新能力均已注册到 meta.capabilities。"""
        caps = MiniQMTProvider.meta.capabilities
        new_caps = [
            "cb_kline", "option_kline", "option_greeks", "index_weight",
            "sector_list", "l2_tick", "auction_data", "futures_kline_qmt",
            "hk_kline", "us_kline", "etf_nav", "repurchase",
            "margin_trading_qmt", "dragon_tiger_qmt", "block_trade_qmt",
        ]
        for cap in new_caps:
            assert cap in caps, f"能力 {cap} 未注册到 meta.capabilities"

    def test_calc_bs_greeks_call(self):
        """BS 模型 call Greeks 计算（S=100,K=100,T=0.25,r=0.05,sigma=0.2）。"""
        g = MiniQMTProvider._calc_bs_greeks(100, 100, 0.25, 0.05, 0.2, "call")
        assert g is not None
        assert abs(g["delta"] - 0.569) < 0.01
        assert abs(g["gamma"] - 0.0393) < 0.001
        assert abs(g["vega"] - 0.196) < 0.01

    def test_calc_bs_greeks_put(self):
        """BS 模型 put Greeks 计算。"""
        g = MiniQMTProvider._calc_bs_greeks(100, 100, 0.25, 0.05, 0.2, "put")
        assert g is not None
        assert g["delta"] < 0  # put delta 为负
        assert abs(g["delta"] - (-0.431)) < 0.01

    def test_calc_bs_greeks_none_params(self):
        """参数不足时返回 None。"""
        assert MiniQMTProvider._calc_bs_greeks(None, 100, 0.25, 0.05, 0.2, "call") is None
        assert MiniQMTProvider._calc_bs_greeks(100, None, 0.25, 0.05, 0.2, "call") is None
        assert MiniQMTProvider._calc_bs_greeks(100, 0, 0.25, 0.05, 0.2, "call") is None
        assert MiniQMTProvider._calc_bs_greeks(100, 100, 0, 0.05, 0.2, "call") is None

    def test_cb_kline_route(self, monkeypatch):
        """fetch(capability=cb_kline) 路由到 _fetch_cb_kline。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("cb_kline")
            yield FetchResult(table="c1_market.cb_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_cb_kline", fake)
        payload = FetchPayload(table="", symbols=["113001.SH"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "cb_kline"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["cb_kline"]

    def test_option_kline_route(self, monkeypatch):
        """fetch(capability=option_kline) 路由到 _fetch_option_kline。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("option_kline")
            yield FetchResult(table="c1_market.option_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_option_kline", fake)
        payload = FetchPayload(table="", symbols=["10000001.SH"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "option_kline"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["option_kline"]

    def test_option_greeks_route(self, monkeypatch):
        """fetch(capability=option_greeks) 路由到 _fetch_option_greeks。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("option_greeks")
            yield FetchResult(table="c1_market.option_greeks", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_option_greeks", fake)
        payload = FetchPayload(table="", symbols=["10000001.SH"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "option_greeks"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["option_greeks"]

    def test_index_weight_route(self, monkeypatch):
        """fetch(capability=index_weight) 路由到 _fetch_index_weight。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("index_weight")
            yield FetchResult(table="c1_market.index_weight", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_index_weight", fake)
        payload = FetchPayload(table="", symbols=["000300.SH"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "index_weight"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["index_weight"]

    def test_sector_list_route(self, monkeypatch):
        """fetch(capability=sector_list) 路由到 _fetch_sector_list。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("sector_list")
            yield FetchResult(table="c1_market.sector_list", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_sector_list", fake)
        payload = FetchPayload(table="", symbols=None, start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "sector_list"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["sector_list"]

    def test_l2_tick_route(self, monkeypatch):
        """fetch(capability=l2_tick) 路由到 _fetch_l2_tick。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("l2_tick")
            yield FetchResult(table="c1_market.l2_tick", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_l2_tick", fake)
        payload = FetchPayload(table="", symbols=["000001.SZ"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "l2_tick"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["l2_tick"]

    def test_auction_data_route(self, monkeypatch):
        """fetch(capability=auction_data) 路由到 _fetch_auction_data。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("auction_data")
            yield FetchResult(table="c1_market.auction_snapshot", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_auction_data", fake)
        payload = FetchPayload(table="", symbols=["000001.SZ"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "auction_data"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["auction_data"]

    def test_futures_kline_qmt_route(self, monkeypatch):
        """fetch(capability=futures_kline_qmt) 路由到 _fetch_futures_kline_qmt。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("futures_kline_qmt")
            yield FetchResult(table="c1_market.futures_kline_qmt", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_futures_kline_qmt", fake)
        payload = FetchPayload(table="", symbols=["IF2407.CFFEX"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "futures_kline_qmt"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["futures_kline_qmt"]

    def test_hk_kline_route(self, monkeypatch):
        """fetch(capability=hk_kline) 路由到 _fetch_hk_kline。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("hk_kline")
            yield FetchResult(table="c1_market.hk_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_hk_kline", fake)
        payload = FetchPayload(table="", symbols=["00700.HK"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "hk_kline"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["hk_kline"]

    def test_us_kline_route(self, monkeypatch):
        """fetch(capability=us_kline) 路由到 _fetch_us_kline。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("us_kline")
            yield FetchResult(table="c1_market.us_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_us_kline", fake)
        payload = FetchPayload(table="", symbols=["AAPL.US"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "us_kline"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["us_kline"]

    def test_etf_nav_route(self, monkeypatch):
        """fetch(capability=etf_nav) 路由到 _fetch_etf_nav。"""
        p = MiniQMTProvider()
        called = []

        def fake(self, payload, policy):
            called.append("etf_nav")
            yield FetchResult(table="c1_market.etf_nav", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQMTProvider, "_fetch_etf_nav", fake)
        payload = FetchPayload(table="", symbols=["510050.SH"], start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "etf_nav"})
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["etf_nav"]

    def test_repurchase_returns_error(self):
        """repurchase 占位方法返回 error。"""
        p = MiniQMTProvider()
        payload = FetchPayload(table="", symbols=None, start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "repurchase"})
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "QMT" in results[0].error or "AKShare" in results[0].error

    def test_margin_trading_qmt_returns_error(self):
        """margin_trading_qmt 占位方法返回 error。"""
        p = MiniQMTProvider()
        payload = FetchPayload(table="", symbols=None, start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "margin_trading_qmt"})
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_dragon_tiger_qmt_returns_error(self):
        """dragon_tiger_qmt 占位方法返回 error。"""
        p = MiniQMTProvider()
        payload = FetchPayload(table="", symbols=None, start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "dragon_tiger_qmt"})
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_block_trade_qmt_returns_error(self):
        """block_trade_qmt 占位方法返回 error。"""
        p = MiniQMTProvider()
        payload = FetchPayload(table="", symbols=None, start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 10), extra={"capability": "block_trade_qmt"})
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_detect_market_type_cb(self):
        """可转债代码识别为 cb。"""
        assert MiniQMTProvider._detect_market_type("113001.SH") == "cb"
        assert MiniQMTProvider._detect_market_type("128001.SZ") == "cb"

    def test_format_tick_timestamp(self):
        """tick 时间戳格式化。"""
        td, ts = MiniQMTProvider._format_tick_timestamp("20240103093015", datetime.date(2024, 1, 3))
        assert td == "2024-01-03"
        assert ts == "2024-01-03 09:30:15"
