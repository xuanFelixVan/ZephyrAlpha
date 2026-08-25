# [BLUEPRINT] MOD-ALT-003 | docs/03_modules/_domain_alt_data/filing_nlp_engine/blueprint.md
# [MODULE] zephyr.alt_data.filing_nlp_engine
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors（判定核心纯内存；llm_extractor/sink 全注入）
# [CONSUMERS] 运行时装配批（公告文本接 announcement_provider 采集产物 / llm_extractor 接 api_llm_pool·llm_gateway / sink 接事件库写入 / 供事件注入与基本面信号消费）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 判定核心纯内存无IO；单条非法Fail-Closed到条；影响评分恒∈[-1,1]、置信度恒∈[0,1]（clip保证）；LLM输出结构/值域非法必回落规则并llm_invalid留痕，不出伪LLM结论；extractor字段如实记录rule|llm；仅信号输入语义无下单含义；sink异常不阻断；frozen dataclass asdict JSON可序列化；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/filing_nlp_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] filing_id/symbol/title空白→InvalidFilingError；llm_extractor/sink非callable或keyword_rules含未知事件类型→InvalidFilingNlpConfigError；llm_extractor/sink运行期异常→回落规则/留痕不阻断
# [TESTS] tests/alt_data/test_filing_nlp_engine.py
# [A_module] module_id=MOD-ALT-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""FilingNlpEngine — 监管文件 NLP 引擎（MOD-ALT-003）

B10-02196（AUD-DRAFT-001-DIGEST P1 波 W-P1-15，D-ALT-DATA-04 §30.2.4）：A 股
公告文本事件级 NLP（范围限 A 股公告，SEC 美股剔除）——巨潮公告文本（消费
announcement_provider 采集产物）→ 事件类型分类（业绩预告/业绩快报/减持/增持/
定增/诉讼/问询函/处罚/分红/回购/其他，规则关键词优先序）+ 影响评分 [-1,1]
（规则词典；可选 llm_extractor 注入升级，输出值域校验不合格回落规则留痕）→
FilingEvent（extractor=rule|llm 如实留痕），入事件表 sink 委托（装配批接线）。

撞名裁定：W-P1-14 B1-00113（D-ALT-04 FilingNLPEngine）spec 与本模块实质全等，
本波先建，canonical=MOD-ALT-003，W-P1-14 到时按 REVIEW 归并（如反向则以
depgraph 先建节点实证为准）。

查重裁定：announcement_provider（MOD-L00-004）为公告**元数据采集**；
financial_parser（MOD-DAT-FIN-PARSER）为财报 PDF/XBRL→**数字指标**解析
（其 docstring 已预留"Filing NLP 复用 PDF 解析产物，互补不重复"）；
news_dual_tagger（MOD-NLP-DUALTAG-001）为新闻双标签面。本模块为公告**文本**
事件级 NLP，解析粒度=事件类型+影响分，LLM 能力经 llm_extractor 注入委托
intelligence 族（api_llm_pool），零密钥零直连。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from typing import Callable, Final, Iterable, Optional

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__: Final = [
    "EVENT_TYPES",
    "ClassifyReport",
    "FilingEvent",
    "FilingInput",
    "FilingNlpEngine",
    "InvalidFilingError",
    "InvalidFilingNlpConfigError",
]

#: 事件类型封闭集合（"其他"恒为兜底类）
EVENT_TYPES: Final = (
    "业绩预告",
    "业绩快报",
    "减持",
    "增持",
    "定增",
    "诉讼",
    "问询函",
    "处罚",
    "分红",
    "回购",
    "其他",
)

#: 默认事件分类规则（按优先序首中即定，匹配面=title+text）
_DEFAULT_EVENT_RULES: Final[dict[str, tuple[str, ...]]] = {
    "业绩预告": ("业绩预告",),
    "业绩快报": ("业绩快报",),
    "减持": ("减持",),
    "增持": ("增持",),
    "定增": ("定增", "非公开发行", "向特定对象发行"),
    "诉讼": ("诉讼", "仲裁"),
    "问询函": ("问询函", "关注函", "监管函"),
    "处罚": ("处罚", "立案调查"),
    "分红": ("分红", "派息", "利润分配"),
    "回购": ("回购",),
}

