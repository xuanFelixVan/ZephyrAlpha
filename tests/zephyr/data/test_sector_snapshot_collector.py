# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""sector_snapshot_collector 单元测试。"""
from __future__ import annotations

from datetime import datetime

import pytest

from zephyr.data.sector_snapshot_collector import (
    _to_decimal,
    _to_uint,
    classify_market_type,
    parse_snapshot,
)

# ---------- _to_decimal ----------

class TestToDecimal:
    def test_normal_float(self):
        assert _to_decimal("3.14") == 3.14

    def test_normal_int(self):
        assert _to_decimal(42) == 42.0

    def test_none(self):
        assert _to_decimal(None) == 0.0

    def test_empty_string(self):
        assert _to_decimal("") == 0.0

    def test_string_none(self):
        assert _to_decimal("None") == 0.0

    def test_invalid(self):
        assert _to_decimal("abc") == 0.0

    def test_custom_default(self):
        assert _to_decimal(None, default=-1.0) == -1.0

    def test_negative(self):
        assert _to_decimal("-5.5") == -5.5


# ---------- _to_uint ----------

class TestToUint:
    def test_normal_int(self):
        assert _to_uint(100) == 100

    def test_float_string(self):
        assert _to_uint("99.9") == 99

    def test_none(self):
        assert _to_uint(None) == 0

    def test_empty(self):
        assert _to_uint("") == 0

    def test_negative_returns_default(self):
        assert _to_uint(-5) == 0

    def test_negative_float_returns_default(self):
        assert _to_uint("-3.2") == 0

    def test_invalid(self):
        assert _to_uint("abc") == 0

    def test_custom_default(self):
        assert _to_uint(None, default=99) == 99


# ---------- classify_market_type ----------

class TestClassifyMarketType:
    def test_mkt_index_880001(self):
        assert classify_market_type("880001.SH") == "mkt_index"

    def test_mkt_index_880009(self):
        assert classify_market_type("880009.SH") == "mkt_index"

    def test_sector_880101(self):
        assert classify_market_type("880101.SH") == "sector"

    def test_sector_880999(self):
        assert classify_market_type("880999.SH") == "sector"

    def test_sz_suffix(self):
        assert classify_market_type("880001.SZ") == "mkt_index"


# ---------- parse_snapshot ----------

class TestParseSnapshot:
    def _make_snap(self, **overrides):
        snap = {
            "ErrorId": "0",
            "Time": "2026-07-22 10:30:00",
            "Now": "3500.5",
            "Open": "3490.0",
            "Max": "3510.0",
            "Min": "3485.0",
            "LastClose": "3488.0",
            "Before5MinNow": "3495.0",
            "Average": "3498.0",
            "Volume": "0",
            "NowVol": "100",
            "Amount": "1234567.89",
            "UpHome": "200",
            "DownHome": "150",
            "Inside": "80",
            "Outside": "120",
            "Zangsu": "0.5",
        }
        snap.update(overrides)
        return snap

    def test_valid_snapshot(self):
        snap = self._make_snap()
        now = datetime(2026, 7, 22, 10, 30, 0)
        row = parse_snapshot(snap, "880101.SH", "sector", "tqcenter_push", now_bj=now)
        assert row is not None
        assert row[0] == now.date()          # trade_date
        assert row[1] == datetime(2026, 7, 22, 10, 30, 0)  # timestamp from Time
        assert row[2] == "880101.SH"         # sector_code
        assert row[3] == "sector"            # market_type
        assert row[4] == 3500.5             # now_price
        assert row[5] == 3490.0             # open_price
        assert row[6] == 3510.0             # max_price
        assert row[7] == 3485.0             # min_price
        assert row[8] == 3488.0             # last_close
        assert row[9] == 3495.0             # before_5min_now
        assert row[10] == 3498.0            # average_price
        assert row[11] == 0                 # volume (板块恒为0)
        assert row[12] == 100               # now_vol
        assert row[13] == 1234567.89        # amount
        assert row[14] == 200               # up_home
        assert row[15] == 150               # down_home
        assert row[16] == 80                # inside
        assert row[17] == 120               # outside
        assert row[18] == 0.5               # zangsu
        assert row[19] == "tqcenter_push"   # data_source
        # fetched_at is dynamic, just check it's a datetime
        assert isinstance(row[20], datetime)

    def test_error_id_not_zero(self):
        snap = self._make_snap(ErrorId="1")
        row = parse_snapshot(snap, "880001.SH", "mkt_index", "tqcenter_push")
        assert row is None

    def test_empty_snapshot(self):
        row = parse_snapshot({}, "880001.SH", "mkt_index", "tqcenter_push")
        assert row is None

    def test_none_snapshot(self):
        row = parse_snapshot(None, "880001.SH", "mkt_index", "tqcenter_push")
        assert row is None

    def test_missing_time_falls_back_to_now(self):
        snap = self._make_snap()
        snap.pop("Time")
        now = datetime(2026, 7, 22, 14, 0, 0)
        row = parse_snapshot(snap, "880101.SH", "sector", "tqcenter_snapshot", now_bj=now)
        assert row is not None
        assert row[1] == now  # timestamp falls back to now_bj

    def test_invalid_time_falls_back_to_now(self):
        snap = self._make_snap(Time="invalid")
        now = datetime(2026, 7, 22, 14, 0, 0)
        row = parse_snapshot(snap, "880101.SH", "sector", "tqcenter_snapshot", now_bj=now)
        assert row is not None
        assert row[1] == now  # timestamp falls back to now_bj

    def test_none_values_use_defaults(self):
        snap = self._make_snap(
            Now=None, Open="", Max="None", Volume=None, UpHome=""
        )
        now = datetime(2026, 7, 22, 10, 30, 0)
        row = parse_snapshot(snap, "880101.SH", "sector", "tqcenter_push", now_bj=now)
        assert row is not None
        assert row[4] == 0.0   # now_price default
        assert row[5] == 0.0   # open_price default
        assert row[6] == 0.0   # max_price default
        assert row[11] == 0    # volume default
        assert row[14] == 0    # up_home default

    def test_mkt_index_classification(self):
        snap = self._make_snap()
        now = datetime(2026, 7, 22, 10, 30, 0)
        row = parse_snapshot(snap, "880001.SH", "mkt_index", "tqcenter_push", now_bj=now)
        assert row is not None
        assert row[3] == "mkt_index"

    def test_tqcenter_snapshot_data_source(self):
        snap = self._make_snap()
        now = datetime(2026, 7, 22, 10, 30, 0)
        row = parse_snapshot(snap, "880101.SH", "sector", "tqcenter_snapshot", now_bj=now)
        assert row is not None
        assert row[19] == "tqcenter_snapshot"
