# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.cliff_detector
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_cliff_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
Cliff Detector — 模块数悬崖检测 (盲点 #36)
特性：
  - 每个模块注册时检查是否接近 1500 极限
  - 800+ 模块 → WARNING, 1200+ → CRITICAL
"""


class CliffDetector:
    """
    模块悬崖检测器 (盲点 #36)
    """

    TOTAL_LIMIT = 1500
    WARNING_THRESHOLD = 800
    CRITICAL_THRESHOLD = 1200

    def __init__(self):
        self._module_count = 0
        self._module_names: list[str] = []

    def register(self, module_name: str) -> dict:
        self._module_count += 1
        self._module_names.append(module_name)

        level = "HEALTHY"
        remaining = self.TOTAL_LIMIT - self._module_count

        if self._module_count >= self.CRITICAL_THRESHOLD:
            level = "CRITICAL"
        elif self._module_count >= self.WARNING_THRESHOLD:
            level = "WARNING"

        return {
            "current_count": self._module_count,
            "total_limit": self.TOTAL_LIMIT,
            "remaining": remaining,
            "level": level,
            "suggestion": "Consider module optimization" if level != "HEALTHY" else "",
        }

    def get_count(self) -> int:
        return self._module_count

    def get_remaining(self) -> int:
        return max(0, self.TOTAL_LIMIT - self._module_count)
