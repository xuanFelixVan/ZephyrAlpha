# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_context_rot

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""上下文腐烂检测"""

class A2AContextRot:
    def detect_rot(self, context_data: dict, age_seconds: float) -> float:
        return min(1.0, age_seconds / 3600)  # 线性衰减，1小时100%腐烂
