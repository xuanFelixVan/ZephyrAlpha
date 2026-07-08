# [A_module] module_id=MOD-INF_ai_behavior | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""遥测 · ai_behavior — AI 行为遥测（7维度 + Error Taxonomy）"""

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
