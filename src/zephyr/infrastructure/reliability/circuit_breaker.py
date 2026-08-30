# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.reliability.circuit_breaker
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停执行。

依据：
    蓝图 MOD-TASK_SYSTEM §6.2.1 + v0.6.0
    任务卡 TASK-INF-0108 (Part 1/4)

功能：
    - 三状态：CLOSED/OPEN/HALF_OPEN
    - 熔断阈值：failure_threshold_continuous=3, timeout_s=60
    - HALF_OPEN 试探性恢复

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: circuit_breaker.py
# 层: 算法
# - id: A1
#   name_zh: ① CircuitBreaker
#   name_en: CircuitBreaker
#   intro: class CircuitBreaker 源码 L74-L135
#   desc: 公共方法（定义序）: call, state, reset；源码 L74-L135
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CircuitBreaker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 3
    recovery_timeout_s: int = 60
    _state: CircuitState = CircuitState.CLOSED
    _failure_count: int = 0
    _last_failure_time: float = 0.0
    _success_count: int = 0
    _half_open_success_threshold: int = 2
    _lock: Lock = field(default_factory=Lock)

    def call(self, func, *args, **kwargs):
        with self._lock:
            if self._state is CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self.recovery_timeout_s:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit {self.name} is OPEN. "
                        f"Retry in {self.recovery_timeout_s - (time.time() - self._last_failure_time):.0f}s"
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._on_failure()
            raise e

    def _on_success(self) -> None:
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._half_open_success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            elif self._state is CircuitState.CLOSED:
                self._failure_count = 0

    def _on_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN

    @property
    def state(self) -> CircuitState:
        return self._state

    @state.setter
    def state(self, value):
        """写入：state（Stage 4 公共化）。"""
        self._state = value

    def reset(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0


class CircuitBreakerOpenError(Exception):
    error_code = "ZA-IF-0010"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code
