# [BLUEPRINT] MOD-ALT-009 | docs/03_modules/_domain_alt_data/research_report_collector/blueprint.md
# [MODULE] zephyr.alt_data.research_report_collector
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（采集核心纯内存；fetch_api/symbol_linker/event_bus/clock 全注入；采集语义参照 zephyr.data.news_collector、映射语义参照 news_symbol_linker）
# [CONSUMERS] 运行时装配批（东财研报 API 绑定 / 标的映射接 symbol_linker / 评级变动事件接事件总线路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 研报五要素非空(report_id/title/rating/org/publish_date); target_price空或正有限值; report_id去重幂等; 标的强制经symbol_linker映射(未注入Fail-Closed，未映射条目跳过留痕不落库); 快照按(symbol,org)维护，(publish_date,report_id)单调，乱序旧文不撼动快照不出事件; 评级变动事件检出序确定性，event_bus回调异常不阻断且内部留痕; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/research_report_collector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ResearchReportError(占位 ZA-ALT-UNREGISTERED-REPORT-COLLECTOR)——fetch_api/symbol_linker未注入、抓取/映射异常、批次或条目类型非法、字段非法、未知report_id查body_ref时抛
# [TESTS] tests/alt_data/test_research_report_collector.py
# [A_module] module_id=MOD-ALT-009 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ResearchReportCollector — 研报采集器（MOD-ALT-009）。

B1-00628（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-012，C2 72）：研报
**元数据采集**（东财研报中心语义：标题/评级/目标价/机构/日期，API 注入）+
**评级变动检测**（(symbol, org) 前后快照 diff）+评级变动事件**入事件总线
回调**+标的映射注入 **news_symbol_linker 语义**+正文结构化产物**引用接口**
（body_ref 指针，不内嵌正文解析）。

查重分工（蓝图 §0）：news_collector=新闻采集面实现（本件=研报元数据专门
采集，不做新闻）；news_symbol_linker=标的映射实现（本件仅注入其语义回调）；
filing_nlp_engine=公告正文 NLP（本件仅存 body_ref 引用，正文结构化归彼）；
sentiment_engine=情绪聚合（消费评级变动事件下游，零交集）。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "CollectedReport",
    "RatingChangeEvent",
    "ResearchReport",
    "ResearchReportCollector",
    "ResearchReportError",
]


class ResearchReportError(Exception):
    """研报采集输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-REPORT-COLLECTOR。
    """


@dataclass(frozen=True)
class ResearchReport:
    """研报元数据（东财研报中心语义，frozen）。"""

    report_id: str
    title: str
    rating: str
    target_price: float | None
    org: str
    publish_date: datetime.date
    raw_symbol: str
    body_ref: str


@dataclass(frozen=True)
class CollectedReport:
    """采集落库记录（含映射后标的，frozen）。"""

    report: ResearchReport
    symbol: str
    collected_at: datetime.datetime


@dataclass(frozen=True)
class RatingChangeEvent:
    """评级变动事件（入事件总线载荷，frozen）。"""

    symbol: str
    org: str
    previous_rating: str
    current_rating: str
    previous_report_id: str
    current_report_id: str
    detected_at: datetime.datetime


