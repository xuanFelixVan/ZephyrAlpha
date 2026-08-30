# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.push_notifier
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Push Notifier — A2A 推送通知

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: push_notifier.py
# 层: 算法
# - id: A1
#   name_zh: ① PushNotifier
#   name_en: PushNotifier
#   intro: class PushNotifier 源码 L51-L77
#   desc: 公共方法（定义序）: subscribers, subscribe, unsubscribe, notify；源码 L51-L77
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PushNotifier
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from collections.abc import Callable


class PushNotifier:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def subscribers(self) -> dict[str, list[Callable]]:
        """只读：subscribers（Stage 4 公共化）。"""
        return self._subscribers

    @subscribers.setter
    def subscribers(self, value):
        """写入：subscribers（Stage 4 公共化）。"""
        self._subscribers = value

    def subscribe(self, agent_id: str, callback: Callable):
        self._subscribers.setdefault(agent_id, []).append(callback)

    def unsubscribe(self, agent_id: str, callback: Callable):
        if agent_id in self._subscribers:
            self._subscribers[agent_id].remove(callback)

    def notify(self, agent_id: str, event: str, data: dict = None) -> int:
        callbacks = self._subscribers.get(agent_id, [])
        for cb in callbacks:
            cb(event, data or {})
        return len(callbacks)
