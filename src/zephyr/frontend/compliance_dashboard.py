# [BLUEPRINT] MOD-FE-010 | docs/03_modules/_domain_frontend/compliance_dashboard/blueprint.md
# [MODULE] zephyr.frontend.compliance_dashboard
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（协议核心纯内存；四卡数据源/趋势数据源/时钟全注入）
# [CONSUMERS] 运行时装配批（compliance_report_registry 适配注入 / 仪表盘面板装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 异常严重级词表闭合(low|medium|high); 整改状态词表闭合(open|in_progress|done|overdue); 趋势指标词表闭合(rule_hit_rate|anomaly_count|evidence_completeness|open_remediation); 数据源记录类型不符Fail-Closed; 命中率/完整度空集=0.0; 清单输出确定性排序; 趋势按日窗口升序(缺值=0.0); 时钟全注入; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/compliance_dashboard/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ComplianceDashboardError(占位 ZA-FE-UNREGISTERED-COMPLIANCE-DASHBOARD)——数据源未注入/记录类型非法/字段非法/趋势指标未知/窗口天数越界/趋势值类型非法时抛
# [TESTS] tests/frontend/test_compliance_dashboard.py
# [A_module] module_id=MOD-FE-010 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ComplianceDashboard — 合规仪表盘数据器（MOD-FE-010）。

B14-04672（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-011，A9 M36-S07）：
GRC 仪表盘思想——**四卡数据聚合**：规则命中率卡 / 审查异常清单卡 /
证据链完整度卡 / 整改任务看板卡（数据源全注入，不 import 合规后端）+
**趋势序列**（按日窗口，指标词表闭合，缺值补 0.0）。

查重分工：compliance_report_registry=合规报告登记（本件经注入 provider
消费其记录语义，不重建登记）；alert_center=告警面板（零交集）。
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AnomalyCard",
    "AnomalyRecord",
    "AnomalySeverity",
    "ComplianceDashboard",
    "ComplianceDashboardError",
    "DashboardSnapshot",
    "EvidenceCard",
    "EvidenceRecord",
    "RemediationCard",
    "RemediationStatus",
    "RemediationTask",
    "RuleCheckRecord",
    "RuleHitCard",
    "TrendMetric",
    "TrendPoint",
]

#: 趋势窗口最大天数
_MAX_TREND_DAYS: Final[int] = 366

#: 异常严重级展示排序（高→低）
_ANOMALY_RANK: Final[dict["AnomalySeverity", int]] = {}


class ComplianceDashboardError(Exception):
    """合规仪表盘数据源/参数非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-COMPLIANCE-DASHBOARD。
    """


