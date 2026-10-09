# [A_test] module_id: MOD-DATA-news_collector_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.data.test_news_collector
# [DOMAIN] D_DATA
# [CONSUMERS] CI pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/data/test_news_collector.py -q
# [TTL] task_bound
# [ARCH-REF] #ARCH-NLP-PIPELINE-001 Phase 1
"""test_news_collector.py — NewsCollector 单测（P1-E3 Phase 1）。

验证核心契约：
  1. collect_news 日期格式校验（非法格式 → NewsCollectorError）
  2. collect_news 空结果返回空 DataFrame（含正确列名）
  3. collect_news TSV 解析正确（列顺序/publish_time 转换）
  4. collect_news_by_ids 空列表返回空 DataFrame
  5. collect_news_by_ids SQL 构造含 IN 子句

测试隔离：monkeypatch ch_reader.query 注入假 TSV，零真实 ClickHouse 依赖。
"""

from __future__ import annotations

import pytest

import zephyr.data.news_collector as nc
from zephyr.data.news_collector import NewsCollectorError, collect_news, collect_news_by_ids

# ============ collect_news：日期校验 ============


class TestCollectNewsDateValidation:
    """日期格式非法 → NewsCollectorError。"""

    def test_invalid_start_date_raises(self) -> None:
        with pytest.raises(NewsCollectorError, match="start_date"):
            collect_news("2026/08/01", "2026-08-08")

    def test_invalid_end_date_raises(self) -> None:
        with pytest.raises(NewsCollectorError, match="end_date"):
            collect_news("2026-08-01", "not-a-date")

    def test_empty_date_string_raises(self) -> None:
        with pytest.raises(NewsCollectorError):
            collect_news("", "2026-08-08")


# ============ collect_news：空结果处理 ============


class TestCollectNewsEmptyResult:
    """ch_reader.query 返回空 → 空 DataFrame（含正确列名）。"""

    def test_empty_tsv_returns_empty_df(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(nc.ch_reader, "query", lambda sql, **kw: "")
        df = collect_news("2026-01-01", "2026-01-31")
        assert df.empty
        assert list(df.columns) == nc._NEWS_QUERY_COLUMNS

    def test_whitespace_tsv_returns_empty_df(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(nc.ch_reader, "query", lambda sql, **kw: "   \n  ")
        df = collect_news("2026-01-01", "2026-01-31")
        assert df.empty
        assert list(df.columns) == nc._NEWS_QUERY_COLUMNS


# ============ collect_news：TSV 解析 ============


class TestCollectNewsParsing:
    """TSV 正确解析为 DataFrame。"""

    _FAKE_TSV = (
        "nid1\t2026-01-05 10:30:00\t央行降准利好市场\t央行宣布降准0.5个百分点\t央行\tCN\tzh\n"
        "nid2\t2026-01-06 14:00:00\t某公司爆雷\t某公司发布业绩预警\t财联社\tCN\tzh\n"
    )

    def test_parses_rows_correctly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(nc.ch_reader, "query", lambda sql, **kw: self._FAKE_TSV)
        df = collect_news("2026-01-01", "2026-01-31")
        assert len(df) == 2
        assert df.iloc[0]["news_id"] == "nid1"
        assert df.iloc[0]["title"] == "央行降准利好市场"
        assert df.iloc[1]["source"] == "财联社"
        # publish_time 应为 datetime
        assert df["publish_time"].dtype.name.startswith("datetime")

    def test_limit_appended_to_sql(self, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: list[str] = []

        def fake_query(sql: str, **kw: object) -> str:
            captured.append(sql)
            return ""

        monkeypatch.setattr(nc.ch_reader, "query", fake_query)
        collect_news("2026-01-01", "2026-01-31", limit=100)
        assert any("LIMIT 100" in s for s in captured)


# ============ collect_news_by_ids ============


class TestCollectNewsByIds:
    """按 news_id 列表查询。"""

    def test_empty_list_returns_empty_df(self) -> None:
        df = collect_news_by_ids([])
        assert df.empty
        assert list(df.columns) == nc._NEWS_QUERY_COLUMNS

    def test_sql_contains_in_clause(self, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: list[str] = []

        def fake_query(sql: str, **kw: object) -> str:
            captured.append(sql)
            return ""

        monkeypatch.setattr(nc.ch_reader, "query", fake_query)
        collect_news_by_ids(["nid1", "nid2"])
        assert any("IN (" in s and "'nid1'" in s and "'nid2'" in s for s in captured)
