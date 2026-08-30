# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.lifecycle.task_heartbeat
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__
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
#   name: default_interval 参数
#   fields: 参数 default_interval（无注解）
#   code: task_heartbeat.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: timeout_factor 参数
#   fields: 参数 timeout_factor（无注解）
#   code: task_heartbeat.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TaskHeartbeat
#   name_en: TaskHeartbeat
#   intro: class TaskHeartbeat 源码 L67-L89
#   desc: 公共方法（定义序）: start, pulse, check, detect_dead；源码 L67-L89
#   inputs: default_interval timeout_factor
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: TaskHeartbeat
#   downstream: zephyr.infrastructure.capacity_assurance.modules.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TaskPulse:
    task_id: str
    last_pulse: float
    interval_seconds: float
    is_alive: bool


class TaskHeartbeat:
    def __init__(self, default_interval: float = 60.0, timeout_factor: float = 3.0):
        self._default_interval = default_interval
        self._timeout_factor = timeout_factor
        self._pulses: dict[str, tuple[float, float]] = {}

    def start(self, task_id: str, interval: float | None = None) -> None:
        self._pulses[task_id] = (time.time(), interval or self._default_interval)

    def pulse(self, task_id: str) -> None:
        if task_id in self._pulses:
            _, interval = self._pulses[task_id]
            self._pulses[task_id] = (time.time(), interval)

    def check(self, task_id: str) -> TaskPulse:
        if task_id not in self._pulses:
            return TaskPulse(task_id, 0.0, self._default_interval, False)
        last, interval = self._pulses[task_id]
        alive = (time.time() - last) <= interval * self._timeout_factor
        return TaskPulse(task_id, last, interval, alive)

    def detect_dead(self) -> list[str]:
        return [tid for tid in self._pulses if not self.check(tid).is_alive]
