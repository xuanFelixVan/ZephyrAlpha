# [A_module] module_id=MOD-INF-health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.infrastructure.health_monitor
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

"""
Health Monitor — 全系统健康聚合模块

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: HealthAggregator, HealthReport, SystemHealth, check_all
#   code: __init__.py import L44
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 HealthAggregator, HealthReport, SystemHealth, check_all, health_aggregator（…
#   desc: __init__ import L44；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: HealthAggregator, HealthReport, SystemHealth, check_all, health_aggregator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.health_monitor.health_aggregator import (
    HealthAggregator,
    HealthReport,
    SystemHealth,
    check_all,
)

__all__ = [
    "HealthAggregator",
    "HealthReport",
    "SystemHealth",
    "check_all",
    "health_aggregator",
]
