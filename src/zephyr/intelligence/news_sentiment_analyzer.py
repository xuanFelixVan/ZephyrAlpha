# [BLUEPRINT] MOD-INF-050 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.intelligence.news_sentiment_analyzer
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] pandas; zephyr.data.news_collector; zephyr.nlp.nlp_inference
# [CONSUMERS] MOD-SIG-002(信号生成器, 消费 SentimentEvent)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 规则法情绪打分MVP桩，LLM打分走zephyr.nlp.nlp_inference扩展口；聚合窗口默认1h，空输入返回空结果不报错
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_intelligence/news_sentiment_analyzer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NewsSentimentAnalyzerError(ZA-IT-0003)
# [TESTS] tests/intelligence/test_news_sentiment_analyzer.py
# [A_module] module_id=MOD-INT-AISA | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-AISA-001 MVP 施工

"""
MOD-INT-AISA NewsSentimentAnalyzer — A股舆情分析器MVP。

功能边界（MVP）：
- 数据消费：复用 news_collector 查询 fund_news_data 已有多源新闻
- 规则法情绪打分：基于关键词表的正负向匹配，产出 [-1, 1] 有向极性
- LLM 扩展口：预留 infer_llm_sentiment() 接口，调用方注入 nlp_inference
- 聚合器：按时间窗口（默认1h）聚合单条 sentiment → 窗口级 sentiment_index
- 事件信号：sentiment_index 突破阈值时产出 SentimentEvent（方向+强度+标的列表）

不建表、不持久化——sentiment 结果以内存态返回，由下游消费方决定是否落盘。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Callable, Final

import pandas as pd

from zephyr.data.news_collector import collect_news

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    from zephyr.nlp.nlp_inference import SentimentResult

_logger = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约
# ============================================================================


class NewsSentimentAnalyzerError(ZephyrBaseError):
    """ZA-IT-0003: NewsSentimentAnalyzer 错误。"""

    error_code = "ZA-IT-0003"


# ============================================================================
# 2. 数据契约
# ============================================================================


@dataclass(frozen=True, slots=True)
class SentimentScore:
    """单条新闻的情绪得分（规则法或LLM法产出）。"""

    news_id: str
    title: str
    polarity: float  # [-1, 1]，负=看空，正=看多，0=中性
    method: str  # "rule" | "llm" | "hybrid"
    keywords: tuple[str, ...] = field(default_factory=tuple)  # 规则法命中的关键词
    raw_text: str = ""  # 截断后原文（≤200字，调试/审计用）


@dataclass(frozen=True, slots=True)
class SentimentWindow:
    """时间窗口内的聚合情绪指标。"""

    window_start: datetime
    window_end: datetime
    news_count: int
    avg_polarity: float  # 窗口平均极性
    positive_ratio: float  # 正向新闻占比
    negative_ratio: float  # 负向新闻占比
    sentiment_index: float  # 综合情绪指数 [-1, 1]，加权平均


@dataclass(frozen=True, slots=True)
class SentimentEvent:
    """舆情事件信号——供下游信号生成器消费。"""

    event_time: datetime
    event_type: str  # "positive_spike" | "negative_spike" | "sentiment_shift"
    sentiment_index: float
    trigger_news_count: int
    symbols: tuple[str, ...] = field(default_factory=tuple)  # 涉及标的（MVP从标题提取）
    description: str = ""


# ============================================================================
# 3. 规则法情绪打分桩
# ============================================================================

# A股舆情关键词表（MVP 静态表，扩展口：支持运行时注入自定义词典）
_POSITIVE_KEYWORDS: Final[frozenset[str]] = frozenset(
    {
        "利好",
        "上涨",
        "涨停",
        "反弹",
        "突破",
        "增持",
        "回购",
        "分红",
        "业绩大增",
        "超预期",
        "净利润增长",
        "营收增长",
        "订单饱满",
        "产能扩张",
        "政策扶持",
        "补贴",
        "降准",
        "降息",
        "流动性宽松",
        "外资流入",
        "机构看好",
        "买入评级",
        "目标价上调",
        "重组",
        "并购",
        "资产注入",
    }
)

_NEGATIVE_KEYWORDS: Final[frozenset[str]] = frozenset(
    {
        "利空",
        "下跌",
        "跌停",
        "崩盘",
        "破发",
        "减持",
        "套现",
        "亏损",
        "业绩暴雷",
        "不及预期",
        "净利润下滑",
        "营收下降",
        "订单取消",
        "产能收缩",
        "政策打压",
        "监管点名",
        "立案调查",
        "加息",
        "流动性收紧",
        "外资流出",
        "机构看空",
        "卖出评级",
        "目标价下调",
        "退市",
        "st",
        "*st",
        "债务违约",
        "信用评级下调",
    }
)

# 正则预编译（提升批量性能）
_POS_PATTERN: Final[re.Pattern[str]] = re.compile("|".join(re.escape(kw) for kw in _POSITIVE_KEYWORDS))
_NEG_PATTERN: Final[re.Pattern[str]] = re.compile("|".join(re.escape(kw) for kw in _NEGATIVE_KEYWORDS))


class RuleBasedSentimentScorer:
    """规则法情绪打分器——关键词匹配，零外部依赖，O(n) 线性扫描。"""

    def __init__(
        self,
        positive_keywords: frozenset[str] | None = None,
        negative_keywords: frozenset[str] | None = None,
    ) -> None:
        self._pos = positive_keywords or _POSITIVE_KEYWORDS
        self._neg = negative_keywords or _NEGATIVE_KEYWORDS
        self._pos_pat = re.compile("|".join(re.escape(kw) for kw in self._pos))
        self._neg_pat = re.compile("|".join(re.escape(kw) for kw in self._neg))

    def score(self, title: str, content: str = "") -> tuple[float, tuple[str, ...]]:
        """返回 (polarity, matched_keywords)。

        规则：
        - 标题权重=1.0，正文权重=0.3（标题信息密度高）
        - 每条正向关键词 +0.15，负向 -0.15，封顶 ±0.90
        - 无匹配 → 0.0 中性
        """
        text = f"{title} {content}" if content else title
        text_lower = text.lower()

        pos_hits = self._pos_pat.findall(text_lower)
        neg_hits = self._neg_pat.findall(text_lower)

        # 去重计数（同一关键词多次出现只算一次，防标题重复词刷分）
        pos_unique = set(pos_hits)
        neg_unique = set(neg_hits)

        # 标题命中 vs 正文命中（简单启发：关键词在标题中出现则权重更高）
        title_lower = title.lower()
        pos_in_title = {kw for kw in pos_unique if kw in title_lower}
        neg_in_title = {kw for kw in neg_unique if kw in title_lower}

        pos_score = len(pos_in_title) * 0.20 + (len(pos_unique) - len(pos_in_title)) * 0.08
        neg_score = len(neg_in_title) * 0.20 + (len(neg_unique) - len(neg_in_title)) * 0.08

        polarity = max(-0.90, min(0.90, pos_score - neg_score))
        matched = tuple(sorted(pos_unique | neg_unique))
        return polarity, matched


# ============================================================================
# 4. LLM 扩展口（调用方注入）
# ============================================================================

LLMSentimentScorer = Callable[[str, str], "SentimentResult"]
"""LLM 情感打分器类型签名：title, content -> SentimentResult。"""


# ============================================================================
# 5. 聚合器
# ============================================================================


class SentimentAggregator:
    """时间窗口聚合器——将单条 sentiment 极性聚合成窗口级指标。"""

    def __init__(self, window_minutes: int = 60) -> None:
        if window_minutes <= 0:
            raise NewsSentimentAnalyzerError("window_minutes 必须 > 0")
        self._window = timedelta(minutes=window_minutes)

    def aggregate_from_df(
        self,
        df: pd.DataFrame,
        polarity_col: str = "polarity",
        time_col: str = "publish_time",
    ) -> list[SentimentWindow]:
        """从 DataFrame 聚合窗口 sentiment。

        Parameters
        ----------
        df : DataFrame，必须含 time_col 和 polarity_col
        polarity_col : 极性列名
        time_col : 时间列名（datetime）

        Returns
        -------
        SentimentWindow 列表，按时间升序。
        """
        if df.empty:
            return []

        required = {time_col, polarity_col}
        missing = required - set(df.columns)
        if missing:
            raise NewsSentimentAnalyzerError(f"DataFrame 缺少列: {missing}")

        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        df = df.dropna(subset=[time_col, polarity_col])
        if df.empty:
            return []

        df = df.sort_values(time_col)
        min_ts = df[time_col].min()
        max_ts = df[time_col].max()

        windows: list[SentimentWindow] = []
        cursor = min_ts.floor("h")  # 对齐整点
        while cursor <= max_ts:
            end = cursor + self._window
            mask = (df[time_col] >= cursor) & (df[time_col] < end)
            chunk = df.loc[mask, polarity_col]

            if not chunk.empty:
                avg_p = float(chunk.mean())
                pos_r = float((chunk > 0).sum() / len(chunk))
                neg_r = float((chunk < 0).sum() / len(chunk))
                windows.append(
                    SentimentWindow(
                        window_start=cursor,
                        window_end=end,
                        news_count=len(chunk),
                        avg_polarity=round(avg_p, 4),
                        positive_ratio=round(pos_r, 4),
                        negative_ratio=round(neg_r, 4),
                        sentiment_index=round(avg_p, 4),
                    )
                )
            cursor = end

        return windows


# ============================================================================
# 6. 主分析器
# ============================================================================


class NewsSentimentAnalyzer:
    """舆情分析器主类——MVP 提供 rule-based 分析，LLM 由调用方注入。"""

    def __init__(
        self,
        window_minutes: int = 60,
        positive_threshold: float = 0.30,
        negative_threshold: float = -0.30,
        llm_scorer: LLMSentimentScorer | None = None,
    ) -> None:
        """
        Parameters
        ----------
        window_minutes : 聚合窗口分钟数，默认 60
        positive_threshold : sentiment_index 超过此值触发 positive_spike 事件
        negative_threshold : sentiment_index 低于此值触发 negative_spike 事件
        llm_scorer : 可选 LLM 打分器，注入后 analyze() 自动走 LLM 而非规则法
        """
        self._rule_scorer = RuleBasedSentimentScorer()
        self._aggregator = SentimentAggregator(window_minutes=window_minutes)
        self._pos_thr = positive_threshold
        self._neg_thr = negative_threshold
        self._llm_scorer = llm_scorer

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------

    def analyze_news_df(
        self,
        df: pd.DataFrame,
        title_col: str = "title",
        content_col: str = "content",
        news_id_col: str = "news_id",
    ) -> pd.DataFrame:
        """对新闻 DataFrame 逐条打分，返回增强 DataFrame（新增 polarity/method/keywords）。

        Parameters
        ----------
        df : 新闻 DataFrame，至少含 title_col 和 news_id_col
        title_col, content_col, news_id_col : 列名映射

        Returns
        -------
        DataFrame（新增列：polarity, method, keywords）
        """
        if df.empty:
            return df.copy()

        records: list[dict] = []
        for _, row in df.iterrows():
            title = str(row.get(title_col, ""))
            content = str(row.get(content_col, ""))
            nid = str(row.get(news_id_col, ""))

            if self._llm_scorer is not None:
                # LLM 扩展口——调用方注入的打分器
                try:
                    llm_result = self._llm_scorer(title, content)
                    polarity = getattr(llm_result, "score", 0.0)
                    method = "llm"
                    keywords = ()
                except Exception:  # noqa: BLE001
                    polarity = 0.0
                    method = "llm_fallback"
                    keywords = ()
            else:
                polarity, keywords = self._rule_scorer.score(title, content)
                method = "rule"

            records.append(
                {
                    "news_id": nid,
                    "title": title,
                    "polarity": round(polarity, 4),
                    "method": method,
                    "keywords": keywords,
                }
            )

        return pd.DataFrame(records)

    def analyze_date_range(
        self,
        start_date: str,
        end_date: str,
        **news_kwargs,
    ) -> tuple[pd.DataFrame, list[SentimentWindow], list[SentimentEvent]]:
        """一站式分析：查新闻 → 打分 → 聚合 → 事件检出。

        Parameters
        ----------
        start_date, end_date : YYYY-MM-DD
        news_kwargs : 透传给 collect_news 的额外参数（region/language/limit 等）

        Returns
        -------
        (scored_df, windows, events)
        """
        news_df = collect_news(start_date, end_date, **news_kwargs)
        scored_df = self.analyze_news_df(news_df)

        if scored_df.empty:
            return scored_df, [], []

        # 合并时间信息（从原始 news_df 关联 publish_time）
        merged = scored_df.merge(
            news_df[["news_id", "publish_time"]],
            on="news_id",
            how="left",
        )
        windows = self._aggregator.aggregate_from_df(merged)
        events = self._detect_events(windows)
        return scored_df, windows, events

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _detect_events(self, windows: list[SentimentWindow]) -> list[SentimentEvent]:
        """从窗口序列中检测 sentiment 突破事件。"""
        events: list[SentimentEvent] = []
        for i, w in enumerate(windows):
            if w.sentiment_index >= self._pos_thr:
                # 连续窗口不重复触发：若上一窗口也是 positive，则跳过（防抖）
                if i > 0 and windows[i - 1].sentiment_index >= self._pos_thr:
                    continue
                events.append(
                    SentimentEvent(
                        event_time=w.window_end,
                        event_type="positive_spike",
                        sentiment_index=w.sentiment_index,
                        trigger_news_count=w.news_count,
                        description=f"窗口 {w.window_start:%m-%d %H:%M}~{w.window_end:%H:%M} 情绪指数 {w.sentiment_index:.2f} 突破正向阈值",
                    )
                )
            elif w.sentiment_index <= self._neg_thr:
                if i > 0 and windows[i - 1].sentiment_index <= self._neg_thr:
                    continue
                events.append(
                    SentimentEvent(
                        event_time=w.window_end,
                        event_type="negative_spike",
                        sentiment_index=w.sentiment_index,
                        trigger_news_count=w.news_count,
                        description=f"窗口 {w.window_start:%m-%d %H:%M}~{w.window_end:%H:%M} 情绪指数 {w.sentiment_index:.2f} 突破负向阈值",
                    )
                )
        return events


# ============================================================================
# 7. 模块导出
# ============================================================================

__all__: Final = [
    "NewsSentimentAnalyzerError",
    "SentimentScore",
    "SentimentWindow",
    "SentimentEvent",
    "RuleBasedSentimentScorer",
    "SentimentAggregator",
    "NewsSentimentAnalyzer",
    "LLMSentimentScorer",
]
