# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.dependency_capacity_guard
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: dependency_capacity_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① DependencyCapacityGuard
#   name_en: DependencyCapacityGuard
#   intro: class DependencyCapacityGuard 源码 L61-L87
#   desc: 公共方法（定义序）: set_capacity, update_load, check_all；源码 L61-L87
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DependencyCapacityGuard
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CapacityViolation:
    dependency: str
    current_load: float
    max_capacity: float
    utilization_pct: float


class DependencyCapacityGuard:
    def __init__(self):
        self._capacities: dict[str, float] = {}
        self._loads: dict[str, float] = {}

    def set_capacity(self, dependency: str, max_capacity: float) -> None:
        if max_capacity <= 0:
            raise ValueError(f"max_capacity must be > 0 for dependency '{dependency}', got {max_capacity}")
        self._capacities[dependency] = max_capacity

    def update_load(self, dependency: str, current_load: float) -> CapacityViolation | None:
        self._loads[dependency] = current_load
        cap = self._capacities.get(dependency, float("inf"))
        util = (current_load / cap * 100) if cap > 0 else 0.0
        if util > 90.0:
            return CapacityViolation(dependency, current_load, cap, util)
        return None

    def check_all(self) -> list[CapacityViolation]:
        violations = []
        for dep in self._capacities:
            load = self._loads.get(dep, 0.0)
            cap = self._capacities[dep]
            util = (load / cap * 100) if cap > 0 else 0.0
            if util > 90.0:
                violations.append(CapacityViolation(dep, load, cap, util))
        return violations