#: 影响评分词典（关键词→单次命中权重，按命中次数累加后 clip 到 [-1,1]）
_IMPACT_LEXICON: Final[dict[str, float]] = {
    "增长": 0.3,
    "超预期": 0.4,
    "利好": 0.3,
    "增持": 0.4,
    "回购": 0.3,
    "分红": 0.2,
    "中标": 0.3,
    "获批": 0.3,
    "减持": -0.4,
    "风险": -0.2,
    "处罚": -0.5,
    "诉讼": -0.3,
    "亏损": -0.4,
    "退市": -0.6,
    "问询": -0.2,
    "违规": -0.5,
}

_RULE_CONFIDENCE: Final = 0.6
_DEFAULT_SOURCE_ID: Final = "cninfo"


# ============================================================================
# 1. 错误契约
# ============================================================================


class InvalidFilingError(ZephyrBaseError):
    """公告输入非法（filing_id/symbol/title 空白）。"""


class InvalidFilingNlpConfigError(ZephyrBaseError):
    """引擎配置非法（llm_extractor/sink 非 callable、keyword_rules 含未知事件类型）。"""


# ============================================================================
# 2. 数据模型
# ============================================================================


@dataclass(frozen=True)
class FilingInput:
    """公告输入。publish_time 合法性在 classify 判定（构造期只校验三字符串字段）。"""

    filing_id: str
    symbol: str
    title: str
    text: str
    publish_time: datetime.datetime

    def __post_init__(self) -> None:
        if not isinstance(self.filing_id, str) or not self.filing_id.strip():
            raise InvalidFilingError("filing_id 空白")
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise InvalidFilingError("symbol 空白")
        if not isinstance(self.title, str) or not self.title.strip():
            raise InvalidFilingError("title 空白")


@dataclass(frozen=True)
class FilingEvent:
    """结构化公告事件。extractor 如实记录 rule|llm。"""

    event_id: str
    symbol: str
    publish_time: datetime.datetime
    event_type: str
    impact_score: float
    confidence: float
    extractor: str
    source_id: str
    summary: str


@dataclass(frozen=True)
class ClassifyReport:
    """分类批次报告。events 按 (publish_time, event_id) 升序。"""

    filings_in: int
    accepted: int
    rejected: int
    events: tuple[FilingEvent, ...]
    rule_hits: int
    llm_hits: int
    llm_invalid: int
    errors: tuple[str, ...] = field(default_factory=tuple)
    sink_attempted: bool = False
    sink_ok: bool = True


# ============================================================================
# 3. 引擎
# ============================================================================


