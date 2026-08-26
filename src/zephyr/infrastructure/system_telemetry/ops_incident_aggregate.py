# [BLUEPRINT] MOD-OPS-001 | docs/03_modules/_domain_infrastructure/ops_incident_aggregate/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.ops_incident_aggregate
# [DOMAIN] D_OPS
# [DEPENDENCIES] 无（协议核心纯内存；clock/event_sink/store 全注入）
# [CONSUMERS] 运行时装配批（运维事件聚合注册 / 事件总线绑定 / 持久化适配器装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分级词表闭合(P0|P1|P2); 状态机 open→ack→mitigating→resolved→postmortem 仅正向单步; 升级仅向更高严重级且终态(resolved/postmortem)禁止; 事件三件套(detected/escalated/resolved)经注入 sink 留痕; 每次变更经注入 store 持久化; 查询按 (detected_at,incident_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure/ops_incident_aggregate/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OpsIncidentError(占位 ZA-OPS-UNREGISTERED-OPS-INCIDENT)——空id/空标题/非法分级/重复检测/未知incident/非法状态迁移/非法升级时抛
# [TESTS] tests/infrastructure/system_telemetry/test_ops_incident_aggregate.py
# [A_module] module_id=MOD-OPS-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""OpsIncidentAggregate — 运维事件聚合根（MOD-OPS-001）。

B9-11460（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-OPS-001，B9 D-OPS）：
OpsIncident 核心聚合——incident_id + 分级（P0~P2 词表闭合）+ 状态机
（open→ack→mitigating→resolved→postmortem 仅正向单步）+ 运维事件三件套
（detected/escalated/resolved 事件 Schema）+ 持久化注入（store 回调）。

查重分工（蓝图 §0）：本件只做事件生命周期聚合与状态机，不做自动处置
（incident_responder 职责）、不做资产视角（asset_inventory 职责）；外部副
作用（事件总线/持久化/时钟）全注入，纯内存确定性，同输入必同输出。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DetectedEvent",
    "EscalatedEvent",
    "IncidentEventKind",
    "IncidentSeverity",
    "IncidentStatus",
    "OpsIncident",
    "OpsIncidentAggregate",
    "OpsIncidentError",
    "ResolvedEvent",
]

#: 严重级序号（序号越小越严重；升级 = 序号减小）
_SEVERITY_RANK: Final[dict["IncidentSeverity", int]] = {}

#: 状态机合法迁移（仅正向单步）
_TRANSITIONS: Final[dict["IncidentStatus", "IncidentStatus"]] = {}


class OpsIncidentError(Exception):
    """运维事件聚合输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-OPS-UNREGISTERED-OPS-INCIDENT。
    """


class IncidentSeverity(str, Enum):
    """事件分级（词表闭合，P0 最紧急）。"""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


_SEVERITY_RANK.update({
    IncidentSeverity.P0: 0,
    IncidentSeverity.P1: 1,
    IncidentSeverity.P2: 2,
})


class IncidentStatus(str, Enum):
    """事件状态机（仅正向单步迁移）。"""

    OPEN = "open"
    ACK = "ack"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    POSTMORTEM = "postmortem"


_TRANSITIONS.update({
    IncidentStatus.OPEN: IncidentStatus.ACK,
    IncidentStatus.ACK: IncidentStatus.MITIGATING,
    IncidentStatus.MITIGATING: IncidentStatus.RESOLVED,
    IncidentStatus.RESOLVED: IncidentStatus.POSTMORTEM,
})

#: 终态（禁止升级/再迁移）
_TERMINAL: Final[frozenset[IncidentStatus]] = frozenset({
    IncidentStatus.RESOLVED,
    IncidentStatus.POSTMORTEM,
})


class IncidentEventKind(str, Enum):
    """运维事件三件套类别。"""

    DETECTED = "detected"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


