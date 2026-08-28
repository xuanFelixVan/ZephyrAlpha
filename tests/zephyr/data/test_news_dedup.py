# [BLUEPRINT] MOD-L00-004 | data_source_integrator_blueprint.md | §4
# [TTL] permanent
"""test_news_dedup.py — 新闻去重模块单元测试（CAND-DAT-025）。

覆盖（Fake 零外部依赖，不触达 ClickHouse）：
  1. _parse_datetime 时区语义固化 —— naive 串/纯日期/tz-aware 三态
     （naive 一律按 Asia/Shanghai 墙钟；tz-aware 先转 Asia/Shanghai 再落地）
  2. existing_news_ids —— 写前预检公共助手（TSV 解析/空结果/失败 fail-open/WHERE 透传）
  3. build_news_row —— tz-aware 输入的 news_id 随修正后的 publish_time 变化（行为变更固化）
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data import news_dedup  # noqa: E402


class TestParseDatetimeTimezone:
    """_parse_datetime 三态语义（CAND-DAT-025：publish_time 规范化唯一真源）。"""

    def test_naive_string_unchanged(self):
        assert news_dedup._parse_datetime("2025-06-15 09:30:00") == "2025-06-15 09:30:00"

    def test_pure_date_stays_midnight(self):
        assert news_dedup._parse_datetime("2025-06-15") == "2025-06-15 00:00:00"

    def test_tz_aware_utc_converts_to_shanghai(self):
        # UTC 午夜 = 北京 08:00（防"UTC 墙钟直接落地"的 8h 漂移复发）
        assert news_dedup._parse_datetime("2025-06-15T00:00:00+00:00") == "2025-06-15 08:00:00"

    def test_tz_aware_beijing_keeps_wallclock(self):
        assert news_dedup._parse_datetime("2025-06-15T09:30:00+08:00") == "2025-06-15 09:30:00"

    def test_rfc2822_gmt_converts(self):
        assert news_dedup._parse_datetime("Sun, 15 Jun 2025 00:00:00 GMT") == "2025-06-15 08:00:00"

    def test_invalid_falls_back_to_prefix(self):
        assert news_dedup._parse_datetime("2025-06-15 abnormal") == "2025-06-15 abnormal"[:19]


class TestExistingNewsIds:
    """existing_news_ids 写前预检助手。"""

    def test_parses_tsv_into_set(self, monkeypatch):
        monkeypatch.setattr(
            news_dedup.ch_reader, "query", lambda sql: "id_a\nid_b\nid_a\n"
        )
        assert news_dedup.existing_news_ids("source='x'") == {"id_a", "id_b"}

    def test_empty_result_returns_empty_set(self, monkeypatch):
        monkeypatch.setattr(news_dedup.ch_reader, "query", lambda sql: "")
        assert news_dedup.existing_news_ids("source='x'") == set()

    def test_query_failure_fail_open(self, monkeypatch):
        def _boom(sql):
            raise RuntimeError("CH down")

        monkeypatch.setattr(news_dedup.ch_reader, "query", _boom)
        assert news_dedup.existing_news_ids("source='x'") == set()

    def test_where_clause_passed_through(self, monkeypatch):
        captured = {}
        monkeypatch.setattr(
            news_dedup.ch_reader, "query", lambda sql: captured.setdefault("sql", sql) or ""
        )
        news_dedup.existing_news_ids("source='akshare_research_report'")
        assert "source='akshare_research_report'" in captured["sql"]
        assert "DISTINCT news_id" in captured["sql"]


class TestBuildNewsRowTzAware:
    def test_tz_aware_input_shifts_publish_time_and_id(self):
        row_old_semantics = hashlib.md5("srcT2025-06-15 00:00:00".encode()).hexdigest()
        row = news_dedup.build_news_row(
            "2025-06-15T00:00:00+00:00", "T", "", "s", "src", "ds"
        )
        # 修正后 publish_time = 北京 08:00；news_id 随之为新值（行为变更固化）
        assert row[1] == "2025-06-15 08:00:00"
        assert row[0] == hashlib.md5("srcT2025-06-15 08:00:00".encode()).hexdigest()
        assert row[0] != row_old_semantics

    def test_naive_input_id_stable(self):
        row = news_dedup.build_news_row("2025-06-15", "T", "", "s", "src", "ds")
        assert row[1] == "2025-06-15 00:00:00"
        assert row[0] == hashlib.md5("srcT2025-06-15 00:00:00".encode()).hexdigest()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
