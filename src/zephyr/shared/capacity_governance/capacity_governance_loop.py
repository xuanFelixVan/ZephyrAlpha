# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.shared.capacity_governance.capacity_governance_loop
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: upper_threshold 参数
#   fields: 参数 upper_threshold（无注解）
#   code: capacity_governance_loop.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: lower_threshold 参数
#   fields: 参数 lower_threshold（无注解）
#   code: capacity_governance_loop.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CapacityGovernanceLoop
#   name_en: CapacityGovernanceLoop
#   intro: class CapacityGovernanceLoop 源码 L74-L102
#   desc: 公共方法（定义序）: evaluate；源码 L74-L102
#   inputs: upper_threshold lower_threshold
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CapacityGovernanceLoop
#   downstream: zephyr.trading.resource_optimization
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GovernanceAction(Enum):
    HOLD = "hold"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    DEGRADE = "degrade"
    ALERT = "alert"


@dataclass
class GovernanceDecision:
    action: GovernanceAction
    reason: str
    confidence: float


class CapacityGovernanceLoop:
    def __init__(self, upper_threshold: float = 0.85, lower_threshold: float = 0.3) -> None:
        self._upper = upper_threshold
        self._lower = lower_threshold

    def evaluate(self, utilization: float) -> GovernanceDecision:
        if utilization <= 0.0:
            return GovernanceDecision(
                GovernanceAction.ALERT,
                f"utilization {utilization:.1%} is zero or negative — possible monitoring failure or cold start",
                0.5,
            )
        if utilization >= self._upper:
            return GovernanceDecision(
                GovernanceAction.SCALE_UP,
                f"utilization {utilization:.1%} >= {self._upper:.1%}",
                0.9,
            )
        if utilization <= self._lower:
            return GovernanceDecision(
                GovernanceAction.SCALE_DOWN,
                f"utilization {utilization:.1%} <= {self._lower:.1%}",
                0.8,
            )
        return GovernanceDecision(
            GovernanceAction.HOLD,
            f"utilization {utilization:.1%} within bounds",
            1.0,
        )
