# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.hawthorne_blind
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
# [A_module] module_id=MOD-INF_hawthorne_blind | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
Hawthorne Blind — AI 霍桑效应消除 (盲点 #31)
特性：
  - 监控数据与 AI 可见信息分离
  - AI 不应感知自己被监控的精确指标
"""

from typing import Any


class HawthorneBlind:
    """
    AI 霍桑效应盲化 (盲点 #31)
    原则：AI 可见容量指标必须经过盲化处理
    """

    def __init__(self):
        self._visible_rules: dict[str, str] = {}

    def add_rule(self, metric: str, visibility: str = "hidden"):
        self._visible_rules[metric] = visibility

    def filter_for_ai(self, raw_metrics: dict) -> dict:
        visible: dict[str, Any] = {}
        for key, value in raw_metrics.items():
            visibility = self._visible_rules.get(key, "hidden")
            if visibility == "visible":
                visible[key] = value
            elif visibility == "aggregated":
                visible[f"agg_{key}"] = "NORMAL" if isinstance(value, (int, float)) else value
            else:
                pass
        return visible
