# [BLUEPRINT] MOD-INT-AISA | docs/03_modules/_domain_intelligence/news_sentiment_analyzer/blueprint.md | §
# [MODULE] zephyr.intelligence.news_sentiment_analyzer
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] pandas; zephyr.data.news_collector; zephyr.nlp.nlp_inference; zephyr.data.ch_writer（persist_windows 钩子惰性导入，默认关）
# [CONSUMERS] MOD-SIG-002(信号生成器, 消费 SentimentEvent); zephyr.intelligence.nightly_sentiment_window(92号 §8.4 M3-② 夜间聚合)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 规则法情绪打分MVP桩，LLM打分走zephyr.nlp.nlp_inference扩展口（取polarity有向极性∈[-1,1]，禁用score强度∈[0,1]——neutral强度0.5会伪造正向）；ST风险警示大小写敏感词边界匹配（防英文普通词st子串误伤）；反转短语（终止重组/并购失败等）先扣除再匹配短词典（防"重组"正向误判负向公告）；聚合窗口默认1h整点对齐，空输入返回空结果不报错
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_intelligence/news_sentiment_analyzer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NewsSentimentAnalyzerError(ZA-IT-0003)
# [TESTS] tests/intelligence/test_news_sentiment_analyzer.py
# [A_module] module_id=MOD-INT-AISA | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-AISA-001 MVP 施工 + GLM 复审修复批

"""
MOD-INT-AISA NewsSentimentAnalyzer — A股舆情分析器MVP。

功能边界（MVP）：
- 数据消费：复用 news_collector 查询 fund_news_data 已有多源新闻
- 规则法情绪打分：基于关键词表的正负向匹配，产出 [-1, 1] 有向极性
- LLM 扩展口：预留 infer_llm_sentiment() 接口，调用方注入 nlp_inference
- 聚合器：按时间窗口（默认1h）聚合单条 sentiment → 窗口级 sentiment_index
- 事件信号：sentiment_index 突破阈值时产出 SentimentEvent（方向+强度+标的列表）

不建表、默认不持久化——sentiment 结果以内存态返回，由下游消费方决定是否落盘；
可选 persist_windows 钩子（92号 §8.4 / tracker #138，默认关）把 SentimentWindow
写 c1_market.news_sentiment_window（window_type='1h'，ReplacingMergeTree 同键替换幂等）。
"""

from __future__ import annotations

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
    """单条新闻的情绪得分（规则法或LLM法产出，公开数据契约）。"""

    news_id: str
    title: str
    polarity: float  # [-1, 1]，负=看空，正=看多，0=中性
    method: str  # "rule" | "llm" | "llm_fallback"
    keywords: tuple[str, ...] = field(default_factory=tuple)  # 规则法命中的关键词


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
# 收词纪律：不收互为子串的词（如"新高"已覆盖"创新高"，防同文本双计分）
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
        "大涨",
        "新高",
        "领涨",
        "强势",
        "中标",
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
        "终止上市",
        "债务违约",
        "质押违约",
        "信用评级下调",
        "大跌",
        "新低",
        "领跌",
        "暴跌",
        "闪崩",
        "爆仓",
    }
)

# 中文反转语境——动宾距离窗口正则（非固定子串：A 股公告"终止**重大资产**重组"
# 中间常插修饰语，固定短语匹配不到）。命中即计负向并从文本扣除命中段，
# 防"终止重大资产重组"命中正向词"重组"误判 +0.20 的语义反转。
# 距离窗口 12 字 + 标点截断（，。；、）防跨句误连。
_NEG_REVERSAL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:终止|停止|暂停)[^，。；、\s]{0,12}?(重组|并购|收购)"
    r"|(重组|并购|收购)(?:失败|告吹|未成|折戟)"
)


def _scan_reversal(text: str) -> tuple[set[str], str]:
    """扫描反转语境，返回 (负向标签集, 扣除命中段后的文本)。

    标签按分支归一化：前向（终止X）→ "终止重组/终止并购/终止收购"；
    后向（X失败）→ "重组失败/并购失败/收购失败"。
    """
    labels: set[str] = set()

    def _sub(m: re.Match[str]) -> str:
        forward_obj, backward_obj = m.group(1), m.group(2)
        if forward_obj:
            labels.add(f"终止{forward_obj}")
        elif backward_obj:
            labels.add(f"{backward_obj}失败")
        return " "

    stripped = _NEG_REVERSAL_PATTERN.sub(_sub, text)
    return labels, stripped


