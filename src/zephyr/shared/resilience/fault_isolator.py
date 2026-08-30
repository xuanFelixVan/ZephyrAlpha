# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.resilience.fault_isolator
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
#   name: failure_threshold 参数
#   fields: 参数 failure_threshold（无注解）
#   code: fault_isolator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FaultIsolator
#   name_en: FaultIsolator
#   intro: class FaultIsolator 源码 L68-L92
#   desc: 公共方法（定义序）: register, report_failure, is_isolated, get_isolated；源码 L68-L92
#   inputs: failure_threshold
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: FaultIsolator
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class IsolationState(Enum):
    HEALTHY = "healthy"
    SUSPECT = "suspect"
    ISOLATED = "isolated"


@dataclass
class FaultDomain:
    name: str
    state: IsolationState
    failure_count: int = 0
    dependencies: list[str] = field(default_factory=list)


class FaultIsolator:
    def __init__(self, failure_threshold: int = 3):
        self._threshold = failure_threshold
        self._domains: dict[str, FaultDomain] = {}

    def register(self, name: str, dependencies: list[str] | None = None) -> None:
        self._domains[name] = FaultDomain(name, IsolationState.HEALTHY, 0, dependencies or [])

    def report_failure(self, name: str) -> FaultDomain:
        domain = self._domains.get(name)
        if not domain:
            return FaultDomain(name, IsolationState.HEALTHY)
        domain.failure_count += 1
        if domain.failure_count >= self._threshold:
            domain.state = IsolationState.ISOLATED
        elif domain.failure_count >= self._threshold // 2:
            domain.state = IsolationState.SUSPECT
        return domain

    def is_isolated(self, name: str) -> bool:
        domain = self._domains.get(name)
        return domain.state is IsolationState.ISOLATED if domain else False

    def get_isolated(self) -> list[str]:
        return [n for n, d in self._domains.items() if d.state is IsolationState.ISOLATED]
