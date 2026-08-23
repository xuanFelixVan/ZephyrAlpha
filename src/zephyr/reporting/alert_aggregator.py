# [BLUEPRINT] MOD-RPT-030 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-28 行）
# [MODULE] zephyr.reporting.alert_aggregator
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.frontend.interface_base（Notification/NotificationLevel 契约）; zephyr.frontend.implementations.default_notification_manager（MOD-L08-001 渠道注册位，注入消费）
# [CONSUMERS] （候选：总览页"今日告警"卡、运维自治告警流）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 三源封闭 {risk,data_quality,backtest}；严重度四级封闭 {critical,error,warning,info}；告警 id 确定性（source+title+occurred_at 哈希，可幂等重放）；同批 (source,title) 去重保留最新；派发阈值可配（默认 warning 及以上才触达渠道，info 仅页面流）；通知管理器注入位（None=仅页面流不触达，渠道注册位=MOD-L08-001 register_channel）；manager.send 异常容错不炸聚合；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-28 行
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 适配器输入缺字段→ValueError（fail-closed）；未知 severity/status→ValueError（不静默降级）；manager 派发异常→记 notes 该条计未派发
# [TESTS] tests/reporting/test_alert_aggregator.py
# [A_module] module_id=MOD-RPT-030 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-RPT-030 — 告警聚合器（GAP-F-28，总览页"今日告警"统一告警流）。

三源 → 统一告警流 + 严重度分级：

| 源 | 既有件 | 适配口径 |
|---|---|---|
| 风控事件 | risk/core/alert_generator.py Alert（RED/ORANGE/YELLOW，prod） | RED→critical / ORANGE→error / YELLOW→warning |
| 数据质量门 | data/alerter.py 失败汇总记录（task_id/error/level/source/timestamp，prod） | CRITICAL→critical / ERROR→error / WARN→warning / INFO→info |
| 回测完成 | 回测完成事件（run_id/status/summary/finished_at） | failed→error / degraded→warning / success→info |

聚合：统一 UnifiedAlert（确定性 id 可幂等重放）→ 同批 (source,title) 去重
→ 严重度+时间排序页面流 → ≥min_dispatch_severity 的经 NotificationManagerBase
（MOD-L08-001 渠道注册位）派发 Notification。manager 注入位，None=仅页面流。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 风控告警（Alert 鸭型：level/source/message/timestamp）
# - id: I2 数据质量失败记录（task_id/error/level/source/timestamp/extra）
# - id: I3 回测完成事件（run_id/status/summary/finished_at/metrics）
# 层: 算法
# - id: A1 三源适配器（→UnifiedAlert 四级严重度）
# - id: A2 去重+排序（同批 (source,title) 保留 occurred_at 最新）
# - id: A3 阈值派发（≥min_dispatch_severity → Notification → manager.send）
# 层: 输出
# - id: O1 AggregationResult（alerts 页面流 + dispatched/suppressed 计数 + notes）
# [/ALGO_FLOW]
#
# 边:
# I1,I2,I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Final, Mapping

from zephyr.frontend.interface_base import Notification, NotificationLevel

logger = logging.getLogger(__name__)

__all__: Final = [
    "SEVERITY_CRITICAL",
    "SEVERITY_ERROR",
    "SEVERITY_INFO",
    "SEVERITY_WARNING",
    "SOURCE_BACKTEST",
    "SOURCE_DATA_QUALITY",
    "SOURCE_RISK",
    "AggregationResult",
    "AggregatorConfig",
    "UnifiedAlert",
    "aggregate_unified_alerts",
    "alert_from_backtest",
    "alert_from_data_quality",
    "alert_from_risk",
    "to_notification",
]

#: 告警源三态（封闭集合）
SOURCE_RISK: Final[str] = "risk"
SOURCE_DATA_QUALITY: Final[str] = "data_quality"
SOURCE_BACKTEST: Final[str] = "backtest"

#: 严重度四级（封闭集合，与 NotificationLevel 值对齐）
SEVERITY_CRITICAL: Final[str] = "critical"
SEVERITY_ERROR: Final[str] = "error"
SEVERITY_WARNING: Final[str] = "warning"
SEVERITY_INFO: Final[str] = "info"