# ST 风险警示专用匹配——大小写敏感 + 词边界（仅大写 ST/*ST 是 A 股警示板标记，
# 小写 st 是英文普通词子串 steady/boost/first/best 的一部分，禁止命中）
_ST_PATTERN: Final[re.Pattern[str]] = re.compile(r"\*ST|(?<![A-Za-z])ST(?![A-Za-z])")

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
        - 标题命中每词 ±0.20，正文命中每词 ±0.08（标题信息密度高）
        - 反转短语（终止重组等）先扣除再匹配短词典，计负向
        - ST/*ST 风险警示：大小写敏感 + 词边界匹配，计负向
        - 同词去重（多次出现只算一次），封顶 ±0.90
        - 无匹配 → 0.0 中性
        """
        text = f"{title} {content}" if content else title
        title_work = title
        matched_neg: set[str] = set()

        # ① 反转语境（终止X/X失败）：命中即计负向并从文本扣除命中段
        rev_labels, text = _scan_reversal(text)
        _, title_work = _scan_reversal(title_work)
        matched_neg |= rev_labels

        # ② ST/*ST 风险警示：大小写敏感词边界（原始大小写文本上匹配）
        st_hits = set(_ST_PATTERN.findall(f"{title_work} {text}"))
        matched_neg |= st_hits

        # ③ 短词典匹配（扣除反转片段后的剩余文本）
        text_lower = text.lower()
        pos_hits = set(self._pos_pat.findall(text_lower))
        neg_hits = set(self._neg_pat.findall(text_lower))
        matched_neg |= neg_hits

        # 标题命中 vs 正文命中（关键词在标题中出现则权重更高）
        title_lower = title_work.lower()
        pos_in_title = {kw for kw in pos_hits if kw in title_lower}
        neg_in_title = {kw for kw in matched_neg if kw in title_lower}

        pos_score = len(pos_in_title) * 0.20 + (len(pos_hits) - len(pos_in_title)) * 0.08
        neg_score = len(neg_in_title) * 0.20 + (len(matched_neg) - len(neg_in_title)) * 0.08

        polarity = max(-0.90, min(0.90, pos_score - neg_score))
        matched = tuple(sorted(pos_hits | matched_neg))
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
                # LLM 扩展口——调用方注入的打分器。
                # 契约：取 polarity（有向极性 [-1,1]）而非 score（强度 [0,1]）——
                # nlp_inference.SentimentResult 语义：score 是强度（neutral=0.5），
                # 误用会把中性新闻伪装成 +0.5 正向（GLM 复审 P0-1 修复）
                try:
                    llm_result = self._llm_scorer(title, content)
                    polarity = float(getattr(llm_result, "polarity", 0.0))
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
        persist: bool = False,
        **news_kwargs,
    ) -> tuple[pd.DataFrame, list[SentimentWindow], list[SentimentEvent]]:
        """一站式分析：查新闻 → 打分 → 聚合 → 事件检出。

        Parameters
        ----------
        start_date, end_date : YYYY-MM-DD
        persist : True 时把聚合窗口写 news_sentiment_window 表（92号 §8.4 / tracker #138，
            默认关；写表异常降级不抛，日志留痕）
        news_kwargs : 透传给 collect_news 的额外参数（region/language/limit 等）

        Returns
        -------
        (scored_df, windows, events)
        """
        news_df = collect_news(start_date, end_date, **news_kwargs)
        scored_df = self.analyze_news_df(news_df)

        if scored_df.empty:
            return scored_df, [], []

        # 合并时间信息（从原始 news_df 关联 publish_time）。
        # news_data 为 SCD 多版本表（news_id 锚定修正稿）：打分逐条输出完整，
        # 聚合侧按 news_id 去重防窗口 news_count 膨胀；collect_news 按
        # publish_time 升序，keep="first" 取最早版本（PIT 语义）
        time_map = news_df[["news_id", "publish_time"]].drop_duplicates(subset="news_id", keep="first")
        merged = scored_df.merge(time_map, on="news_id", how="left").drop_duplicates(subset="news_id", keep="first")
        windows = self._aggregator.aggregate_from_df(merged)
        events = self._detect_events(windows)
        if persist:
            self.persist_windows(windows)
        return scored_df, windows, events

    def persist_windows(
        self,
        windows: list[SentimentWindow],
        *,
        data_source: str = "rule",
        writer: Callable[[object], bool] | None = None,
    ) -> bool:
        """持久化钩子：把 SentimentWindow 列表写 news_sentiment_window 表（默认不调用=关）。

        tracker #138 闭环（92号 §8.4）：window_type='1h'、scope='market'；
        ReplacingMergeTree(scope,symbol,window_type,window_ts) 同键替换 → 重跑幂等。

        Parameters
        ----------
        windows : SentimentWindow 列表（空列表直接返回 True 不写）
        data_source : 打分方法留痕（rule/llm/llm_fallback/mixed）
        writer : 写表函数注入（签名 FetchResult→bool；None=ch_writer.write_result）

        Returns
        -------
        是否写入成功；写表异常降级返回 False（fail-open 不抛）。
        """
        if not windows:
            return True
        try:
            from zephyr.data.provider_base import FetchResult

            rows = []
            for w in windows:
                pos_n = int(round(w.positive_ratio * w.news_count))
                neg_n = int(round(w.negative_ratio * w.news_count))
                neu_n = w.news_count - pos_n - neg_n
                rows.append(
                    (
                        w.window_start.strftime("%Y-%m-%d %H:%M:%S"),
                        w.window_end.strftime("%Y-%m-%d %H:%M:%S"),
                        "1h",
                        "market",
                        "",
                        w.sentiment_index,
                        w.avg_polarity,
                        pos_n,
                        neg_n,
                        neu_n,
                        w.news_count,
                        "",
                        data_source,
                    )
                )
            # 列序=DDL-as-Code 真源 schemas/categories/market_news_sentiment_window.py INSERT_COLUMNS
            insert_columns = (
                "(window_ts, window_end, window_type, scope, symbol, sentiment_index, avg_polarity, "
                "positive_count, negative_count, neutral_count, total_count, top_events_json, data_source)"
            )
            fetch = FetchResult(
                table="c1_market.news_sentiment_window",
                columns=[c.strip() for c in insert_columns.strip("()").split(",")],
                rows=rows,
                last_key="",
                elapsed_sec=0.0,
            )
            if writer is not None:
                return bool(writer(fetch))
            from zephyr.data import ch_writer

            return ch_writer.write_result(fetch, columns=insert_columns)
        except Exception as exc:  # noqa: BLE001 — 写表异常降级不抛（钩子默认关，开了也不炸主流程）
            import logging

            logging.getLogger(__name__).warning("persist_windows 写表异常，降级返回 False: %s", exc)
            return False

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
