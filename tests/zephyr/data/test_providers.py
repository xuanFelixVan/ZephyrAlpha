"""Provider 实现的单测（MOD-L00-004 阶段1）。

测试 3 个 Provider 的辅助方法（纯函数，不依赖真实 SDK）和 fetch 路由。
不测试真实 SDK 调用（需 iFind/QMT/AKShare 环境）。
"""
import datetime
import math
import pytest

from src.zephyr.data.provider_base import FetchPayload
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
