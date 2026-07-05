# [A_module] module_id=MOD-INF_alerts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.alerts
# [INVARIANTS] INFO<WARNING<ERROR<CRITICAL severity order; rules loaded from config/alert_rules.yaml; fail-safe on missing config
# [MODIFY-GUARD] facade.py; schema.py; config/alert_rules.yaml
# [CONSUMERS] zephyr.security.access_control; zephyr.security.budget_enforcement
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] yaml.YAMLError; OSError; RuntimeError
# [TESTS] tests/system-telemetry/test_alerts.py
# [TTL] permanent
"""AlertSubsystem — 告警规则评估引擎（MOD-INF-015 §9 · alerts）.

加载 config/alert_rules.yaml，提供 fire / health / evaluate / ack / pending API。
AlertLevel: INFO < WARNING < ERROR < CRITICAL 四级严重度。
"""

from __future__ import annotations

import enum
import logging
import time
import uuid
from collections import deque
from pathlib import Path

import yaml
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class AlertLevel(enum.IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


class AlertSubsystem:
    _CONFIG_PATH = REPO_ROOT / "config" / "alert_rules.yaml"

    # 5.24.6 修复：list 无界增长 -> deque(maxlen=1000)，超限自动丢弃最旧告警
    _MAX_PENDING_ALERTS = 1000

    def __init__(self, module_id: str = "", test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._pending_alerts: deque[dict] = deque(maxlen=self._MAX_PENDING_ALERTS)
        self._rules: list[dict] = self._load_rules() if self._CONFIG_PATH.exists() else []

    def _load_rules(self) -> list[dict]:
        try:
            data = yaml.safe_load(self._CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("rules", []) if data else []
        except Exception:
            return []

    def fire(self, level: AlertLevel, message: str, labels: dict | None = None) -> dict:
        if not isinstance(level, AlertLevel):
            level = AlertLevel(level)
        alert = {
            "module_id": self._module_id,
            "level": level.name,
            "message": message,
            "labels": labels or {},
            "fired": not self._test_mode,
        }
        if len(self._pending_alerts) == self._MAX_PENDING_ALERTS:
            logger.warning("pending_alerts full (maxlen=%d), dropping oldest", self._MAX_PENDING_ALERTS)
        self._pending_alerts.append(alert)
        return alert

    def health(self) -> dict:
        return {
            "module_id": self._module_id,
            "pending_alerts": len(self._pending_alerts),
            "rules_loaded": len(self._rules),
            "test_mode": self._test_mode,
        }

    def pending(self) -> list[dict]:
        return list(self._pending_alerts)

    def evaluate(self, metric_name: str, value: float) -> list[dict]:
        triggered = []
        for rule in self._rules:
            if rule.get("metric") == metric_name:
                condition = rule.get("condition", "")
                if self._check_condition(value, condition):
                    triggered.append(
                        {
                            "id": rule.get("id") or uuid.uuid4().hex[:12],
                            "name": rule.get("name"),
                            "module_id": self._module_id,
                            "severity": rule.get("severity"),
                            "level": rule.get("severity"),
                            "message": f"{metric_name} {condition} {value}",
                            "value": value,
                            "fired": time.time(),
                        }
                    )
        if len(self._pending_alerts) + len(triggered) > self._MAX_PENDING_ALERTS:
            logger.warning(
                "pending_alerts will overflow (current=%d, adding=%d, maxlen=%d), dropping oldest",
                len(self._pending_alerts), len(triggered), self._MAX_PENDING_ALERTS,
            )
        self._pending_alerts.extend(triggered)
        return triggered

    def ack(self, alert_id: str) -> bool:
        # 5.24.6 修复：deque 不支持列表推导重新赋值（会丢失 maxlen），改为遍历删除
        for i, a in enumerate(self._pending_alerts):
            if a.get("id") == alert_id:
                del self._pending_alerts[i]
                return True
        return False

    @staticmethod
    def _check_condition(value: float, condition: str) -> bool:
        try:
            op = condition[0] if condition else ""
            threshold = float(condition[1:])
            if op == ">":
                return value > threshold
            if op == "<":
                return value < threshold
        except (ValueError, IndexError):
            pass
        return False


__all__ = [
    "CRITICAL",
    "ERROR",
    "INFO",
    "WARNING",
    "AlertLevel",
    "AlertSubsystem",
    "ack",
    "alert",
    "before",
    "condition",
    "data",
    "evaluate",
    "fire",
    "health",
    "level",
    "op",
    "pending",
    "threshold",
    "triggered",
]
