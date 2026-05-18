# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer2_communication.trigger_monitor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""触发监控器"""

class TriggerMonitor:
    def __init__(self):
        self._triggers: dict = {}

    def watch(self, trigger_id: str, condition: callable) -> None:
        self._triggers[trigger_id] = condition

    def check(self, trigger_id: str, context: dict) -> bool:
        fn = self._triggers.get(trigger_id)
        return fn(context) if fn else False
