# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.alerts.alert_senders
# [DOMAIN] D_SHARED
# [DEPENDENCIES] stdlib(smtplib/email/urllib/json/logging)
# [CONSUMERS] zephyr.risk.core.alert_generator(EmailChannel/WeChatChannel sender 注入); zephyr.reporting.report_publisher(WEBHOOK/EMAIL sender 注入)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 默认不启用(显式构造+注入才生效, 不替换现有 no-op 默认); best-effort(发送失败/异常返回 False 不抛, 不阻断告警/归档主链路); 不落盘不日志输出凭据(password/webhook_url 脱敏); 传输层可注入(测试零网络)
# [MODIFY-GUARD] 55_monitoring_review.md §3.3/§6; 54_reconciliation_attribution.md §3.7
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/shared/alerts/test_alert_senders.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: webhook_url(企业微信机器人) / SMTP(host/port/username/password/from/to) 配置 + http_post/smtp_factory 传输注入(测试逃生门)
# I2: 待发内容(alert 对象/report 对象/纯文本)——duck-typing getattr 取字段, 不 import 上层域(防 shared→risk/reporting 反向依赖)
# F1: WeChatWebhookSender.send_markdown(content)——企业微信 markdown 消息 POST, status_code==200 且 errcode==0 为送达
# F2: EmailSmtpSender.send_mail(subject, body)——SMTP_SSL/STARTTLS 发送, 异常即 False
# F3: as_alert_sender()/as_report_sender()——适配 alert_generator.Alert / report_publisher.ArchivedReport 的可调用门面
# O1: bool 送达结果(False=软失败, 调用方记 FAILED/告警不阻断)
# [/ALGO_FLOW]
"""D_SHARED — Email/WeChat 实发 sender（55 号 §6 暂缓项施工，AI-NIGHT-001 包P）。

55 号 §3.3/§6 裁定：Email/WeChat sender 原为 no-op 占位，首批策略实盘上线前
必须注入实现。本模块提供**可注入实发**（显式构造 + 注入才生效，默认不启用、
不替换任何现有 no-op 默认）：

  - WeChatWebhookSender：企业微信机器人 webhook（markdown 消息）；
  - EmailSmtpSender：SMTP（SSL/STARTTLS）邮件。

不变量：best-effort——发送失败/网络异常返回 False 不抛（告警分级"日志必达、
外部通道 best-effort 不阻断"，55 号 §3.1B）；凭据不日志不落盘；传输层
（http_post / smtp_factory）可注入，测试零网络。

用法（alert_generator 通道注入）：
    sender = WeChatWebhookSender(webhook_url="https://qyapi.weixin.qq.com/...")
    EmailChannel(sender=EmailSmtpSender(...).as_alert_sender())
    WeChatChannel(sender=sender.as_alert_sender())
用法（ReportPublisher 渠道注入）：
    ReportPublisher(webhook_sender=sender.as_report_sender(),
                    email_sender=EmailSmtpSender(...).as_report_sender())
"""

from __future__ import annotations

import json
import logging
import smtplib
import urllib.request
from email.mime.text import MIMEText
from typing import Any, Callable, Final, Sequence

_logger = logging.getLogger(__name__)

_DEFAULT_HTTP_TIMEOUT_S: Final[float] = 5.0
_DEFAULT_SMTP_TIMEOUT_S: Final[float] = 10.0


class WeChatWebhookSender:
    """企业微信机器人 webhook 实发 sender（markdown 消息）。

    Args:
        webhook_url: 企业微信机器人 webhook 完整 URL（含 key；视为凭据不日志输出）。
        http_post: 传输注入 callable(url, body: bytes, timeout) -> 响应（需有
            .status 或 .status_code，.read() 返回 JSON 字节）；None=urllib 实发。
        timeout_seconds: HTTP 超时。
    """

    def __init__(
        self,
        webhook_url: str,
        *,
        http_post: Callable[[str, bytes, float], Any] | None = None,
        timeout_seconds: float = _DEFAULT_HTTP_TIMEOUT_S,
    ) -> None:
        if not webhook_url or not webhook_url.strip():
            raise ValueError("webhook_url 不能为空")
        self._webhook_url = webhook_url
        self._http_post = http_post or self._urllib_post
        self._timeout = timeout_seconds

    @staticmethod
    def _urllib_post(url: str, body: bytes, timeout: float) -> Any:
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        return urllib.request.urlopen(req, timeout=timeout)  # noqa: S310 —— URL 由 owner 配置

    def send_markdown(self, content: str) -> bool:
        """发送 markdown 消息。返回 True=送达；失败/异常=False（best-effort）。"""
        if not content or not content.strip():
            _logger.warning("WeChat sender 拒绝空内容发送")
            return False
        body = json.dumps(
            {"msgtype": "markdown", "markdown": {"content": content}},
            ensure_ascii=False,
        ).encode("utf-8")
        try:
            resp = self._http_post(self._webhook_url, body, self._timeout)
            status = getattr(resp, "status", None) or getattr(resp, "status_code", 0)
            raw = resp.read() if hasattr(resp, "read") else b"{}"
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            ok = status == 200 and int(payload.get("errcode", 0)) == 0
            if not ok:
                _logger.warning(
                    "WeChat webhook 软失败: status=%s errcode=%s", status, payload.get("errcode")
                )
            return ok
        except Exception as exc:  # noqa: BLE001 —— best-effort 不阻断
            _logger.warning("WeChat webhook 发送异常: %s", type(exc).__name__)
            return False

    def as_alert_sender(self) -> Callable[[Any], bool]:
        """适配 alert_generator.Alert 的可调用门面（duck-typing 取 level/source/message）。"""

        def _send(alert: Any) -> bool:
            level = getattr(getattr(alert, "level", None), "value", "unknown")
            source = getattr(alert, "source", "unknown")
            message = getattr(alert, "message", "")
            content = f"**[告警:{str(level).upper()}] {source}**\n> {message}"
            return self.send_markdown(content)

        return _send

    def as_report_sender(self) -> Callable[[Any], bool]:
        """适配 report_publisher.ArchivedReport 的可调用门面（duck-typing 取元数据）。"""

        def _send(archived: Any) -> bool:
            source = getattr(getattr(archived, "source", None), "value", "unknown")
            content = (
                f"**[报告归档] {getattr(archived, 'report_id', '?')}**\n"
                f"> 来源: {source} | 类型: {getattr(archived, 'report_type', '?')}\n"
                f"> 指纹: {str(getattr(archived, 'content_hash', ''))[:16]}..."
            )
            return self.send_markdown(content)

        return _send


