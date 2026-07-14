# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.observability.notifier
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.event_bus
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
# [A_module] module_id=MOD-INF_notifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Notifier — 多渠道 Owner 通知。

依据：
    蓝图 MOD-TASK_SYSTEM §6.3.5 + v0.6.0
    任务卡 TASK-INF-0109 (Part 5/5)
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT


class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    FILE = "file"
    CONSOLE = "console"


@dataclass
class Notification:
    notification_id: str
    level: NotificationLevel
    title: str
    message: str
    task_id: str = ""
    channel: NotificationChannel = NotificationChannel.CONSOLE
    timestamp_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class NotifyConfig:
    enabled: bool = True
    min_level: NotificationLevel = NotificationLevel.INFO
    rate_limit_per_minute: int = 30


class Notifier:
    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (REPO_ROOT / "data" / "notifications")
        self._config = NotifyConfig()
        self._notification_count = 0
        self._window_start = datetime.now(UTC)

    def notify(self, level: NotificationLevel, title: str, message: str, task_id: str = "") -> Notification:
        notification = Notification(
            notification_id=f"NOTIF-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            level=level,
            title=title,
            message=message,
            task_id=task_id,
        )

        if not self._config.enabled:
            return notification

        prefix_map = {
            NotificationLevel.INFO: "[INFO]",
            NotificationLevel.WARNING: "[WARN]",
            NotificationLevel.CRITICAL: "[CRIT]",
        }
        prefix = prefix_map.get(level, "[?]")
        print(f"{prefix} {title}: {message}")

        self._output_dir.mkdir(parents=True, exist_ok=True)
        notification_path = self._output_dir / f"{notification.notification_id}.json"
        notification_path.write_text(
            json.dumps(
                {
                    "notification_id": notification.notification_id,
                    "level": notification.level.value,
                    "title": notification.title,
                    "message": notification.message,
                    "task_id": notification.task_id,
                    "timestamp_utc": notification.timestamp_utc,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        self._notification_count += 1

        return notification

    def notify_completion(self, task_id: str, summary: str) -> Notification:
        return self.notify(
            NotificationLevel.INFO,
            f"Task Complete: {task_id}",
            summary,
            task_id=task_id,
        )

    def notify_failure(self, task_id: str, error: str) -> Notification:
        return self.notify(
            NotificationLevel.CRITICAL,
            f"Task Failed: {task_id}",
            error,
            task_id=task_id,
        )

    def notify_owner_attention(self, task_id: str, reason: str) -> Notification:
        return self.notify(
            NotificationLevel.WARNING,
            f"Owner Attention Required: {task_id}",
            f"Reason: {reason}",
            task_id=task_id,
        )

    _subscribed: bool = False

    def subscribe_eventbus(self) -> None:
        """事件驱动订阅——pipeline_failed/kill_switch_triggered 自动通知 Owner（永久系统四要素：自动触发）。"""
        if self._subscribed:
            return
        from zephyr.shared.event_bus import bus

        notifier = self

        def _on_pipeline_failed(payload: object) -> None:
            data = payload if isinstance(payload, dict) else {}
            task_id = str(data.get("task_id", ""))
            error = str(data.get("error", "pipeline failed"))
            notifier.notify_failure(task_id, error)

        def _on_kill_switch_triggered(payload: object) -> None:
            data = payload if isinstance(payload, dict) else {}
            reason = str(data.get("reason", "kill switch triggered"))
            notifier.notify_owner_attention("kill_switch", reason)

        bus.subscribe("pipeline_failed", _on_pipeline_failed)
        bus.subscribe("kill_switch_triggered", _on_kill_switch_triggered)
        self._subscribed = True
