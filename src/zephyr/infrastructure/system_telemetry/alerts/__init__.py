# [A_module] module_id=MOD-INF-alerts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""
AlertSubsystem — 告警规则评估引擎（MOD-INF-015 §9 · alerts）.

加载 config/alert_rules.yaml，提供 fire / health / evaluate / ack / pending API。
AlertLevel: INFO < WARNING < ERROR < CRITICAL 四级严重度。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: module_id 参数
#   fields: 参数 module_id（无注解）
#   code: __init__.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: test_mode 参数
#   fields: 参数 test_mode（无注解）
#   code: __init__.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AlertSubsystem
#   name_en: AlertSubsystem
#   intro: class AlertSubsystem 源码 L75-L167
#   desc: 公共方法（定义序）: fire, health, pending, evaluate, ack；源码 L75-L167
#   inputs: module_id test_mode
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AlertSubsystem
#   downstream: zephyr.security.access_control; zephyr.security.budget_enforcement
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
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
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
                len(self._pending_alerts),
                len(triggered),
                self._MAX_PENDING_ALERTS,
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