class FilingNlpEngine:
    """A 股公告文本事件级 NLP（判定核心纯内存，IO 全注入）。

    Args:
        llm_extractor: 可选，(FilingInput) -> {"event_type","impact_score","confidence"}；
            输出结构/值域非法 → 回落规则路径并 llm_invalid 留痕
        keyword_rules: 可选事件分类规则 dict[event_type, tuple[keyword, ...]]，
            整体替换内置规则；事件类型须 ∈ EVENT_TYPES
        sink: 可选，(tuple[FilingEvent, ...]) -> None
    """

    def __init__(
        self,
        llm_extractor: Optional[Callable[[FilingInput], dict]] = None,
        *,
        keyword_rules: Optional[dict[str, tuple[str, ...]]] = None,
        sink: Optional[Callable[[tuple[FilingEvent, ...]], None]] = None,
    ) -> None:
        if llm_extractor is not None and not callable(llm_extractor):
            raise InvalidFilingNlpConfigError("llm_extractor 非 callable")
        if sink is not None and not callable(sink):
            raise InvalidFilingNlpConfigError("sink 非 callable")
        if keyword_rules is not None:
            unknown = [t for t in keyword_rules if t not in EVENT_TYPES or t == "其他"]
            if unknown:
                raise InvalidFilingNlpConfigError(f"keyword_rules 含未知/兜底事件类型: {unknown}")
        self._llm = llm_extractor
        self._rules = keyword_rules if keyword_rules is not None else _DEFAULT_EVENT_RULES
        self._sink = sink

    # ------------------------------------------------------------------
    # 主流程
    # ------------------------------------------------------------------

    def classify(self, filings: Iterable) -> ClassifyReport:
        items = list(filings or [])
        errors: list[str] = []
        events: list[FilingEvent] = []
        rejected = rule_hits = llm_hits = llm_invalid = 0
        for item in items:
            filing = self._coerce(item)
            if filing is None or not isinstance(filing.publish_time, datetime.datetime):
                rejected += 1
                continue
            event, used_llm = self._classify_one_inner(filing, errors)
            if used_llm is True:
                llm_hits += 1
            elif used_llm is False:
                llm_invalid += 1
            else:
                rule_hits += 1
            events.append(event)

        ordered = tuple(sorted(events, key=lambda e: (e.publish_time, e.event_id)))
        sink_attempted, sink_ok = self._emit(ordered, errors)
        return ClassifyReport(
            filings_in=len(items),
            accepted=len(events),
            rejected=rejected,
            events=ordered,
            rule_hits=rule_hits,
            llm_hits=llm_hits,
            llm_invalid=llm_invalid,
            errors=tuple(errors),
            sink_attempted=sink_attempted,
            sink_ok=sink_ok,
        )

    def classify_one(self, filing: FilingInput) -> FilingEvent:
        """单条分类便捷口（输入须为合法 FilingInput）。"""
        if not isinstance(filing, FilingInput):
            raise InvalidFilingError("filing 非 FilingInput")
        if not isinstance(filing.publish_time, datetime.datetime):
            raise InvalidFilingError("publish_time 非 datetime")
        event, _ = self._classify_one_inner(filing, [])
        return event

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    @staticmethod
    def _coerce(item) -> Optional[FilingInput]:
        try:
            if isinstance(item, FilingInput):
                return item
            if isinstance(item, dict):
                return FilingInput(
                    filing_id=item.get("filing_id", ""),
                    symbol=item.get("symbol", ""),
                    title=item.get("title", ""),
                    text=item.get("text", "") or "",
                    publish_time=item.get("publish_time"),
                )
        except (InvalidFilingError, TypeError, ValueError):
            return None
        return None

    def _classify_one_inner(self, filing: FilingInput, errors: list[str]) -> tuple[FilingEvent, Optional[bool]]:
        if self._llm is not None:
            event = self._try_llm(filing, errors)
            if event is not None:
                return event, True
            errors.append(f"llm 输出非法/异常，回落规则[{filing.filing_id}]")
            return self._rule_event(filing), False
        return self._rule_event(filing), None

    def _try_llm(self, filing: FilingInput, errors: list[str]) -> Optional[FilingEvent]:
        try:
            out = self._llm(filing)
        except Exception as exc:  # noqa: BLE001 - LLM 异常回落规则不出伪结论
            log.warning("filing llm extract failed: %s (%s)", filing.filing_id, exc)
            errors.append(f"llm_extractor 异常[{filing.filing_id}]: {exc}")
            return None
        if not isinstance(out, dict):
            return None
        event_type = out.get("event_type")
        try:
            impact = float(out.get("impact_score"))
            confidence = float(out.get("confidence"))
        except (TypeError, ValueError):
            return None
        if event_type not in EVENT_TYPES:
            return None
        if not (-1.0 <= impact <= 1.0) or not (0.0 <= confidence <= 1.0):
            return None
        return self._build_event(filing, event_type, impact, confidence, "llm")

    def _rule_event(self, filing: FilingInput) -> FilingEvent:
        haystack = f"{filing.title}\n{filing.text}"
        event_type = "其他"
        for candidate in EVENT_TYPES:
            if candidate == "其他":
                continue
            keywords = self._rules.get(candidate)
            if keywords and any(kw in haystack for kw in keywords):
                event_type = candidate
                break
        score = 0.0
        for keyword, weight in _IMPACT_LEXICON.items():
            score += weight * haystack.count(keyword)
        score = max(-1.0, min(1.0, score))
        return self._build_event(filing, event_type, score, _RULE_CONFIDENCE, "rule")

    @staticmethod
    def _build_event(
        filing: FilingInput,
        event_type: str,
        impact: float,
        confidence: float,
        extractor: str,
    ) -> FilingEvent:
        return FilingEvent(
            event_id=filing.filing_id,
            symbol=filing.symbol,
            publish_time=filing.publish_time,
            event_type=event_type,
            impact_score=impact,
            confidence=confidence,
            extractor=extractor,
            source_id=_DEFAULT_SOURCE_ID,
            summary=filing.title[:80],
        )

    def _emit(self, events: tuple[FilingEvent, ...], errors: list[str]) -> tuple[bool, bool]:
        if self._sink is None:
            return False, True
        try:
            self._sink(events)
            return True, True
        except Exception as exc:  # noqa: BLE001 - sink 异常不阻断判定
            log.warning("filing event sink failed: %s", exc)
            errors.append(f"sink 异常: {exc}")
            return True, False
