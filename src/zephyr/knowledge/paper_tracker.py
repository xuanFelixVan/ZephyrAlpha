# [BLUEPRINT] MOD-KNW-013 | docs/03_modules/_domain_knowledge/paper_tracker/blueprint.md
# [MODULE] zephyr.knowledge.paper_tracker
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（协议核心纯内存；arxiv_fetcher/summarizer/hypothesis_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（主题订阅注册 / arXiv 抓取适配器绑定 / 假设提取对接）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 主题订阅注册表唯一(topic_id); arXiv API 调用全注入不真发; DOI/标题规范化指纹去重全局唯一; 摘要经注入本地LLM(未注入留空); 关键词趋势滚动窗确定性统计(文档频次); 假设对接仅经注入sink上报候选词不实现抽取; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/paper_tracker/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PaperTrackerError(占位 ZA-KNW-UNREGISTERED-PAPER-TRACKER)——空topic_id/重复订阅/未知topic/抓取器未注入/抓取异常/未知paper/非法趋势窗参数时抛
# [TESTS] tests/knowledge/test_paper_tracker.py
# [A_module] module_id=MOD-KNW-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""PaperTracker — 论文追踪器（MOD-KNW-013）。

B6-08549（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-016，B6 D-RESEARCH-07）：
Zotero 式论文追踪——arXiv API 按主题订阅（API 调用全注入不真发）+
标题/DOI 去重（规范化指纹）+ 本地 LLM 摘要（注入摘要器）+
关键词频次趋势检测（滚动窗统计）+ 与假设提取对接（注入 hypothesis_sink）。

