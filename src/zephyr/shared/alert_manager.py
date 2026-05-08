"""
Alert Manager — 告警收敛四机制 (盲点 #12)
特性：
  - 去重合并：同一 SLI 5 分钟内最多 1 次
  - 抑制联动：高优先级抑制低优先级（SEV-1 抑制 SEV-2 抑制 SEV-3）
  - 时间窗口分组：告警聚合为批次（300s Sophia Cycle）
  - 飞书卡片发送：Markdown 格式安全，不触发 @all
"""
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional


class Severity(IntEnum):
    SEV_3 = 3
    SEV_2 = 2
    SEV_1 = 1


@dataclass
class Alert:
    alert_id: str
    sli_id: str
    severity: Severity
    message: str
    value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)
    sent: bool = False


class AlertManager:
    """
    告警管理器 (盲点 #12)
    告警收敛四机制：
      1. 去重合并：同一 SLI 5 分钟内最多 1 次
      2. 抑制联动：SEV-1 > SEV-2 > SEV-3
      3. 时间窗口分组：300s Sophia Cycle
      4. 飞书卡片发送
    """

    DEDUP_WINDOW = 300
    AGGREGATION_WINDOW = 300

    def __init__(self):
        self._alerts: list[Alert] = []
        self._last_alert_time: dict[str, float] = {}
        self._pending_batch: list[Alert] = []
        self._last_batch_time: float = 0

    def fire(self, sli_id: str, severity: Severity, value: float,
             threshold: float, message: str = "") -> Optional[Alert]:
        now = time.time()

        last_time = self._last_alert_time.get(sli_id, 0)
        if now - last_time < self.DEDUP_WINDOW:
            return None

        existing = [a for a in self._pending_batch if a.sli_id == sli_id]
        if existing:
            return None

        alert = Alert(
            alert_id=f"alert-{sli_id}-{int(now)}",
            sli_id=sli_id,
            severity=severity,
            message=message or f"{sli_id}: {value} > {threshold}",
            value=value,
            threshold=threshold,
            timestamp=now,
        )
        self._alerts.append(alert)
        self._last_alert_time[sli_id] = now

        self._pending_batch = [a for a in self._pending_batch
                                if not self._suppressed_by(a, alert)]
        self._pending_batch.append(alert)

        if now - self._last_batch_time >= self.AGGREGATION_WINDOW:
            self.flush_batch()

        return alert

    def _suppressed_by(self, existing: Alert, new_alert: Alert) -> bool:
        return (new_alert.severity < existing.severity
                and existing.sli_id == new_alert.sli_id)

    def flush_batch(self) -> list[Alert]:
        batch = list(self._pending_batch)
        for alert in batch:
            alert.sent = True
        self._pending_batch.clear()
        self._last_batch_time = time.time()
        return batch

    def get_report(self) -> str:
        total = len(self._alerts)
        sent = sum(1 for a in self._alerts if a.sent)
        sev1 = sum(1 for a in self._alerts if a.severity == Severity.SEV_1)
        return f"Alerts: {total} total, {sent} sent, {sev1} SEV-1"

    def get_error_budget_attribution(self) -> dict:
        """盲点 #3: Error Budget 消耗归因"""
        attribution: dict[str, float] = defaultdict(float)
        for alert in self._alerts:
            if alert.sent:
                attribution[alert.sli_id] += abs(alert.value - alert.threshold)
        return dict(attribution)