class EmailSmtpSender:
    """SMTP 邮件实发 sender（SSL / STARTTLS）。

    Args:
        host/port: SMTP 服务地址。
        username/password: 认证凭据（password 视为秘密，不日志不落盘）。
        from_addr/to_addrs: 发件人/收件人列表。
        use_ssl: True=SMTP_SSL；False=STARTTLS。
        smtp_factory: 传输注入 callable(host, port, timeout) -> SMTP 风格对象
            （需支持 login/sendmail/quit 或 send_message）；None=smtplib 实发。
        timeout_seconds: SMTP 超时。
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: Sequence[str],
        *,
        use_ssl: bool = True,
        smtp_factory: Callable[[str, int, float], Any] | None = None,
        timeout_seconds: float = _DEFAULT_SMTP_TIMEOUT_S,
    ) -> None:
        if not host or not host.strip():
            raise ValueError("SMTP host 不能为空")
        if not to_addrs:
            raise ValueError("to_addrs 不能为空")
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from = from_addr
        self._to = list(to_addrs)
        self._use_ssl = use_ssl
        self._smtp_factory = smtp_factory
        self._timeout = timeout_seconds

    def _open_connection(self) -> Any:
        if self._smtp_factory is not None:
            return self._smtp_factory(self._host, self._port, self._timeout)
        cls = smtplib.SMTP_SSL if self._use_ssl else smtplib.SMTP
        conn = cls(self._host, self._port, timeout=self._timeout)
        if not self._use_ssl:
            conn.starttls()
        return conn

    def send_mail(self, subject: str, body: str) -> bool:
        """发送纯文本邮件。返回 True=送达；失败/异常=False（best-effort）。"""
        if not subject or not subject.strip():
            _logger.warning("Email sender 拒绝空主题发送")
            return False
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self._from
        msg["To"] = ", ".join(self._to)
        conn = None
        try:
            conn = self._open_connection()
            if self._username:
                conn.login(self._username, self._password)
            conn.sendmail(self._from, self._to, msg.as_string())
            return True
        except Exception as exc:  # noqa: BLE001 —— best-effort 不阻断
            _logger.warning("Email SMTP 发送异常: %s", type(exc).__name__)
            return False
        finally:
            if conn is not None:
                try:
                    conn.quit()
                except Exception:  # noqa: BLE001 —— 关闭失败不掩盖发送结果
                    pass

    def as_alert_sender(self) -> Callable[[Any], bool]:
        """适配 alert_generator.Alert 的可调用门面。"""

        def _send(alert: Any) -> bool:
            level = getattr(getattr(alert, "level", None), "value", "unknown")
            source = getattr(alert, "source", "unknown")
            subject = f"[ZephyrAlert:{str(level).upper()}] {source}"
            body = (
                f"级别: {str(level).upper()}\n来源: {source}\n"
                f"时间: {getattr(alert, 'timestamp', '')}\n\n{getattr(alert, 'message', '')}"
            )
            return self.send_mail(subject, body)

        return _send

    def as_report_sender(self) -> Callable[[Any], bool]:
        """适配 report_publisher.ArchivedReport 的可调用门面。"""

        def _send(archived: Any) -> bool:
            source = getattr(getattr(archived, "source", None), "value", "unknown")
            subject = f"[ZephyrReport] {getattr(archived, 'report_id', '?')} ({getattr(archived, 'report_type', '?')})"
            body = (
                f"报告: {getattr(archived, 'report_id', '?')}\n来源: {source}\n"
                f"类型: {getattr(archived, 'report_type', '?')}\n"
                f"归档: {getattr(archived, 'archive_id', '?')} @ {getattr(archived, 'archived_at', '')}\n"
                f"内容指纹: {getattr(archived, 'content_hash', '')}\n\n"
                f"{json.dumps(getattr(archived, 'content', {}), ensure_ascii=False, default=str, indent=2)}"
            )
            return self.send_mail(subject, body)

        return _send


__all__ = [
    "EmailSmtpSender",
    "WeChatWebhookSender",
]
