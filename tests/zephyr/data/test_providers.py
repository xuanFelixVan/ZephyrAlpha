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
