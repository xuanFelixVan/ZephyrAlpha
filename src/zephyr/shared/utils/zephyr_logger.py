# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.zephyr_logger
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.logging
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
#   code: zephyr_logger.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 LogLevel, TraceContext, ZephyrLogger, configure_root_logger, get_logger, mo…
#   desc: __init__ import L0；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: LogLevel, TraceContext, ZephyrLogger, configure_root_logger, get_logger, module…
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.utils.logging import (
    LogLevel,
    TraceContext,  # [DEPRECATED] 兼容别名，新代码用 trace_context
    ZephyrLogger,
    configure_root_logger,
    get_logger,
    module_id_var,
    session_id_var,
    trace_context,
    trace_id_var,
)

__all__ = [
    "LogLevel",
    "TraceContext",
    "ZephyrLogger",
    "configure_root_logger",
    "get_logger",
    "module_id_var",
    "session_id_var",
    "trace_context",
    "trace_id_var",
]
