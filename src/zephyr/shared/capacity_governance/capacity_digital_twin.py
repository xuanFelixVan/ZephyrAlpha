# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.capacity_digital_twin
# [DOMAIN] D_SHARED
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name（无注解）
#   code: capacity_digital_twin.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CapacityDigitalTwin
#   name_en: CapacityDigitalTwin
#   intro: class CapacityDigitalTwin 源码 L63-L88
#   desc: 公共方法（定义序）: ingest, predict, name；源码 L63-L88
#   inputs: name
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CapacityDigitalTwin
#   downstream: zephyr.trading.resource_optimization
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class TwinState:
    cpu_utilization: float
    memory_utilization: float
    io_throughput: float
    active_connections: int
    timestamp: str


class CapacityDigitalTwin:
    def __init__(self, name: str) -> None:
        self._name = name
        self._states: list[TwinState] = []
        self._max_states = 1000

    def ingest(self, state: TwinState) -> None:
        self._states.append(state)
        if len(self._states) > self._max_states:
            self._states = self._states[-self._max_states :]

    def predict(self, horizon_steps: int = 10) -> TwinState:
        if not self._states:
            return TwinState(0.0, 0.0, 0.0, 0, "")
        last = self._states[-1]
        return TwinState(
            last.cpu_utilization,
            last.memory_utilization,
            last.io_throughput,
            last.active_connections,
            datetime.now(UTC).isoformat(),
        )

    @property
    def name(self) -> str:
        return self._name
