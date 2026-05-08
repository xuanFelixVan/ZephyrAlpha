"""AI 行为遥测 — 极简出站钩子（Phase 1）

后续可对接 CTR-P1-013、OLTP 或专用 topic；当前 fail-soft，仅标准库 logging。
"""
from __future__ import annotations


import json
import logging
from typing import Any

_logger = logging.getLogger(__name__)


def emit_ai_behavior_event(event_type: str, payload: dict[str, Any]) -> None:
    """记录一条 AI 行为相关事件（如规则触发、token 计量占位）。"""
    _logger.info("ai_behavior event=%s data=%s", event_type, json.dumps(payload, default=str))
