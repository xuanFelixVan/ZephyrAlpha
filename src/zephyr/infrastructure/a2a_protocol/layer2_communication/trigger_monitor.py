# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.trigger_monitor
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
# [A_module] module_id=MOD-INF_trigger_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""触发监控器"""


class TriggerMonitor:
    def __init__(self):
        self._triggers: dict = {}

    def watch(self, trigger_id: str, condition: callable) -> None:
        self._triggers[trigger_id] = condition

    def check(self, trigger_id: str, context: dict) -> bool:
        fn = self._triggers.get(trigger_id)
        return fn(context) if fn else False
