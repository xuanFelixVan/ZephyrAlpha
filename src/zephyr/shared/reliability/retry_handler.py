# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.reliability.retry_handler
# [DOMAIN] D_SHARED
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

"""


Retry Handler — 指数退避重试 + 可恢复/不可恢复错误分类。

依据：
    蓝图 MOD-TASK_SYSTEM §6.2.2 + v0.6.0
    任务卡 TASK-INF-0108 (Part 2/4)

功能：
    - 指数退避：base_delay=1s, max_delay=64s, max_retries=5
    - 可恢复错误（network/timeout）-> 重试
    - 不可恢复错误（ValueError/AssertionError）-> 立即失败

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 被保护函数 func 可调用对象
#   fields: func 加 *args/**kwargs，execute 内被反复调用直至成功或耗尽重试
#   code: execute(func, *args, **kwargs) L95
# - id: I2
#   name: 重试配置 RetryConfig 数据类
#   fields: base_delay_s=1.0、max_delay_s=64.0、max_retries=5、backoff_multiplier=2.0、jitter=True
#   code: RetryConfig L49-L55
# 层: 算法
# - id: A1
#   name_zh: ① 错误可恢复性分类
#   name_en: is_unrecoverable
#   intro: 用 isinstance 对照六类不可恢复异常，决定立即失败还是继续重试
#   desc: UNRECOVERABLE_EXCEPTIONS=(ValueError, TypeError, AssertionError, SyntaxError, ImportError, AttributeError)；命中即不可恢复；其余（如 network/timeout 类）视为可恢复
#   inputs: I1
#   outputs: bool 分类结果
# - id: A2
#   name_zh: ② 指数退避重试循环
#   name_en: execute
#   intro: 失败按指数退避睡眠后重试，不可恢复错误或次数耗尽立即收兵
#   desc: for i in 0..max_retries：调 func 成功即记 RetryAttempt(success=True) 返回；异常先记尝试，再用 A1 分类——不可恢复或 i==max_retries 返回带 final_error 的失败；否则 delay=min(base_delay_s×backoff_multiplier^i, max_delay_s)，jitter 开启时 delay×=(0.5+random.random())，time.sleep(delay) 后进入下一轮
#   inputs: I1 I2
#   outputs: RetryResult
#   invariant: 最多执行 max_retries+1 次；退避延迟封顶 max_delay_s
# 层: 输出
# - id: O1
#   name_zh: 重试结果报告
#   name_en: RetryResult
#   intro: 含 success/逐次 RetryAttempt 明细/total_time_s/final_error 的重试全过程报告
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

UNRECOVERABLE_EXCEPTIONS: Final[tuple] = (
    ValueError,
    TypeError,
    AssertionError,
    SyntaxError,
    ImportError,
    AttributeError,
)


@dataclass
class RetryConfig:
    base_delay_s: float = 1.0
    max_delay_s: float = 64.0
    max_retries: int = 5
    backoff_multiplier: float = 2.0
    jitter: bool = True


@dataclass
class RetryAttempt:
    attempt: int
    success: bool
    delay_s: float
    exception: Exception | None = None
    total_time_s: float = 0.0


@dataclass
class RetryResult:
    success: bool
    attempts: list[RetryAttempt]
    total_time_s: float
    final_error: Exception | None = None


class RetryHandler:
    def __init__(self, config: RetryConfig | None = None) -> None:
        self._config = config or RetryConfig()

    @property
    def config(self):
        """只读：config（Stage 4 公共化）。"""
        return self._config

    @config.setter
    def config(self, value):
        """写入：config（Stage 4 公共化）。"""
        self._config = value

    @staticmethod
    def is_unrecoverable(exc: Exception) -> bool:
        return isinstance(exc, UNRECOVERABLE_EXCEPTIONS)

    def execute(self, func: Callable, *args: Any, **kwargs: Any) -> RetryResult:
        attempts: list[RetryAttempt] = []
        t0 = time.time()

        for i in range(self._config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                attempts.append(
                    RetryAttempt(
                        attempt=i + 1,
                        success=True,
                        delay_s=time.time() - t0,
                    )
                )
                return RetryResult(
                    success=True,
                    attempts=attempts,
                    total_time_s=time.time() - t0,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                attempts.append(
                    RetryAttempt(
                        attempt=i + 1,
                        success=False,
                        delay_s=time.time() - t0,
                        exception=e,
                    )
                )

                if self._is_unrecoverable(e) or i == self._config.max_retries:
                    return RetryResult(
                        success=False,
                        attempts=attempts,
                        total_time_s=time.time() - t0,
                        final_error=e,
                    )

                delay = min(
                    self._config.base_delay_s * (self._config.backoff_multiplier**i),
                    self._config.max_delay_s,
                )

                if self._config.jitter:
                    import random

                    delay *= 0.5 + random.random()

                time.sleep(delay)

        return RetryResult(success=False, attempts=attempts, total_time_s=time.time() - t0)

    @staticmethod
    def _is_unrecoverable(exc: Exception) -> bool:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return RetryHandler.is_unrecoverable(exc)