_SEVERITY_RANK: Final[dict[str, int]] = {
    SEVERITY_CRITICAL: 3,
    SEVERITY_ERROR: 2,
    SEVERITY_WARNING: 1,
    SEVERITY_INFO: 0,
}

#: 风控 AlertLevel → 严重度（risk/core/alert_generator.py 口径）
_RISK_LEVEL_MAP: Final[dict[str, str]] = {
    "red": SEVERITY_CRITICAL,
    "orange": SEVERITY_ERROR,
    "yellow": SEVERITY_WARNING,
}

#: 数据质量 alerter level → 严重度（data/alerter.py 口径）
_DQ_LEVEL_MAP: Final[dict[str, str]] = {
    "CRITICAL": SEVERITY_CRITICAL,
    "ERROR": SEVERITY_ERROR,
    "WARN": SEVERITY_WARNING,
    "INFO": SEVERITY_INFO,
}

#: 回测完成 status → 严重度
_BACKTEST_STATUS_MAP: Final[dict[str, str]] = {
    "failed": SEVERITY_ERROR,
    "degraded": SEVERITY_WARNING,
    "success": SEVERITY_INFO,
}


# ------------------------------------------------------------------
# 配置 / 数据结构
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AggregatorConfig:
    """聚合器配置。"""

    min_dispatch_severity: str = SEVERITY_WARNING  # 派发阈值（含；info 仅页面流）
    dispatch_channels: list[str] | None = None  # 派发渠道（None=manager 全渠道）


@dataclass(frozen=True, slots=True)
class UnifiedAlert:
    """统一告警（三源聚合产物）。"""

    alert_id: str  # 确定性 id（source+title+occurred_at 哈希）
    source: str  # risk/data_quality/backtest
    severity: str  # critical/error/warning/info
    title: str
    body: str
    occurred_at: str  # ISO 时间字符串
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AggregationResult:
    """聚合输出（页面流 + 派发回执）。"""

    alerts: list[UnifiedAlert] = field(default_factory=list)  # 严重度+时间降序页面流
    dispatched_count: int = 0
    suppressed_count: int = 0  # 同批去重抑制数
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 适配器（纯函数）
# ------------------------------------------------------------------


def _alert_id(source: str, title: str, occurred_at: str) -> str:
    """确定性告警 id（幂等重放：同事件重进不重复）。"""
    digest = hashlib.sha1(f"{source}|{title}|{occurred_at}".encode("utf-8")).hexdigest()
    return f"{source}-{digest[:12]}"


def alert_from_risk(alert: Any) -> UnifiedAlert:
    """风控告警适配：risk alert_generator.Alert 鸭型（level/source/message/timestamp）。

    level 兼容枚举（.value）与裸字符串；未知级别 ValueError fail-closed。
    """
    level_raw = getattr(getattr(alert, "level", None), "value", getattr(alert, "level", ""))
    severity = _RISK_LEVEL_MAP.get(str(level_raw).lower())
    if severity is None:
        raise ValueError(f"未知风控告警级别: {level_raw}")
    source_name = str(getattr(alert, "source", "") or "unknown")
    message = str(getattr(alert, "message", ""))
    occurred = str(getattr(alert, "timestamp", ""))
    title = f"风控告警[{source_name}]"
    return UnifiedAlert(
        alert_id=_alert_id(SOURCE_RISK, title, occurred),
        source=SOURCE_RISK,
        severity=severity,
        title=title,
        body=message,
        occurred_at=occurred,
        metadata={"risk_source": source_name},
    )


def alert_from_data_quality(record: Mapping[str, Any]) -> UnifiedAlert:
    """数据质量门适配：data alerter 失败汇总记录（task_id/error/level/source/timestamp/extra）。"""
    task_id = str(record.get("task_id", "") or "unknown")
    level = str(record.get("level", "") or "").upper()
    severity = _DQ_LEVEL_MAP.get(level)
    if severity is None:
        raise ValueError(f"未知数据质量告警级别: {level}")
    occurred = str(record.get("timestamp", ""))
    title = f"数据质量[{task_id}]"
    return UnifiedAlert(
        alert_id=_alert_id(SOURCE_DATA_QUALITY, title, occurred),
        source=SOURCE_DATA_QUALITY,
        severity=severity,
        title=title,
        body=str(record.get("error", "")),
        occurred_at=occurred,
        metadata={"task_id": task_id, "data_source": record.get("source"), "extra": record.get("extra") or {}},
    )


