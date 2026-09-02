# [BLUEPRINT] MOD-FE-004 | docs/03_modules/_domain_frontend/notification_router/blueprint.md
# [MODULE] zephyr.frontend.notification_router
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（协议核心纯内存；通道发送器/时钟全注入，密钥仅 secrets 引用不落地）
# [CONSUMERS] 运行时装配批（alert_manager 挂接 / 企业微信·飞书 webhook 发送器装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 严重级词表闭合(info|warning|critical); 通道词表闭合(wecom|feishu); secret_ref 仅 secrets:// 引用(明文URL拒绝); 静默时段内非 critical 抑制(critical 不静默); 超时未 ack 升级更严重通道(单次升级不循环); 投递 best-effort(发送器异常记失败不阻断); 时钟全注入; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/notification_router/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] NotificationRouterError(占位 ZA-FE-UNREGISTERED-NOTIFICATION-ROUTER)——非法严重级/通道/明文密钥引用/空通知字段/未知通知ack/非法静默窗/非法ack超时时抛
# [TESTS] tests/frontend/test_notification_router.py
# [A_module] module_id=MOD-FE-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""NotificationRouter — 通知路由器（MOD-FE-004）。

B1-00138（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-004，C2 D-FE-13）：
Alertmanager 路由思想——**严重级→通道路由表** + **通道适配**（企业微信/飞书
webhook 发送器注入，密钥入 secrets 引用不落地）+ **静默时段**（注入时钟，
critical 不静默）+ **未确认升级**（超时未 ack 升级更严重通道，单次不循环）
+ 与 alert_manager 挂接语义（Notification 入站载荷）。

查重分工：alert_senders=实发传输层（本件复用其 sender 语义经 ChannelBinding
注入，不重建传输）；alert_manager/alert_router=告警分级与站内路由（本件=
外部 IM 通道路由与升级策略，不重复站内收敛）。
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChannelBinding",
    "DeliveryRecord",
    "EscalationRecord",
    "Notification",
    "NotificationChannel",
    "NotificationRouter",
    "NotificationRouterError",
    "RouteDecision",
    "Severity",
    "SilentWindow",
]

#: 密钥引用唯一合法协议头（密钥不落地，仅 secrets 引用）
_SECRET_SCHEME: Final[str] = "secrets://"

#: 严重级序号（升级语义按序号增大）
_SEVERITY_RANK: Final[dict["Severity", int]] = {}


class NotificationRouterError(Exception):
    """通知路由输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-NOTIFICATION-ROUTER。
    """


