"""MOD-INF-026 §36 — 三层通知告警通道。

NotificationChannel ABC + ConsoleChannel + FeishuWebhook + SmtpEmailChannel。
Passive (仅 Dashboard) / Semi-Active (飞书/邮件) / Blocking (拒绝操作)。
"""

from __future__ import annotations

import json
import os
import smtplib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

from pydantic import BaseModel, Field


class NotificationRecord(BaseModel):
    channel: str
    severity: str
    message: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivered: Optional[bool] = None


class NotificationChannel(ABC):

    @abstractmethod
    def send(self, severity: str, message: str) -> NotificationRecord:
        ...

    @property
    @abstractmethod
    def channel_name(self) -> str:
        ...


class ConsoleChannel(NotificationChannel):

    _SEVERITY_PREFIX: dict[str, str] = {
        "passive": "[INFO]",
        "semi_active": "[WARN]",
        "blocking": "[CRITICAL]",
    }

    @property
    def channel_name(self) -> str:
        return "console"

    def send(self, severity: str, message: str) -> NotificationRecord:
        prefix = self._SEVERITY_PREFIX.get(severity, "[UNKNOWN]")
        print(f"{prefix} {message}")
        return NotificationRecord(channel="console", severity=severity, message=message, delivered=True)


class FeishuWebhook(NotificationChannel):

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self._webhook_url = webhook_url or os.environ.get("ZEPHYR_FEISHU_WEBHOOK", "")

    @property
    def channel_name(self) -> str:
        return "feishu"

    def send(self, severity: str, message: str) -> NotificationRecord:
        record = NotificationRecord(channel="feishu", severity=severity, message=message)

        if not self._webhook_url:
            record.delivered = False
            return record

        payload = json.dumps({
            "msg_type": "text",
            "content": {"text": f"[{severity.upper()}] {message}"},
        }).encode("utf-8")

        try:
            req = Request(
                self._webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=10) as resp:
                if resp.status < 300:
                    record.delivered = True
                else:
                    record.delivered = False
        except (URLError, OSError):
            record.delivered = False

        return record


class SmtpEmailChannel(NotificationChannel):

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_addr: Optional[str] = None,
        to_addrs: Optional[list[str]] = None,
        use_tls: bool = True,
    ) -> None:
        self._smtp_host = smtp_host or os.environ.get("ZEPHYR_SMTP_HOST", "")
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user or os.environ.get("ZEPHYR_SMTP_USER", "")
        self._smtp_password = smtp_password or os.environ.get("ZEPHYR_SMTP_PASSWORD", "")
        self._from_addr = from_addr or os.environ.get("ZEPHYR_SMTP_FROM", self._smtp_user)
        self._to_addrs = to_addrs if to_addrs else (
            os.environ.get("ZEPHYR_SMTP_TO", "").split(",")
            if os.environ.get("ZEPHYR_SMTP_TO") else []
        )
        self._use_tls = use_tls

    @property
    def channel_name(self) -> str:
        return "email"

    def send(self, severity: str, message: str) -> NotificationRecord:
        record = NotificationRecord(channel="email", severity=severity, message=message)

        if not self._smtp_host or not self._to_addrs:
            record.delivered = False
            return record

        try:
            subject = f"[ZephyrAlpha {severity.upper()}] Asset Inventory Alert"
            body = f"Severity: {severity}\nTime: {datetime.now(timezone.utc).isoformat()}\n\n{message}"
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self._from_addr
            msg["To"] = ", ".join(self._to_addrs)

            if self._use_tls:
                server = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)
                server.ehlo()
                server.starttls()
                server.ehlo()
                if self._smtp_user and self._smtp_password:
                    server.login(self._smtp_user, self._smtp_password)
                server.sendmail(self._from_addr, self._to_addrs, msg.as_string())
                server.quit()
            else:
                server = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)
                if self._smtp_user and self._smtp_password:
                    server.login(self._smtp_user, self._smtp_password)
                server.sendmail(self._from_addr, self._to_addrs, msg.as_string())
                server.quit()

            record.delivered = True
        except Exception:
            record.delivered = False

        return record


class NotificationManager:
    """通道选择和路由——宽进严出"""

    def __init__(
        self,
        console: bool = True,
        feishu_url: Optional[str] = None,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        email_from: Optional[str] = None,
        email_to: Optional[list[str]] = None,
    ) -> None:
        self._channels: list[NotificationChannel] = []

        if console:
            self._channels.append(ConsoleChannel())

        if feishu_url or os.environ.get("ZEPHYR_FEISHU_WEBHOOK"):
            self._channels.append(FeishuWebhook(feishu_url))

        if smtp_host or os.environ.get("ZEPHYR_SMTP_HOST"):
            self._channels.append(SmtpEmailChannel(
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                smtp_user=smtp_user,
                smtp_password=smtp_password,
                from_addr=email_from,
                to_addrs=email_to,
            ))

    def notify_all(self, severity: str, message: str) -> list[NotificationRecord]:
        return [ch.send(severity, message) for ch in self._channels]

    def notify_specific(self, channel_name: str, severity: str, message: str) -> Optional[NotificationRecord]:
        for ch in self._channels:
            if ch.channel_name == channel_name:
                return ch.send(severity, message)
        return None