class AnomalySeverity(str, Enum):
    """审查异常严重级（词表闭合）。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


_ANOMALY_RANK.update(
    {
        AnomalySeverity.HIGH: 0,
        AnomalySeverity.MEDIUM: 1,
        AnomalySeverity.LOW: 2,
    }
)


class RemediationStatus(str, Enum):
    """整改任务状态（词表闭合）。"""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    OVERDUE = "overdue"


class TrendMetric(str, Enum):
    """趋势指标（词表闭合，按日窗口取值）。"""

    RULE_HIT_RATE = "rule_hit_rate"
    ANOMALY_COUNT = "anomaly_count"
    EVIDENCE_COMPLETENESS = "evidence_completeness"
    OPEN_REMEDIATION = "open_remediation"


@dataclass(frozen=True)
class RuleCheckRecord:
    """规则检查记录（命中率卡数据源）。"""

    rule_id: str
    hit: bool


@dataclass(frozen=True)
class AnomalyRecord:
    """审查异常记录（异常清单卡数据源）。"""

    anomaly_id: str
    severity: AnomalySeverity
    summary: str
    open: bool


@dataclass(frozen=True)
class EvidenceRecord:
    """证据链记录（完整度卡数据源）。"""

    evidence_id: str
    complete: bool
    missing_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class RemediationTask:
    """整改任务记录（看板卡数据源）。"""

    task_id: str
    status: RemediationStatus
    owner: str = ""


@dataclass(frozen=True)
class RuleHitCard:
    """规则命中率卡。"""

    total_checks: int
    hits: int
    hit_rate: float


@dataclass(frozen=True)
class AnomalyCard:
    """审查异常清单卡（open 项按严重级高→低、id 字典序确定性排序）。"""

    total: int
    open_count: int
    by_severity: Mapping[AnomalySeverity, int]
    open_items: tuple[AnomalyRecord, ...]


@dataclass(frozen=True)
class EvidenceCard:
    """证据链完整度卡。"""

    total: int
    complete_count: int
    completeness: float
    incomplete_ids: tuple[str, ...]


@dataclass(frozen=True)
class RemediationCard:
    """整改任务看板卡（by_status 四态齐全）。"""

    total: int
    by_status: Mapping[RemediationStatus, int]
    overdue_ids: tuple[str, ...]


@dataclass(frozen=True)
class TrendPoint:
    """趋势点（日窗口）。"""

    day: datetime.date
    value: float


@dataclass(frozen=True)
class DashboardSnapshot:
    """四卡聚合快照。"""

    generated_at: datetime.datetime
    rule_hit: RuleHitCard
    anomalies: AnomalyCard
    evidence: EvidenceCard
    remediation: RemediationCard


class ComplianceDashboard:
    """合规仪表盘数据器（四卡聚合 + 日窗口趋势；数据源全注入）。

    Args:
        rule_checks_provider: 规则检查记录数据源（返回 Iterable[RuleCheckRecord]）。
        anomalies_provider: 审查异常记录数据源。
        evidence_provider: 证据链记录数据源。
        remediation_provider: 整改任务记录数据源。
        trend_providers: 趋势指标 → 取值器（date → float | None）。
        clock: 时钟注入（快照时间戳/趋势默认止日）。
    """

    def __init__(
        self,
        *,
        rule_checks_provider: Callable[[], Iterable[RuleCheckRecord]],
        anomalies_provider: Callable[[], Iterable[AnomalyRecord]],
        evidence_provider: Callable[[], Iterable[EvidenceRecord]],
        remediation_provider: Callable[[], Iterable[RemediationTask]],
        trend_providers: Mapping[TrendMetric, Callable[[datetime.date], float | None]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        providers = {
            "rule_checks_provider": rule_checks_provider,
            "anomalies_provider": anomalies_provider,
            "evidence_provider": evidence_provider,
            "remediation_provider": remediation_provider,
        }
        for name, provider in providers.items():
            if not callable(provider):
                raise ComplianceDashboardError(f"{name} 未注入（数据源 Fail-Closed）")
        for metric, provider in (trend_providers or {}).items():
            if not isinstance(metric, TrendMetric):
                raise ComplianceDashboardError(f"趋势指标非法: {metric!r}")
            if not callable(provider):
                raise ComplianceDashboardError(f"趋势数据源不可调用: {metric.value}")
        self._rule_checks_provider = rule_checks_provider
        self._anomalies_provider = anomalies_provider
        self._evidence_provider = evidence_provider
        self._remediation_provider = remediation_provider
        self._trend = dict(trend_providers or {})
        self._clock = clock or datetime.datetime.now

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _fetch(provider, record_type: type, name: str) -> tuple:
        raw = provider()
        if isinstance(raw, (str, bytes)) or not isinstance(raw, Iterable):
            raise ComplianceDashboardError(f"{name} 数据源返回不可迭代: {type(raw)!r}")
        records = tuple(raw)
        for record in records:
            if not isinstance(record, record_type):
                raise ComplianceDashboardError(f"{name} 记录类型非法: {record!r}")
        return records

    # ── 四卡聚合 ──────────────────────────────────────────────────────────

    def rule_hit_card(self) -> RuleHitCard:
        """规则命中率卡（空集命中率=0.0）。"""
        records = self._fetch(self._rule_checks_provider, RuleCheckRecord, "rule_checks")
        for record in records:
            if not isinstance(record.rule_id, str) or not record.rule_id:
                raise ComplianceDashboardError("rule_id 为空")
            if not isinstance(record.hit, bool):
                raise ComplianceDashboardError(f"hit 字段类型非法: {record.hit!r}")
        total = len(records)
        hits = sum(1 for r in records if r.hit)
        rate = round(hits / total, 6) if total else 0.0
        return RuleHitCard(total_checks=total, hits=hits, hit_rate=rate)

    def anomaly_card(self) -> AnomalyCard:
        """审查异常清单卡（open 项确定性排序）。"""
        records = self._fetch(self._anomalies_provider, AnomalyRecord, "anomalies")
        for record in records:
            if not isinstance(record.anomaly_id, str) or not record.anomaly_id:
                raise ComplianceDashboardError("anomaly_id 为空")
            if not isinstance(record.severity, AnomalySeverity):
                raise ComplianceDashboardError(f"异常严重级非法: {record.severity!r}")
            if not isinstance(record.open, bool):
                raise ComplianceDashboardError(f"open 字段类型非法: {record.open!r}")
        open_items = tuple(
            sorted(
                (r for r in records if r.open),
                key=lambda r: (_ANOMALY_RANK[r.severity], r.anomaly_id),
            )
        )
        by_severity = {sev: 0 for sev in AnomalySeverity}
        for record in open_items:
            by_severity[record.severity] += 1
        return AnomalyCard(
            total=len(records),
            open_count=len(open_items),
            by_severity=by_severity,
            open_items=open_items,
        )

    def evidence_card(self) -> EvidenceCard:
        """证据链完整度卡（空集完整度=0.0）。"""
        records = self._fetch(self._evidence_provider, EvidenceRecord, "evidence")
        for record in records:
            if not isinstance(record.evidence_id, str) or not record.evidence_id:
                raise ComplianceDashboardError("evidence_id 为空")
            if not isinstance(record.complete, bool):
                raise ComplianceDashboardError(f"complete 字段类型非法: {record.complete!r}")
            for field_name in record.missing_fields:
                if not isinstance(field_name, str):
                    raise ComplianceDashboardError(f"missing_fields 元素非法: {field_name!r}")
        total = len(records)
        complete_count = sum(1 for r in records if r.complete)
        completeness = round(complete_count / total, 6) if total else 0.0
        incomplete_ids = tuple(sorted(r.evidence_id for r in records if not r.complete))
        return EvidenceCard(
            total=total,
            complete_count=complete_count,
            completeness=completeness,
            incomplete_ids=incomplete_ids,
        )

    def remediation_card(self) -> RemediationCard:
        """整改任务看板卡（by_status 四态齐全，overdue 清单确定性排序）。"""
        records = self._fetch(self._remediation_provider, RemediationTask, "remediation")
        for record in records:
            if not isinstance(record.task_id, str) or not record.task_id:
                raise ComplianceDashboardError("task_id 为空")
            if not isinstance(record.status, RemediationStatus):
                raise ComplianceDashboardError(f"整改状态非法: {record.status!r}")
        by_status = {status: 0 for status in RemediationStatus}
        for record in records:
            by_status[record.status] += 1
        overdue_ids = tuple(sorted(r.task_id for r in records if r.status is RemediationStatus.OVERDUE))
        return RemediationCard(total=len(records), by_status=by_status, overdue_ids=overdue_ids)

    def snapshot(self) -> DashboardSnapshot:
        """四卡聚合快照（时间戳取注入时钟）。"""
        return DashboardSnapshot(
            generated_at=self._clock(),
            rule_hit=self.rule_hit_card(),
            anomalies=self.anomaly_card(),
            evidence=self.evidence_card(),
            remediation=self.remediation_card(),
        )

    # ── 趋势 ─────────────────────────────────────────────────────────────

    def trend(
        self,
        metric: TrendMetric,
        days: int,
        end_date: datetime.date | None = None,
    ) -> tuple[TrendPoint, ...]:
        """日窗口趋势序列（升序；缺值=0.0；止日默认注入时钟当日）。"""
        if not isinstance(metric, TrendMetric):
            raise ComplianceDashboardError(f"趋势指标非法: {metric!r}")
        if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= _MAX_TREND_DAYS:
            raise ComplianceDashboardError(f"趋势窗口天数非法: {days!r}（须 1..{_MAX_TREND_DAYS}）")
        provider = self._trend.get(metric)
        if provider is None:
            raise ComplianceDashboardError(f"趋势数据源未注入: {metric.value}")
        end = end_date if end_date is not None else self._clock().date()
        if not isinstance(end, datetime.date):
            raise ComplianceDashboardError(f"end_date 类型非法: {end!r}")
        points: list[TrendPoint] = []
        for offset in range(days - 1, -1, -1):
            day = end - datetime.timedelta(days=offset)
            raw = provider(day)
            if raw is None:
                value = 0.0
            elif isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise ComplianceDashboardError(f"趋势值类型非法: {raw!r}（{day}）")
            else:
                value = float(raw)
            points.append(TrendPoint(day=day, value=value))
        return tuple(points)
