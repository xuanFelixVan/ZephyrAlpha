# [BLUEPRINT] MOD-L00-004 | data_source_integrator_blueprint.md | §4
# [TTL] permanent
"""test_news_taxonomy.py — 四分分类法唯一真源单元测试（CAND-DAT-024）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from zephyr.data.news_taxonomy import (  # noqa: E402
    ALL_CATEGORIES,
    CATEGORY_ANNOUNCEMENT,
    CATEGORY_MACRO_DATA,
    CATEGORY_NEWS,
    CATEGORY_RESEARCH_REPORT,
    SOURCES_ANNOUNCEMENT,
    SOURCES_MACRO_DATA,
    SOURCES_RESEARCH_REPORT,
    category_of,
)


class TestCategoryOf:
    def test_specials(self):
        assert category_of("巨潮网") == CATEGORY_ANNOUNCEMENT
        assert category_of("cninfo") == CATEGORY_ANNOUNCEMENT
        assert category_of("akshare_research_report") == CATEGORY_RESEARCH_REPORT
        assert category_of("akshare_economic_baidu") == CATEGORY_MACRO_DATA

    def test_media_fallback(self):
        assert category_of("财联社") == CATEGORY_NEWS
        assert category_of("cls") == CATEGORY_NEWS
        assert category_of("eastmoney") == CATEGORY_NEWS

    def test_unknown_and_empty_fallback_news(self):
        assert category_of("不存在的源xyz") == CATEGORY_NEWS
        assert category_of("") == CATEGORY_NEWS
        assert category_of(None) == CATEGORY_NEWS  # type: ignore[arg-type]

    def test_whitespace_tolerant(self):
        assert category_of(" 巨潮网 ") == CATEGORY_ANNOUNCEMENT


class TestVocabulary:
    def test_all_categories_quartet(self):
        assert set(ALL_CATEGORIES) == {
            CATEGORY_ANNOUNCEMENT,
            CATEGORY_RESEARCH_REPORT,
            CATEGORY_MACRO_DATA,
            CATEGORY_NEWS,
        }

    def test_source_sets_disjoint(self):
        assert not (SOURCES_ANNOUNCEMENT & SOURCES_RESEARCH_REPORT)
        assert not (SOURCES_ANNOUNCEMENT & SOURCES_MACRO_DATA)
        assert not (SOURCES_RESEARCH_REPORT & SOURCES_MACRO_DATA)