@dataclass(frozen=True)
class DetectedEvent:
    """检测事件 Schema（事件创设载体，frozen）。"""

    incident_id: str
    severity: IncidentSeverity
    title: str
    source: str
    occurred_at: datetime.datetime


@dataclass(frozen=True)
class EscalatedEvent:
    """升级事件 Schema（严重级上调留痕，frozen）。"""

    incident_id: str
    from_severity: IncidentSeverity
    to_severity: IncidentSeverity
    reason: str
    occurred_at: datetime.datetime


@dataclass(frozen=True)
class ResolvedEvent:
    """解决事件 Schema（处置闭环留痕，frozen）。"""

    incident_id: str
    resolution: str
    occurred_at: datetime.datetime


@dataclass(frozen=True)
class OpsIncident:
    """运维事件聚合快照（frozen，每次变更整体替换）。"""

    incident_id: str
    severity: IncidentSeverity
    status: IncidentStatus
    title: str
    source: str
    detected_at: datetime.datetime
    updated_at: datetime.datetime
    history: tuple[IncidentEventKind, ...]


class OpsIncidentAggregate:
    """运维事件聚合根（注册表 + 状态机 + 三件套事件 + 持久化注入）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        event_sink: Callable[[object], None] | None = None,
        store: Callable[[OpsIncident], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._event_sink = event_sink
        self._store = store
        self._incidents: dict[str, OpsIncident] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _emit(self, event: object) -> None:
        if self._event_sink is not None:
            try:
                self._event_sink(event)
            except Exception:  # noqa: BLE001 — 事件留痕不阻断（蓝图 §1）
                _log.exception("event_sink 事件投递失败")

    def _persist(self, incident: OpsIncident) -> None:
        if self._store is not None:
            try:
                self._store(incident)
            except Exception:  # noqa: BLE001 — 持久化失败不阻断内存态
                _log.exception("store 持久化失败: %s", incident.incident_id)

    def _get(self, incident_id: str) -> OpsIncident:
        incident = self._incidents.get(incident_id)
        if incident is None:
            raise OpsIncidentError(f"未知 incident: {incident_id!r}")
        return incident

    def _transition(
        self, incident_id: str, expected: IncidentStatus, target: IncidentStatus
    ) -> OpsIncident:
        current = self._get(incident_id)
        if current.status is not expected:
            raise OpsIncidentError(
                f"非法状态迁移: incident {incident_id!r} 当前 {current.status.value}，"
                f"须 {expected.value} 方可迁移至 {target.value}"
            )
        nxt = OpsIncident(
            incident_id=current.incident_id,
            severity=current.severity,
            status=target,
            title=current.title,
            source=current.source,
            detected_at=current.detected_at,
            updated_at=self._clock(),
            history=current.history,
        )
        self._incidents[incident_id] = nxt
        self._persist(nxt)
        return nxt

    # ── 检测（创设） ─────────────────────────────────────────────────────

    def detect(self, event: DetectedEvent) -> OpsIncident:
        """检测登记：校验三件套 Schema → 创设 OPEN 事件 → 留痕+持久化。"""
        if not event.incident_id:
            raise OpsIncidentError("incident_id 为空")
        if not isinstance(event.severity, IncidentSeverity):
            raise OpsIncidentError(f"非法分级: {event.severity!r}（词表 P0|P1|P2）")
        if not event.title:
            raise OpsIncidentError("title 为空")
        if not event.source:
            raise OpsIncidentError("source 为空")
        if event.incident_id in self._incidents:
            raise OpsIncidentError(f"incident_id 重复: {event.incident_id!r}")
        incident = OpsIncident(
            incident_id=event.incident_id,
            severity=event.severity,
            status=IncidentStatus.OPEN,
            title=event.title,
            source=event.source,
            detected_at=event.occurred_at,
            updated_at=event.occurred_at,
            history=(IncidentEventKind.DETECTED,),
        )
        self._incidents[event.incident_id] = incident
        self._emit(event)
        self._persist(incident)
        _log.info("事件检测登记: %s (%s)", event.incident_id, event.severity.value)
        return incident

    # ── 状态机 ───────────────────────────────────────────────────────────

    def acknowledge(self, incident_id: str) -> OpsIncident:
        """认领：open → ack。"""
        return self._transition(incident_id, IncidentStatus.OPEN, IncidentStatus.ACK)

    def start_mitigation(self, incident_id: str) -> OpsIncident:
        """处置中：ack → mitigating。"""
        return self._transition(incident_id, IncidentStatus.ACK, IncidentStatus.MITIGATING)

    def resolve(self, event: ResolvedEvent) -> OpsIncident:
        """解决：mitigating → resolved（ResolvedEvent 留痕）。"""
        if not event.resolution:
            raise OpsIncidentError("resolution 为空")
        incident = self._transition(
            event.incident_id, IncidentStatus.MITIGATING, IncidentStatus.RESOLVED
        )
        incident = OpsIncident(
            incident_id=incident.incident_id,
            severity=incident.severity,
            status=incident.status,
            title=incident.title,
            source=incident.source,
            detected_at=incident.detected_at,
            updated_at=incident.updated_at,
            history=incident.history + (IncidentEventKind.RESOLVED,),
        )
        self._incidents[event.incident_id] = incident
        self._emit(event)
        self._persist(incident)
        return incident

    def close_postmortem(self, incident_id: str) -> OpsIncident:
        """复盘闭环：resolved → postmortem（终态）。"""
        return self._transition(incident_id, IncidentStatus.RESOLVED, IncidentStatus.POSTMORTEM)

    # ── 升级 ─────────────────────────────────────────────────────────────

    def escalate(self, event: EscalatedEvent) -> OpsIncident:
        """升级：仅向更高严重级（P2→P1→P0）；终态禁止；EscalatedEvent 留痕。"""
        current = self._get(event.incident_id)
        if current.status in _TERMINAL:
            raise OpsIncidentError(
                f"终态禁止升级: incident {event.incident_id!r} 当前 {current.status.value}"
            )
        if not isinstance(event.to_severity, IncidentSeverity):
            raise OpsIncidentError(f"非法目标分级: {event.to_severity!r}")
        if event.from_severity is not current.severity:
            raise OpsIncidentError(
                f"升级源分级不符: 声明 {event.from_severity!r}，当前 {current.severity!r}"
            )
        if _SEVERITY_RANK[event.to_severity] >= _SEVERITY_RANK[current.severity]:
            raise OpsIncidentError(
                f"非法升级: {current.severity.value} → {event.to_severity.value}，"
                "仅允许向更高严重级"
            )
        if not event.reason:
            raise OpsIncidentError("升级 reason 为空")
        nxt = OpsIncident(
            incident_id=current.incident_id,
            severity=event.to_severity,
            status=current.status,
            title=current.title,
            source=current.source,
            detected_at=current.detected_at,
            updated_at=self._clock(),
            history=current.history + (IncidentEventKind.ESCALATED,),
        )
        self._incidents[event.incident_id] = nxt
        self._emit(event)
        self._persist(nxt)
        _log.warning(
            "事件升级: %s %s → %s (%s)",
            event.incident_id, current.severity.value, event.to_severity.value, event.reason,
        )
        return nxt

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get(self, incident_id: str) -> OpsIncident:
        """单事件快照查询（未知 → Fail-Closed）。"""
        return self._get(incident_id)

    def list_incidents(self, status: IncidentStatus | None = None) -> list[OpsIncident]:
        """事件列表（可按状态过滤；按 (detected_at, incident_id) 确定性排序）。"""
        if status is not None and not isinstance(status, IncidentStatus):
            raise OpsIncidentError(f"非法状态过滤: {status!r}")
        out = [
            inc for inc in self._incidents.values()
            if status is None or inc.status is status
        ]
        out.sort(key=lambda i: (i.detected_at, i.incident_id))
        return out
