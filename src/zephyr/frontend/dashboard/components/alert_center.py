# [BLUEPRINT] MOD-FE-003 | docs/03_modules/_domain_frontend/alert_center/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.alert_center
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 标准库(dataclasses/datetime/statistics); panel(可选, try/except 测试环境 None)
# [CONSUMERS] zephyr.frontend.dashboard.app_panel（运行时装配批挂「告警中心」Tab）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fetch/render 纯函数无IO; 输入非法Fail-Closed; render 输出 JSON 可序列化; 不 import 告警后端(数据源 DI 注入)
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/alert_center/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlertCenterInputError(占位 ZA-FE-UNREGISTERED-ALERT-CENTER)——severity/status 非法/时间倒挂/记录类型错误时抛
# [TESTS] tests/frontend/test_alert_center.py
# [A_module] module_id=MOD-FE-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""alert_center · 告警中心面板组件（MOD-FE-003）。

B14-04625（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-FE-002，A9运维架构
§8.3.2 D-FRONTEND-08）：AL-P1~P4 分级实时列表 + 6 维收敛视图（时间/空间/
根因/抑制/升级/静默）+ MTTR 与日均告警统计 + 确认率/误报率追踪。

数据源复用 alert_router 数据源：告警记录经 DI 注入（运行时装配批从
alert_manager/alert_router 适配），本组件不 import 告警后端、不重建路由。
组件形态与 gate_statistics 一致（dataclass + fetch + render dict payload，
测试环境零 panel 依赖）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final

logger = logging.getLogger(__name__)

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

__all__: Final = [
    "AlertCenterData",
    "AlertCenterInputError",
    "AlertCenterRecord",
    "AlertCenterStats",
    "VALID_SEVERITIES",
    "VALID_STATUSES",
    "fetch_alert_center",
    "render_alert_center",
]

VALID_SEVERITIES: Final[frozenset[str]] = frozenset({"AL-P1", "AL-P2", "AL-P3", "AL-P4"})
VALID_STATUSES: Final[frozenset[str]] = frozenset({"active", "acknowledged", "resolved", "silenced"})
_SEVERITY_ORDER: Final[tuple[str, ...]] = ("AL-P1", "AL-P2", "AL-P3", "AL-P4")


class AlertCenterInputError(Exception):
    """告警中心输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-ALERT-CENTER。
    """


@dataclass(frozen=True)
class AlertCenterRecord:
    """单条告警记录（DI 注入的数据源形态，与 alert_router 产出对齐）。"""

    alert_id: str
    title: str
    severity: str  # AL-P1~P4
    source: str
    status: str  # active/acknowledged/resolved/silenced
    created_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    root_cause: str = ""
    suppressed: bool = False
    escalated: bool = False
    false_positive: bool = False

    def __post_init__(self) -> None:
        if self.severity not in VALID_SEVERITIES:
            raise AlertCenterInputError(f"非法告警级别: {self.severity!r}")
        if self.status not in VALID_STATUSES:
            raise AlertCenterInputError(f"非法告警状态: {self.status!r}")
        if self.resolved_at is not None and self.resolved_at < self.created_at:
            raise AlertCenterInputError("resolved_at 早于 created_at（时间倒挂）")
        if self.acknowledged_at is not None and self.acknowledged_at < self.created_at:
            raise AlertCenterInputError("acknowledged_at 早于 created_at（时间倒挂）")


@dataclass(frozen=True)
class AlertCenterStats:
    """告警统计：在野分级计数 + MTTR + 日均 + 确认率 + 误报率。"""

    total: int
    active_by_severity: dict[str, int]
    mttr_seconds: float | None
    daily_average: float
    ack_rate: float
    false_positive_rate: float


@dataclass(frozen=True)
class AlertCenterData:
    """告警中心面板数据（stats + 6 维收敛视图 + 实时列表）。"""

    stats: AlertCenterStats
    views: dict[str, object] = field(default_factory=dict)
    active_list: tuple[AlertCenterRecord, ...] = ()


# ──────────────────────────────────────────────────────────────────────────────
# fetch：记录 → 面板数据（纯函数）
# ──────────────────────────────────────────────────────────────────────────────


