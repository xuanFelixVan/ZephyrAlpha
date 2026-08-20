# [BLUEPRINT] MOD-H1_REDIS_HOT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""kline_resampler 单元测试。"""

from __future__ import annotations

import pytest

from zephyr.data.kline_resampler import (
    _SYNTH_MAP,
    _build_delete_sql,
    _build_synth_sql,
    _get_date_range,
)

# ---------- _SYNTH_MAP ----------


class TestSynthMap:
    def test_15m_from_1m(self):
        assert _SYNTH_MAP["15m"] == ("1m", 15)

    def test_30m_from_1m(self):
        assert _SYNTH_MAP["30m"] == ("1m", 30)

    def test_60m_from_1m(self):
        assert _SYNTH_MAP["60m"] == ("1m", 60)

    def test_no_5m_source(self):
        """5m 不作为合成源（仅 1m 合成更高级别）。"""
        for source, _ in _SYNTH_MAP.values():
            assert source == "1m"


# ---------- _build_delete_sql ----------


class TestBuildDeleteSql:
    def test_basic(self):
        sql = _build_delete_sql("15m", "2026-07-01", "2026-07-22")
        assert "ALTER TABLE" in sql
        assert "c1_market.kline_sector_880" in sql
        assert "period = '15m'" in sql
        assert "2026-07-01" in sql
        assert "2026-07-22" in sql
        assert "mutations_sync = 2" in sql

    def test_30m(self):
        sql = _build_delete_sql("30m", "2026-07-01", "2026-07-22")
        assert "period = '30m'" in sql

    def test_60m(self):
        sql = _build_delete_sql("60m", "2026-01-01", "2026-07-22")
        assert "period = '60m'" in sql


# ---------- _build_synth_sql ----------


class TestBuildSynthSql:
    def test_15m_sql(self):
        sql = _build_synth_sql("1m", "15m", 15, "2026-07-01", "2026-07-22")
        assert "INSERT INTO" in sql
        assert "c1_market.kline_sector_880" in sql
        assert "'15m' AS period" in sql
        assert "period = '1m'" in sql
        assert "INTERVAL 15 MINUTE" in sql
        assert "argMin(open, timestamp)" in sql
        assert "max(high)" in sql
        assert "min(low)" in sql
        assert "argMax(close, timestamp)" in sql
        assert "sum(volume)" in sql
        assert "sum(amount)" in sql
        assert "synth_1m" in sql

    def test_30m_sql(self):
        sql = _build_synth_sql("1m", "30m", 30, "2026-07-01", "2026-07-22")
        assert "'30m' AS period" in sql
        assert "INTERVAL 30 MINUTE" in sql

    def test_60m_sql(self):
        sql = _build_synth_sql("1m", "60m", 60, "2026-07-01", "2026-07-22")
        assert "'60m' AS period" in sql
        assert "INTERVAL 60 MINUTE" in sql

    def test_date_range_in_sql(self):
        sql = _build_synth_sql("1m", "15m", 15, "2026-07-01", "2026-07-22")
        assert "2026-07-01" in sql
        assert "2026-07-22" in sql

    def test_group_by_window(self):
        sql = _build_synth_sql("1m", "15m", 15, "2026-07-01", "2026-07-22")
        assert "GROUP BY sector_code" in sql
        assert "toStartOfInterval" in sql


# ---------- _get_date_range ----------


class TestGetDateRange:
    def test_7_days_range(self):
        start, end = _get_date_range(7)
        # end should be today (UTC date)
        # start should be 7 days before end
        from datetime import UTC, datetime, timedelta

        expected_end = datetime.now(UTC).date()
        expected_start = expected_end - timedelta(days=7)
        assert start == expected_start.strftime("%Y-%m-%d")
        assert end == expected_end.strftime("%Y-%m-%d")

    def test_30_days_range(self):
        start, end = _get_date_range(30)
        from datetime import UTC, datetime, timedelta

        expected_end = datetime.now(UTC).date()
        expected_start = expected_end - timedelta(days=30)
        assert start == expected_start.strftime("%Y-%m-%d")

    def test_format(self):
        start, end = _get_date_range(1)
        # Should be YYYY-MM-DD format
        assert len(start) == 10
        assert len(end) == 10
        assert start[4] == "-"
        assert end[4] == "-"

    def test_start_before_end(self):
        start, end = _get_date_range(7)
        assert start < end
