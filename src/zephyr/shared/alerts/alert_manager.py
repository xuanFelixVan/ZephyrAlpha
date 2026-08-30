# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.alerts.alert_manager
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__ ; zephyr.feedback_loop.auto_evolution ; zephyr.security.llm_defense.llm_security.layers.l6_observability
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_alerts 参数
#   fields: 参数 max_alerts（无注解）
#   code: alert_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AlertManager
#   name_en: AlertManager
#   intro: class AlertManager 源码 L73-L106
#   desc: 公共方法（定义序）: create, raise_alert, acknowledge, get_active, get_by_severity；源码 L73-L106
#   inputs: max_alerts
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: AlertManager
#   downstream: zephyr.infrastructure.capacity_assurance.modules.__init__ ; zephyr.feedback_loo…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    alert_id: str
    title: str
    severity: AlertSeverity
    source: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


class AlertManager:
    def __init__(self, max_alerts: int = 1000):
        self._alerts: list[Alert] = []
        self._max_alerts = max_alerts

    def create(self, title: str, severity: AlertSeverity, source: str, message: str, **metadata: Any) -> Alert:
        alert = Alert(
            alert_id=str(uuid.uuid4())[:8],
            title=title,
            severity=severity,
            source=source,
            message=message,
            metadata=metadata,
        )
        self._alerts.append(alert)
        if len(self._alerts) > self._max_alerts:
            self._alerts = self._alerts[-self._max_alerts :]
        return alert

    def raise_alert(self, title: str, severity: AlertSeverity, source: str, message: str, **metadata: Any) -> Alert:
        return self.create(title, severity, source, message, **metadata)

    def acknowledge(self, alert_id: str) -> bool:
        for a in self._alerts:
            if a.alert_id == alert_id:
                a.acknowledged = True
                return True
        return False

    def get_active(self) -> list[Alert]:
        return [a for a in self._alerts if not a.acknowledged]

    def get_by_severity(self, severity: AlertSeverity) -> list[Alert]:
        return [a for a in self._alerts if a.severity == severity]
