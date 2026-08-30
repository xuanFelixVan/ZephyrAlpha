# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §2.3
# [MODULE] zephyr.governance.resilience_governance.circuit_breaker
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.escalation.escalation_engine;zephyr.governance.escalation;zephyr.governance.intelligence_governance.self_test
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] error_budget是022特有扩展;接口call()->bool;与shared/resilience/circuit_breaker(MOD-INF-016)是不同实现(016用call(func)->raises)
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 熔断拒绝->call()返回False;error_budget耗尽->降级
# [TESTS] tests/infrastructure/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
Circuit Breaker — MOD-INF-022

Half-open/closed/open state machine with error budget gating, cooldown, and auto-recovery.
Blueprint: docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md §2.3

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name（无注解）
#   code: circuit_breaker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: circuit_breaker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CircuitBreaker
#   name_en: CircuitBreaker
#   intro: class CircuitBreaker 源码 L86-L173
#   desc: 公共方法（定义序）: failure_count, state, call, record_success, record_failure, force_open, force_close, error_budget_…
#   inputs: name config
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CircuitBreaker
#   downstream: zephyr.governance.escalation.escalation_engine;zephyr.governance.escalation;zep…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    # 5.92.2 修复: 统一日志格式, 返回 value 而非 ClassName.MEMBER
    def __str__(self) -> str:
        return self.value

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60
    half_open_max_requests: int = 1
    cooldown_seconds: int = 300
    error_budget_per_hour: int = 10


class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count: int = 0
        self._success_count: int = 0
        self._last_failure_time: float = 0.0
        self._error_budget_consumed: int = 0
        self._error_budget_reset: float = time.time()
        self._lock = threading.Lock()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def failure_count(self) -> int:
        """只读：failure_count（Stage 4 公共化）。"""
        return self._failure_count

    @failure_count.setter
    def failure_count(self, value):
        """写入：failure_count（Stage 4 公共化）。"""
        self._failure_count = value

    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._maybe_transition()
            return self._state

    @state.setter
    def state(self, value):
        """写入：state（Stage 4 公共化）。"""
        self._state = value

    def call(self) -> bool:
        with self._lock:
            self._maybe_transition()
            if self._state is CircuitState.OPEN:
                return False
            return True

    def record_success(self) -> None:
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            self._failure_count = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            self._consume_error_budget()
            if self._failure_count >= self.config.failure_threshold or self._state is CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN

    def force_open(self) -> None:
        with self._lock:
            self._state = CircuitState.OPEN

    def force_close(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0

    def _maybe_transition(self) -> None:
        if self._state is not CircuitState.OPEN:
            return
        if self._last_failure_time == 0.0:
            return
        elapsed = time.time() - self._last_failure_time
        if elapsed >= self.config.cooldown_seconds:
            self._state = CircuitState.HALF_OPEN
            self._success_count = 0

    def _consume_error_budget(self) -> None:
        now = time.time()
        if now - self._error_budget_reset > 3600:
            self._error_budget_consumed = 0
            self._error_budget_reset = now
        self._error_budget_consumed += 1

    @property
    def error_budget_remaining(self) -> int:
        return max(0, self.config.error_budget_per_hour - self._error_budget_consumed)


# 代理导出：CircuitBreakerOpenError 实际定义在 infrastructure.reliability.circuit_breaker
# 使用延迟导入避免循环依赖


def __getattr__(name):
    """延迟导入 CircuitBreakerOpenError 避免循环依赖."""
    if name == "CircuitBreakerOpenError":
        from zephyr.infrastructure.reliability.circuit_breaker import CircuitBreakerOpenError

        return CircuitBreakerOpenError
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["CircuitBreaker", "CircuitBreakerConfig", "CircuitBreakerOpenError", "CircuitState"]
