# [BLUEPRINT] MOD-NLP-IMPACT-001 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-22 行）
# [MODULE] zephyr.nlp.news_impact_grader
# [DOMAIN] D_DATA
# [DEPENDENCIES] （纯函数：输入 news_data 行映射注入）
# [CONSUMERS] （候选：新闻页指标卡「影响评估」+ 热点聚类「主题 ×N」）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 影响三级封闭 A（宏观/政策/系统性）/B（题材/行业/公司重大）/C（一般兜底）；A 级=宏观政策关键词命中即定（不看源数）；B 级=主题词或公司重大词命中；热点聚类=主题关键词命中计数（一新闻可多主题）；多源共振=同主题 ≥2 独立来源；样本截断留痕；空输入 degraded 不炸；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-22 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] news_items 元素类型非法→ValueError（fail-closed）；单新闻字段缺失按空串参与不抛
# [TESTS] tests/nlp/test_news_impact_grader.py
# [A_module] module_id=MOD-NLP-IMPACT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-NLP-IMPACT-001 — 新闻影响评估分级 + 热点聚类（GAP-F-22，新闻页后端）。

两件套（关键词规则 MVP，纯函数）：
1. **影响评估分级**（A/B/C 封闭三级）：
   - A 级=宏观/政策/系统性事件（央行/国务院/降准降息/关税/战争/金融危机
     等关键词命中即定，不依赖多源——此类事件单源即重大影响）；
   - B 级=题材/行业/公司重大（主题词命中，或 订单/中标/合同/并购/重组/
     预增 等公司重大词命中）；
   - C 级=其余兜底（不硬编升级）。
   与 MOD-NLP-DUALTAG-001 双标签（可预测性/预期差）正交：那是"新闻怎么读"，
   这是"新闻多大影响"。
2. **热点聚类**（"半导体国产化 ×48"主题计数形态）：主题关键词命中计数
   （一新闻可命中多主题），按计数降序；同主题 ≥2 独立来源 → 多源共振标注
   （对齐 MOD-NLP-AGGREGATOR-001 跨源一致性语义）；样本截断留痕。
   主题词典与 MOD-SIG-066 同源语义、本模块自维护小集（消费形态不同——
   归因 vs 聚类计数，config.theme_keywords 可覆盖）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 新闻清单 list[NewsItemInput]（news_id/title/content/source/publish_time）
# 层: 算法
# - id: A1 A/B/C 分级（关键词规则）
# - id: A2 主题聚类计数 + 多源共振
# 层: 输出
# - id: O1 NewsImpactReport（graded + hotspots + grade_counts）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# A1,A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final, Mapping, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "GRADE_A",
    "GRADE_B",
    "GRADE_C",
    "GradedNews",
    "HotTheme",
    "NewsImpactConfig",
    "NewsImpactReport",
    "NewsItemInput",
    "grade_and_cluster_news",
]

#: 影响三级（封闭集合）
GRADE_A: Final[str] = "A"
GRADE_B: Final[str] = "B"
GRADE_C: Final[str] = "C"

#: A 级宏观/政策/系统性关键词（命中即 A，单源即重大）
_DEFAULT_MACRO_KEYWORDS: Final[tuple[str, ...]] = (
    "央行", "国务院", "降准", "降息", "加息", "MLF", "LPR", "关税",
    "证监会", "金融危机", "战争", "违约", "主权", "特别国债", "刺激政策",
)

#: B 级公司重大补充词（主题词外的行业/公司重大事件）
_DEFAULT_MAJOR_EVENT_KEYWORDS: Final[tuple[str, ...]] = (
    "订单", "中标", "合同", "并购", "重组", "预增", "扭亏", "业绩快报",
)

#: 默认主题词典（主题 → 关键词组；与 MOD-SIG-066 同源语义、自维护小集）
_DEFAULT_THEME_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "半导体": ("半导体", "芯片", "晶圆", "光刻", "存储器", "国产化", "自主可控"),
    "人工智能": ("人工智能", "AI", "大模型", "算力", "AIGC"),
    "机器人": ("机器人", "人形机器人", "减速器"),
    "新能源": ("锂电", "光伏", "储能", "固态电池", "风电", "新能源汽车"),
    "军工": ("军工", "国防", "航母", "导弹", "低空经济", "商业航天"),
    "医药": ("医药", "创新药", "疫苗", "CXO", "医疗器械"),
    "券商金融": ("券商", "证券", "保险", "银行", "并购重组"),
    "地产": ("地产", "房地产", "保障房", "城中村"),
    "消费": ("消费", "白酒", "食品", "免税", "零售", "家电"),
    "数字经济": ("信创", "数据要素", "数字货币", "区块链", "云计算"),
    "有色资源": ("有色", "稀土", "黄金", "铜", "铝", "煤炭", "钢铁"),
}


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class NewsImpactConfig:
    """分级+聚类配置（MVP 初拍值）。"""

    macro_keywords: tuple[str, ...] = _DEFAULT_MACRO_KEYWORDS
    major_event_keywords: tuple[str, ...] = _DEFAULT_MAJOR_EVENT_KEYWORDS
    theme_keywords: Mapping[str, tuple[str, ...]] | None = None  # None=默认主题词典
    max_samples_per_theme: int = 3  # 主题样本留痕条数上限
    multi_source_min: int = 2  # 多源共振最少独立来源数


