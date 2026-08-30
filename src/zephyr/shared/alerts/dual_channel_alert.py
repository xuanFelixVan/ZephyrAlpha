# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.alerts.dual_channel_alert
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__ ; zephyr.feedback_loop.auto_evolution
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
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: dual_channel_alert.py
# 层: 算法
# - id: A1
#   name_zh: ① DualChannelAlert
#   name_en: DualChannelAlert
#   intro: class DualChannelAlert 源码 L67-L93
#   desc: 公共方法（定义序）: send, get_failed_channels；源码 L67-L93
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DualChannelAlert
#   downstream: zephyr.infrastructure.capacity_assurance.modules.__init__ ; zephyr.feedback_loo…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Channel(Enum):
    DASHBOARD = "dashboard"
    MESSAGING = "messaging"


@dataclass
class DualAlert:
    title: str
    message: str
    dashboard_sent: bool = False
    messaging_sent: bool = False


class DualChannelAlert:
    def __init__(self):
        self._alerts: list[DualAlert] = []

    def send(
        self, title: str, message: str, channels: tuple[Channel, ...] = (Channel.DASHBOARD, Channel.MESSAGING)
    ) -> DualAlert:
        alert = DualAlert(
            title=title,
            message=message,
            dashboard_sent=Channel.DASHBOARD in channels,
            messaging_sent=Channel.MESSAGING in channels,
        )
        self._alerts.append(alert)
        return alert

    def get_failed_channels(self) -> list[tuple[DualAlert, list[Channel]]]:
        result = []
        for a in self._alerts:
            failed = []
            if not a.dashboard_sent:
                failed.append(Channel.DASHBOARD)
            if not a.messaging_sent:
                failed.append(Channel.MESSAGING)
            if failed:
                result.append((a, failed))
        return result
