# [BLUEPRINT] MOD-ALT-001 | docs/03_modules/_domain_alt_data/social_sentiment_collector/blueprint.md
# [MODULE] zephyr.alt_data.social_sentiment_collector
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors（判定核心纯内存；fetcher/scorer/sink 全注入）
# [CONSUMERS] 运行时装配批（fetcher 接股吧/雪球页面抓取 / scorer 接 news_sentiment_analyzer·nlp_inference·LLM 池 / sink 接 ch_writer 落 ClickHouse）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 判定核心纯内存无IO；fetcher/scorer 非callable构造即Fail-Closed；单帖非法Fail-Closed到条；PIT严格（publish_time<=trade_date 23:59:59）；scorer输出越界/NaN/异常→unscored留痕不出伪情感分；sink异常不阻断；frozen dataclass asdict JSON可序列化；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/social_sentiment_collector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetcher/scorer/sink非callable→InvalidCollectorConfigError；trade_date/symbols非法→ValueError；SocialPost字段空白→InvalidSocialPostError；fetcher/scorer/sink运行期异常→errors留痕不阻断
# [TESTS] tests/alt_data/test_social_sentiment_collector.py
# [A_module] module_id=MOD-ALT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SocialSentimentCollector — 社媒情绪采集器（MOD-ALT-001）

B10-01341（AUD-DRAFT-001-DIGEST P1 波 W-P1-15，A1 §2.1）：帖子级社媒文本
（股吧/雪球，fetcher 注入）→ 标准化 SocialPost → 情感打分（scorer 注入委托
news_sentiment_analyzer / nlp_inference / LLM 池，本模块不内嵌打分引擎）→
按 (trade_date, symbol) 日频聚合（sentiment_mean / engagement 加权 / 正压比）
→ SocialSentimentDaily，落账 sink 委托（装配批接 ch_writer 落 ClickHouse）。

查重裁定：akshare_provider stock_hot_rank（MOD-L00-004）为东财人气/关注
**数值榜单**日快照（已接线）；本模块做**帖子级文本情绪**，不重复。B10-01842
（§29.12）①社媒情绪面归并本模块；B13-04069（A3 情绪面板族）归并见 fragment。
LLM 解读面归 llm_market_interpreter（MOD-INT-MKT-INTERPRETER），本模块只产
日频聚合行，仅信号输入语义无下单含义。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass, field
from typing import Callable, Final, Iterable, Optional, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__: Final = [
    "CollectReport",
    "InvalidCollectorConfigError",
    "InvalidSocialPostError",
    "SocialPost",
    "SocialSentimentCollector",
    "SocialSentimentDaily",
]


# ============================================================================
# 1. 错误契约
# ============================================================================


class InvalidSocialPostError(ZephyrBaseError):
    """帖子字段非法（空白 post_id/symbol/text、时间非法）。"""


class InvalidCollectorConfigError(ZephyrBaseError):
    """采集器配置非法（fetcher/scorer/sink 非 callable）。"""


# ============================================================================
# 2. 数据模型
# ============================================================================


@dataclass(frozen=True)
class SocialPost:
    """标准化社媒帖。likes/comments/reads 为 engagement 计数（非负）。"""

    post_id: str
    symbol: str
    publish_time: datetime.datetime
    text: str
    source: str
    likes: int = 0
    comments: int = 0
    reads: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.post_id, str) or not self.post_id.strip():
            raise InvalidSocialPostError("post_id 空白")
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise InvalidSocialPostError("symbol 空白")
        if not isinstance(self.text, str) or not self.text.strip():
            raise InvalidSocialPostError("text 空白")
        if not isinstance(self.publish_time, datetime.datetime):
            raise InvalidSocialPostError("publish_time 非 datetime")


@dataclass(frozen=True)
class SocialSentimentDaily:
    """(trade_date, symbol) 日频情绪聚合行。scored_count=0 时三个分数字段为 None。"""

    trade_date: str
    symbol: str
    post_count: int
    scored_count: int
    sentiment_mean: Optional[float]
    engagement_weighted_mean: Optional[float]
    positive_ratio: Optional[float]
    sources: tuple[str, ...]


@dataclass(frozen=True)
class CollectReport:
    """采集报告。dailies 按 symbol 升序；errors 为留痕文本元组。"""

    trade_date: str
    fetched: int
    accepted: int
    rejected: int
    unscored: int
    dailies: tuple[SocialSentimentDaily, ...]
    errors: tuple[str, ...] = field(default_factory=tuple)
    sink_attempted: bool = False
    sink_ok: bool = True


# ============================================================================
# 3. 采集器
# ============================================================================


