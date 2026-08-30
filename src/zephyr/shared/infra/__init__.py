# [A_module] module_id=MOD-SHR-infra | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: ProcessLifecycleGateway
#   code: __init__.py import L32
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ProcessLifecycleGateway, cache, idempotency, limiter, lock, observer, outbo…
#   desc: __init__ import L32；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: ProcessLifecycleGateway, cache, idempotency, limiter, lock, observer, outbox, p…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

from . import cache

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [TTL] permanent
"""shared.infra — auto-generated package init."""

__all__ = [
    "ProcessLifecycleGateway",
    "cache",
    "idempotency",
    "limiter",
    "lock",
    "observer",
    "outbox",
    "process_lifecycle_gateway",
    "process_pool",
]
