"""
audit_trail.bridge — 审计桥接辅助模块

为所有使用内存 _audit_log 的模块提供一行式核心链接入。
避免每个模块重复写 try/except ImportError 样板代码。

用法:
    from zephyr.audit_trail.bridge import write_to_core

    write_to_core("gate_override", {"gate_id": "G0", "action": "override"})
"""

from __future__ import annotations

from typing import Any

_WRITER = None
_AVAILABLE = False

try:
    from zephyr.audit_trail.writer import AuditWriter as _CoreWriter
    _AVAILABLE = True
except ImportError:
    _CoreWriter = None


def _get_writer():
    global _WRITER
    if _WRITER is None and _AVAILABLE:
        try:
            _WRITER = _CoreWriter()
        except Exception:
            pass
    return _WRITER


def write_to_core(event_type: str, event: dict[str, Any]) -> str | None:
    """写入核心不可变审计链。成功返回 chain_hash，失败返回 None。"""
    writer = _get_writer()
    if writer is None:
        return None
    try:
        core_event = dict(event)
        core_event["event_type"] = event_type
        if "agent_id" not in core_event:
            core_event["agent_id"] = event_type
        return writer.write(core_event)
    except Exception:
        return None
