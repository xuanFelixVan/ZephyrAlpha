# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_hardware_router

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A 硬件路由器——GPU/CPU 调度"""

class A2AHardwareRouter:
    def route(self, task_type: str) -> str:
        routes = {"inference": "gpu", "training": "gpu", "governance": "cpu", "default": "cpu"}
        return routes.get(task_type, "cpu")
