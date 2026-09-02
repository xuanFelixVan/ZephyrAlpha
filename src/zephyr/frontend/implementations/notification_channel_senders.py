# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §4.1 渠道注册位扩展
# [MODULE] zephyr.frontend.implementations.notification_channel_senders
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.interface_base; zephyr.frontend.implementations.default_notification_manager
# [CONSUMERS] MOD-L08-001(register_channel 生产接线位: email/wechat 渠道) ; MOD-RPT-030(告警聚合派发通道) ; 运维自治(告警通知)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] SMTP/webhook 调用走注入位(smtp_send/http_post 可调用),未注入=未接线态 __call__ 返回 False 记 WARNING(fail-visible 不抛,本批禁真实发送); 凭据经 EmailChannelConfig/WeChatChannelConfig 注入(Owner 窗口),码内零密钥零真实端点; sender 协议对齐 MOD-L08-001(True/None=已受理,False=显式失败,传输异常内化为 False 不外抛); 配置非法 fail-closed(InvalidNotificationError); frozen dataclass,payload asdict JSON 可序列化
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/blueprint.md
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidNotificationError(ZA-FE-0004,配置非法 fail-closed); 发送失败不抛(False+日志留痕)
# [TESTS] tests/frontend/test_notification_channel_senders.py
# [A_module] module_id=MOD-L08-001_senders | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Email/WeChat 通知渠道 sender（MOD-L08-001 register_channel 生产接线位）。

55 号 §6 暂缓项"Email/WeChat sender 实发"的注册位实装：两个通道类实现
MOD-L08-001 ``NotificationSender`` 协议（``Callable[[Notification], bool | None]``），
经 ``DefaultNotificationManager.register_channel("email"/"wechat", sender)`` 接线。

传输注入位（凭据 Owner 窗口）：
  - EmailNotificationSender(smtp_send=...)：``EmailPayload -> bool | None``，
    生产侧由 Owner 窗口把 smtplib 会话适配进该可调用（含凭据读取）；
  - WeChatNotificationSender(http_post=...)：``(webhook_url, payload, timeout_s)
    -> bool | None``，生产侧适配 requests/httpx POST（企业微信机器人 webhook）。
  本模块零 smtplib/requests import、零真实发送——未注入传输=未接线态，
  __call__ 显式失败 False + WARNING 留痕（fail-visible，与 MOD-L08-001
  "sender 返回 False=显式失败"语义衔接，派发方可见未接线）。

B-011 数据边界同 MOD-L08-001：本类只转发调用方给定的 Notification 内容，
不自行附加持仓/交易明细（脱敏责任在调用方）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Final

from zephyr.frontend.implementations.default_notification_manager import (
    InvalidNotificationError,
)
from zephyr.frontend.interface_base import Notification

_logger = logging.getLogger(__name__)

__all__: Final = [
    "EmailChannelConfig",
    "EmailNotificationSender",
    "EmailPayload",
    "SmtpSendTransport",
    "WebhookPostTransport",
    "WeChatChannelConfig",
    "WeChatNotificationSender",
]

#: SMTP 传输注入位签名（生产接线 smtplib 适配，测试 mock）
SmtpSendTransport = Callable[["EmailPayload"], "bool | None"]

#: webhook 传输注入位签名：(url, payload, timeout_s)（生产接线 requests/httpx，测试 mock）
WebhookPostTransport = Callable[[str, Mapping[str, Any], float], "bool | None"]


def _require_non_empty(field: str, value: str) -> str:
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise InvalidNotificationError(f"{field} 不允许为空", details={"field": field})
    return text


