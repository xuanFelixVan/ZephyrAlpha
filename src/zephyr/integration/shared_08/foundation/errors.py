# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.foundation.errors
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_errors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""errors.py —— re-export shim（真源：zephyr.shared.foundation.errors）

P3 治本（2026-06-29）：本文件原为 zephyr.shared.foundation.errors 的漂移副本
（两份 class ZephyrBaseError 定义字节级一致，仅头部元数据不同），违反真源唯一原则。
现改为 re-export shim，从 shared 层真源导入全部 13 个 Error 类。

理由：
  1. 真源唯一——shared.foundation.errors 是 ZephyrBaseError 体系唯一真源
  2. 消除 breaking change——两个路径指向同一类对象，消费者 `except ZephyrBaseError`
     无论从哪个路径获取都能捕获子类异常
  3. 消除循环依赖——shared.infra_06 改引 shared.foundation.errors 后不再触发
     integration→shared→integration 循环链

新 AI 引导：新增 Error 子类时，改 zephyr.shared.foundation.errors（真源），
本 shim 自动 re-export，无需同步维护两份。
"""

from zephyr.shared.foundation.errors import (  # noqa: F401 (re-export)
    ConfigError,
    ContextError,
    ContractError,
    DataError,
    FeedbackError,
    GateError,
    IOError,
    PipelineError,
    SecurityError,
    TaskError,
    UnimplementedError,
    ValidationError,
    ZephyrBaseError,
)

__all__ = [
    "ConfigError",
    "ContextError",
    "ContractError",
    "DataError",
    "FeedbackError",
    "GateError",
    "IOError",
    "PipelineError",
    "SecurityError",
    "TaskError",
    "UnimplementedError",
    "ValidationError",
    "ZephyrBaseError",
]
