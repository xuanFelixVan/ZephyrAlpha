# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §4.1
# [MODULE] zephyr.frontend.implementations.default_notification_manager
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.interface_base; zephyr.shared.foundation.errors
# [CONSUMERS] D_RISK(风控告警分发) ; D_COMPLIANCE(合规告警) ; 运维自治(告警通知)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] log渠道内建恒可用; send全部渠道成功才返回True(部分失败=False); 未知渠道计失败不抛错; sender异常容错(记ERROR,该渠道计失败); sender返回False=显式失败,其余返回值(含None)视为已受理; 重复注册同名渠道→InvalidNotificationError; 空title通知→InvalidNotificationError
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidNotificationError
# [TESTS] tests/frontend/test_default_notification_manager.py
# [A_module] module_id=MOD-L08-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Default Notification Manager — 默认通知管理器 (MOD-L08-001 步骤1)

NotificationManagerBase 的具体实现（蓝图 §4.1 / §16 步骤1：
send 返回 bool，channels 返回 list[str]）。

渠道模型（OCP）：
  - log     内建渠道（logging 输出，恒可用，无需外部依赖）
  - 外部渠道  register_channel(name, sender) 注入——微信通知能力③的生产接线位
            （sender 协议: Callable[[Notification], bool | None]；
             返回 False=显式失败，其余返回值含 None 视为已受理；异常容错计失败）
B-011 数据边界：本管理器只分发调用方给定的 Notification 内容，
不自行附加持仓/交易明细（脱敏责任在调用方）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Final

from zephyr.frontend.interface_base import Notification, NotificationManagerBase
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "DefaultNotificationManager",
    "InvalidNotificationError",
    "NotificationSender",
]

#: 通知发送器协议（True/None=已受理, False=显式失败, 异常=失败）
NotificationSender = Callable[[Notification], "bool | None"]


class InvalidNotificationError(ZephyrBaseError):
    """通知/渠道注册非法（空标题、重复渠道名等）。"""

    error_code = "ZA-FE-0004"


class DefaultNotificationManager(NotificationManagerBase):
    """默认通知分发管理器（log 内建 + 外部渠道注册）。"""

    def __init__(self) -> None:
        self._channels: dict[str, NotificationSender] = {"log": self._send_log}

    @staticmethod
    def _send_log(notification: Notification) -> bool:
        _logger.info(
            "NOTIFICATION level=%s source=%s title=%s body=%s",
            notification.level,
            notification.source_layer,
            notification.title,
            notification.body,
        )
        return True

    def register_channel(self, name: str, sender: NotificationSender) -> None:
        """注册外部通知渠道（微信等生产接线位）。

        Raises:
            InvalidNotificationError: 渠道名为空 / 与既有渠道重名 / sender 不可调用。
        """
        name = name.strip()
        if not name:
            raise InvalidNotificationError("渠道名不允许为空", details={})
        if name in self._channels:
            raise InvalidNotificationError(
                f"渠道已注册: {name}（禁止覆盖既有渠道）",
                details={"channel": name},
            )
        if not callable(sender):
            raise InvalidNotificationError(f"渠道 sender 不可调用: {name}", details={"channel": name})
        self._channels[name] = sender

    def channels(self) -> list[str]:
        """返回可用通知渠道列表。"""
        return sorted(self._channels)

    def send(self, notification: Notification, channels: list[str] | None = None) -> bool:
        """发送通知到指定渠道（None=全渠道），返回是否全部成功。"""
        if not notification.title.strip():
            raise InvalidNotificationError(
                "通知标题不允许为空", details={"notification_id": notification.notification_id}
            )
        targets = channels if channels is not None else self.channels()
        all_ok = True
        for name in targets:
            sender = self._channels.get(name)
            if sender is None:
                _logger.error("NOTIFICATION_CHANNEL_UNKNOWN channel=%s", name)
                all_ok = False
                continue
            try:
                outcome = sender(notification)
            except Exception as exc:  # noqa: BLE001 — 单渠道故障不影响其余渠道
                _logger.error("NOTIFICATION_SEND_ERROR channel=%s error=%s", name, exc)
                all_ok = False
                continue
            if outcome is False:
                _logger.warning("NOTIFICATION_SEND_REJECTED channel=%s", name)
                all_ok = False
        return all_ok
