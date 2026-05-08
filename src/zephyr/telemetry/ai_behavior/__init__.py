"""L12 · ai_behavior — AI 行为遥测（幻觉率/token/规则触发）"""

from zephyr.telemetry.ai_behavior.event_sink import emit_ai_behavior_event

__all__ = ['emit_ai_behavior_event', 'event_sink']
