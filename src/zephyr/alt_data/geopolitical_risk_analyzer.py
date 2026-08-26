# [BLUEPRINT] MOD-ALT-014 | docs/03_modules/_domain_alt_data/geopolitical_risk_analyzer/blueprint.md
# [MODULE] zephyr.alt_data.geopolitical_risk_analyzer
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（协议核心纯内存；事件源/传导矩阵/制裁名单/事件总线/时钟全注入，复用 event_geopolitical_map 语义不 import）
# [CONSUMERS] 运行时装配批（事件源接免费新闻/RSS 采集族 / 风险事件入事件总线仅作信号输入 / 传导矩阵接 intelligence 地缘映射）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 协议核心纯内存无IO；事件源强制注入（未注入 Fail-Closed 不旁路）；severity/传导系数恒∈[0,1]；risk_score=severity×max(命中商品传导系数,默认1.0) 恒∈[0,1]；制裁名单命中必标记；event_id 去重幂等；仅达发布阈值或制裁命中的事件入总线；同输入必同输出；仅信号输入语义无下单含义
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/geopolitical_risk_analyzer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GeopoliticalRiskError(占位 ZA-ALT-UNREGISTERED-GEO-RISK)——事件源未注入/非callable/传导系数越界/阈值乱序/event_id空白/severity越界/country空白/重复评估事件时抛
# [TESTS] tests/alt_data/test_geopolitical_risk_analyzer.py
# [A_module] module_id=MOD-ALT-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""GeopoliticalRiskAnalyzer — 地缘政治风险分析器（MOD-ALT-014）。

B5-07092（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-025，B5
D-ALT-DATA-12）：地缘风险分析——**事件采集**（免费新闻/RSS 注入源）
+ **风险评分**（国家/商品**传导矩阵**注入映射，severity×max 传导系数）
+ 公开**制裁名单比对**筛查（名单注入，命中标记）+ **风险事件入事件
总线**回调（仅达发布阈值或制裁命中者），仅作信号输入。

查重分工（蓝图 §0）：intelligence/event_geopolitical_map=地缘事件→板块
静态映射（本件=事件评分/制裁筛查/总线发布运行时面，不重建映射表，传导
矩阵全注入）；本件不做新闻抓取（采集在 connector 族），事件源注入委托。
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "GeoEvent",
    "GeopoliticalRiskAnalyzer",
    "GeopoliticalRiskError",
    "RiskEvent",
    "RiskLevel",
]

#: 事件源签名：() -> GeoEvent 序列（API 全注入不真发）
EventSource = Callable[[], Sequence["GeoEvent"]]

#: 事件总线签名：RiskEvent -> None（仅作信号输入）
EventBus = Callable[["RiskEvent"], None]


class GeopoliticalRiskError(Exception):
    """地缘风险分析输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-GEO-RISK。
    """


