# [BLUEPRINT] MOD-INF-015 | docs/03_modules/l01_infrastructure/system-telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.l01_infrastructure.system_telemetry.ai_behavior
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] 独立ring buffer+独立持久化;FeatureFlag控制;7维度全覆盖
# [MODIFY-GUARD] event_sink.py; facade.py
# [CONSUMERS] facade.py; behavioral_auditor
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeatureFlag关闭→跳过写入;写入失败→日志warning
# [TESTS] tests/unit/telemetry/
"""L12 · ai_behavior — AI 行为遥测（7维度 + Error Taxonomy）"""
from zephyr.l01_infrastructure.system_telemetry.ai_behavior.event_sink import (
    AIBehaviorEvent,
    ErrorContext,
    emit_ai_behavior_event,
    validate_error_context,
)

__all__ = [
    "AIBehaviorEvent",
    "ErrorContext",
    "emit_ai_behavior_event",
    "validate_error_context",
    "event_sink",
]