def _require_positive(field: str, value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise InvalidNotificationError(f"{field} 必须为正数", details={"field": field, "value": repr(value)})
    return float(value)


def _level_text(notification: Notification) -> str:
    """level 枚举/裸字符串兼容（与 MOD-RPT-030 适配器同口径）。"""
    return str(getattr(notification.level, "value", notification.level))


# ----------------------------------------------------------------------
# Email 渠道
# ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EmailChannelConfig:
    """邮件渠道配置（凭据 Owner 窗口注入，码内零密钥）。

    fail-closed 校验（__post_init__）：空 host/from/to、to_addrs 含空项、
    端口越界（须 1-65535）、超时非正一律 InvalidNotificationError。
    """

    host: str
    from_addr: str
    to_addrs: tuple[str, ...]
    port: int = 465
    username: str = ""
    password: str = ""
    use_tls: bool = True
    timeout_s: float = 10.0

    def __post_init__(self) -> None:
        _require_non_empty("host", self.host)
        _require_non_empty("from_addr", self.from_addr)
        if not self.to_addrs:
            raise InvalidNotificationError("to_addrs 不允许为空", details={"field": "to_addrs"})
        for addr in self.to_addrs:
            _require_non_empty("to_addrs 项", addr)
        if not isinstance(self.port, int) or isinstance(self.port, bool) or not (0 < self.port < 65536):
            raise InvalidNotificationError(
                "port 越界（须 1-65535）", details={"field": "port", "value": repr(self.port)}
            )
        _require_positive("timeout_s", self.timeout_s)


@dataclass(frozen=True, slots=True)
class EmailPayload:
    """SMTP 传输注入位契约（生产适配层据此发信）。"""

    host: str
    port: int
    username: str
    password: str
    use_tls: bool
    timeout_s: float
    from_addr: str
    to_addrs: tuple[str, ...]
    subject: str
    text: str


class EmailNotificationSender:
    """邮件通知渠道（MOD-L08-001 注册位 sender 协议实现）。

    Args:
        config: 渠道配置（fail-closed 校验见 EmailChannelConfig）。
        smtp_send: SMTP 传输注入位；None=未接线态（__call__ 显式失败 False）。
    """

    def __init__(
        self,
        config: EmailChannelConfig,
        smtp_send: SmtpSendTransport | None = None,
    ) -> None:
        self._config = config
        self._smtp_send = smtp_send

    def __call__(self, notification: Notification) -> bool:
        """发送一封告警邮件。False=显式失败（未接线/传输拒/传输异常）。"""
        if self._smtp_send is None:
            _logger.warning(
                "EMAIL_CHANNEL_UNWIRED title=%s（SMTP 传输未注入，Owner 窗口接线位）",
                notification.title,
            )
            return False
        cfg = self._config
        payload = EmailPayload(
            host=cfg.host.strip(),
            port=cfg.port,
            username=cfg.username,
            password=cfg.password,
            use_tls=cfg.use_tls,
            timeout_s=cfg.timeout_s,
            from_addr=cfg.from_addr.strip(),
            to_addrs=tuple(a.strip() for a in cfg.to_addrs),
            subject=f"[{_level_text(notification)}] {notification.title}",
            text=f"来源: {notification.source_layer}\n\n{notification.body}",
        )
        try:
            outcome = self._smtp_send(payload)
        except Exception as exc:  # noqa: BLE001 — 传输异常内化为显式失败（sender 协议）
            _logger.error("EMAIL_SEND_ERROR error=%s", exc)
            return False
        return outcome is not False


# ----------------------------------------------------------------------
# WeChat 渠道（企业微信机器人 webhook）
# ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WeChatChannelConfig:
    """企业微信机器人渠道配置（webhook_url 含 key，Owner 窗口注入）。

    fail-closed 校验（__post_init__）：空 url / 非 http(s) scheme /
    超时非正一律 InvalidNotificationError。
    """

    webhook_url: str
    timeout_s: float = 10.0

    def __post_init__(self) -> None:
        url = _require_non_empty("webhook_url", self.webhook_url)
        if not url.startswith(("http://", "https://")):
            raise InvalidNotificationError(
                "webhook_url 须为 http(s) 地址",
                details={"field": "webhook_url", "value": url},
            )
        _require_positive("timeout_s", self.timeout_s)


class WeChatNotificationSender:
    """企业微信机器人通知渠道（markdown 消息，注册位 sender 协议实现）。

    Args:
        config: 渠道配置（fail-closed 校验见 WeChatChannelConfig）。
        http_post: webhook 传输注入位；None=未接线态（__call__ 显式失败 False）。
    """

    def __init__(
        self,
        config: WeChatChannelConfig,
        http_post: WebhookPostTransport | None = None,
    ) -> None:
        self._config = config
        self._http_post = http_post

    def __call__(self, notification: Notification) -> bool:
        """推送一条企业微信 markdown 消息。False=显式失败。"""
        if self._http_post is None:
            _logger.warning(
                "WECHAT_CHANNEL_UNWIRED title=%s（webhook 传输未注入，Owner 窗口接线位）",
                notification.title,
            )
            return False
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": (
                    f"**[{_level_text(notification)}] {notification.title}**\n"
                    f"> 来源: {notification.source_layer}\n\n"
                    f"{notification.body}"
                )
            },
        }
        try:
            outcome = self._http_post(self._config.webhook_url.strip(), payload, float(self._config.timeout_s))
        except Exception as exc:  # noqa: BLE001 — 传输异常内化为显式失败（sender 协议）
            _logger.error("WECHAT_SEND_ERROR error=%s", exc)
            return False
        return outcome is not False