class SocialSentimentCollector:
    """帖子级社媒情绪日频采集器（判定核心纯内存，IO 全注入）。

    Args:
        fetcher: (trade_date: str, symbols: list[str]) -> Iterable[SocialPost|dict]
        scorer: (text: str) -> float，输出须 ∈ [-1, 1]
        sink: 可选，(tuple[SocialSentimentDaily, ...]) -> None
        max_posts: 单批帖子数硬顶（防爆量，默认 20000）
    """

    def __init__(
        self,
        fetcher: Callable[[str, Sequence[str]], Iterable],
        scorer: Callable[[str], float],
        sink: Optional[Callable[[tuple[SocialSentimentDaily, ...]], None]] = None,
        *,
        max_posts: int = 20000,
    ) -> None:
        if not callable(fetcher):
            raise InvalidCollectorConfigError("fetcher 非 callable")
        if not callable(scorer):
            raise InvalidCollectorConfigError("scorer 非 callable")
        if sink is not None and not callable(sink):
            raise InvalidCollectorConfigError("sink 非 callable")
        if not isinstance(max_posts, int) or max_posts < 1:
            raise InvalidCollectorConfigError("max_posts 须为正整数")
        self._fetcher = fetcher
        self._scorer = scorer
        self._sink = sink
        self._max_posts = max_posts

    # ------------------------------------------------------------------
    # 主流程
    # ------------------------------------------------------------------

    def collect(self, trade_date: str, symbols: Sequence[str]) -> CollectReport:
        day_end = self._parse_trade_date(trade_date)
        if not symbols or any(not isinstance(s, str) or not s.strip() for s in symbols):
            raise ValueError("symbols 须为非空字符串序列")

        errors: list[str] = []
        raw = self._fetch(trade_date, symbols, errors)
        accepted: list[SocialPost] = []
        rejected = 0
        for item in raw[: self._max_posts]:
            post = self._coerce(item)
            if post is None or post.publish_time > day_end:  # 非法条 + PIT 未来帖
                rejected += 1
                continue
            accepted.append(post)
        if len(raw) > self._max_posts:
            rejected += len(raw) - self._max_posts
            errors.append(f"max_posts 截断: {len(raw) - self._max_posts} 条拒收")

        scored: dict[str, list[tuple[float, int]]] = {}
        counts: dict[str, int] = {}
        sources: dict[str, set[str]] = {}
        unscored = 0
        for post in accepted:
            counts[post.symbol] = counts.get(post.symbol, 0) + 1
            sources.setdefault(post.symbol, set()).add(post.source)
            polarity = self._score(post.text, errors)
            if polarity is None:
                unscored += 1
                continue
            weight = 1 + max(post.likes, 0) + max(post.comments, 0) + max(post.reads, 0)
            scored.setdefault(post.symbol, []).append((polarity, weight))

        dailies = tuple(
            self._aggregate(trade_date, symbol, counts[symbol], scored.get(symbol, []), sources[symbol])
            for symbol in sorted(counts)
        )
        sink_attempted, sink_ok = self._emit(dailies, errors)
        return CollectReport(
            trade_date=trade_date,
            fetched=len(raw),
            accepted=len(accepted),
            rejected=rejected,
            unscored=unscored,
            dailies=dailies,
            errors=tuple(errors),
            sink_attempted=sink_attempted,
            sink_ok=sink_ok,
        )

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_trade_date(trade_date: str) -> datetime.datetime:
        if not isinstance(trade_date, str):
            raise ValueError("trade_date 须为 YYYY-MM-DD 字符串")
        try:
            day = datetime.datetime.strptime(trade_date, "%Y-%m-%d")
        except (TypeError, ValueError):
            raise ValueError(f"trade_date 非法: {trade_date!r}") from None
        return day.replace(hour=23, minute=59, second=59)

    def _fetch(self, trade_date: str, symbols: Sequence[str], errors: list[str]) -> list:
        try:
            return list(self._fetcher(trade_date, list(symbols)) or [])
        except Exception as exc:  # noqa: BLE001 - 单批抓取失败容错为空批
            log.warning("social sentiment fetch failed: %s", exc)
            errors.append(f"fetcher 异常: {exc}")
            return []

    @staticmethod
    def _coerce(item) -> Optional[SocialPost]:
        try:
            if isinstance(item, SocialPost):
                return item
            if isinstance(item, dict):
                return SocialPost(
                    post_id=item.get("post_id", ""),
                    symbol=item.get("symbol", ""),
                    publish_time=item.get("publish_time"),
                    text=item.get("text", ""),
                    source=item.get("source", "unknown"),
                    likes=int(item.get("likes", 0) or 0),
                    comments=int(item.get("comments", 0) or 0),
                    reads=int(item.get("reads", 0) or 0),
                )
        except (InvalidSocialPostError, TypeError, ValueError):
            return None
        return None

    def _score(self, text: str, errors: list[str]) -> Optional[float]:
        try:
            value = float(self._scorer(text))
        except Exception as exc:  # noqa: BLE001 - scorer 异常不出伪情感分
            log.warning("social sentiment scorer failed: %s", exc)
            errors.append(f"scorer 异常: {exc}")
            return None
        if math.isnan(value) or value < -1.0 or value > 1.0:
            errors.append(f"scorer 输出越界/NaN: {value}")
            return None
        return value

    @staticmethod
    def _aggregate(
        trade_date: str,
        symbol: str,
        post_count: int,
        scored: list[tuple[float, int]],
        sources: set[str],
    ) -> SocialSentimentDaily:
        if not scored:
            return SocialSentimentDaily(
                trade_date=trade_date,
                symbol=symbol,
                post_count=post_count,
                scored_count=0,
                sentiment_mean=None,
                engagement_weighted_mean=None,
                positive_ratio=None,
                sources=tuple(sorted(sources)),
            )
        total_w = sum(w for _, w in scored)
        mean = sum(p for p, _ in scored) / len(scored)
        weighted = sum(p * w for p, w in scored) / total_w
        positive = sum(1 for p, _ in scored if p > 0) / len(scored)
        return SocialSentimentDaily(
            trade_date=trade_date,
            symbol=symbol,
            post_count=post_count,
            scored_count=len(scored),
            sentiment_mean=mean,
            engagement_weighted_mean=weighted,
            positive_ratio=positive,
            sources=tuple(sorted(sources)),
        )

    def _emit(self, dailies: tuple[SocialSentimentDaily, ...], errors: list[str]) -> tuple[bool, bool]:
        if self._sink is None:
            return False, True
        try:
            self._sink(dailies)
            return True, True
        except Exception as exc:  # noqa: BLE001 - sink 异常不阻断判定
            log.warning("social sentiment sink failed: %s", exc)
            errors.append(f"sink 异常: {exc}")
            return True, False
