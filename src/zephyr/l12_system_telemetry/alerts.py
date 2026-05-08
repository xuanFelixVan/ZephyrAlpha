"""AlertSubsystem — 告警规则评估引擎（MOD-INF-015 §9 · alerts）.

加载 config/alert_rules.yaml，提供 health() / pending 等查询 API。
AlertLevel: INFO < WARNING < ERROR < CRITICAL 四级严重度。
"""

from __future__ import annotations

import enum
from pathlib import Path

import yaml


class AlertLevel(enum.IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


class AlertSubsystem:
    _CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "alert_rules.yaml"

    def __init__(self, module_id: str = "", test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._pending_alerts: list[dict] = []
        self._rules: list[dict] = self._load_rules() if self._CONFIG_PATH.exists() else []

    def _load_rules(self) -> list[dict]:
        try:
            data = yaml.safe_load(self._CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("rules", []) if data else []
        except Exception:
            return []

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
                    triggered.append({
                        "id": rule.get("id"),
                        "name": rule.get("name"),
                        "severity": rule.get("severity"),
                        "value": value,
                    })
        self._pending_alerts.extend(triggered)
        return triggered

    def ack(self, alert_id: str) -> bool:
        before = len(self._pending_alerts)
        self._pending_alerts = [a for a in self._pending_alerts if a.get("id") != alert_id]
        return len(self._pending_alerts) < before

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
