# [BLUEPRINT] MOD-ALT-002 | docs/03_modules/_domain_alt_data/web_scraper_engine/blueprint.md
# [MODULE] zephyr.alt_data.web_scraper_engine
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors（判定核心纯内存；fetcher/seen/sink 全注入）
# [CONSUMERS] 运行时装配批（fetcher 接 requests/playwright 抓取层 / seen 接 news_dedup 库窗口 / sink 接 ch_writer 落 ClickHouse / 调度挂 D_DATA scheduler）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 判定核心纯内存无IO；目标非法/重复/未知提取器/域外登记期Fail-Closed；限速按域名最小间隔台账且仅抓取成功才更新；单目标异常不阻断批次；seen异常fail-open留痕（对齐news_dedup）；sink异常不阻断；frozen dataclass asdict JSON可序列化；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/web_scraper_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 目标非法/重复/域外→InvalidScrapeTargetError；未知提取器→UnknownExtractorError；fetcher/extractors/seen/sink/max_records配置非法→InvalidScraperConfigError；fetcher/seen/sink运行期异常→errors留痕不阻断
# [TESTS] tests/alt_data/test_web_scraper_engine.py
# [A_module] module_id=MOD-ALT-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""WebScraperEngine — 网页爬取引擎（MOD-ALT-002）

B10-02195（AUD-DRAFT-001-DIGEST P1 波 W-P1-15，D-ALT-DATA-03 §30.2.4）：
**无 API 页面定向爬取通用核心**——目标登记（URL/域名/提取器/限速）→ 合规
限速判定（按域名最小间隔内存台账，纯函数）→ fetcher 注入抓取 → 规则提取器
（内置 html_text + 自定义注入注册表）→ 去重（批内内容哈希 + seen 注入委托
news_dedup 窗口口径）→ ScrapedRecord，落账 sink 委托（装配批接 ch_writer 落
ClickHouse），调度面挂 D_DATA scheduler（装配批接线）。