class ResearchReportCollector:
    """研报采集器（元数据采集 + 标的映射 + 快照 diff + 事件总线）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        fetch_api: Callable[[], "list[ResearchReport]"] | None = None,
        symbol_linker: Callable[[str], "str | None"] | None = None,
        event_bus: Callable[[RatingChangeEvent], None] | None = None,
    ) -> None:
        for name, fn in (
            ("clock", clock),
            ("fetch_api", fetch_api),
            ("symbol_linker", symbol_linker),
            ("event_bus", event_bus),
        ):
            if fn is not None and not callable(fn):
                raise ResearchReportError(f"{name} 非 callable")
        self._clock = clock or datetime.datetime.now
        self._fetch_api = fetch_api
        self._linker = symbol_linker
        self._event_bus = event_bus
        self._reports: dict[str, CollectedReport] = {}
        #: (symbol, org) -> (rating, report_id, publish_date) 最新快照
        self._snapshots: dict[tuple[str, str], tuple[str, str, datetime.date]] = {}
        self._events: list[RatingChangeEvent] = []

    # ── 采集 ──────────────────────────────────────────────────────────────

    def collect(self) -> int:
        """采集一批：API 注入抓取 → 校验 → 标的映射 → 落库 + 快照 diff 评级变动事件。

        返回本次新落库条数；report_id 去重幂等；未映射条目跳过留痕。
        """
        if self._fetch_api is None:
            raise ResearchReportError("fetch_api 未注入（API 全注入不真发，禁止旁路）")
        if self._linker is None:
            raise ResearchReportError("symbol_linker 未注入（标的强制映射，禁止原始名落库）")
        try:
            batch = self._fetch_api()
        except Exception as exc:
            raise ResearchReportError(f"fetch_api 抓取异常: {exc}") from exc
        if not isinstance(batch, (list, tuple)):
            raise ResearchReportError(f"fetch_api 返回类型非法: {type(batch)!r}（须 list[ResearchReport]）")
        for item in batch:
            if not isinstance(item, ResearchReport):
                raise ResearchReportError(f"研报条目类型非法: {type(item)!r}（须 ResearchReport）")
            self._validate(item)
        ordered = sorted(batch, key=lambda r: (r.publish_date, r.report_id))

        new_count = 0
        for report in ordered:
            if report.report_id in self._reports:
                continue  # 幂等去重
            try:
                symbol = self._linker(report.raw_symbol)
            except Exception as exc:
                raise ResearchReportError(f"symbol_linker 映射异常: {report.raw_symbol!r}: {exc}") from exc
            if not isinstance(symbol, str) or not symbol:
                _log.warning("标的未映射跳过: %s (%s)", report.report_id, report.raw_symbol)
                continue
            collected = CollectedReport(report=report, symbol=symbol, collected_at=self._clock())
            self._reports[report.report_id] = collected
            new_count += 1
            self._apply_snapshot(collected)
        return new_count

    @staticmethod
    def _validate(report: ResearchReport) -> None:
        for field_name in ("report_id", "title", "rating", "org", "raw_symbol", "body_ref"):
            value = getattr(report, field_name)
            if not isinstance(value, str) or not value:
                raise ResearchReportError(f"{field_name} 为空")
        if not isinstance(report.publish_date, datetime.date):
            raise ResearchReportError(f"publish_date 类型非法: {report.publish_date!r}")
        if report.target_price is not None:
            if isinstance(report.target_price, bool) or not isinstance(report.target_price, (int, float)):
                raise ResearchReportError(f"target_price 类型非法: {report.target_price!r}")
            if not math.isfinite(float(report.target_price)) or float(report.target_price) <= 0.0:
                raise ResearchReportError(f"target_price 须为正有限值: {report.target_price!r}")

    def _apply_snapshot(self, collected: CollectedReport) -> None:
        report = collected.report
        key = (collected.symbol, report.org)
        previous = self._snapshots.get(key)
        if previous is not None and (report.publish_date, report.report_id) <= (previous[2], previous[1]):
            return  # 乱序旧文不撼动快照、不出事件
        self._snapshots[key] = (report.rating, report.report_id, report.publish_date)
        if previous is not None and previous[0] != report.rating:
            event = RatingChangeEvent(
                symbol=collected.symbol,
                org=report.org,
                previous_rating=previous[0],
                current_rating=report.rating,
                previous_report_id=previous[1],
                current_report_id=report.report_id,
                detected_at=self._clock(),
            )
            self._events.append(event)
            _log.info("评级变动: %s %s %s -> %s", collected.symbol, report.org, previous[0], report.rating)
            if self._event_bus is not None:
                try:
                    self._event_bus(event)
                except Exception:  # noqa: BLE001 — 事件总线异常不阻断（蓝图 §1）
                    _log.exception("event_bus 回调失败")

    # ── 查询 ─────────────────────────────────────────────────────────────

    def reports(self, symbol: str | None = None) -> tuple[CollectedReport, ...]:
        """已采集研报（(publish_date, report_id) 升序，确定性）。"""
        out = [c for c in self._reports.values() if symbol is None or c.symbol == symbol]
        out.sort(key=lambda c: (c.report.publish_date, c.report.report_id))
        return tuple(out)

    def latest_rating(self, symbol: str, org: str) -> "str | None":
        """(symbol, org) 最新快照评级（无快照 → None）。"""
        snapshot = self._snapshots.get((symbol, org))
        return snapshot[0] if snapshot is not None else None

    def events(self) -> tuple[RatingChangeEvent, ...]:
        """评级变动事件流（检出序，确定性）。"""
        return tuple(self._events)

    def body_ref_of(self, report_id: str) -> str:
        """正文结构化产物引用（未知 report_id → Fail-Closed）。"""
        collected = self._reports.get(report_id)
        if collected is None:
            raise ResearchReportError(f"未知 report_id: {report_id!r}")
        return collected.report.body_ref