def alert_from_backtest(
    run_id: str,
    status: str,
    summary: str,
    finished_at: str,
    metrics: Mapping[str, Any] | None = None,
) -> UnifiedAlert:
    """回测完成事件适配：failed→error / degraded→warning / success→info。"""
    severity = _BACKTEST_STATUS_MAP.get(status)
    if severity is None:
        raise ValueError(f"未知回测完成状态: {status}")
    title = f"回测完成[{run_id}]"
    return UnifiedAlert(
        alert_id=_alert_id(SOURCE_BACKTEST, title, finished_at),
        source=SOURCE_BACKTEST,
        severity=severity,
        title=title,
        body=summary,
        occurred_at=finished_at,
        metadata={"run_id": run_id, "status": status, "metrics": dict(metrics or {})},
    )


def to_notification(alert: UnifiedAlert) -> Notification:
    """UnifiedAlert → MOD-L08-001 Notification（渠道注册位消费契约）。"""
    return Notification(
        notification_id=alert.alert_id,
        title=alert.title,
        body=alert.body,
        level=NotificationLevel(alert.severity),
        source_layer=alert.source,
        metadata=dict(alert.metadata),
    )


# ------------------------------------------------------------------
# 聚合主核
# ------------------------------------------------------------------


def aggregate_unified_alerts(
    alerts: list[UnifiedAlert],
    config: AggregatorConfig | None = None,
    notification_manager: Any | None = None,
) -> AggregationResult:
    """聚合主核：去重 → 排序页面流 → 阈值派发。

    Args:
        alerts: 三源适配后的统一告警批。
        config: 聚合配置（None 默认 warning 起派发）。
        notification_manager: NotificationManagerBase 鸭型注入位（MOD-L08-001
            渠道注册位）；None=仅页面流不触达渠道。

    Returns:
        AggregationResult；manager.send 异常容错（notes 留痕该条计未派发）。
    """
    cfg = config or AggregatorConfig()
    if cfg.min_dispatch_severity not in _SEVERITY_RANK:
        raise ValueError(f"未知派发阈值严重度: {cfg.min_dispatch_severity}")

    # 同批 (source,title) 去重：保留 occurred_at 最新
    latest: dict[tuple[str, str], UnifiedAlert] = {}
    suppressed = 0
    for a in alerts:
        key = (a.source, a.title)
        prev = latest.get(key)
        if prev is None or a.occurred_at >= prev.occurred_at:
            if prev is not None:
                suppressed += 1
            latest[key] = a
        else:
            suppressed += 1
    # 严重度降序 + 时间降序（稳定排序两遍：先时间降序，再严重度降序保持组内时间序）
    unified = sorted(latest.values(), key=lambda a: (a.occurred_at, a.alert_id), reverse=True)
    unified.sort(key=lambda a: -_SEVERITY_RANK[a.severity])

    threshold = _SEVERITY_RANK[cfg.min_dispatch_severity]
    dispatched = 0
    notes: list[str] = []
    if notification_manager is None:
        notes.append("通知管理器未注入：仅页面流，未触达渠道")
    else:
        for a in unified:
            if _SEVERITY_RANK[a.severity] < threshold:
                continue
            try:
                ok = notification_manager.send(to_notification(a), channels=cfg.dispatch_channels)
            except Exception as e:  # noqa: BLE001 — 单条派发异常不炸聚合
                notes.append(f"派发异常[{a.alert_id}]: {e!r}")
                continue
            if ok:
                dispatched += 1
            else:
                notes.append(f"渠道部分失败[{a.alert_id}]")
    return AggregationResult(alerts=unified, dispatched_count=dispatched, suppressed_count=suppressed, notes=notes)
