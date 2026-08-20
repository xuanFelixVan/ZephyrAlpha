# [BLUEPRINT] MOD-INF-043 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""Unit tests for scripts/ch/optimize_merge.py — ReplacingMergeTree 合并维护工具。

锁定事实（2026-08-16 实证）：
  - 全部业务表 ReplacingMergeTree，merge 不保证完成 → 需分区级 OPTIMIZE FINAL 周期维护
  - 分区标识两形态：裸月份 201901 / 元组键 ('60min',201901)
  - 非时间分区必须跳过（防对非月份分区误 OPTIMIZE）
"""

from __future__ import annotations

import datetime
import importlib.util
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("optimize_merge", _ROOT / "scripts" / "ch" / "optimize_merge.py")
om = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(om)


class TestExtractMonth:
    @pytest.mark.parametrize(
        "partition,expected",
        [
            ("201901", "201901"),
            ("('60min',201901)", "201901"),
            ("('120min',202108)", "202108"),
            ("2026", None),
            ("abc", None),
            ("all", None),
        ],
    )
    def test_extract(self, partition, expected):
        assert om.extract_month(partition) == expected


class TestPartitionLiteral:
    def test_plain_month(self):
        assert om.partition_literal("201901") == "201901"

    def test_tuple_passthrough(self):
        assert om.partition_literal("('60min',201901)") == "('60min',201901)"

    def test_string_quoted(self):
        assert om.partition_literal("2026-W01") == "'2026-W01'"


class TestWeeklyCutoff:
    def test_normal(self):
        assert om.weekly_cutoff(datetime.date(2026, 8, 16), months=3) == "202605"

    def test_cross_year(self):
        assert om.weekly_cutoff(datetime.date(2026, 2, 1), months=3) == "202511"


class TestListPartitions:
    def test_range_and_skip_nontime(self, monkeypatch):
        fake = "201812\n201901\n('60min',201901)\n202109\n"
        monkeypatch.setattr(om.ch_reader, "query", lambda sql, **kw: fake)
        got = om.list_partitions("c1_market.kline_5min", "201901", "202108")
        assert got == ["201901", "('60min',201901)"]

    def test_all_when_no_range(self, monkeypatch):
        fake = "201901\n202109\n"
        monkeypatch.setattr(om.ch_reader, "query", lambda sql, **kw: fake)
        assert om.list_partitions("c1_market.kline_5min", None, None) == ["201901", "202109"]


class TestOptimizePartition:
    def test_dry_run_no_query(self, monkeypatch):
        calls = []
        monkeypatch.setattr(om.ch_reader, "query", lambda sql, **kw: calls.append(sql) or "")
        assert om.optimize_partition("c1_market.kline_5min", "202101", dry_run=True)
        assert calls == []

    def test_real_run_sql_form(self, monkeypatch):
        calls = []
        monkeypatch.setattr(om.ch_reader, "query", lambda sql, **kw: calls.append(sql) or "")
        assert om.optimize_partition("c1_market.kline_5min", "202101")
        assert calls == ["OPTIMIZE TABLE c1_market.kline_5min PARTITION 202101 FINAL"]

    def test_failure_isolated(self, monkeypatch):
        def boom(sql, **kw):
            raise RuntimeError("CH down")

        monkeypatch.setattr(om.ch_reader, "query", boom)
        assert om.optimize_partition("c1_market.kline_5min", "202101") is False