def fetch_alert_center(
    records: list[AlertCenterRecord] | tuple[AlertCenterRecord, ...],
    now_utc: datetime | None = None,
    top_n_root_cause: int = 10,
) -> AlertCenterData:
    """告警记录 → 面板数据（统计 + 6 维收敛视图 + 实时列表）。"""
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    if top_n_root_cause < 1:
        raise AlertCenterInputError("top_n_root_cause 须 ≥ 1")
    recs = list(records) if records is not None else None
    if recs is None or any(not isinstance(r, AlertCenterRecord) for r in recs):
        raise AlertCenterInputError("records 须为 AlertCenterRecord 序列")

    total = len(recs)
    # ① 在野分级计数
    active_by_severity = {sev: 0 for sev in _SEVERITY_ORDER}
    for r in recs:
        if r.status == "active":
            active_by_severity[r.severity] += 1
    # ② MTTR（resolved 记录解决耗时均值）
    resolved_durations = [
        (r.resolved_at - r.created_at).total_seconds()
        for r in recs
        if r.status == "resolved" and r.resolved_at is not None
    ]
    mttr = sum(resolved_durations) / len(resolved_durations) if resolved_durations else None
    # ③ 日均告警（覆盖天数 = now − 最早 created，<1 天按 1 天）
    if recs:
        earliest = min(r.created_at for r in recs)
        coverage_days = max((now_utc - earliest).total_seconds() / 86400.0, 1e-9)
        daily_average = total / max(coverage_days, 1.0) if coverage_days < 1.0 else total / coverage_days
    else:
        daily_average = 0.0
    # ④ 确认率 / 误报率
    acked = sum(1 for r in recs if r.status in ("acknowledged", "resolved"))
    ack_rate = acked / total if total else 0.0
    fp = sum(1 for r in recs if r.false_positive)
    fp_rate = fp / total if total else 0.0

    stats = AlertCenterStats(
        total=total,
        active_by_severity=active_by_severity,
        mttr_seconds=mttr,
        daily_average=daily_average,
        ack_rate=ack_rate,
        false_positive_rate=fp_rate,
    )

    # 6 维收敛视图：时间/空间/根因/抑制/升级/静默
    by_time: dict[str, int] = {}
    by_space: dict[str, int] = {}
    by_root_cause: dict[str, int] = {}
    for r in recs:
        hour_key = r.created_at.strftime("%Y-%m-%dT%H:00")
        by_time[hour_key] = by_time.get(hour_key, 0) + 1
        by_space[r.source] = by_space.get(r.source, 0) + 1
        rc = r.root_cause or "未标注"
        by_root_cause[rc] = by_root_cause.get(rc, 0) + 1
    by_root_cause = dict(sorted(by_root_cause.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n_root_cause])
    views: dict[str, object] = {
        "by_time": dict(sorted(by_time.items())),
        "by_space": dict(sorted(by_space.items(), key=lambda kv: (-kv[1], kv[0]))),
        "by_root_cause": by_root_cause,
        "suppressed": tuple(r for r in recs if r.suppressed),
        "escalated": tuple(r for r in recs if r.escalated),
        "silenced": tuple(r for r in recs if r.status == "silenced"),
    }
    active_list = tuple(r for r in recs if r.status == "active")
    return AlertCenterData(stats=stats, views=views, active_list=active_list)


# ──────────────────────────────────────────────────────────────────────────────
# render：面板数据 → JSON 可序列化 dict payload（纯函数）
# ──────────────────────────────────────────────────────────────────────────────


def _record_to_dict(r: AlertCenterRecord) -> dict:
    return {
        "alert_id": r.alert_id,
        "title": r.title,
        "severity": r.severity,
        "source": r.source,
        "status": r.status,
        "created_at": r.created_at.isoformat(),
        "acknowledged_at": r.acknowledged_at.isoformat() if r.acknowledged_at else None,
        "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
        "root_cause": r.root_cause,
        "suppressed": r.suppressed,
        "escalated": r.escalated,
        "false_positive": r.false_positive,
    }


def render_alert_center(data: AlertCenterData) -> dict:
    """渲染告警中心面板为 dict payload（JSON 可序列化；panel 布局留装配批）。"""
    if not isinstance(data, AlertCenterData):
        raise AlertCenterInputError("data 须为 AlertCenterData")
    s = data.stats
    views = data.views
    return {
        "page": "alert_center",
        "stats": {
            "total": s.total,
            "active_by_severity": dict(s.active_by_severity),
            "mttr_seconds": s.mttr_seconds,
            "daily_average": s.daily_average,
            "ack_rate": s.ack_rate,
            "false_positive_rate": s.false_positive_rate,
        },
        "views": {
            "by_time": dict(views["by_time"]),
            "by_space": dict(views["by_space"]),
            "by_root_cause": dict(views["by_root_cause"]),
            "suppressed": [_record_to_dict(r) for r in views["suppressed"]],
            "escalated": [_record_to_dict(r) for r in views["escalated"]],
            "silenced": [_record_to_dict(r) for r in views["silenced"]],
        },
        "active_list": [_record_to_dict(r) for r in data.active_list],
    }
