# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] zephyr.data.news_taxonomy
# [DOMAIN] D_DATA
# [DEPENDENCIES] (纯常量/纯函数，零依赖)
# [CONSUMERS] scripts.ch.tag_news_category; scripts.ml.run_sentiment_batch; zephyr.nlp.sentiment_aggregator（category 兜底映射）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 源→category 唯一真源（SSoT）：四分口径 announcement/research_report/macro_data/news；未识别源兜底 news；政策维度正交不进 category（regime 关键词旗标线）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无异常——未知源一律返回 news
# [TESTS] tests/zephyr/data/test_news_taxonomy.py
# [TTL] permanent
"""news_taxonomy — 新闻语料四分分类法唯一真源（CAND-DAT-024）。

四类（按源确定，无需模型）：
- ``announcement``     公告（法定披露源：巨潮/cninfo 等）
- ``research_report``  研报（券商研究报告源：akshare_research_report）
- ``macro_data``       宏观数据（纯数据条目源：akshare_economic_baidu 等）
- ``news``             媒体新闻（其余全部，兜底）

政策=内容旗标（跨源），不进 category——regime ``_POLICY_KEYWORDS`` 线覆盖。

依据: CAND-DAT-024（candidate_module_registry.yaml v1.1.3）
Version: 0.1.0
"""

from __future__ import annotations

from typing import Final

CATEGORY_ANNOUNCEMENT: Final[str] = "announcement"
CATEGORY_RESEARCH_REPORT: Final[str] = "research_report"
CATEGORY_MACRO_DATA: Final[str] = "macro_data"
CATEGORY_NEWS: Final[str] = "news"

ALL_CATEGORIES: Final[tuple[str, ...]] = (
    CATEGORY_ANNOUNCEMENT,
    CATEGORY_RESEARCH_REPORT,
    CATEGORY_MACRO_DATA,
    CATEGORY_NEWS,
)

# ── 源名单（新增源在此登记，勿在消费方硬编码）──
SOURCES_ANNOUNCEMENT: Final[frozenset[str]] = frozenset({"巨潮网", "cninfo"})
SOURCES_RESEARCH_REPORT: Final[frozenset[str]] = frozenset({"akshare_research_report"})
SOURCES_MACRO_DATA: Final[frozenset[str]] = frozenset({"akshare_economic_baidu"})


def category_of(source: str) -> str:
    """源标识 → category（未识别兜底 news；空串按 news 处理）。"""
    s = (source or "").strip()
    if s in SOURCES_ANNOUNCEMENT:
        return CATEGORY_ANNOUNCEMENT
    if s in SOURCES_RESEARCH_REPORT:
        return CATEGORY_RESEARCH_REPORT
    if s in SOURCES_MACRO_DATA:
        return CATEGORY_MACRO_DATA
    return CATEGORY_NEWS


__all__: Final = [
    "ALL_CATEGORIES",
    "CATEGORY_ANNOUNCEMENT",
    "CATEGORY_MACRO_DATA",
    "CATEGORY_NEWS",
    "CATEGORY_RESEARCH_REPORT",
    "SOURCES_ANNOUNCEMENT",
    "SOURCES_MACRO_DATA",
    "SOURCES_RESEARCH_REPORT",
    "category_of",
]
