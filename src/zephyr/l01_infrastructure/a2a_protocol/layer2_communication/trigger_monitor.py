"""触发监控器"""

class TriggerMonitor:
    def __init__(self):
        self._triggers: dict = {}

    def watch(self, trigger_id: str, condition: callable) -> None:
        self._triggers[trigger_id] = condition

    def check(self, trigger_id: str, context: dict) -> bool:
        fn = self._triggers.get(trigger_id)
        return fn(context) if fn else False