查重分工（蓝图 §0）：kb_engine=知识库通用 CRUD/FTS（本件不做条目持久化）；
knowledge_quality_assessor=条目质量四维评分（零交集）；rag_pipeline=问答
管道（本件产出 PaperRecord 可供其 ingest，不实现检索）；假设实体注册归
hypothesis_registry（本件仅经注入 sink 上报候选词，不新建假设实体）。
"""

from __future__ import annotations

import datetime
import hashlib
import logging
import re
from collections import Counter, deque
from dataclasses import dataclass
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "FetchReport",
    "KeywordTrend",
    "PaperRecord",
    "PaperTracker",
    "PaperTrackerError",
    "Subscription",
]

#: 注入抓取器返回的原始条目键约定（Mapping）：
#:   title(str, 必填) / authors(Sequence[str]) / doi(str) / arxiv_id(str)
#:   published_at(datetime) / abstract(str)
_TITLE_TOKEN_RE: Final = re.compile(r"\w+")
_KEYWORD_RE: Final = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_DOI_PREFIXES: Final = ("https://doi.org/", "http://doi.org/", "doi:")
_MIN_KEYWORD_LEN: Final = 4
_STOPWORDS: Final = frozenset({
    "about", "against", "based", "been", "between", "could", "from",
    "have", "into", "should", "that", "their", "there", "this",
    "through", "under", "using", "were", "when", "where", "which",
    "will", "with", "would",
})


class PaperTrackerError(Exception):
    """论文追踪输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-PAPER-TRACKER。
    """


@dataclass(frozen=True)
class Subscription:
    """主题订阅（arXiv 查询载体，frozen）。"""

    topic_id: str
    query: str
    max_results: int = 50
    active: bool = True


@dataclass(frozen=True)
class PaperRecord:
    """论文条目（去重后入库载体，frozen）。"""

    paper_id: str
    topic_id: str
    title: str
    authors: tuple[str, ...]
    doi: str | None
    arxiv_id: str | None
    published_at: datetime.datetime | None
    fetched_at: datetime.datetime
    summary: str


@dataclass(frozen=True)
class FetchReport:
    """单次抓取报告（frozen）。"""

    topic_id: str
    fetched_count: int
    new_count: int
    duplicate_count: int
    skipped_count: int


@dataclass(frozen=True)
class KeywordTrend:
    """关键词滚动窗趋势（文档频次，frozen）。"""

    keyword: str
    recent_count: int
    older_count: int
    rising: bool


def _normalize_doi(doi: object) -> str | None:
    """DOI 规范化：去空白/小写/剥 URL 与 doi: 前缀；空 → None。"""
    if not isinstance(doi, str):
        return None
    text = doi.strip().lower()
    for prefix in _DOI_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):]
    return text or None


def _title_fingerprint(title: str) -> str:
    """标题规范化指纹：小写 + 去全部非词字符（标点/空白不敏感）。"""
    return "".join(_TITLE_TOKEN_RE.findall(title.lower()))


def _extract_keywords(text: str) -> tuple[str, ...]:
    """关键词抽取：小写词元，长度≥4 且非停用词，确定性排序去重。"""
    words = _KEYWORD_RE.findall(text.lower())
    return tuple(sorted({w for w in words if len(w) >= _MIN_KEYWORD_LEN and w not in _STOPWORDS}))


class PaperTracker:
    """论文追踪器（订阅注册表 + 注入抓取 + 指纹去重 + 趋势 + 假设对接）。"""

    def __init__(
        self,
        *,
        arxiv_fetcher: Callable[[Subscription], Sequence[Mapping[str, object]]] | None = None,
        summarizer: Callable[[str, str], str] | None = None,
        hypothesis_sink: Callable[[str, tuple[str, ...]], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        trend_window: int = 200,
        trend_recent: int = 20,
        trend_min_count: int = 3,
        trend_growth: float = 2.0,
    ) -> None:
        if trend_window <= 0:
            raise PaperTrackerError(f"trend_window 非法: {trend_window}（须 > 0）")
        if trend_recent <= 0 or trend_recent > trend_window:
            raise PaperTrackerError(
                f"trend_recent 非法: {trend_recent}（须 0 < recent <= window={trend_window}）"
            )
        if trend_min_count <= 0:
            raise PaperTrackerError(f"trend_min_count 非法: {trend_min_count}（须 > 0）")
        if trend_growth <= 0:
            raise PaperTrackerError(f"trend_growth 非法: {trend_growth}（须 > 0）")
        self._arxiv_fetcher = arxiv_fetcher
        self._summarizer = summarizer
        self._sink = hypothesis_sink
        self._clock = clock or datetime.datetime.now
        self._trend_recent = trend_recent
        self._trend_min_count = trend_min_count
        self._trend_growth = trend_growth
        self._subs: dict[str, Subscription] = {}
        self._papers: dict[str, PaperRecord] = {}
        self._fp_index: dict[str, str] = {}     # 标题指纹 -> paper_id
        self._doi_index: dict[str, str] = {}    # 规范化 DOI -> paper_id
        self._arxiv_index: dict[str, str] = {}  # arXiv id -> paper_id
        # 滚动窗：每篇入库论文的关键词集合（文档频次统计用）
        self._history: deque[tuple[str, ...]] = deque(maxlen=trend_window)

    # ── 主题订阅注册表 ────────────────────────────────────────────────────

    def subscribe(self, subscription: Subscription) -> None:
        """登记主题订阅：topic_id 唯一；空 id/query/非法 max_results → Fail-Closed。"""
        if not subscription.topic_id:
            raise PaperTrackerError("topic_id 为空")
        if not subscription.query:
            raise PaperTrackerError(f"query 为空: topic {subscription.topic_id!r}")
        if subscription.max_results <= 0:
            raise PaperTrackerError(
                f"max_results 非法: {subscription.max_results}（须 > 0）"
            )
        if subscription.topic_id in self._subs:
            raise PaperTrackerError(f"重复订阅: {subscription.topic_id!r}")
        self._subs[subscription.topic_id] = subscription

    def unsubscribe(self, topic_id: str) -> None:
        """注销主题订阅（未知 → Fail-Closed；已入库论文保留）。"""
        if topic_id not in self._subs:
            raise PaperTrackerError(f"未知 topic: {topic_id!r}")
        del self._subs[topic_id]

    def list_subscriptions(self) -> tuple[Subscription, ...]:
        """订阅列表（按 topic_id 确定性排序）。"""
        return tuple(self._subs[tid] for tid in sorted(self._subs))

    # ── 抓取与去重入库 ────────────────────────────────────────────────────

    def _paper_id_of(self, doi: str | None, arxiv_id: str | None, fingerprint: str) -> str:
        if doi:
            return f"doi:{doi}"
        if arxiv_id:
            return f"arxiv:{arxiv_id}"
        digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]
        return f"t:{digest}"

    def _summarize(self, title: str, abstract: str) -> str:
        if self._summarizer is None:
            return ""
        try:
            return str(self._summarizer(title, abstract))
        except Exception:  # noqa: BLE001 — 摘要失败不阻断入库
            _log.exception("summarizer 摘要失败: %s", title)
            return ""

    def _ingest(self, topic_id: str, raw: Mapping[str, object]) -> str:
        """单条入库：返回 new/duplicate/skipped。指纹优先级 DOI > arXiv > 标题。"""
        title_obj = raw.get("title")
        title = str(title_obj).strip() if title_obj is not None else ""
        if not title:
            return "skipped"
        doi = _normalize_doi(raw.get("doi"))
        arxiv_raw = raw.get("arxiv_id")
        arxiv_id = str(arxiv_raw).strip() if arxiv_raw is not None else ""
        arxiv_id = arxiv_id or None
        fingerprint = _title_fingerprint(title)
        if not fingerprint:
            return "skipped"
        if (doi and doi in self._doi_index) or (
            arxiv_id and arxiv_id in self._arxiv_index
        ) or fingerprint in self._fp_index:
            return "duplicate"

        authors_obj = raw.get("authors") or ()
        authors = tuple(str(a) for a in authors_obj)  # type: ignore[union-attr]
        published_obj = raw.get("published_at")
        published_at = published_obj if isinstance(published_obj, datetime.datetime) else None
        abstract_obj = raw.get("abstract")
        abstract = str(abstract_obj) if abstract_obj is not None else ""
        summary = self._summarize(title, abstract)
        paper_id = self._paper_id_of(doi, arxiv_id, fingerprint)
        record = PaperRecord(
            paper_id=paper_id,
            topic_id=topic_id,
            title=title,
            authors=authors,
            doi=doi,
            arxiv_id=arxiv_id,
            published_at=published_at,
            fetched_at=self._clock(),
            summary=summary,
        )
        self._papers[paper_id] = record
        self._fp_index[fingerprint] = paper_id
        if doi:
            self._doi_index[doi] = paper_id
        if arxiv_id:
            self._arxiv_index[arxiv_id] = paper_id
        keywords = _extract_keywords(f"{title} {summary}")
        self._history.append(keywords)
        self._emit_hypothesis(paper_id, keywords)
        return "new"

    def _emit_hypothesis(self, paper_id: str, keywords: tuple[str, ...]) -> None:
        """假设对接：当前处于 rising 态的本文关键词上报注入 sink（不新建假设）。"""
        if self._sink is None or not keywords:
            return
        rising = {t.keyword for t in self.keyword_trends() if t.rising}
        terms = tuple(k for k in keywords if k in rising)
        if not terms:
            return
        try:
            self._sink(paper_id, terms)
        except Exception:  # noqa: BLE001 — sink 异常不阻断入库
            _log.exception("hypothesis_sink 上报失败: %s", paper_id)

    def fetch_topic(self, topic_id: str) -> FetchReport:
        """按主题抓取：订阅须已登记；抓取器未注入 → Fail-Closed 不旁路。"""
        subscription = self._subs.get(topic_id)
        if subscription is None:
            raise PaperTrackerError(f"未知 topic: {topic_id!r}（未订阅）")
        if self._arxiv_fetcher is None:
            raise PaperTrackerError("arxiv_fetcher 未注入（API 调用全注入，禁止真发）")
        try:
            raw_list = list(self._arxiv_fetcher(subscription))
        except Exception as exc:  # noqa: BLE001 — 抓取异常统一收口 Fail-Closed
            _log.exception("arXiv 抓取异常: %s", topic_id)
            raise PaperTrackerError(f"arXiv 抓取失败: {topic_id!r}: {exc}") from exc
        new = duplicate = skipped = 0
        for raw in raw_list:
            if not isinstance(raw, Mapping):
                skipped += 1
                continue
            outcome = self._ingest(topic_id, raw)
            if outcome == "new":
                new += 1
            elif outcome == "duplicate":
                duplicate += 1
            else:
                skipped += 1
        return FetchReport(
            topic_id=topic_id,
            fetched_count=len(raw_list),
            new_count=new,
            duplicate_count=duplicate,
            skipped_count=skipped,
        )

    def fetch_all(self) -> tuple[FetchReport, ...]:
        """全量抓取：仅 active 订阅，按 topic_id 确定性顺序。"""
        return tuple(
            self.fetch_topic(tid)
            for tid in sorted(self._subs)
            if self._subs[tid].active
        )

    # ── 关键词趋势（滚动窗文档频次） ───────────────────────────────────────

    def keyword_trends(self) -> tuple[KeywordTrend, ...]:
        """滚动窗趋势：recent 段 vs older 段文档频次；按关键词确定性排序。"""
        history = list(self._history)
        recent = history[-self._trend_recent:]
        older = history[:-self._trend_recent]
        recent_counts: Counter[str] = Counter()
        older_counts: Counter[str] = Counter()
        for keywords in recent:
            recent_counts.update(keywords)
        for keywords in older:
            older_counts.update(keywords)
        trends = []
        for keyword in sorted(set(recent_counts) | set(older_counts)):
            recent_count = recent_counts.get(keyword, 0)
            older_count = older_counts.get(keyword, 0)
            rising = (
                recent_count >= self._trend_min_count
                and recent_count > older_count * self._trend_growth
            )
            trends.append(KeywordTrend(
                keyword=keyword,
                recent_count=recent_count,
                older_count=older_count,
                rising=rising,
            ))
        return tuple(trends)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get_paper(self, paper_id: str) -> PaperRecord:
        """单条查询（未知 → Fail-Closed）。"""
        record = self._papers.get(paper_id)
        if record is None:
            raise PaperTrackerError(f"未知 paper: {paper_id!r}")
        return record

    def list_papers(self, topic_id: str | None = None) -> tuple[PaperRecord, ...]:
        """论文列表（可按主题过滤；按 (fetched_at, paper_id) 确定性排序）。"""
        records = [
            r for r in self._papers.values()
            if topic_id is None or r.topic_id == topic_id
        ]
        records.sort(key=lambda r: (r.fetched_at, r.paper_id))
        return tuple(records)