查重裁定：rss_provider / eastmoney_news_provider / cls_provider /
announcement_provider（均 MOD-L00-004）为 **API/RSS 结构化源** source-specific
provider；news_collector（MOD-DATA-NEWS-001）为库内读取面。本模块承接无 API
页面（雪球热帖页/股吧列表页等）定向爬取，不复制任何具体源 provider 逻辑与
news_dedup 窗口查询。
"""

from __future__ import annotations

import datetime
import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Callable, Final, Iterable, Optional, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__: Final = [
    "InvalidScrapeTargetError",
    "InvalidScraperConfigError",
    "ScrapeReport",
    "ScrapeTarget",
    "ScrapedRecord",
    "UnknownExtractorError",
    "WebScraperEngine",
]

_TAG_RE: Final = re.compile(r"<[^>]+>")
_WS_RE: Final = re.compile(r"\s+")


# ============================================================================
# 1. 错误契约
# ============================================================================


class InvalidScrapeTargetError(ZephyrBaseError):
    """抓取目标非法（空白字段/负间隔/重复登记/域外/未知目标 id）。"""


class UnknownExtractorError(ZephyrBaseError):
    """目标引用了未注册的提取器。"""


class InvalidScraperConfigError(ZephyrBaseError):
    """引擎配置非法（fetcher/extractors/seen/sink/max_records 非 callable 或非正）。"""


# ============================================================================
# 2. 数据模型
# ============================================================================


@dataclass(frozen=True)
class ScrapeTarget:
    """定向抓取目标。min_interval_seconds 为按域名的最小抓取间隔。"""

    target_id: str
    url: str
    domain: str
    extractor: str
    min_interval_seconds: int = 3600


@dataclass(frozen=True)
class ScrapedRecord:
    """结构化抓取记录。content_hash=MD5(title+content) 供去重与落库幂等。"""

    target_id: str
    record_id: str
    title: str
    content: str
    publish_time: Optional[str]
    url: str
    content_hash: str


@dataclass(frozen=True)
class ScrapeReport:
    """抓取批次报告。records 按 (target_id, record_id) 升序。"""

    targets_visited: int
    fetched: int
    extracted: int
    invalid: int
    dedup_dropped: int
    skipped_throttle: int
    records: tuple[ScrapedRecord, ...]
    errors: tuple[str, ...] = field(default_factory=tuple)
    sink_attempted: bool = False
    sink_ok: bool = True


# ============================================================================
# 3. 内置提取器
# ============================================================================


def _extract_html_text(content: str) -> Iterable[dict]:
    """去标签+空白规整，非空时产单条文本记录（record_id=内容哈希）。"""
    text = _WS_RE.sub(" ", _TAG_RE.sub(" ", content)).strip()
    if not text:
        return
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    yield {"record_id": digest, "title": text[:80], "content": text}


_BUILTIN_EXTRACTORS: Final = {"html_text": _extract_html_text}


# ============================================================================
# 4. 引擎
# ============================================================================


class WebScraperEngine:
    """无 API 页面定向爬取引擎（判定核心纯内存，IO 全注入）。

    Args:
        fetcher: (url: str) -> str，返回页面 html/text
        extractors: 自定义提取器注册表 name -> callable(content) -> Iterable[dict|ScrapedRecord]
        seen: 可选，(content_hash: str) -> bool，True=已入库应去重（委托 news_dedup 窗口）
        sink: 可选，(tuple[ScrapedRecord, ...]) -> None
        allowed_domains: 可选域名允许清单（配置后域外目标登记 Fail-Closed）
        max_records_per_target: 单目标单批记录硬顶（默认 200）
    """

    def __init__(
        self,
        fetcher: Callable[[str], str],
        *,
        extractors: Optional[dict[str, Callable[[str], Iterable]]] = None,
        seen: Optional[Callable[[str], bool]] = None,
        sink: Optional[Callable[[tuple[ScrapedRecord, ...]], None]] = None,
        allowed_domains: Optional[Sequence[str]] = None,
        max_records_per_target: int = 200,
    ) -> None:
        if not callable(fetcher):
            raise InvalidScraperConfigError("fetcher 非 callable")
        if extractors is not None and any(not callable(fn) for fn in extractors.values()):
            raise InvalidScraperConfigError("extractors 含非 callable")
        if seen is not None and not callable(seen):
            raise InvalidScraperConfigError("seen 非 callable")
        if sink is not None and not callable(sink):
            raise InvalidScraperConfigError("sink 非 callable")
        if not isinstance(max_records_per_target, int) or max_records_per_target < 1:
            raise InvalidScraperConfigError("max_records_per_target 须为正整数")
        self._fetcher = fetcher
        self._extractors = {**_BUILTIN_EXTRACTORS, **(extractors or {})}
        self._seen = seen
        self._sink = sink
        self._allowed_domains = frozenset(allowed_domains) if allowed_domains else None
        self._max_records = max_records_per_target
        self._targets: dict[str, ScrapeTarget] = {}
        self._last_fetch: dict[str, datetime.datetime] = {}  # domain -> 上次成功抓取时刻

    # ------------------------------------------------------------------
    # 登记与限速
    # ------------------------------------------------------------------

    def register_target(self, target: ScrapeTarget) -> None:
        if not isinstance(target, ScrapeTarget):
            raise InvalidScrapeTargetError("target 非 ScrapeTarget")
        if not target.target_id.strip() or not target.url.strip() or not target.domain.strip():
            raise InvalidScrapeTargetError("target_id/url/domain 空白")
        if not isinstance(target.min_interval_seconds, int) or target.min_interval_seconds < 0:
            raise InvalidScrapeTargetError("min_interval_seconds 须为非负整数")
        if target.target_id in self._targets:
            raise InvalidScrapeTargetError(f"target_id 重复登记: {target.target_id}")
        if target.extractor not in self._extractors:
            raise UnknownExtractorError(f"未知提取器: {target.extractor}")
        if self._allowed_domains is not None and target.domain not in self._allowed_domains:
            raise InvalidScrapeTargetError(f"域外目标: {target.domain}")
        self._targets[target.target_id] = target

    def can_fetch(self, target_id: str, now: datetime.datetime) -> bool:
        target = self._targets.get(target_id)
        if target is None:
            raise InvalidScrapeTargetError(f"未知目标: {target_id}")
        last = self._last_fetch.get(target.domain)
        if last is None:
            return True
        return (now - last).total_seconds() >= target.min_interval_seconds

    # ------------------------------------------------------------------
    # 主流程
    # ------------------------------------------------------------------

    def scrape(
        self,
        now: datetime.datetime,
        target_ids: Optional[Sequence[str]] = None,
    ) -> ScrapeReport:
        ids = list(target_ids) if target_ids is not None else sorted(self._targets)
        unknown = [i for i in ids if i not in self._targets]
        if unknown:
            raise InvalidScrapeTargetError(f"未知目标: {unknown}")

        errors: list[str] = []
        fetched = extracted = invalid = dedup_dropped = skipped = 0
        kept: list[ScrapedRecord] = []
        batch_hashes: set[str] = set()

        for target_id in ids:
            target = self._targets[target_id]
            if not self.can_fetch(target_id, now):
                skipped += 1
                continue
            content = self._fetch(target, errors)
            if content is None:
                continue
            fetched += 1
            self._last_fetch[target.domain] = now  # 仅成功才更新台账
            for record in self._extract(target, content, errors):
                if record is None:
                    invalid += 1
                    continue
                extracted += 1
                if record.content_hash in batch_hashes or self._is_seen(record.content_hash, errors):
                    dedup_dropped += 1
                    continue
                batch_hashes.add(record.content_hash)
                kept.append(record)

        records = tuple(sorted(kept, key=lambda r: (r.target_id, r.record_id)))
        sink_attempted, sink_ok = self._emit(records, errors)
        return ScrapeReport(
            targets_visited=len(ids),
            fetched=fetched,
            extracted=extracted,
            invalid=invalid,
            dedup_dropped=dedup_dropped,
            skipped_throttle=skipped,
            records=records,
            errors=tuple(errors),
            sink_attempted=sink_attempted,
            sink_ok=sink_ok,
        )

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _fetch(self, target: ScrapeTarget, errors: list[str]) -> Optional[str]:
        try:
            content = self._fetcher(target.url)
        except Exception as exc:  # noqa: BLE001 - 单目标失败不阻断批次
            log.warning("scrape fetch failed: %s (%s)", target.target_id, exc)
            errors.append(f"fetcher 异常[{target.target_id}]: {exc}")
            return None
        if not isinstance(content, str):
            errors.append(f"fetcher 返回非 str[{target.target_id}]")
            return None
        return content

    def _extract(self, target: ScrapeTarget, content: str, errors: list[str]) -> Iterable[Optional[ScrapedRecord]]:
        extractor = self._extractors[target.extractor]
        try:
            items = list(extractor(content) or [])
        except Exception as exc:  # noqa: BLE001 - 提取异常按空批容错
            log.warning("scrape extract failed: %s (%s)", target.target_id, exc)
            errors.append(f"extractor 异常[{target.target_id}]: {exc}")
            return
        count = 0
        for item in items:
            if count >= self._max_records:
                errors.append(f"max_records 截断[{target.target_id}]")
                return
            record = self._coerce(target, item)
            count += 1
            yield record

    @staticmethod
    def _coerce(target: ScrapeTarget, item) -> Optional[ScrapedRecord]:
        if isinstance(item, ScrapedRecord):
            return item if item.record_id.strip() and item.title.strip() else None
        if not isinstance(item, dict):
            return None
        record_id = str(item.get("record_id", "") or "")
        title = str(item.get("title", "") or "")
        if not record_id.strip() or not title.strip():
            return None
        content = str(item.get("content", "") or "")
        publish_time = item.get("publish_time")
        digest = hashlib.md5((title + content).encode("utf-8")).hexdigest()
        return ScrapedRecord(
            target_id=target.target_id,
            record_id=record_id,
            title=title,
            content=content,
            publish_time=str(publish_time) if publish_time is not None else None,
            url=target.url,
            content_hash=digest,
        )

    def _is_seen(self, content_hash: str, errors: list[str]) -> bool:
        if self._seen is None:
            return False
        try:
            return bool(self._seen(content_hash))
        except Exception as exc:  # noqa: BLE001 - fail-open 对齐 news_dedup 惯例
            log.warning("scrape dedup seen failed: %s", exc)
            errors.append(f"seen 异常(fail-open): {exc}")
            return False

    def _emit(self, records: tuple[ScrapedRecord, ...], errors: list[str]) -> tuple[bool, bool]:
        if self._sink is None:
            return False, True
        try:
            self._sink(records)
            return True, True
        except Exception as exc:  # noqa: BLE001 - sink 异常不阻断判定
            log.warning("scrape sink failed: %s", exc)
            errors.append(f"sink 异常: {exc}")
            return True, False