class Severity(str, Enum):
    """通知严重级（词表闭合，序号越大越严重）。"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


_SEVERITY_RANK.update(
    {
        Severity.INFO: 0,
        Severity.WARNING: 1,
        Severity.CRITICAL: 2,
    }
)


class NotificationChannel(str, Enum):
    """通知通道（词表闭合：企业微信/飞书 webhook）。"""

    WECOM = "wecom"
    FEISHU = "feishu"


@dataclass(frozen=True)
class ChannelBinding:
    """通道适配绑定：注入发送器 + secrets 引用（密钥不落地）。"""

    channel: NotificationChannel
    secret_ref: str
    sender: Callable[["Notification", "ChannelBinding"], bool]


@dataclass(frozen=True)
class SilentWindow:
    """静默时段（日内分钟区间；start_minute > end_minute 表示跨午夜）。"""

    start_minute: int
    end_minute: int


@dataclass(frozen=True)
class Notification:
    """入站通知（alert_manager 挂接载荷，frozen）。"""

    title: str
    content: str
    severity: Severity
    source: str


@dataclass(frozen=True)
class DeliveryRecord:
    """单通道投递留痕（best-effort：ok=False 不阻断主链路）。"""

    notification_id: str
    channel: NotificationChannel
    ok: bool
    detail: str
    escalated: bool
    sent_at: datetime.datetime


@dataclass(frozen=True)
class RouteDecision:
    """路由决策回执（notify 返回，frozen）。"""

    notification_id: str
    severity: Severity
    channels: tuple[NotificationChannel, ...]
    suppressed: bool
    deliveries: tuple[DeliveryRecord, ...]


@dataclass(frozen=True)
class EscalationRecord:
    """未确认升级留痕（超时未 ack → 更严重通道）。"""

    notification_id: str
    severity: Severity
    channels: tuple[NotificationChannel, ...]
    deliveries: tuple[DeliveryRecord, ...]
    escalated_at: datetime.datetime


class NotificationRouter:
    """通知路由器（严重级→通道路由 + 静默时段 + 未确认升级）。

    Args:
        route_table: 严重级 → 通道路由表（按序投递）。
        bindings: 通道适配绑定（发送器注入 + secrets 引用）。
        escalation_table: 严重级 → 超时未 ack 时的升级通道表（可空）。
        silent_windows: 静默时段序列（注入时钟判定；critical 不静默）。
        clock: 时钟注入（确定性判定）。
        ack_timeout: 确认超时（正 timedelta）。
    """

    def __init__(
        self,
        *,
        route_table: Mapping[Severity, tuple[NotificationChannel, ...]],
        bindings: Mapping[NotificationChannel, ChannelBinding],
        escalation_table: Mapping[Severity, tuple[NotificationChannel, ...]] | None = None,
        silent_windows: Sequence[SilentWindow] = (),
        clock: Callable[[], datetime.datetime] | None = None,
        ack_timeout: datetime.timedelta = datetime.timedelta(minutes=5),
    ) -> None:
        if not route_table:
            raise NotificationRouterError("route_table 为空（无严重级→通道路由）")
        if not bindings:
            raise NotificationRouterError("bindings 为空（无通道适配绑定）")
        for channel, binding in bindings.items():
            if not isinstance(channel, NotificationChannel):
                raise NotificationRouterError(f"非法通道: {channel!r}")
            if not isinstance(binding, ChannelBinding):
                raise NotificationRouterError(f"通道绑定类型非法: {binding!r}")
            if binding.channel is not channel:
                raise NotificationRouterError(f"通道绑定不一致: key={channel!r} binding={binding.channel!r}")
            self._validate_secret_ref(binding.secret_ref)
            if not callable(binding.sender):
                raise NotificationRouterError(f"通道 {channel.value} 发送器不可调用")
        for severity, channels in route_table.items():
            self._validate_route(severity, channels, bindings)
        esc = dict(escalation_table or {})
        for severity, channels in esc.items():
            self._validate_route(severity, channels, bindings)
        if isinstance(silent_windows, (str, bytes)):
            raise NotificationRouterError("silent_windows 类型非法")
        for window in silent_windows:
            if not isinstance(window, SilentWindow):
                raise NotificationRouterError(f"静默窗类型非法: {window!r}")
            for minute in (window.start_minute, window.end_minute):
                if not isinstance(minute, int) or isinstance(minute, bool) or not 0 <= minute < 1440:
                    raise NotificationRouterError(f"静默窗分钟非法: {minute!r}（须 0..1439）")
        if not isinstance(ack_timeout, datetime.timedelta) or ack_timeout <= datetime.timedelta(0):
            raise NotificationRouterError("ack_timeout 非法（须为正 timedelta）")
        self._route: dict[Severity, tuple[NotificationChannel, ...]] = {s: tuple(cs) for s, cs in route_table.items()}
        self._esc: dict[Severity, tuple[NotificationChannel, ...]] = {s: tuple(cs) for s, cs in esc.items()}
        self._bindings = dict(bindings)
        self._silent = tuple(silent_windows)
        self._clock = clock or datetime.datetime.now
        self._ack_timeout = ack_timeout
        self._counter = 0
        # notification_id -> (通知, 确认截止, 是否已升级)
        self._pending: dict[str, tuple[Notification, datetime.datetime, bool]] = {}
        self._acked: set[str] = set()
        self._suppressed: list[Notification] = []
        self._history: list[DeliveryRecord] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_secret_ref(secret_ref: str) -> None:
        if not isinstance(secret_ref, str) or not secret_ref:
            raise NotificationRouterError("secret_ref 为空")
        if not secret_ref.startswith(_SECRET_SCHEME) or len(secret_ref) <= len(_SECRET_SCHEME):
            raise NotificationRouterError(f"secret_ref 非法: {secret_ref!r}（密钥仅 {_SECRET_SCHEME} 引用，不落地）")
        if "http" in secret_ref.lower():
            raise NotificationRouterError(f"secret_ref 疑似明文 URL: {secret_ref!r}（禁止落地）")

    @staticmethod
    def _validate_route(
        severity: Severity,
        channels: tuple[NotificationChannel, ...],
        bindings: Mapping[NotificationChannel, ChannelBinding],
    ) -> None:
        if not isinstance(severity, Severity):
            raise NotificationRouterError(f"非法严重级: {severity!r}")
        if isinstance(channels, (str, bytes)) or not channels:
            raise NotificationRouterError(f"严重级 {severity.value} 路由通道为空")
        for channel in channels:
            if not isinstance(channel, NotificationChannel):
                raise NotificationRouterError(f"非法通道: {channel!r}")
            if channel not in bindings:
                raise NotificationRouterError(f"通道 {channel.value} 未绑定发送器")

    def _in_silent(self, now: datetime.datetime) -> bool:
        minute = now.hour * 60 + now.minute
        for window in self._silent:
            start, end = window.start_minute, window.end_minute
            if start <= end:
                if start <= minute < end:
                    return True
            elif minute >= start or minute < end:  # 跨午夜
                return True
        return False

    def _deliver(
        self,
        notification_id: str,
        notification: Notification,
        channel: NotificationChannel,
        now: datetime.datetime,
        *,
        escalated: bool,
    ) -> DeliveryRecord:
        binding = self._bindings[channel]
        try:
            ok = bool(binding.sender(notification, binding))
            detail = "sent" if ok else "send_failed"
        except Exception:  # noqa: BLE001 — 投递 best-effort，发送器异常不阻断
            _log.exception("通道发送器异常: %s -> %s", notification_id, channel.value)
            ok, detail = False, "sender_exception"
        if not ok:
            _log.warning("通知投递失败: %s -> %s (%s)", notification_id, channel.value, detail)
        record = DeliveryRecord(
            notification_id=notification_id,
            channel=channel,
            ok=ok,
            detail=detail,
            escalated=escalated,
            sent_at=now,
        )
        self._history.append(record)
        return record

    # ── 路由 ─────────────────────────────────────────────────────────────

    def notify(self, notification: Notification) -> RouteDecision:
        """路由：校验 → 静默判定（critical 不静默）→ 按路由表投递 → 登记待确认。"""
        if not isinstance(notification, Notification):
            raise NotificationRouterError(f"通知类型非法: {notification!r}")
        if not isinstance(notification.severity, Severity):
            raise NotificationRouterError(f"严重级非法: {notification.severity!r}")
        for field_name, value in (
            ("title", notification.title),
            ("content", notification.content),
            ("source", notification.source),
        ):
            if not isinstance(value, str) or not value:
                raise NotificationRouterError(f"通知字段 {field_name} 为空")
        now = self._clock()
        notification_id = f"ntf-{self._counter:06d}"
        self._counter += 1
        if notification.severity is not Severity.CRITICAL and self._in_silent(now):
            self._suppressed.append(notification)
            _log.info("通知静默抑制: %s (%s)", notification_id, notification.title)
            return RouteDecision(notification_id, notification.severity, (), True, ())
        channels = self._route[notification.severity]
        deliveries = tuple(self._deliver(notification_id, notification, ch, now, escalated=False) for ch in channels)
        self._pending[notification_id] = (notification, now + self._ack_timeout, False)
        return RouteDecision(notification_id, notification.severity, channels, False, deliveries)

    # ── 确认 / 升级 ───────────────────────────────────────────────────────

    def ack(self, notification_id: str) -> bool:
        """确认：首次 ack=True；重复 ack=False；未知通知 Fail-Closed。"""
        if notification_id in self._acked:
            return False
        entry = self._pending.pop(notification_id, None)
        if entry is None:
            raise NotificationRouterError(f"未知通知: {notification_id!r}")
        self._acked.add(notification_id)
        return True

    def check_escalations(self) -> tuple[EscalationRecord, ...]:
        """未确认升级：超时未 ack → 升级通道投递（单次升级不循环）。"""
        now = self._clock()
        records: list[EscalationRecord] = []
        for notification_id in sorted(self._pending):
            notification, deadline, escalated = self._pending[notification_id]
            if escalated or now < deadline:
                continue
            channels = self._esc.get(notification.severity, ())
            self._pending[notification_id] = (notification, deadline, True)
            if not channels:
                _log.warning("通知 %s 超时未 ack 且无升级通道，标记已升级不再重试", notification_id)
                continue
            deliveries = tuple(self._deliver(notification_id, notification, ch, now, escalated=True) for ch in channels)
            records.append(EscalationRecord(notification_id, notification.severity, channels, deliveries, now))
        return tuple(records)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def pending_acks(self) -> tuple[str, ...]:
        """待确认通知 id（确定性排序）。"""
        return tuple(sorted(self._pending))

    def suppressed(self) -> tuple[Notification, ...]:
        """静默抑制通知序列（按抑制先后）。"""
        return tuple(self._suppressed)

    def history(self) -> tuple[DeliveryRecord, ...]:
        """全部投递留痕（按投递先后）。"""
        return tuple(self._history)
