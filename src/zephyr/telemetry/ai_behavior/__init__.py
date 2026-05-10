"""Backward-compatibility shim — still imports from local event_sink for legacy API (SRC-0035).

For new code, use: from zephyr.l12_system_telemetry.ai_behavior import ...
"""

from zephyr.telemetry.ai_behavior.event_sink import emit_ai_behavior_event

__all__ = ["emit_ai_behavior_event", "event_sink"]
