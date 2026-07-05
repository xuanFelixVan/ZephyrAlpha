# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.alert_router
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_infrastructure.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 告警路由不可绕过;去重窗口不可缩短
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_alert_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Alert Router — alert_router.py





module_id: MOD-INF-023


告警路由与疲劳管理：四级路由 + 去重(6h) + 聚合(batch/causal) + 静默策略。


对标 blueprint.md §5.4 / TASK-INF-0028 / D-023-13。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class Alert:
    alert_id: str

    module_id: str

    detector_id: str

    drift_dimension: str

    severity: str

    tier: str

    message: str

    timestamp: str = ""

    ack_required: bool = False

    acked: bool = False

    acked_at: str | None = None


class AlertRouter:
    SILENCE_NIGHT_START: int = 22

    SILENCE_NIGHT_END: int = 8

    DEDUP_WINDOW_HOURS: int = 6

    PERSISTENT_THRESHOLD: int = 3

    FOCUS_TIME_HOURS: int = 2

    def __init__(self) -> None:
        self._sent_alerts: dict[str, list[datetime]] = {}

        self._focus_start: datetime | None = None

    def classify(self, module_id: str, drift_dimension: str, severity: str) -> str:
        if severity == "HIGH":
            # 5.136.4 修复: 移除未使用的 parts = drift_dimension.split("_") 赋值
            if any(kw in drift_dimension.lower() for kw in ("contract", "security", "p0", "ssot")):
                return "P0_CRITICAL"

            return "P0"

        elif severity == "MEDIUM":
            return "P1"

        else:
            return "P2"

    def should_silence(self) -> bool:
        now = datetime.now(UTC)

        hour = now.hour

        weekday = now.weekday()

        if self.SILENCE_NIGHT_END <= hour < self.SILENCE_NIGHT_START:
            return False

        if weekday >= 5:
            return True

        if self._focus_start:
            elapsed = (now - self._focus_start).total_seconds() / 3600

            if elapsed < self.FOCUS_TIME_HOURS:
                return True

            self._focus_start = None

        return True

    def start_focus_time(self) -> None:
        self._focus_start = datetime.now(UTC)

    def should_deduplicate(self, alert_key: str) -> bool:
        now = datetime.now(UTC)

        cutoff = now - timedelta(hours=self.DEDUP_WINDOW_HOURS)

        history = self._sent_alerts.get(alert_key, [])

        recent = [t for t in history if t > cutoff]

        self._sent_alerts[alert_key] = recent

        if len(recent) >= self.PERSISTENT_THRESHOLD:
            return False

        if recent:
            return True

        return False

    def record_alert(self, alert_key: str) -> None:
        now = datetime.now(UTC)

        self._sent_alerts.setdefault(alert_key, []).append(now)

    def route(self, alerts: list[Alert]) -> list[dict[str, object]]:
        actions: list[dict[str, object]] = []

        for alert in alerts:
            key = f"{alert.module_id}:{alert.detector_id}:{alert.drift_dimension}"

            if self.should_silence() and alert.tier != "P0_CRITICAL":
                continue

            if alert.tier != "P0_CRITICAL" and self.should_deduplicate(key):
                continue

            self.record_alert(key)

            action = {
                "alert_id": alert.alert_id,
                "module_id": alert.module_id,
                "tier": alert.tier,
                "channel": "feishu",
                "message": alert.message,
                "ack_required": alert.tier == "P0_CRITICAL",
                "escalation_timeout_min": 30 if alert.tier == "P0_CRITICAL" else 0,
                "aggregation": "hourly" if alert.tier == "P0" else ("daily" if alert.tier == "P1" else "none"),
            }

            actions.append(action)

        return actions

    def batch_alerts(self, alerts: list[Alert]) -> dict[str, object]:
        if len(alerts) <= 10:
            return {"batched": True, "count": len(alerts), "top": []}

        sorted_alerts = sorted(alerts, key=lambda a: {"P0_CRITICAL": 0, "P0": 1, "P1": 2, "P2": 3}.get(a.tier, 99))

        top3 = sorted_alerts[:3]

        return {
            "batched": True,
            "count": len(alerts),
            "top3": [{"module_id": a.module_id, "dimension": a.drift_dimension, "tier": a.tier} for a in top3],
            "remaining": len(alerts) - 3,
        }
