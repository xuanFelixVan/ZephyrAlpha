# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
# [TESTS] zephyr.data.implementations.tick_depth_backfill
# [DOMAIN] D_DATA
"""tick_depth_backfill 单元测试（五档盘口历史回填计算层，裁定⑤ 2026-09-09）。

覆盖：行构造 30 列同序/五档缺失降级/Decimal 转换边界/回填迭代写链
（fetch 与 write_result 全 mock，不依赖 xtquant 与 CH）。
"""

import os
import sys
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

import pytest

import zephyr.data.implementations.tick_depth_backfill as tb
from zephyr.data.implementations.tick_depth_backfill import (
    _to_decimal,
    _to_uint,
    backfill_days,
    build_depth_row,
)

_DATA_SOURCE = "miniqmt"
_RECORDED = "2026-09-09 15:00:00"


class TestDecimalConverters:
    def test_to_decimal_normal(self):
        assert _to_decimal("11.69") == Decimal("11.69")
        assert _to_decimal(11.69) == Decimal("11.69")

    def test_to_decimal_none_and_garbage(self):
        assert _to_decimal(None) is None
        assert _to_decimal("abc") is None

    def test_to_uint_normal_and_negative(self):
        assert _to_uint(100) == 100
        assert _to_uint("42") == 42
        assert _to_uint(-1) is None
        assert _to_uint(None) is None
        assert _to_uint(float("nan")) is None


def _xt_row(bids, asks, bid_vols, ask_vols, price="11.69", volume=962110, amount=1129283900.0):
    """构造类 xtquant tick DataFrame 行（dict-like）。"""
    return {
        "lastPrice": price,
        "price": price,
        "volume": volume,
        "amount": amount,
        "bidPrice": bids,
        "askPrice": asks,
        "bidVol": bid_vols,
        "askVol": ask_vols,
    }


class TestBuildDepthRow:
    def test_full_5level_row_30_columns_ordered(self):
        """五档齐全 → 30 列 tuple，与 INSERT_COLUMNS 同序，quality_flag=1。"""
        row = _xt_row(
            bids=["11.69", "11.68", "11.67", "11.66", "11.65"],
            asks=["11.70", "11.71", "11.72", "11.73", "11.74"],
            bid_vols=[4965, 3236, 2632, 5981, 12438],
            ask_vols=[2930, 2774, 3304, 3223, 1911],
        )
        r = build_depth_row("000001.SZ", "20260907142633", row, _DATA_SOURCE, _RECORDED)

        assert len(r) == 30
        # 列序抽查（与 tick_depth_5.py INSERT_COLUMNS 对齐）
        assert r[0] == "2026-09-07"          # trade_date
        assert r[1] == "2026-09-07 14:26:33"  # timestamp
        assert r[2] == _RECORDED             # recorded_time
        assert r[3] == "000001"            # symbol（纯码，与 tick_data 同构）
        assert r[4] == "stock"               # market_type
        assert r[5] == Decimal("11.69")      # price
        assert r[6] == 962110                # volume
        assert r[8] == _DATA_SOURCE          # data_source
        assert r[9] == Decimal("11.69")      # bid_price1
        assert r[13] == Decimal("11.65")     # bid_price5
        assert r[14] == Decimal("11.70")     # ask_price1
        assert r[18] == Decimal("11.74")     # ask_price5
        assert r[19] == 4965                 # bid_volume1
        assert r[23] == 12438                # bid_volume5
        assert r[24] == 2930                 # ask_volume1
        assert r[28] == 1911                 # ask_volume5
        assert r[29] == 1                    # quality_flag

    def test_etf_market_type(self):
        """ETF 代码前缀 → market_type=etf（与 tick_data 口径一致）。"""
        row = _xt_row(["1.0"], ["1.1"], [10], [20])
        r = build_depth_row("510300.SH", "20260907142633", row, _DATA_SOURCE, _RECORDED)
        assert r[3] == "510300"
        assert r[4] == "etf"

    def test_missing_depth_degrades_quality_flag(self):
        """无五档（老数据形态）→ 深度列全 None，quality_flag=0。"""
        row = _xt_row(bids=[], asks=[], bid_vols=[], ask_vols=[])
        r = build_depth_row("000001.SZ", "20260907142633", row, _DATA_SOURCE, _RECORDED)
        assert r[5] == Decimal("11.69")   # 主字段仍在
        assert all(v is None for v in r[9:29])  # 20 个深度列全 None
        assert r[29] == 0

    def test_partial_depth_keeps_existing_levels(self):
        """部分档位缺失（None/越界）→ 已有档位保留，缺失为 None。"""
        row = _xt_row(
            bids=["11.69", None, "11.67"],
            asks=["11.70"],
            bid_vols=[100, 200],
            ask_vols=[300],
        )
        r = build_depth_row("000001.SZ", "20260907142633", row, _DATA_SOURCE, _RECORDED)
        assert r[9] == Decimal("11.69")   # bid1
        assert r[10] is None              # bid2 缺
        assert r[11] == Decimal("11.67")  # bid3
        assert r[12] is None              # bid4/5 越界
        assert r[14] == Decimal("11.70")  # ask1
        assert r[15] is None
        assert r[19] == 100
        assert r[20] == 200
        assert r[21] is None
        assert r[24] == 300
        assert r[29] == 1  # 有价有 bid1/ask1 → 正常

    def test_bad_price_degrades(self):
        """价格非法 → price=None → quality_flag=0（行仍保留供排查）。"""
        row = _xt_row(["11.69"], ["11.70"], [10], [20], price="N/A")
        r = build_depth_row("000001.SZ", "20260907142633", row, _DATA_SOURCE, _RECORDED)
        assert r[5] is None
        assert r[29] == 0

    def test_short_index_falls_back_recorded_date(self):
        """索引不足 14 位 → 时间戳退化为 recorded 日期 00:00:00。"""
        row = _xt_row(["11.69"], ["11.70"], [10], [20])
        r = build_depth_row("000001.SZ", "2026", row, _DATA_SOURCE, _RECORDED)
        assert r[0] == "2026-09-09"
        assert r[1] == "2026-09-09 00:00:00"


