# [BLUEPRINT] MOD-L00-005 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""Provider 实现的单测（MOD-L00-004 阶段1）。

测试 3 个 Provider（akshare/miniqmt/tqcenter）的辅助方法（纯函数，不依赖真实 SDK）和 fetch 路由。
不测试真实 SDK 调用（需 QMT/AKShare/通达信 环境）。
"""

import datetime
import sys
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.zephyr.data.implementations.akshare_provider import (
    AkshareIngestProvider,
)
from src.zephyr.data.implementations.akshare_provider import (
    safe_float as ak_safe_float,
)
from src.zephyr.data.implementations.baostock_provider import BaostockProvider
from src.zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider
from src.zephyr.data.implementations.tqcenter_provider import (
    TQCenterProvider,
)
from src.zephyr.data.implementations.tqcenter_provider import (
    _safe_val as tq_safe_val,
)
from src.zephyr.data.implementations.tushare_provider import TushareProvider
from src.zephyr.data.policy_registry import SourcePolicy
from src.zephyr.data.provider_base import FetchPayload, FetchResult

# ============== AkshareIngestProvider 测试 ==============


class TestAKShareHelpers:
    def test_quarter_to_date_q1(self):
        assert AkshareIngestProvider.quarter_to_date("2025年第1季度") == "2025-03-31"

    def test_quarter_to_date_q4(self):
        assert AkshareIngestProvider.quarter_to_date("2024年第4季度") == "2024-12-31"

    def test_quarter_to_date_q2(self):
        assert AkshareIngestProvider.quarter_to_date("2025年第2季度") == "2025-06-30"

    def test_quarter_to_date_q3(self):
        assert AkshareIngestProvider.quarter_to_date("2025年第3季度") == "2025-09-30"

    def test_month_to_date_june(self):
        assert AkshareIngestProvider.month_to_date("2025年6月") == "2025-06-30"

    def test_month_to_date_december(self):
        assert AkshareIngestProvider.month_to_date("2025年12月") == "2025-12-31"

    def test_month_to_date_february_leap(self):
        """闰年 2 月末。"""
        assert AkshareIngestProvider.month_to_date("2024年2月") == "2024-02-29"

    def test_month_to_date_february_nonleap(self):
        assert AkshareIngestProvider.month_to_date("2025年2月") == "2025-02-28"

    def test_module_safe_float(self):
        assert ak_safe_float(1.5) == 1.5
        assert ak_safe_float(None) is None
        assert ak_safe_float("abc") is None


class TestAKShareFetchRoute:
    def test_unknown_capability_yields_error(self):
        p = AkshareIngestProvider()
        payload = FetchPayload(
            table="t",
            symbols=None,
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 2),
            extra={"capability": "nonexistent"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_meta(self):
        assert AkshareIngestProvider.meta.name == "akshare"
        assert AkshareIngestProvider.source_name == "akshare"
        assert (
            "VPN" in AkshareIngestProvider.meta.known_issues[0]
            or "vpn" in AkshareIngestProvider.meta.known_issues[0].lower()
        )


# ============== MiniQmtIngestProvider 测试 ==============


class TestMiniQMTHelpers:
    def test_date_to_str(self):
        assert MiniQmtIngestProvider.date_to_str(datetime.date(2024, 1, 9)) == "20240109"
        assert MiniQmtIngestProvider.date_to_str(datetime.date(2024, 12, 31)) == "20241231"

    def test_ts_to_date(self):
        """毫秒时间戳 → YYYY-MM-DD。1704067200000 = 2024-01-01 00:00:00 UTC。"""
        result = MiniQmtIngestProvider.ts_to_date(1704067200000)
        assert result == "2024-01-01"

    def test_ts_to_date_end_of_day(self):
        """2024-01-01 23:59:59 UTC → 2024-01-01。"""
        result = MiniQmtIngestProvider.ts_to_date(1704153599000)
        assert result == "2024-01-01"

    def test_stock_to_symbol_sz(self):
        assert MiniQmtIngestProvider.stock_to_symbol("000001.SZ") == "000001"

    def test_stock_to_symbol_sh(self):
        assert MiniQmtIngestProvider.stock_to_symbol("600000.SH") == "600000"

    def test_safe_float_normal(self):
        assert MiniQmtIngestProvider.safe_float(1.5) == 1.5
        assert MiniQmtIngestProvider.safe_float("2.3") == 2.3

    def test_safe_float_none(self):
        assert MiniQmtIngestProvider.safe_float(None) is None

    def test_safe_float_nan(self):
        assert MiniQmtIngestProvider.safe_float(float("nan")) is None

    def test_safe_float_invalid(self):
        assert MiniQmtIngestProvider.safe_float("abc") is None


class TestMiniQMTFetchRoute:
    def test_unknown_capability_yields_error(self):
        p = MiniQmtIngestProvider()
        payload = FetchPayload(
            table="t",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 2),
            extra={"capability": "nonexistent"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_meta(self):
        assert MiniQmtIngestProvider.meta.name == "miniqmt"
        assert MiniQmtIngestProvider.source_name == "miniqmt"
        assert MiniQmtIngestProvider.meta.requires_process is True
        assert MiniQmtIngestProvider.meta.thread_safety == "single_thread"


# ============== TQCenterProvider 测试 ==============
# 纯函数单测（不依赖通达信客户端 SDK，符合 test_providers.py 既有约定）


class TestTQCenterHelpers:
    """TQCenterProvider 辅助方法（纯函数，不依赖真实 tqcenter SDK）。"""

    def test_safe_val_none(self):
        assert tq_safe_val(None, "def") == "def"

    def test_safe_val_nan(self):
        assert tq_safe_val(float("nan"), 0) == 0

    def test_safe_val_normal(self):
        assert tq_safe_val(1.5, 0) == 1.5
        assert tq_safe_val("x", "def") == "x"

    def test_ts_to_datetime_datetime(self):
        """datetime 直接返回 (date, datetime)。"""
        dt = datetime.datetime(2026, 7, 30, 14, 30, 0)
        d, out = TQCenterProvider._ts_to_datetime(dt, "1d")
        assert d == datetime.date(2026, 7, 30)
        assert out == dt

    def test_ts_to_datetime_str(self):
        """字符串时间戳解析。"""
        d, dt = TQCenterProvider._ts_to_datetime("2026-07-30 14:30:00", "1d")
        assert d == datetime.date(2026, 7, 30)
        assert dt == datetime.datetime(2026, 7, 30, 14, 30, 0)

    def test_ts_to_datetime_pd_timestamp_1d(self):
        """pandas.Timestamp 日K → date + naive datetime。"""
        pd = pytest.importorskip("pandas")
        ts = pd.Timestamp("2026-07-30")
        d, dt = TQCenterProvider._ts_to_datetime(ts, "1d")
        assert d == datetime.date(2026, 7, 30)
        assert dt == datetime.datetime(2026, 7, 30)

    def test_parse_snapshot_valid(self):
        """有效快照 dict → 元组行（含 18 字段 + data_source）。
        #ARCH-DATA-016：SDK 返回 PascalCase 键（以 2026-08-14 实测 dump 为准）。"""
        trade_date = datetime.date(2026, 7, 30)
        ts = datetime.datetime(2026, 7, 30, 15, 0, 0)
        snap = {
            "Now": 10.5,
            "Open": 10.0,
            "Max": 10.8,
            "Min": 9.9,
            "LastClose": 10.2,
            "Before5MinNow": 10.3,
            "Average": 10.4,
            "Volume": 1000,
            "NowVol": 50,
            "Amount": 10500.0,
            "UpHome": 100,
            "DownHome": 80,
            "Inside": 40,
            "Outside": 60,
            "Zangsu": 0.5,
        }
        row = TQCenterProvider._parse_snapshot("880001", snap, trade_date, ts)
        assert row is not None
        assert row[0] == trade_date  # trade_date
        assert row[1] == ts  # timestamp
        assert row[2] == "880001"  # sector_code
        assert row[3] == "sector"  # market_type
        assert row[4] == 10.5  # now_price
        assert row[8] == 10.2  # last_close
        assert row[11] == 1000  # volume
        assert row[-1] == "tqcenter"  # data_source

    def test_parse_snapshot_none(self):
        """None 快照 → None。"""
        row = TQCenterProvider._parse_snapshot(
            "880001", None, datetime.date(2026, 7, 30), datetime.datetime(2026, 7, 30)
        )
        assert row is None

    def test_parse_kline_df_empty(self):
        """空/None DataFrame → 空行列表。"""
        p = TQCenterProvider()
        assert p._parse_kline_df(None, ["880001"], "1d") == []
        assert p._parse_kline_df({}, ["880001"], "1d") == []

    def test_parse_kline_df_valid(self):
        """有效 dict-of-DataFrames → 解析出 K线行。"""
        pd = pytest.importorskip("pandas")
        ts = datetime.datetime(2026, 7, 30)
        idx = pd.DatetimeIndex([ts])
        df = {
            "Open": pd.DataFrame({"880001": [10.0]}, index=idx),
            "High": pd.DataFrame({"880001": [10.8]}, index=idx),
            "Low": pd.DataFrame({"880001": [9.9]}, index=idx),
            "Close": pd.DataFrame({"880001": [10.5]}, index=idx),
            "Volume": pd.DataFrame({"880001": [1000]}, index=idx),
            "Amount": pd.DataFrame({"880001": [10500.0]}, index=idx),
            "ForwardFactor": pd.DataFrame({"880001": [1.0]}, index=idx),
        }
        p = TQCenterProvider()
        rows = p._parse_kline_df(df, ["880001"], "1d")
        assert len(rows) == 1
        row = rows[0]
        assert row[0] == "1d"  # period
        assert row[3] == "880001"  # sector_code
        assert float(row[5]) == 10.0  # open (Decimal→float 比较)
        assert float(row[6]) == 10.8  # high
        assert row[-1] == "tqcenter"  # data_source