@dataclass(frozen=True, slots=True)
class NewsItemInput:
    """新闻输入（news_data 行映射）。"""

    news_id: str
    title: str = ""
    content: str = ""
    source: str = ""
    publish_time: str = ""


@dataclass(frozen=True, slots=True)
class GradedNews:
    """单条新闻影响分级。"""

    news_id: str
    grade: str  # A/B/C
    reason: str
    themes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class HotTheme:
    """热点主题（"主题 ×N"形态）。"""

    theme: str
    count: int
    sources: list[str] = field(default_factory=list)
    multi_source: bool = False
    sample_news_ids: list[str] = field(default_factory=list)
    sample_titles: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class NewsImpactReport:
    """分级+聚类输出（观测层消费，不接交易）。"""

    graded: list[GradedNews] = field(default_factory=list)
    hotspots: list[HotTheme] = field(default_factory=list)
    grade_counts: dict[str, int] = field(default_factory=dict)
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 主核（纯函数）
# ------------------------------------------------------------------


def _match_keywords(text: str, keywords: Sequence[str]) -> str | None:
    for kw in keywords:
        if kw in text:
            return kw
    return None


def grade_and_cluster_news(
    news_items: Sequence[NewsItemInput],
    config: NewsImpactConfig | None = None,
) -> NewsImpactReport:
    """新闻影响分级 + 热点聚类主核（纯函数，不触库）。

    Args:
        news_items: 新闻清单（NewsItemInput 序列；空 → degraded）。
        config: 配置（None 用默认；theme_keywords 覆盖默认词典）。

    Returns:
        NewsImpactReport；graded 输入序保持，hotspots 计数降序。

    Raises:
        ValueError: news_items 元素类型非法（fail-closed）。
    """
    cfg = config or NewsImpactConfig()
    themes = cfg.theme_keywords or _DEFAULT_THEME_KEYWORDS
    if not news_items:
        return NewsImpactReport(degraded=True, notes=["空新闻清单，分级聚类整体降级"])

    graded: list[GradedNews] = []
    grade_counts: dict[str, int] = {GRADE_A: 0, GRADE_B: 0, GRADE_C: 0}
    theme_map: dict[str, list[NewsItemInput]] = {}
    for n in news_items:
        if not isinstance(n, NewsItemInput):
            raise ValueError(f"news_items 元素非法（须 NewsItemInput）: {type(n).__name__}")
        text = f"{n.title} {n.content}"
        hit_themes = [t for t, kws in themes.items() if _match_keywords(text, kws)]
        macro_hit = _match_keywords(text, cfg.macro_keywords)
        major_hit = _match_keywords(text, cfg.major_event_keywords)
        if macro_hit:
            grade, reason = GRADE_A, f"宏观/政策关键词命中「{macro_hit}」（单源即重大）"
        elif hit_themes:
            grade, reason = GRADE_B, f"题材命中（{'/'.join(hit_themes)}）"
        elif major_hit:
            grade, reason = GRADE_B, f"公司重大事件关键词命中「{major_hit}」"
        else:
            grade, reason = GRADE_C, "无题材/重大词命中，一般新闻兜底"
        graded.append(GradedNews(news_id=n.news_id, grade=grade, reason=reason, themes=hit_themes))
        grade_counts[grade] += 1
        for t in hit_themes:
            theme_map.setdefault(t, []).append(n)

    hotspots: list[HotTheme] = []
    for theme, items in theme_map.items():
        sources = sorted({i.source for i in items if i.source})
        hotspots.append(
            HotTheme(
                theme=theme,
                count=len(items),
                sources=sources,
                multi_source=len(sources) >= cfg.multi_source_min,
                sample_news_ids=[i.news_id for i in items[: cfg.max_samples_per_theme]],
                sample_titles=[i.title for i in items[: cfg.max_samples_per_theme]],
            )
        )
    hotspots.sort(key=lambda h: (-h.count, h.theme))
    return NewsImpactReport(
        graded=graded,
        hotspots=hotspots,
        grade_counts=grade_counts,
        degraded=False,
        notes=[],
    )
