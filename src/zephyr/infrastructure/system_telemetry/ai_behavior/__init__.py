# [A_module] module_id=MOD-INF-ai_behavior | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.ai_behavior
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] 独立ring buffer+独立持久化;FeatureFlag控制;7维度全覆盖
# [MODIFY-GUARD] event_sink.py; facade.py
# [CONSUMERS] facade.py; behavioral-auditor
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeatureFlag关闭->跳过写入;写入失败->日志warning
# [TESTS] tests/infrastructure/
# [TTL] permanent
"""
遥测 · ai_behavior — AI 行为遥测（7维度 + Error Taxonomy）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: AIBehaviorEvent, ErrorContext, emit_ai_behavior_event, validate_error…
#   code: __init__.py import L43
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AIBehaviorEvent, ErrorContext, emit_ai_behavior_event, event_sink, validate…
#   desc: __init__ import L43；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: AIBehaviorEvent, ErrorContext, emit_ai_behavior_event, event_sink, validate_err…
#   downstream: facade.py; behavioral-auditor
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.system_telemetry.ai_behavior.event_sink import (
    AIBehaviorEvent,
    ErrorContext,
    emit_ai_behavior_event,
    validate_error_context,
)

__all__ = [
    "AIBehaviorEvent",
    "ErrorContext",
    "emit_ai_behavior_event",
    "event_sink",
    "validate_error_context",
]