class TestBackfillDays:
    def test_writes_fetch_results_per_symbol_day(self):
        """每 (标的, 日) 一次 FetchResult 写链；表名/列数/错误隔离正确。"""
        row = _xt_row(
            bids=["11.69", "11.68", "11.67", "11.66", "11.65"],
            asks=["11.70", "11.71", "11.72", "11.73", "11.74"],
            bid_vols=[1, 2, 3, 4, 5],
            ask_vols=[6, 7, 8, 9, 10],
        )
        results = {
            ("000001.SZ", "20260908"): ([build_depth_row("000001.SZ", "20260908143000", row, _DATA_SOURCE, _RECORDED)], None),
            ("000001.SZ", "20260909"): ([], "get_market_data_ex failed: boom"),
        }

        with patch.object(tb, "fetch_symbol_day_depth", side_effect=lambda s, d, ds=None: results[(s, d)]), \
                patch.object(tb, "write_result", return_value=True) as wr:
            out = list(backfill_days(["000001.SZ"], ["20260908", "20260909"]))

        assert len(out) == 2
        ok_res, err_res = out
        assert err_res.error is not None and "20260909" in err_res.error
        assert ok_res.error is None
        assert ok_res.table == "c1_market.tick_depth_5"
        assert len(ok_res.rows) == 1
        assert len(ok_res.columns) == 30
        assert wr.call_count == 1  # 失败日不写 CH

    def test_ch_write_failure_reported(self):
        """CH 写失败 → FetchResult.error 上报（不静默丢行）。"""
        with patch.object(tb, "fetch_symbol_day_depth", return_value=([build_depth_row("000001.SZ", "20260908143000", _xt_row(["1"], ["2"], [1], [2]), _DATA_SOURCE, _RECORDED)], None)), \
                patch.object(tb, "write_result", return_value=False):
            out = list(backfill_days(["000001.SZ"], ["20260908"]))
        assert len(out) == 1
        assert out[0].error is not None and "CH write failed" in out[0].error