class TestTQCenterFetchRoute:
    """TQCenterProvider fetch 路由 + meta 单测（不连接真实 SDK）。"""

    def test_meta(self):
        assert TQCenterProvider.meta.name == "tqcenter"
        assert TQCenterProvider.source_name == "tqcenter"
        assert TQCenterProvider.meta.requires_process is True
        assert TQCenterProvider.meta.thread_safety == "single_thread"
        assert TQCenterProvider.meta.auth_type == "anonymous"

    def test_not_connected_yields_error(self):
        """未连接时 fetch 返回 error 结果。"""
        p = TQCenterProvider()
        payload = FetchPayload(
            table="t",
            symbols=["880001"],
            start=datetime.date(2026, 7, 30),
            end=datetime.date(2026, 7, 31),
            extra={"capability": "kline_sector_880"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "未连接" in results[0].error

    def test_unknown_capability_yields_error(self):
        """已连接但 capability 未知 → error（用 mock tq 绕过 SDK）。"""
        p = TQCenterProvider()
        p._connected = True
        p._tq = MagicMock()
        payload = FetchPayload(
            table="t",
            symbols=["880001"],
            start=datetime.date(2026, 7, 30),
            end=datetime.date(2026, 7, 31),
            extra={"capability": "nonexistent"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "unsupported capability" in results[0].error


# ============== 新能力测试（阶段4） ==============


class TestMiniQMTNewCapabilities:
    """MiniQmtIngestProvider 新增能力（kline_1min/financial_statement/index_constituent）的单元测试。"""

    def test_ts_to_datetime(self):
        """毫秒时间戳 → YYYY-MM-DD HH:MM:SS。1704067200000 = 2024-01-01 00:00:00 UTC。"""
        result = MiniQmtIngestProvider.ts_to_datetime(1704067200000)
        assert result == "2024-01-01 00:00:00"

    def test_ts_to_datetime_end_of_day(self):
        """2024-01-01 23:59:59 UTC。"""
        result = MiniQmtIngestProvider.ts_to_datetime(1704153599000)
        assert result == "2024-01-01 23:59:59"

    def test_kline_1min_route(self, monkeypatch):
        """fetch(capability=kline_1min) 路由到 _fetch_kline(period=1m)。"""
        p = MiniQmtIngestProvider()
        called = {}

        def fake_fetch_kline(self, payload, policy, period, **kwargs):
            called["period"] = period
            yield FetchResult(
                table="c1_market.kline_1min",
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_kline", fake_fetch_kline)
        payload = FetchPayload(
            table="c1_market.kline_1min",
            symbols=["000001.SZ"],
            start=datetime.date(2025, 6, 30),
            end=datetime.date(2025, 6, 30),
            extra={"capability": "kline_1min"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("period") == "1m"

    def test_kline_5min_route(self, monkeypatch):
        """fetch(capability=kline_5min) 路由到 _fetch_kline(period=5m)。"""
        p = MiniQmtIngestProvider()
        called = {}

        def fake_fetch_kline(self, payload, policy, period, **kwargs):
            called["period"] = period
            yield FetchResult(
                table="c1_market.kline_5min",
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_kline", fake_fetch_kline)
        payload = FetchPayload(
            table="c1_market.kline_5min",
            symbols=["000001.SZ"],
            start=datetime.date(2025, 6, 30),
            end=datetime.date(2025, 6, 30),
            extra={"capability": "kline_5min"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("period") == "5m"

    def test_kline_daily_route(self, monkeypatch):
        """fetch(capability=kline_daily) 路由到 _fetch_kline(period=1d)。"""
        p = MiniQmtIngestProvider()
        called = {}

        def fake_fetch_kline(self, payload, policy, period, **kwargs):
            called["period"] = period
            yield FetchResult(
                table="c1_market.kline_daily",
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_kline", fake_fetch_kline)
        payload = FetchPayload(
            table="c1_market.kline_daily",
            symbols=["000001.SZ"],
            start=datetime.date(2025, 6, 1),
            end=datetime.date(2025, 6, 30),
            extra={"capability": "kline_daily"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("period") == "1d"

    def test_balance_sheet_route(self, monkeypatch):
        """fetch(capability=balance_sheet) 路由到 _fetch_financial_statement(Balance)。"""
        p = MiniQmtIngestProvider()
        called = {}

        def fake_fetch(self, payload, policy, table_list):
            called["table_list"] = table_list
            yield FetchResult(
                table="c3_fundamental.balance",
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_financial_statement", fake_fetch)
        payload = FetchPayload(
            table="c3_fundamental.balance",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2025, 6, 30),
            extra={"capability": "balance_sheet"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called.get("table_list") == "Balance"

    def test_index_constituent_route(self, monkeypatch):
        """fetch(capability=index_constituent) 路由到 _fetch_index_constituent。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake_fetch(self, payload, policy):
            called.append("index_constituent")
            yield FetchResult(
                table="c1_market.index_constituent",
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
            )

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_index_constituent", fake_fetch)
        payload = FetchPayload(
            table="c1_market.index_constituent",
            symbols=None,
            start=datetime.date(2025, 6, 30),
            end=datetime.date(2025, 6, 30),
            extra={"capability": "index_constituent"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["index_constituent"]

    def test_financial_capabilities_map(self):
        """验证财务能力映射完整性。"""
        from src.zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider as M

        # 检查 fetch 方法中的映射字典
        # 由于 _FINANCIAL_CAPABILITIES 是方法内局部变量，这里通过路由测试间接验证
        # 已在 test_balance_sheet_route 中验证 Balance 映射
        assert hasattr(M, "fetch_financial_statement")
        assert hasattr(M, "fetch_index_constituent")
        assert hasattr(M, "fetch_kline")


# ============== 第二批新增能力测试（15 个数据下载能力）==============


class TestMiniQMTBatch2Capabilities:
    """MiniQmtIngestProvider 第二批新增能力（15 个数据下载）的单元测试。"""

    def test_all_15_capabilities_registered(self):
        """验证 15 个新能力均已注册到 meta.capabilities。"""
        caps = MiniQmtIngestProvider.meta.capabilities
        # 兼容 str 与 CapabilityContract（治本修复#ARCH-CAP-NULL-SYMBOLS-001）
        cap_ids = {c.capability_id if hasattr(c, "capability_id") else c for c in caps}
        new_caps = [
            "kline_cb",
            "option_kline",
            "option_greeks",
            "index_weight",
            "sector_list",
            "l2_tick",
            "auction_data",
            "futures_kline_qmt",
            "hk_kline",
            "kline_us_daily",
            "etf_nav",
            "repurchase",
            "margin_trading_qmt",
            "dragon_tiger_qmt",
            "block_trade_qmt",
        ]
        for cap in new_caps:
            assert cap in cap_ids, f"能力 {cap} 未注册到 meta.capabilities"

    def test_calc_bs_greeks_call(self):
        """BS 模型 call Greeks 计算（S=100,K=100,T=0.25,r=0.05,sigma=0.2）。"""
        g = MiniQmtIngestProvider.calc_bs_greeks(100, 100, 0.25, 0.05, 0.2, "call")
        assert g is not None
        assert abs(g["delta"] - 0.569) < 0.01
        assert abs(g["gamma"] - 0.0393) < 0.001
        assert abs(g["vega"] - 0.196) < 0.01

    def test_calc_bs_greeks_put(self):
        """BS 模型 put Greeks 计算。"""
        g = MiniQmtIngestProvider.calc_bs_greeks(100, 100, 0.25, 0.05, 0.2, "put")
        assert g is not None
        assert g["delta"] < 0  # put delta 为负
        assert abs(g["delta"] - (-0.431)) < 0.01

    def test_calc_bs_greeks_none_params(self):
        """参数不足时返回 None。"""
        assert MiniQmtIngestProvider.calc_bs_greeks(None, 100, 0.25, 0.05, 0.2, "call") is None
        assert MiniQmtIngestProvider.calc_bs_greeks(100, None, 0.25, 0.05, 0.2, "call") is None
        assert MiniQmtIngestProvider.calc_bs_greeks(100, 0, 0.25, 0.05, 0.2, "call") is None
        assert MiniQmtIngestProvider.calc_bs_greeks(100, 100, 0, 0.05, 0.2, "call") is None

    def test_cb_kline_route(self, monkeypatch):
        """fetch(capability=kline_cb) 路由到 _fetch_kline_cb。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("kline_cb")
            yield FetchResult(table="c1_market.cb_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_kline_cb", fake)
        payload = FetchPayload(
            table="",
            symbols=["113001.SH"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "kline_cb"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["kline_cb"]

    def test_option_kline_route(self, monkeypatch):
        """fetch(capability=option_kline) 路由到 _fetch_option_kline。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("option_kline")
            yield FetchResult(table="c1_market.option_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_option_kline", fake)
        payload = FetchPayload(
            table="",
            symbols=["10000001.SH"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "option_kline"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["option_kline"]

    def test_option_greeks_route(self, monkeypatch):
        """fetch(capability=option_greeks) 路由到 _fetch_option_greeks。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("option_greeks")
            yield FetchResult(table="c1_market.option_greeks", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_option_greeks", fake)
        payload = FetchPayload(
            table="",
            symbols=["10000001.SH"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "option_greeks"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["option_greeks"]

    def test_index_weight_route(self, monkeypatch):
        """fetch(capability=index_weight) 路由到 _fetch_index_weight。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("index_weight")
            yield FetchResult(table="c1_market.index_weight", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_index_weight", fake)
        payload = FetchPayload(
            table="",
            symbols=["000300.SH"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "index_weight"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["index_weight"]

    def test_sector_list_route(self, monkeypatch):
        """fetch(capability=sector_list) 路由到 _fetch_sector_list。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("sector_list")
            yield FetchResult(table="c1_market.sector_list", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_sector_list", fake)
        payload = FetchPayload(
            table="",
            symbols=None,
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "sector_list"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["sector_list"]

    def test_l2_tick_route(self, monkeypatch):
        """fetch(capability=l2_tick) 路由到 _fetch_l2_tick。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("l2_tick")
            yield FetchResult(table="c1_market.l2_tick", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_l2_tick", fake)
        payload = FetchPayload(
            table="",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "l2_tick"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["l2_tick"]

    def test_auction_data_route(self, monkeypatch):
        """fetch(capability=auction_data) 路由到 _fetch_auction_data。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("auction_data")
            yield FetchResult(table="c1_market.auction_snapshot", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_auction_data", fake)
        payload = FetchPayload(
            table="",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "auction_data"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["auction_data"]

    def test_futures_kline_qmt_route(self, monkeypatch):
        """fetch(capability=futures_kline_qmt) 路由到 _fetch_kline_futures_qmt。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("futures_kline_qmt")
            yield FetchResult(table="c1_market.futures_kline_qmt", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_kline_futures_qmt", fake)
        payload = FetchPayload(
            table="",
            symbols=["IF2407.CFFEX"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "futures_kline_qmt"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["futures_kline_qmt"]

    def test_kline_futures_route(self, monkeypatch):
        """fetch(capability=kline_futures) 路由到 _fetch_kline_futures_qmt（tracker #246 治本：
        原错路由 _KLINE_1D_CAPABILITIES→_fetch_kline，symbols 空时拉沪深A股全量个股写入期货表）。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("kline_futures")
            yield FetchResult(table="c1_market.kline_futures", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_kline_futures_qmt", fake)
        payload = FetchPayload(
            table="c1_market.kline_futures",
            symbols=["IF2407.CFFEX"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "kline_futures"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["kline_futures"]

    def test_kline_futures_whitelist_guard(self, monkeypatch):
        """tracker #246 白名单护栏：fetch_kline_futures_qmt 剔除非 IF/IC/IM/IH 标的（个股/商品期货）。"""
        monkeypatch.setitem(sys.modules, "xtquant", MagicMock())  # 方法内 import xtquant，测试环境 mock
        p = MiniQmtIngestProvider()
        captured = []

        def fake_simple_kline(self, payload, policy, default_table, include_exchange=False):
            captured.append(list(payload.symbols or []))
            yield FetchResult(table=default_table, columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "_fetch_simple_kline", fake_simple_kline)
        payload = FetchPayload(
            table="c1_market.kline_futures",
            symbols=["IF00.IF", "IC2407.CFFEX", "IM0", "IH2409.CFFEX", "000001.SZ", "600000.SH", "RB2407.SHF", "I2407.DCE"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "kline_futures"},
        )
        list(p.fetch_kline_futures_qmt(payload, SourcePolicy()))
        assert captured == [["IF00.IF", "IC2407.CFFEX", "IM0", "IH2409.CFFEX"]]


    def test_hk_kline_route(self, monkeypatch):
        """fetch(capability=hk_kline) 路由到 _fetch_hk_kline。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("hk_kline")
            yield FetchResult(table="c1_market.hk_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_hk_kline", fake)
        payload = FetchPayload(
            table="",
            symbols=["00700.HK"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "hk_kline"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["hk_kline"]

    def test_us_kline_route(self, monkeypatch):
        """fetch(capability=kline_us_daily) 路由到 _fetch_us_kline。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("kline_us_daily")
            yield FetchResult(table="c1_market.us_kline", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_us_kline", fake)
        payload = FetchPayload(
            table="",
            symbols=["AAPL.US"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "kline_us_daily"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["kline_us_daily"]

    def test_etf_nav_route(self, monkeypatch):
        """fetch(capability=etf_nav) 路由到 _fetch_etf_nav。"""
        p = MiniQmtIngestProvider()
        called = []

        def fake(self, payload, policy):
            called.append("etf_nav")
            yield FetchResult(table="c1_market.etf_nav", columns=[], rows=[], last_key="", elapsed_sec=0.0)

        monkeypatch.setattr(MiniQmtIngestProvider, "fetch_etf_nav", fake)
        payload = FetchPayload(
            table="",
            symbols=["510050.SH"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "etf_nav"},
        )
        list(p.fetch(payload, SourcePolicy()))
        assert called == ["etf_nav"]

    def test_repurchase_returns_error(self):
        """repurchase 占位方法返回 error。"""
        p = MiniQmtIngestProvider()
        payload = FetchPayload(
            table="",
            symbols=None,
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "repurchase"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None
        assert "QMT" in results[0].error or "AKShare" in results[0].error

    def test_margin_trading_qmt_returns_error(self):
        """margin_trading_qmt 占位方法返回 error。"""
        p = MiniQmtIngestProvider()
        payload = FetchPayload(
            table="",
            symbols=None,
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "margin_trading_qmt"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_dragon_tiger_qmt_returns_error(self):
        """dragon_tiger_qmt 占位方法返回 error。"""
        p = MiniQmtIngestProvider()
        payload = FetchPayload(
            table="",
            symbols=None,
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "dragon_tiger_qmt"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_block_trade_qmt_returns_error(self):
        """block_trade_qmt 占位方法返回 error。"""
        p = MiniQmtIngestProvider()
        payload = FetchPayload(
            table="",
            symbols=None,
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
            extra={"capability": "block_trade_qmt"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is not None

    def test_detect_market_type_cb(self):
        """可转债代码识别为 cb。"""
        assert MiniQmtIngestProvider.detect_market_type("113001.SH") == "cb"
        assert MiniQmtIngestProvider.detect_market_type("128001.SZ") == "cb"

    def test_format_tick_timestamp(self):
        """tick 时间戳格式化。"""
        td, ts = MiniQmtIngestProvider.format_tick_timestamp("20240103093015", datetime.date(2024, 1, 3))
        assert td == "2024-01-03"
        assert ts == "2024-01-03 09:30:15"


# ============== MiniQMT 高复杂度函数 smoke test（P3 防回归）==============
# 覆盖5个零测试覆盖的高复杂度函数（QMT 是 memory 反复踩坑源头）：
#   _load_cb_details_map(22) / fetch_financial_statement(18) / _fetch_shareholder(18)
#   / _fetch_financial_by_table(18) / _fetch_futures_term_structure(16)
# 用 MagicMock 模拟 xtquant.xtdata，验证空数据不崩溃 + 有效数据返回正确格式。


class TestMiniQMTSmoke:
    """miniqmt_provider 5个高复杂度函数 smoke test（P3 防回归）。"""

    def _make_provider(self, monkeypatch):
        """构造带 xtquant mock 的 provider，返回 (provider, mock_xtdata)。"""
        mock_xtquant = MagicMock()
        mock_xtdata = mock_xtquant.xtdata
        # 设置 __name__ 供 fake_call 按 fn 名派发（MagicMock 默认 __name__ 是子 mock）
        for fn_name in (
            "get_market_data_ex",
            "download_history_data",
            "get_stock_list_in_sector",
            "get_financial_data",
            "download_financial_data2",
            "get_instrument_detail",
        ):
            getattr(mock_xtdata, fn_name).__name__ = fn_name
        monkeypatch.setitem(sys.modules, "xtquant", mock_xtquant)
        monkeypatch.setitem(sys.modules, "xtquant.xtdata", mock_xtdata)
        p = MiniQmtIngestProvider()
        return p, mock_xtdata

    # ---- 1. _load_cb_details_map（复杂度22）----

    def test_load_cb_details_map_empty(self, monkeypatch):
        """akshare + QMT 均失败 → 返回 {} 不崩溃。"""
        p, _ = self._make_provider(monkeypatch)

        def fake_call(fn, policy, *a, **kw):
            raise RuntimeError("mock empty")

        monkeypatch.setattr(p, "_call_with_policy", fake_call)
        result = p._load_cb_details_map(SourcePolicy())
        assert result == {}

    def test_load_cb_details_map_valid(self, monkeypatch):
        """akshare bond_zh_cov 返回1条 → 解析出 cb_key + underlying + convert_price。"""
        pd = pytest.importorskip("pandas")
        p, _ = self._make_provider(monkeypatch)
        # mock akshare 模块（真实 akshare 的 bond_zh_cov 访问触发 pkg_resources
        # 弃用警告，被 pytest filterwarnings=error 当异常，绕过用 mock）
        mock_ak = MagicMock()
        mock_ak.bond_zh_cov.__name__ = "bond_zh_cov"
        monkeypatch.setitem(sys.modules, "akshare", mock_ak)
        bond_df = pd.DataFrame(
            [
                {
                    "债券代码": "113001",
                    "正股代码": "600000",
                    "转股价": 10.5,
                }
            ]
        )

        def fake_call(fn, policy, *a, **kw):
            if getattr(fn, "__name__", "") == "bond_zh_cov":
                return bond_df
            return []

        monkeypatch.setattr(p, "_call_with_policy", fake_call)
        result = p._load_cb_details_map(SourcePolicy())
        assert "113001.SH" in result
        assert result["113001.SH"]["underlying"] == "600000.SH"
        assert result["113001.SH"]["convert_price"] == 10.5

    # ---- 2. fetch_financial_statement（复杂度18）----

    def test_fetch_financial_statement_empty(self, monkeypatch):
        """空数据 → FetchResult rows=[] 不崩溃。"""
        p, _ = self._make_provider(monkeypatch)
        monkeypatch.setattr(p, "_call_with_policy", lambda fn, pol, *a, **kw: {})
        payload = FetchPayload(
            table="c3_fundamental.balance",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 3, 31),
            extra={},
        )
        results = list(p.fetch_financial_statement(payload, SourcePolicy(), "Balance"))
        assert len(results) == 1
        assert results[0].rows == []

    def test_fetch_financial_statement_valid(self, monkeypatch):
        """有效财务数据（m_anntime 在窗口内）→ rows 非空，首列为 symbol。"""
        pd = pytest.importorskip("pandas")
        p, _ = self._make_provider(monkeypatch)
        df = pd.DataFrame(
            [
                {
                    "m_anntime": "20240115",
                    "m_timetag": "20231231",
                    "total_assets": 1e9,
                }
            ]
        )

        def fake_call(fn, policy, *a, **kw):
            if getattr(fn, "__name__", "") == "get_financial_data":
                return {"000001.SZ": {"Balance": df}}
            return None

        monkeypatch.setattr(p, "_call_with_policy", fake_call)
        payload = FetchPayload(
            table="c3_fundamental.balance",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 3, 31),
            extra={},
        )
        results = list(p.fetch_financial_statement(payload, SourcePolicy(), "Balance"))
        assert len(results) == 1
        assert len(results[0].rows) == 1
        assert results[0].rows[0][0] == "000001"  # _stock_to_symbol 去后缀

    # ---- 3. _fetch_shareholder（复杂度18）----

    def test_fetch_shareholder_empty(self, monkeypatch):
        """空数据 → FetchResult rows=[] 不崩溃，columns 含 symbol。"""
        p, _ = self._make_provider(monkeypatch)
        monkeypatch.setattr(p, "_call_with_policy", lambda fn, pol, *a, **kw: {})
        payload = FetchPayload(
            table="c3_fundamental.shareholder_count",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 3, 31),
            extra={},
        )
        results = list(p._fetch_shareholder(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].rows == []
        assert "symbol" in results[0].columns

    # ---- 4. _fetch_financial_by_table（复杂度18）----

    def test_fetch_financial_by_table_empty(self, monkeypatch):
        """空数据 → FetchResult rows=[] 不崩溃。"""
        p, _ = self._make_provider(monkeypatch)
        monkeypatch.setattr(p, "_call_with_policy", lambda fn, pol, *a, **kw: {})
        payload = FetchPayload(
            table="c3_fundamental.performance",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 3, 31),
            extra={},
        )
        results = list(p._fetch_financial_by_table(payload, SourcePolicy(), "Performance"))
        assert len(results) == 1
        assert results[0].rows == []

    # ---- 5. _fetch_futures_term_structure（复杂度16，含 #ARCH-FUTURES-OPTION-EXCHANGE-FILL）----

    def test_fetch_futures_term_structure_valid(self, monkeypatch):
        """有效期货K线 → rows 含 exchange 列（从合约代码后缀提取）。"""
        pd = pytest.importorskip("pandas")
        p, _ = self._make_provider(monkeypatch)
        idx = pd.DatetimeIndex(pd.date_range("2024-07-01", periods=3))
        mock_df = pd.DataFrame({"close": [4000.0, 4050.0, 4100.0]}, index=idx)

        def fake_call(fn, policy, *args, **kwargs):
            if getattr(fn, "__name__", "") == "get_market_data_ex":
                # args = ([], [stock_code], "1d", start_str, end_str)
                code = args[1][0]
                return {code: mock_df}
            return None  # download_history_data

        monkeypatch.setattr(p, "_call_with_policy", fake_call)
        payload = FetchPayload(
            table="c1_market.futures_term_structure",
            symbols=["IF2409.CFFEX", "IF2410.CFFEX"],
            start=datetime.date(2024, 7, 1),
            end=datetime.date(2024, 7, 3),
            extra={},
        )
        results = list(p._fetch_futures_term_structure(payload, SourcePolicy()))
        assert len(results) == 1
        assert "exchange" in results[0].columns
        assert len(results[0].rows) == 3
        ex_idx = results[0].columns.index("exchange")
        assert all(row[ex_idx] == "CFFEX" for row in results[0].rows)


# ============== #ARCH-DATA-015: baostock 黑名单治本（schema 对齐 + 登录泄漏修复） ==============


class _FakeBsResultSet:
    """模拟 baostock 查询结果集（error_code + next/get_row_data 迭代）。"""

    def __init__(self, rows):
        self.error_code = "0"
        self._rows = rows
        self._idx = -1

    def next(self):
        self._idx += 1
        return self._idx < len(self._rows)

    def get_row_data(self):
        return self._rows[self._idx]


class TestBaostockSchemaAlign:
    """baostock provider 产出列名必须与 CH 表 schema 对齐（08-10 表重建后旧列名零交集静默空写）。"""

    def _provider(self):
        from src.zephyr.data.implementations.baostock_provider import BaostockProvider

        return BaostockProvider()

    def test_bs_code_to_symbol(self):
        from src.zephyr.data.implementations.baostock_provider import _bs_code_to_symbol

        assert _bs_code_to_symbol("sh.600000") == "600000.SH"
        assert _bs_code_to_symbol("sz.000001") == "000001.SZ"
        assert _bs_code_to_symbol("") == ""

    def test_index_constituent_columns(self):
        p = self._provider()
        p.tls.bs = MagicMock()
        p.tls.bs.query_hs300_stocks = MagicMock(
            return_value=_FakeBsResultSet([["2026-08-01", "sh.600000", "浦发银行"]])
        )
        p.tls.logged_in = True
        payload = FetchPayload(
            table="c1_market.index_constituent",
            symbols=None,
            start=datetime.date(2026, 8, 1),
            end=datetime.date(2026, 8, 1),
            extra={"capability": "index_constituent"},
        )
        results = list(p._fetch_index_constituent(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].columns == ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]
        assert results[0].rows == [("2026-08-01", "000300.SH", "600000.SH", 0, "", "baostock")]

    def test_trade_calendar_columns(self):
        p = self._provider()
        p.tls.bs = MagicMock()
        p.tls.bs.query_trade_dates = MagicMock(
            return_value=_FakeBsResultSet(
                [
                    ["2026-08-13", "1"],
                    ["2026-08-14", "1"],
                    ["2026-08-15", "0"],
                ]
            )
        )
        p.tls.logged_in = True
        payload = FetchPayload(
            table="c1_market.trade_calendar",
            symbols=None,
            start=datetime.date(2026, 8, 13),
            end=datetime.date(2026, 8, 15),
            extra={"capability": "trade_calendar"},
        )
        results = list(p._fetch_trade_calendar(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].columns == ["exchange", "cal_date", "is_open", "pretrade_date"]
        rows = results[0].rows
        assert rows[0] == ("SSE", "2026-08-13", 1, "2026-08-13")  # 首个开市日 pretrade=自身
        assert rows[1] == ("SSE", "2026-08-14", 1, "2026-08-13")
        assert rows[2] == ("SSE", "2026-08-15", 0, "2026-08-14")  # 非开市日 pretrade=上一开市日

    def test_login_failure_closes_socket(self, monkeypatch):
        """登录失败（如 10001011 黑名单）必须调 logout 释放 socket（防 ResourceWarning 放大）。"""
        fake_bs = MagicMock()
        fake_bs.login.return_value = MagicMock(error_code="10001011", error_msg="黑名单用户")
        monkeypatch.setitem(sys.modules, "baostock", fake_bs)
        p = self._provider()
        with pytest.raises(RuntimeError, match="10001011"):
            p._ensure_login()
        fake_bs.logout.assert_called_once()


class TestBaostockKlineDailyFallback:
    """#196：kline_daily 主表降级源必须不复权（adjustflag=3，对齐 miniQMT 主口径）。

    P0 污染实证：adjustflag=2（前复权）写 c1_market.kline_daily——ReplacingMergeTree
    同键 (symbol, trade_date) 后写覆盖先写，同一行 raw/qfq 取决于源跑序，且 qfq 锚定
    抓取日历史价随分红漂移不可复现，除权日附近收益信号直接错误。
    """

    def _provider(self):
        p = BaostockProvider()
        p.tls.bs = MagicMock()
        p.tls.logged_in = True
        return p

    def test_fetch_kline_daily_uses_no_adjust(self):
        """写主表的降级 K 线请求必须 adjustflag=3（不复权）。"""
        p = self._provider()
        p.tls.bs.query_history_k_data_plus = MagicMock(
            return_value=_FakeBsResultSet(
                [["2026-08-01", "sh.600000", "10.0", "10.5", "9.9", "10.2", "1000", "10200.00"]]
            )
        )
        payload = FetchPayload(
            table="c1_market.kline_daily",
            symbols=["sh.600000"],
            start=datetime.date(2026, 8, 1),
            end=datetime.date(2026, 8, 1),
            extra={"capability": "kline_daily"},
        )
        results = list(p._fetch_kline_daily(payload, SourcePolicy()))
        assert len(results) == 1 and not results[0].error
        assert results[0].table == "c1_market.kline_daily"
        kwargs = p.tls.bs.query_history_k_data_plus.call_args.kwargs
        assert kwargs["adjustflag"] == "3"  # #196: 不复权，对齐 kline_daily 主口径

    def test_fetch_kline_daily_columns_align_schema_219(self):
        """#219：fallback 产出列名必须对齐 kline_daily schema，防写层交集过滤丢键列。

        修复前透传 baostock 原始列名 date/code——write_result 按表列交集过滤后
        仅剩 6 价格列，date/code 丢弃 → CH 键列落 DEFAULT 产 symbol=''/
        trade_date=1970-01-01 垃圾键行。本用例钉住：列名对齐 DDL 真源
        （schemas/categories/market_kline_daily.py INSERT_COLUMNS）、symbol 值
        转纯数字（对齐 miniqmt 主写口径）、不再产垃圾键。
        """
        from schemas.categories.market_kline_daily import INSERT_COLUMNS

        p = self._provider()
        p.tls.bs.query_history_k_data_plus = MagicMock(
            return_value=_FakeBsResultSet(
                [["2026-08-01", "sh.600000", "10.0", "10.5", "9.9", "10.2", "1000", "10200.00"]]
            )
        )
        payload = FetchPayload(
            table="c1_market.kline_daily",
            symbols=["sh.600000"],
            start=datetime.date(2026, 8, 1),
            end=datetime.date(2026, 8, 1),
            extra={"capability": "kline_daily"},
        )
        results = list(p._fetch_kline_daily(payload, SourcePolicy()))
        assert len(results) == 1 and not results[0].error
        cols = results[0].columns
        # 键列必须在（垃圾键根因=键列被交集过滤丢弃）；baostock 原始名不得透传
        assert "trade_date" in cols and "symbol" in cols
        assert "date" not in cols and "code" not in cols
        # 全部产出列 ⊆ schema INSERT_COLUMNS（DDL 真源），写层交集过滤零丢弃
        schema_cols = {c.strip() for c in INSERT_COLUMNS.strip("()").split(",")}
        assert set(cols) <= schema_cols
        # 行值：symbol 转纯数字 600000（sh.600000 去小写前缀），不再产垃圾键
        row = results[0].rows[0]
        assert row[cols.index("trade_date")] == "2026-08-01"
        assert row[cols.index("symbol")] == "600000"
        assert row[cols.index("symbol")] != ""
        assert row[cols.index("trade_date")] != "1970-01-01"
        assert row[cols.index("data_source")] == "Baostock"


class TestBaostockDelistedKline:
    """JOB-084：退市股历史 K 线回填（universe 解析/行映射/覆盖跳过/不复权口径）。"""

    def _provider(self):
        from src.zephyr.data.implementations.baostock_provider import BaostockProvider

        p = BaostockProvider()
        p.tls.bs = MagicMock()
        p.tls.logged_in = True
        return p

    _POLICY = staticmethod(lambda: MagicMock(rpm=0, max_retries=0, retry_on=[], initial_wait_sec=0, backoff="fixed"))

    def _wire(self, p, monkeypatch, universe_rows, kline_rows, span_tsv=""):
        p.tls.bs.query_stock_basic = MagicMock(return_value=_FakeBsResultSet(universe_rows))
        p.tls.bs.query_history_k_data_plus = MagicMock(return_value=_FakeBsResultSet(kline_rows))
        import zephyr.data.ch_reader as provider_ch_reader

        monkeypatch.setattr(provider_ch_reader, "query", lambda sql, timeout=0: span_tsv)
        return p

    _UNIVERSE = [
        ["sz.000005", "ST星源(退)", "1990-12-10", "2024-04-26", "1", "0"],  # 保留
        ["sh.600000", "浦发银行", "1999-11-10", "", "1", "1"],  # 在市→剔
        ["sh.900901", "B股退", "1992-01-01", "2020-01-01", "1", "0"],  # B股前缀→剔
        ["sh.000001", "上证指数", "", "", "2", "1"],  # 指数→剔
        ["sz.150001", "基金退", "2010-01-01", "2020-01-01", "5", "0"],  # 基金→剔
    ]

    _KLINE = [
        ["2024-04-25", "sz.000005", "0.85", "0.87", "0.83", "0.85", "0.84", "1000", "850.00", "0.5", "1.1905"],
        # 退市末日：volume/amount/turn/pctChg 空（实证形态）→ 0 兜底；preclose 0.85
        ["2024-04-26", "sz.000005", "0.83", "0.83", "0.83", "0.83", "0.85", "", "", "", ""],
        ["2024-04-23", "sz.000005", "", "", "", "", "", "100", "80", "", "0"],  # close 空→丢行
    ]

    def test_universe_filter(self):
        p = self._provider()
        p.tls.bs.query_stock_basic = MagicMock(return_value=_FakeBsResultSet(self._UNIVERSE))
        out = p._fetch_delisted_universe(p.tls.bs, self._POLICY())
        assert out == [("sz.000005", "000005", "1990-12-10", "2024-04-26")]

    def test_row_mapper(self):
        rows = BaostockProvider._map_delisted_kline_rows(self._KLINE, "000005")
        assert len(rows) == 2  # close 空行被丢
        r1, r2 = rows
        assert r1[0] == "2024-04-25" and r1[1] == "000005"
        assert r1[5] == 0.85 and r1[6] == 1000 and r1[7] == 850.00
        assert r1[8] == round((0.87 - 0.83) / 0.84 * 100, 4)  # amplitude
        assert r1[9] == 1.1905 and r1[10] == 0.01 and r1[11] == 0.5  # pct/change/turn
        assert r1[12] == 1 and r1[13] == "A_share" and r1[14] == "Baostock" and r1[15] == 1
        # 末日空值兜底 + change 由 preclose 计算
        assert r2[6] == 0 and r2[7] == 0.0 and r2[9] == 0.0 and r2[11] == 0.0
        assert r2[10] == -0.02 and r2[8] == 0.0

    def test_fetch_full_flow_and_adjustflag(self, monkeypatch):
        p = self._wire(self._provider(), monkeypatch, self._UNIVERSE, self._KLINE)
        payload = FetchPayload(
            table="", symbols=None, start=None, end=None, extra={"capability": "kline_daily_delisted"}
        )
        results = list(p._fetch_kline_daily_delisted(payload, self._POLICY()))
        assert len(results) == 1 and not results[0].error
        assert len(results[0].rows) == 2
        assert results[0].last_key == "2024-04-26"
        # 不复权口径（对齐 kline_daily 主口径 miniQMT 不复权）
        kwargs = p.tls.bs.query_history_k_data_plus.call_args.kwargs
        assert kwargs["adjustflag"] == "3"
        assert kwargs["start_date"] == "1990-12-10" and kwargs["end_date"] == "2024-04-26"

    def test_span_covered_skips_fetch(self, monkeypatch):
        # 已覆盖 [ipo+10d, out-10d] → 跳过不抓（月度幂等刷新只抓新退市股）
        p = self._wire(
            self._provider(), monkeypatch, self._UNIVERSE, self._KLINE, span_tsv="000005\t1990-12-15\t2024-04-20"
        )
        payload = FetchPayload(
            table="", symbols=None, start=None, end=None, extra={"capability": "kline_daily_delisted"}
        )
        results = list(p._fetch_kline_daily_delisted(payload, self._POLICY()))
        assert results == []
        p.tls.bs.query_history_k_data_plus.assert_not_called()

    def test_span_partial_coverage_still_fetches(self, monkeypatch):
        # 仅有 2020 后段（min 2020-01-02 > ipo+10d）→ 历史有洞，必须抓
        p = self._wire(
            self._provider(), monkeypatch, self._UNIVERSE, self._KLINE, span_tsv="000005\t2020-01-02\t2024-04-26"
        )
        payload = FetchPayload(
            table="", symbols=None, start=None, end=None, extra={"capability": "kline_daily_delisted"}
        )
        results = list(p._fetch_kline_daily_delisted(payload, self._POLICY()))
        assert len(results) == 1 and len(results[0].rows) == 2

    def test_universe_empty_yields_error(self, monkeypatch):
        p = self._wire(self._provider(), monkeypatch, [], [])
        payload = FetchPayload(
            table="", symbols=None, start=None, end=None, extra={"capability": "kline_daily_delisted"}
        )
        results = list(p._fetch_kline_daily_delisted(payload, self._POLICY()))
        assert len(results) == 1 and results[0].error and "universe" in results[0].error


class TestAKShareData015Capabilities:
    """akshare 新增 trade_calendar / index_constituent 能力（死 fallback 补全）。"""

    def test_capabilities_registered(self):
        from src.zephyr.data.implementations.akshare_provider import _AKSHARE_CAPABILITIES

        assert "trade_calendar" in _AKSHARE_CAPABILITIES
        assert "index_constituent" in _AKSHARE_CAPABILITIES

    def test_cn_code_to_symbol(self):
        from src.zephyr.data.implementations.akshare_provider import _cn_code_to_symbol

        assert _cn_code_to_symbol("600000") == "600000.SH"
        assert _cn_code_to_symbol("000001") == "000001.SZ"
        assert _cn_code_to_symbol("300750") == "300750.SZ"
        assert _cn_code_to_symbol("430047") == "430047.BJ"

    def test_trade_calendar_fetch(self, monkeypatch):
        import pandas as pd

        fake_ak = MagicMock()
        fake_ak.tool_trade_date_hist_sina = MagicMock(
            return_value=pd.DataFrame(
                {
                    "trade_date": [datetime.date(2026, 8, 13), datetime.date(2026, 8, 14)],
                }
            )
        )
        monkeypatch.setitem(sys.modules, "akshare", fake_ak)
        p = AkshareIngestProvider()
        payload = FetchPayload(
            table="c1_market.trade_calendar",
            symbols=None,
            start=datetime.date(2026, 8, 13),
            end=datetime.date(2026, 8, 14),
            extra={"capability": "trade_calendar"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is None
        assert len(results[0].rows) == 2


# ============== MiniQMT 批量抓取健壮性（单票跳过/断连重连/失败率阈值）==============


class TestMiniQMTBatchRobustness:
    """miniQMT fetch_kline 批量抓取健壮性（4 项修复的 provider 侧）。

    纯合成数据：monkeypatch xtquant 模块 + provider._call_with_policy，
    不依赖真实 QMT。
    """

    def _wire(self, monkeypatch, call_behaviors):
        """构造 provider + xtquant mock。

        call_behaviors: dict[stock_code, "ok"|Exception 实例]，
        _call_with_policy 按 fn 名+stock_code 派发。
        """
        mock_xtquant = MagicMock()
        mock_xtdata = mock_xtquant.xtdata
        for fn_name in ("download_history_data", "get_market_data_ex", "get_stock_list_in_sector"):
            getattr(mock_xtdata, fn_name).__name__ = fn_name
        monkeypatch.setitem(sys.modules, "xtquant", mock_xtquant)
        monkeypatch.setitem(sys.modules, "xtquant.xtdata", mock_xtdata)

        import pandas as pd

        p = MiniQmtIngestProvider()
        p._connected = True

        def fake_call(fn, policy, *a, **kw):
            fn_name = getattr(fn, "__name__", "")
            if fn_name == "get_stock_list_in_sector":
                return list(call_behaviors.keys())
            stock_code = a[0] if fn_name == "download_history_data" else a[1][0]
            behavior = call_behaviors[stock_code]
            if isinstance(behavior, Exception):
                raise behavior
            if fn_name == "download_history_data":
                return None
            # get_market_data_ex 返回单条日线
            df = pd.DataFrame(
                {"open": [1.0], "high": [1.1], "low": [0.9], "close": [1.05], "volume": [100], "amount": [105.0]},
                index=[20260818],
            )
            return {stock_code: df}

        monkeypatch.setattr(p, "_call_with_policy", fake_call)
        return p

    def _payload(self, symbols):
        return FetchPayload(
            table="c1_market.kline_daily",
            symbols=symbols,
            start=datetime.date(2026, 8, 18),
            end=datetime.date(2026, 8, 18),
            extra={},
        )

    def test_single_stock_failure_skipped_batch_success(self, monkeypatch):
        """a) 单票异常被跳过且任务成功：1/4 失败（25%>5% 会失败，改用 20 只 1 只失败=5%）。"""
        # 20 只标的 1 只失败 → 失败率 5%，不超阈值（严格大于才失败）→ 任务成功
        symbols = [f"{i:06d}.SZ" for i in range(1, 21)]
        behaviors = dict.fromkeys(symbols, "ok")
        behaviors["000007.SZ"] = ValueError("数据缺失")
        p = self._wire(monkeypatch, behaviors)
        results = list(p.fetch_kline(self._payload(symbols), SourcePolicy(), "1d"))
        errors = [r for r in results if r.error]
        oks = [r for r in results if not r.error]
        assert errors == [], f"不应有 error 结果: {[r.error for r in errors]}"
        assert len(oks) == 19, "19 只成功标的各 yield 一批"
        # 成功的每批有 1 行数据
        assert all(len(r.rows) == 1 for r in oks)

    def test_fail_rate_over_threshold_yields_error(self, monkeypatch):
        """b) 失败率超阈值任务失败：10 只标的 2 只失败=20%>5% → 尾部 yield error。"""
        symbols = [f"{i:06d}.SZ" for i in range(1, 11)]
        behaviors = dict.fromkeys(symbols, "ok")
        behaviors["000001.SZ"] = ValueError("停牌")
        behaviors["000002.SZ"] = RuntimeError("数据异常")
        p = self._wire(monkeypatch, behaviors)
        results = list(p.fetch_kline(self._payload(symbols), SourcePolicy(), "1d"))
        errors = [r for r in results if r.error]
        oks = [r for r in results if not r.error]
        assert len(oks) == 8, "8 只成功标的正常 yield"
        assert len(errors) == 1, "收尾恰好 yield 一个 error"
        assert "失败率" in errors[0].error and "20.0%" in errors[0].error

    def test_connection_error_marks_disconnected_and_aborts(self, monkeypatch):
        """c) 断连异常置 _connected=False 并中止本批（后续标的不再尝试）。"""
        symbols = [f"{i:06d}.SZ" for i in range(1, 6)]
        behaviors = dict.fromkeys(symbols, "ok")
        behaviors["000003.SZ"] = ConnectionResetError(10054, "远程主机强迫关闭了一个现有的连接")
        p = self._wire(monkeypatch, behaviors)
        assert p._connected is True
        results = list(p.fetch_kline(self._payload(symbols), SourcePolicy(), "1d"))
        assert p._connected is False, "断连必须置 _connected=False 触发 scheduler 自动重连"
        errors = [r for r in results if r.error]
        oks = [r for r in results if not r.error]
        assert len(oks) == 2, "断连前 2 只成功标的正常 yield"
        assert len(errors) == 1, "断连立即 yield error 中止"
        assert "连接断开" in errors[0].error or "QMT" in errors[0].error

    def test_is_connection_error_detection(self):
        """连接类异常判定辅助函数。"""
        from src.zephyr.data.implementations.miniqmt_provider import _is_connection_error

        class XtNetError(Exception):
            isNetError = True

        assert _is_connection_error(XtNetError("qmt disconnected"))
        assert _is_connection_error(ConnectionResetError(10054, "reset"))
        assert _is_connection_error(OSError("socket error"))
        assert _is_connection_error(Exception("WinError 10054"))
        assert not _is_connection_error(ValueError("数据缺失"))
        assert not _is_connection_error(KeyError("no data"))


class TestAKShareData015CapabilitiesContinued:
    """TestAKShareData015Capabilities 剩余用例（trade_calendar 收尾 + index_constituent）。"""

    def test_trade_calendar_columns_rows(self, monkeypatch):
        import pandas as pd

        fake_ak = MagicMock()
        fake_ak.tool_trade_date_hist_sina = MagicMock(
            return_value=pd.DataFrame(
                {
                    "trade_date": [datetime.date(2026, 8, 13), datetime.date(2026, 8, 14)],
                }
            )
        )
        monkeypatch.setitem(sys.modules, "akshare", fake_ak)
        p = AkshareIngestProvider()
        payload = FetchPayload(
            table="c1_market.trade_calendar",
            symbols=None,
            start=datetime.date(2026, 8, 13),
            end=datetime.date(2026, 8, 14),
            extra={"capability": "trade_calendar"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error is None
        assert results[0].columns == ["exchange", "cal_date", "is_open", "pretrade_date"]
        assert results[0].rows == [
            ("SSE", datetime.date(2026, 8, 13), 1, datetime.date(2026, 8, 13)),
            ("SSE", datetime.date(2026, 8, 14), 1, datetime.date(2026, 8, 13)),
        ]

    def test_index_constituent_fetch(self, monkeypatch):
        import pandas as pd

        fake_ak = MagicMock()
        fake_ak.index_stock_cons_csindex = MagicMock(
            return_value=pd.DataFrame(
                {
                    "成分券代码": ["600000", "000001"],
                }
            )
        )
        monkeypatch.setitem(sys.modules, "akshare", fake_ak)
        p = AkshareIngestProvider()
        payload = FetchPayload(
            table="c1_market.index_constituent",
            symbols=None,
            start=datetime.date(2026, 8, 14),
            end=datetime.date(2026, 8, 14),
            extra={"capability": "index_constituent"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        # JOB-077（DS-084，2026-08-15）：扩展为四指数（300/500/1000/中证全指），
        # 每指数一批；权重经 index_stock_cons_weight_csindex（mock 无该接口→MagicMock
        # len=0→weight 降级 0）；data_source 细化为 akshare_csindex
        assert len(results) == 4
        assert results[0].error is None
        assert results[0].columns == ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]
        assert results[0].rows == [
            ("2026-08-14", "000300.SH", "600000.SH", 0, "", "akshare_csindex"),
            ("2026-08-14", "000300.SH", "000001.SZ", 0, "", "akshare_csindex"),
        ]
        # 四指数代码顺序固定
        assert [r.rows[0][1] for r in results] == [
            "000300.SH",
            "000905.SH",
            "000852.SH",
            "000985.SH",
        ]


# ============== TushareProvider ST 名称变更回填（JOB-083，DS-085 历史段）==============


class TestTushareStNamechange:
    """ST 历史状态名称变更推导回填：区间推导 + 变化日快照合成 + 接缝路由。"""

    def test_st_type_of(self):
        f = TushareProvider._st_type_of
        assert f("ST海虹") == "ST"
        assert f("*ST中天") == "*ST"
        assert f("S*ST光明") == "*ST"
        assert f("SST前锋") == "ST"
        assert f("浦发银行") is None
        assert f("退市苏吴") is None
        assert f("") is None

    def test_ts_code_to_a_share6(self):
        f = TushareProvider._ts_code_to_a_share6
        assert f("600000.SH") == "600000"
        assert f("000001.SZ") == "000001"
        assert f("300750.SZ") == "300750"
        assert f("688001.SH") == "688001"  # 科创板有 ST 实例（JOB-077 实盘快照实证 13 只）
        assert f("830799.BJ") == "830799"
        assert f("00700.HK") is None  # 港股后缀排除
        assert f("ABCDEF") is None  # 无后缀排除
        assert f("139001.SZ") is None  # 非 A 股板块前缀排除

    def test_parse_yyyymmdd(self):
        f = TushareProvider._parse_yyyymmdd
        assert f("19980615") == datetime.date(1998, 6, 15)
        assert f("2020-01-02") == datetime.date(2020, 1, 2)
        assert f("") is None and f(None) is None and f("nan") is None
        assert f("20201340") is None  # 非法月日（8 位数字）→ None 不崩溃

    def test_derive_st_intervals(self):
        df = pd.DataFrame(
            {
                "ts_code": ["600000.SH", "000503.SZ", "688001.SH", "300750.SZ", "600001.SH"],
                "name": ["浦发银行", "ST海虹", "ST科创", "*ST宁德", "SST坏日期"],
                "start_date": ["20100101", "19980615", "20210101", "20200101", "baddate"],
                "end_date": [None, "20000320", None, "20201231", None],
            }
        )
        intervals = TushareProvider()._derive_st_intervals(df)
        # 600000 非 ST 剔除；600001 起始日不可解析剔除；688001 科创板保留
        assert intervals == [
            ("000503", "ST海虹", "ST", datetime.date(1998, 6, 15), datetime.date(2000, 3, 20)),
            ("688001", "ST科创", "ST", datetime.date(2021, 1, 1), None),
            ("300750", "*ST宁德", "*ST", datetime.date(2020, 1, 1), datetime.date(2020, 12, 31)),
        ]

    def test_synthesize_change_day_snapshots(self):
        days = [
            datetime.date(2020, 1, 2),
            datetime.date(2020, 1, 3),
            datetime.date(2020, 1, 6),
            datetime.date(2020, 1, 7),
        ]
        intervals = [
            ("600001", "ST甲", "ST", datetime.date(2020, 1, 2), datetime.date(2020, 1, 6)),
            # 01-04 为周六 → 顺延 01-06（一）生效；end None=持续
            ("600002", "*ST乙", "*ST", datetime.date(2020, 1, 4), None),
        ]
        rows = TushareProvider()._synthesize_st_snapshots(intervals, days)
        by_date: dict[str, dict] = {}
        for td, sym, name, st_type, src in rows:
            by_date.setdefault(td, {})[sym] = (name, st_type, src)
        # 01-03 集合无变化不产出；01-06 乙戴帽；01-07 甲摘帽（01-06 为最后 ST 日）
        assert set(by_date.keys()) == {"2020-01-02", "2020-01-06", "2020-01-07"}
        assert set(by_date["2020-01-02"]) == {"600001"}
        assert set(by_date["2020-01-06"]) == {"600001", "600002"}
        assert set(by_date["2020-01-07"]) == {"600002"}
        assert by_date["2020-01-02"]["600001"] == ("ST甲", "ST", "tushare_namechange_derived")

    def _wired_provider(self, monkeypatch, namechange_df, ch_fake):
        p = TushareProvider()
        p._connected = True
        pro = MagicMock()
        pro.namechange = MagicMock(return_value=namechange_df)
        pro.namechange.__name__ = "namechange"
        p._pro = pro
        import zephyr.data.ch_reader as provider_ch_reader

        monkeypatch.setattr(provider_ch_reader, "query", ch_fake)
        return p

    def test_fetch_route_and_seam(self, monkeypatch):
        df = pd.DataFrame(
            {
                "ts_code": ["000503.SZ"],
                "name": ["ST海虹"],
                "start_date": ["20200102"],
                "end_date": ["20200110"],
                "ann_date": ["20191231"],
                "change_reason": ["ST"],
            }
        )

        def fake_query(sql, timeout=0):
            if "min(trade_date)" in sql:
                return "2020-01-20"  # 实盘快照接缝日 → 回填窗口 [01-01, 01-19]
            if "DISTINCT trade_date" in sql:
                return "\n".join(f"2020-01-{d:02d}" for d in (2, 3, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17))
            return ""

        p = self._wired_provider(monkeypatch, df, fake_query)
        payload = FetchPayload(
            table="",
            symbols=None,
            start=datetime.date(2020, 1, 1),
            end=None,
            extra={"capability": "st_namechange_backfill"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1 and not results[0].error
        # 区间 [01-02, 01-10]：01-02 生效产出快照；01-10(五) 最后 ST 日，
        # 01-13(一) 集合变空 → 全空快照不产出（文档化限制）
        assert results[0].rows == [("2020-01-02", "000503", "ST海虹", "ST", "tushare_namechange_derived")]
        assert results[0].last_key == "2020-01-02"

    def test_seam_missing_yields_error_not_crash(self, monkeypatch):
        p = self._wired_provider(monkeypatch, pd.DataFrame(), lambda sql, timeout=0: "")
        payload = FetchPayload(
            table="",
            symbols=None,
            start=None,
            end=None,
            extra={"capability": "st_namechange_backfill"},
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].error and "接缝" in results[0].error

    def test_namechange_paged_concat_dedup(self, monkeypatch):
        # 无参调用被 tushare 截断至 10000 行（2026-08-16 实证）——逐年分页合并去重
        def nc(start_date=None, end_date=None, **kw):
            year = int(str(start_date)[:4])
            if year in (2020, 2021):  # 跨年页重复行 → 必须去重
                return pd.DataFrame(
                    {
                        "ts_code": ["000503.SZ"],
                        "name": ["ST海虹"],
                        "start_date": ["20200102"],
                        "end_date": [None],
                    }
                )
            return pd.DataFrame()

        p = TushareProvider()
        p._connected = True
        pro = MagicMock()
        pro.namechange = MagicMock(side_effect=nc)
        pro.namechange.__name__ = "namechange"
        p._pro = pro
        df = p._fetch_namechange_paged(
            MagicMock(rpm=0, max_retries=0, retry_on=[], initial_wait_sec=0, backoff="fixed"),
            from_year=2020,
        )
        assert len(df) == 1
        assert df.iloc[0]["name"] == "ST海虹"


# ============== MiniQmt 期权 IV 曲面 CH 降级（QMT 期权历史K线失效治本） ==============


class TestMiniQmtOptionIvChFallback:
    """QMT 模拟账户期权历史K线不可用时，从 CH option_kline 降级取收盘价。"""

    @staticmethod
    def _detail_stub():
        return {
            "Underlying": "510050.SH",
            "ExercisePrice": 2.85,
            "EndDelivDate": "20260923",
            "OptType": 1,
            "ExchangeID": "SHO",
        }

    def test_load_option_close_from_ch_parses_tsv(self, monkeypatch):
        from src.zephyr.data.implementations import miniqmt_provider as mq

        p = MiniQmtIngestProvider()
        tsv = "2026-08-17\t0.1500\takshare_sina\n2026-08-18\t0.1439\takshare_sina"
        monkeypatch.setattr(mq.ch_reader, "query", lambda sql: tsv)
        df, src = p._load_option_close_from_ch("10010971.SHO", "20260814", "20260819")
        assert src == "akshare_sina"
        assert list(df.index) == ["20260817", "20260818"]
        assert df.loc["20260818", "close"] == pytest.approx(0.1439)

    def test_load_option_close_from_ch_empty(self, monkeypatch):
        from src.zephyr.data.implementations import miniqmt_provider as mq

        p = MiniQmtIngestProvider()
        monkeypatch.setattr(mq.ch_reader, "query", lambda sql: "")
        df, src = p._load_option_close_from_ch("10010971.SHO", "20260814", "20260819")
        assert df is None and src == ""

    def test_load_option_close_from_ch_query_error(self, monkeypatch):
        from src.zephyr.data.implementations import miniqmt_provider as mq

        p = MiniQmtIngestProvider()

        def _raise(sql):
            raise RuntimeError("ch down")

        monkeypatch.setattr(mq.ch_reader, "query", _raise)
        df, src = p._load_option_close_from_ch("10010971.SHO", "20260814", "20260819")
        assert df is None and src == ""

    def test_compute_iv_falls_back_to_ch(self, monkeypatch):
        p = MiniQmtIngestProvider()
        monkeypatch.setattr(p, "_get_option_detail_safe", lambda *a, **k: self._detail_stub())
        monkeypatch.setattr(p, "_download_option_price_df", lambda *a, **k: None)
        opt_df = pd.DataFrame({"close": [0.25]}, index=pd.Index(["20260817"], dtype=object))
        monkeypatch.setattr(p, "_load_option_close_from_ch", lambda *a, **k: (opt_df, "akshare_sina"))
        ul_df = pd.DataFrame({"close": [3.05]}, index=pd.Index(["20260817"], dtype=object))
        monkeypatch.setattr(p, "_download_underlying_price_df", lambda *a, **k: ul_df)

        rows = p._compute_iv_for_option("10010971.SHO", "20260814", "20260819", SourcePolicy())
        assert len(rows) == 1
        assert rows[0][0] == "2026-08-17"
        assert rows[0][6] is not None and rows[0][6] > 0  # IV 反解成功
        assert rows[0][-1] == "akshare_sina"  # 数据血缘标记为实际来源

    def test_compute_iv_qmt_path_keeps_miniqmt_source(self, monkeypatch):
        p = MiniQmtIngestProvider()
        monkeypatch.setattr(p, "_get_option_detail_safe", lambda *a, **k: self._detail_stub())
        opt_df = pd.DataFrame({"close": [0.25]}, index=pd.Index(["20260817"], dtype=object))
        monkeypatch.setattr(p, "_download_option_price_df", lambda *a, **k: opt_df)
        ul_df = pd.DataFrame({"close": [3.05]}, index=pd.Index(["20260817"], dtype=object))
        monkeypatch.setattr(p, "_download_underlying_price_df", lambda *a, **k: ul_df)

        def _no_ch(*a, **k):
            raise AssertionError("QMT 有数据时不应触发 CH 降级")

        monkeypatch.setattr(p, "_load_option_close_from_ch", _no_ch)
        rows = p._compute_iv_for_option("10010971.SHO", "20260814", "20260819", SourcePolicy())
        assert len(rows) == 1
        assert rows[0][-1] == "miniqmt"

    def test_compute_iv_empty_when_both_sources_empty(self, monkeypatch):
        p = MiniQmtIngestProvider()
        monkeypatch.setattr(p, "_get_option_detail_safe", lambda *a, **k: self._detail_stub())
        monkeypatch.setattr(p, "_download_option_price_df", lambda *a, **k: None)
        monkeypatch.setattr(p, "_load_option_close_from_ch", lambda *a, **k: (None, ""))
        rows = p._compute_iv_for_option("10010971.SHO", "20260814", "20260819", SourcePolicy())
        assert rows == []


class TestAKShareKlineFuturesScope:
    """tracker #246 治本：akshare _fetch_kline_futures 收口股指期货 IF/IC/IM/IH + 白名单护栏。

    原实现无视 payload.symbols，拉 futures_display_main_sina 全品种宇宙（82 个含商品期货）；
    治本后 symbols 空时默认新浪主力连续 IF0/IC0/IM0/IH0（#ARCH-146 口径），
    显式 symbols 经 ^(IF|IC|IM|IH)\\d+$ 白名单过滤。
    """

    @staticmethod
    def _kline_df() -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "日期": "2026-08-20",
                    "开盘价": 4000.0,
                    "最高价": 4010.0,
                    "最低价": 3990.0,
                    "收盘价": 4005.0,
                    "成交量": 12345,
                    "持仓量": 67890,
                }
            ]
        )

    @staticmethod
    def _mock_ak(monkeypatch, kline_df) -> MagicMock:
        mock_ak = MagicMock()
        mock_ak.futures_main_sina.__name__ = "futures_main_sina"
        mock_ak.futures_main_sina.return_value = kline_df
        mock_ak.futures_display_main_sina.__name__ = "futures_display_main_sina"
        monkeypatch.setitem(sys.modules, "akshare", mock_ak)
        return mock_ak

    def test_default_symbols_index_futures_only(self, monkeypatch):
        """symbols 空 → 仅采 IF0/IC0/IM0/IH0，不再调 futures_display_main_sina 全品种宇宙。"""
        mock_ak = self._mock_ak(monkeypatch, self._kline_df())
        p = AkshareIngestProvider()
        payload = FetchPayload(
            table="c1_market.kline_futures",
            symbols=None,
            start=datetime.date(2026, 8, 1),
            end=datetime.date(2026, 8, 21),
            extra={"capability": "kline_futures"},
        )
        results = list(p._fetch_kline_futures(payload, SourcePolicy()))
        called = [c.kwargs["symbol"] for c in mock_ak.futures_main_sina.call_args_list]
        assert called == ["IF0", "IC0", "IM0", "IH0"]
        mock_ak.futures_display_main_sina.assert_not_called()
        rows = [r for res in results for r in res.rows]
        assert len(rows) == 4
        for row in rows:
            assert row[10] == "1d"  # period
            assert row[11] == "cffex"  # exchange
            assert row[12] == "akshare"  # data_source

    def test_whitelist_drops_stock_and_commodity(self, monkeypatch):
        """显式 symbols 混入个股/商品期货 → 白名单剔除，仅采 IF0。"""
        mock_ak = self._mock_ak(monkeypatch, self._kline_df())
        p = AkshareIngestProvider()
        payload = FetchPayload(
            table="c1_market.kline_futures",
            symbols=["IF0", "000001.SZ", "000001", "RB0", "I2407"],
            start=datetime.date(2026, 8, 1),
            end=datetime.date(2026, 8, 21),
            extra={"capability": "kline_futures"},
        )
        results = list(p._fetch_kline_futures(payload, SourcePolicy()))
        called = [c.kwargs["symbol"] for c in mock_ak.futures_main_sina.call_args_list]
        assert called == ["IF0"]
        rows = [r for res in results for r in res.rows]
        assert len(rows) == 1
        assert rows[0][2] == "IF0"

    def test_all_illegal_symbols_yields_error(self, monkeypatch):
        """symbols 全部不合法 → 空结果 + error 留痕，不触网。"""
        mock_ak = self._mock_ak(monkeypatch, self._kline_df())
        p = AkshareIngestProvider()
        payload = FetchPayload(
            table="c1_market.kline_futures",
            symbols=["000001.SZ", "600000.SH"],
            start=datetime.date(2026, 8, 1),
            end=datetime.date(2026, 8, 21),
            extra={"capability": "kline_futures"},
        )
        results = list(p._fetch_kline_futures(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].rows == []
        assert results[0].error is not None
        mock_ak.futures_main_sina.assert_not_called()

