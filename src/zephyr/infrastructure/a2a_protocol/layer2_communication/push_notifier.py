# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.push_notifier
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_push_notifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Push Notifier — A2A 推送通知"""

from collections.abc import Callable


class PushNotifier:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

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
