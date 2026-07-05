# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.telemetry
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_telemetry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AssetInventoryTelemetry — MOD-INF-026 自监控指标

蓝图 §27：OpenTelemetry 三支柱（Metrics/Traces/Logs）风格的盘点器自监控。
"""

import logging
import os
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from zephyr.shared.security.secrets import get_secret_or_default

logger = logging.getLogger(__name__)

_sys_telemetry = None


def _get_sys_telemetry():
    global _sys_telemetry
    if _sys_telemetry is None:
        try:
            from zephyr.infrastructure.system_telemetry.facade import Telemetry

            _sys_telemetry = Telemetry("asset-inventory", test_mode=os.environ.get("ZALPHA_TEST_MODE", "") == "1")
        except Exception:
            _sys_telemetry = False
    return _sys_telemetry if _sys_telemetry is not False else None


class MetricPoint(BaseModel):
    name: str = Field(description="指标名")
    value: float = Field(description="指标值")
    labels: dict[str, str] = Field(default_factory=dict, description="标签")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InventorySelfMetrics:
    """盘点系统自监控——内存中累计，可导出到 JSON / stdout / OTEL。"""

    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histories: dict[str, list[float]] = defaultdict(list)
        self._start_times: dict[str, float] = {}
        self._errors: list[str] = []

    def start_operation(self, name: str) -> None:
        self._start_times[name] = time.monotonic()

    def end_operation(self, name: str) -> float:
        t0 = self._start_times.pop(name, time.monotonic())
        elapsed = time.monotonic() - t0
        self._histories[f"{name}_duration_sec"].append(elapsed)
        return elapsed

    def inc(self, name: str, delta: float = 1.0, **labels: str) -> None:
        self._counters[name] += delta

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def record_error(self, msg: str) -> None:
        self._errors.append(msg)
        self.inc("errors_total")

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histories": {
                k: {"count": len(v), "avg": sum(v) / len(v) if v else 0.0, "max": max(v) if v else 0.0}
                for k, v in self._histories.items()
            },
            "errors_count": len(self._errors),
            "errors_recent": self._errors[-10:],
            "snapshot_at": datetime.now(UTC).isoformat(),
        }

    def print(self) -> None:
        snap = self.snapshot()
        print("=== InventorySelfMetrics ===")
        print(f"  Counters: {snap['counters']}")
        print(f"  Gauges:   {snap['gauges']}")
        if snap["errors_recent"]:
            print(f"  Errors:   {snap['errors_count']} total, recent:")
            for e in snap["errors_recent"]:
                print(f"    - {e}")
        print("==============================")

    def push_to_facade(self) -> None:
        telemetry = _get_sys_telemetry()
        if telemetry is None:
            return
        try:
            for name, value in self._gauges.items():
                telemetry.metrics.gauge(name, value)
            for name, value in self._counters.items():
                telemetry.metrics.counter(f"{name}_total", value)
            telemetry.health.register()
        except Exception as exc:
            logger.warning("telemetry push_to_facade failed: %s", exc)


TELEMETRY = InventorySelfMetrics()


def get_telemetry() -> InventorySelfMetrics:
    return TELEMETRY


# ============================================================================
# SRC-0040: 从 notifications.py 合并 — NotificationManager + 通知通道
# ============================================================================

import json as _json
import smtplib as _smtplib
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
from email.mime.text import MIMEText as _MIMEText
from urllib.error import URLError as _URLError
from urllib.request import Request as _Request
from urllib.request import urlopen as _urlopen


class NotificationRecord(BaseModel):
    """通知记录。"""

    channel: str
    severity: str
    message: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    delivered: bool | None = None


class NotificationChannel(_ABC):
    """通知通道抽象基类。"""

    @_abstractmethod
    def send(self, severity: str, message: str) -> NotificationRecord: ...

    @property
    @_abstractmethod
    def channel_name(self) -> str: ...


class ConsoleChannel(NotificationChannel):
    """控制台通知通道。"""

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
    """飞书 Webhook 通知通道。"""

    def __init__(self, webhook_url: str | None = None) -> None:
        self._webhook_url = webhook_url or get_secret_or_default("ZEPHYR_FEISHU_WEBHOOK", "")

    @property
    def channel_name(self) -> str:
        return "feishu"

    def send(self, severity: str, message: str) -> NotificationRecord:
        record = NotificationRecord(channel="feishu", severity=severity, message=message)

        if not self._webhook_url:
            record.delivered = False
            return record

        payload = _json.dumps(
            {
                "msg_type": "text",
                "content": {"text": f"[{severity.upper()}] {message}"},
            }
        ).encode("utf-8")

        try:
            req = _Request(
                self._webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with _urlopen(req, timeout=10) as resp:
                if resp.status < 300:
                    record.delivered = True
                else:
                    record.delivered = False
        except (_URLError, OSError):
            record.delivered = False

        return record


class SmtpEmailChannel(NotificationChannel):
    """SMTP 邮件通知通道。"""

    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        from_addr: str | None = None,
        to_addrs: list[str] | None = None,
        use_tls: bool = True,
    ) -> None:
        self._smtp_host = smtp_host or os.environ.get("ZEPHYR_SMTP_HOST", "")
        # 5.155.18 修复: smtp_port 改为可通过环境变量配置, 带范围校验
        if smtp_port is None:
            try:
                smtp_port = int(os.environ.get("ZEPHYR_SMTP_PORT", "587"))
            except (TypeError, ValueError):
                smtp_port = 587
        if not (1 <= smtp_port <= 65535):
            smtp_port = 587
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user or get_secret_or_default("ZEPHYR_SMTP_USER", "")
        self._smtp_password = smtp_password or get_secret_or_default("ZEPHYR_SMTP_PASSWORD", "")
        self._from_addr = from_addr or os.environ.get("ZEPHYR_SMTP_FROM", self._smtp_user)
        self._to_addrs = (
            to_addrs
            if to_addrs
            else (os.environ.get("ZEPHYR_SMTP_TO", "").split(",") if os.environ.get("ZEPHYR_SMTP_TO") else [])
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
            body = f"Severity: {severity}\nTime: {datetime.now(UTC).isoformat()}\n\n{message}"
            msg = _MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self._from_addr
            msg["To"] = ", ".join(self._to_addrs)

            if self._use_tls:
                server = _smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)
                server.ehlo()
                server.starttls()
                server.ehlo()
                if self._smtp_user and self._smtp_password:
                    server.login(self._smtp_user, self._smtp_password)
                server.sendmail(self._from_addr, self._to_addrs, msg.as_string())
                server.quit()
            else:
                server = _smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)
                if self._smtp_user and self._smtp_password:
                    server.login(self._smtp_user, self._smtp_password)
                server.sendmail(self._from_addr, self._to_addrs, msg.as_string())
                server.quit()

            record.delivered = True
        except Exception:
            record.delivered = False

        return record


class NotificationManager:
    """通知通道选择与路由——宽进严出。"""

    def __init__(
        self,
        console: bool = True,
        feishu_url: str | None = None,
        smtp_host: str | None = None,
        smtp_port: int = 587,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        email_from: str | None = None,
        email_to: list[str] | None = None,
    ) -> None:
        self._channels: list[NotificationChannel] = []

        if console:
            self._channels.append(ConsoleChannel())

        if feishu_url or get_secret_or_default("ZEPHYR_FEISHU_WEBHOOK", ""):
            self._channels.append(FeishuWebhook(feishu_url))

        if smtp_host or os.environ.get("ZEPHYR_SMTP_HOST"):
            self._channels.append(
                SmtpEmailChannel(
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    smtp_user=smtp_user,
                    smtp_password=smtp_password,
                    from_addr=email_from,
                    to_addrs=email_to,
                )
            )

    def notify_all(self, severity: str, message: str) -> list[NotificationRecord]:
        return [ch.send(severity, message) for ch in self._channels]

    def notify_specific(self, channel_name: str, severity: str, message: str) -> NotificationRecord | None:
        for ch in self._channels:
            if ch.channel_name == channel_name:
                return ch.send(severity, message)
        return None
