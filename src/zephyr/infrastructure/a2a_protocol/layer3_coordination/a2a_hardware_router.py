# [A_module] module_id=MOD-INF_a2a_hardware_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_hardware_router

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A 硬件路由器——GPU/CPU 调度"""


class A2AHardwareRouter:
    def route(self, task_type: str) -> str:
        routes = {"inference": "gpu", "training": "gpu", "governance": "cpu", "default": "cpu"}
        return routes.get(task_type, "cpu")