class RiskLevel(str, Enum):
    """风险等级（按阈值分档）。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class GeoEvent:
    """地缘事件（采集源产物，frozen）。"""

    event_id: str
    country: str
    headline: str
    severity: float
    commodities: tuple[str, ...]
    entities: tuple[str, ...]
    occurred_at: datetime.datetime


@dataclass(frozen=True)
class RiskEvent:
    """风险事件评估产物（入事件总线载荷，frozen）。"""

    event_id: str
    country: str
    headline: str
    risk_score: float
    risk_level: RiskLevel
    sanction_hit: bool
    hit_entities: tuple[str, ...]
    occurred_at: datetime.datetime
    assessed_at: datetime.datetime


class GeopoliticalRiskAnalyzer:
    """地缘风险分析器（采集注入 + 传导矩阵评分 + 制裁筛查 + 总线发布）。"""

    def __init__(
        self,
        *,
        event_source: EventSource | None,
        transmission_matrix: Mapping[str, Mapping[str, float]],
        sanction_list: Iterable[str] = (),
        publish_threshold: float = 0.3,
        high_threshold: float = 0.7,
        clock: Callable[[], datetime.datetime] | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        if event_source is None or not callable(event_source):
            raise GeopoliticalRiskError("event_source 未注入（事件采集强制注入，禁止旁路）")
        if not 0.0 <= publish_threshold <= high_threshold <= 1.0:
            raise GeopoliticalRiskError(
                f"阈值须满足 0<=publish<=high<=1: {publish_threshold!r}/{high_threshold!r}"
            )
        matrix: dict[str, dict[str, float]] = {}
        for country, row in transmission_matrix.items():
            if not country or not str(country).strip():
                raise GeopoliticalRiskError("传导矩阵国家键空白")
            clean_row: dict[str, float] = {}
            for commodity, coef in row.items():
                if not commodity or not str(commodity).strip():
                    raise GeopoliticalRiskError(f"传导矩阵商品键空白: {country!r}")
                if not 0.0 <= coef <= 1.0:
                    raise GeopoliticalRiskError(
                        f"传导系数越界: {country!r}/{commodity!r}={coef!r}（须∈[0,1]）"
                    )
                clean_row[str(commodity)] = float(coef)
            matrix[str(country)] = clean_row

        self._event_source = event_source
        self._matrix = matrix
        self._sanctions = frozenset(str(e) for e in sanction_list)
        self._publish_threshold = publish_threshold
        self._high_threshold = high_threshold
        self._clock = clock or datetime.datetime.now
        self._event_bus = event_bus
        self._assessed: dict[str, RiskEvent] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _validate_event(self, event: GeoEvent) -> None:
        if not isinstance(event, GeoEvent):
            raise GeopoliticalRiskError(f"事件源产物非 GeoEvent: {type(event)!r}")
        if not event.event_id or not event.event_id.strip():
            raise GeopoliticalRiskError("event_id 空白")
        if not event.country or not event.country.strip():
            raise GeopoliticalRiskError(f"country 空白: {event.event_id!r}")
        if not 0.0 <= event.severity <= 1.0:
            raise GeopoliticalRiskError(
                f"severity 越界: {event.severity!r}（须∈[0,1]，event {event.event_id!r}）"
            )

    def _level_of(self, risk_score: float) -> RiskLevel:
        if risk_score >= self._high_threshold:
            return RiskLevel.HIGH
        if risk_score >= self._publish_threshold:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    # ── 评估 ──────────────────────────────────────────────────────────────

    def assess(self, event: GeoEvent) -> RiskEvent:
        """单事件评估：传导矩阵评分 + 制裁名单比对（event_id 去重幂等）。"""
        self._validate_event(event)
        known = self._assessed.get(event.event_id)
        if known is not None:
            return known  # 幂等：同 event_id 返回首次评估产物

        coefs = [
            self._matrix[event.country][c]
            for c in event.commodities
            if c in self._matrix.get(event.country, {})
        ]
        max_coef = max(coefs) if coefs else 1.0  # 无传导映射→保守按原烈度
        risk_score = min(1.0, max(0.0, event.severity * max_coef))
        hit_entities = tuple(sorted(e for e in event.entities if e in self._sanctions))
        risk_event = RiskEvent(
            event_id=event.event_id,
            country=event.country,
            headline=event.headline,
            risk_score=risk_score,
            risk_level=self._level_of(risk_score),
            sanction_hit=bool(hit_entities),
            hit_entities=hit_entities,
            occurred_at=event.occurred_at,
            assessed_at=self._clock(),
        )
        self._assessed[event.event_id] = risk_event
        return risk_event

    # ── 采集 + 发布 ─────────────────────────────────────────────────────────

    def run(self) -> list[RiskEvent]:
        """采集注入源事件 → 逐一评估 → 达发布阈值或制裁命中者入事件总线。"""
        try:
            events = tuple(self._event_source())
        except GeopoliticalRiskError:
            raise
        except Exception as exc:  # noqa: BLE001 — 事件源违约 Fail-Closed
            raise GeopoliticalRiskError(f"event_source 执行异常: {exc}") from exc

        published: list[RiskEvent] = []
        for event in events:
            risk_event = self.assess(event)
            if risk_event.risk_score >= self._publish_threshold or risk_event.sanction_hit:
                published.append(risk_event)
                if self._event_bus is not None:
                    try:
                        self._event_bus(risk_event)
                    except Exception:  # noqa: BLE001 — 总线回调不阻断（蓝图 §1）
                        _log.exception("event_bus 发布失败: %s", risk_event.event_id)
                _log.info(
                    "地缘风险事件入总线: %s（%s score=%.3f sanction=%s）",
                    risk_event.event_id, risk_event.country,
                    risk_event.risk_score, risk_event.sanction_hit,
                )
        return published

    # ── 查询 ─────────────────────────────────────────────────────────────

    def history(self) -> tuple[RiskEvent, ...]:
        """全部已评估事件（按 (occurred_at, event_id) 确定性排序）。"""
        return tuple(sorted(
            self._assessed.values(), key=lambda r: (r.occurred_at, r.event_id)
        ))
