# [A_test] module_id: MOD-GOV_test_instrument_master | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.data.test_instrument_master
# [TESTS] src/zephyr/data/instrument_master.py
# [TTL] task_bound
"""90 号 Phase2 项（#18 资产覆盖）：轻量 Instrument Master toy 断言。

裁定真源：90_methodology_open_questions.md §18（v2.0.0）——
  ① 轻量 IM（拒绝 200+ 字段重型系统）；② 最小字段集=15 字段+A股必需补充
  （板块代码/ST标志及变更日期/退市整理期/上市日期/停牌/昨收价/最小申报单位）；
  ③ ST 状态 PIT 跟踪采纳（effective_date 子表）。
"""

from __future__ import annotations

import pytest

from zephyr.data.instrument_master import (
    INSTRUMENT_MASTER_DDL,
    ST_STATUS_PIT_DDL,
    normalize_instrument_row,
)


class TestDDL:
    def test_main_table_has_ashare_required_fields(self):
        """A 股必需补充字段（裁定②）全部在表结构内。"""
        for col in (
            "board",  # 板块代码（决定涨跌幅 ±10%/20%/30%）
            "is_st",  # ST/*ST 标志
            "st_change_date",  # ST 变更日期
            "in_delisting_period",  # 退市整理期
            "list_date",  # 上市日期（次新过滤）
            "is_suspended",  # 停牌标志
            "prev_close",  # 昨收价（算涨跌停价）
            "min_order_unit",  # 最小申报单位
            "float_shares",  # 流通股本（#15 市值分层取数）
        ):
            assert col in INSTRUMENT_MASTER_DDL, col

    def test_st_pit_subtable_has_effective_date(self):
        """ST 状态 PIT 子表（裁定③）含 effective_date。"""
        assert "effective_date" in ST_STATUS_PIT_DDL
        assert "is_st" in ST_STATUS_PIT_DDL

    def test_ddl_is_clickhouse_replacing(self):
        """与项目既有 PIT 版本语义一致（ReplacingMergeTree）。"""
        assert "ReplacingMergeTree" in INSTRUMENT_MASTER_DDL


class TestNormalizeRow:
    def _base(self):
        return {
            "symbol": "600000.SH",
            "exchange": "SH",
            "security_type": "stock",
            "board": "main",
            "list_date": "1999-11-10",
        }

    def test_main_board_min_unit_100(self):
        row = normalize_instrument_row(self._base())
        assert row["min_order_unit"] == 100

    def test_star_board_min_unit_200(self):
        """科创板最小申报单位 200 股起（裁定②）。"""
        raw = self._base() | {"symbol": "688001.SH", "board": "star"}
        row = normalize_instrument_row(raw)
        assert row["min_order_unit"] == 200

    def test_explicit_min_unit_respected(self):
        row = normalize_instrument_row(self._base() | {"min_order_unit": 100})
        assert row["min_order_unit"] == 100

    def test_missing_required_raises(self):
        with pytest.raises(ValueError):
            normalize_instrument_row({"symbol": "600000.SH"})

    def test_invalid_exchange_raises(self):
        with pytest.raises(ValueError):
            normalize_instrument_row(self._base() | {"exchange": "HK"})

    def test_invalid_board_raises(self):
        with pytest.raises(ValueError):
            normalize_instrument_row(self._base() | {"board": "nasdaq"})
