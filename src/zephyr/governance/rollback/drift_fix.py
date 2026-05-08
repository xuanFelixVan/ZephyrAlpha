"""G-CT-005 消费端 — Rollback.on_drift_fix() 消费漂移事件执行自动修复."""
from __future__ import annotations

import importlib.util
import os
from typing import Any

_events_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "drift_detector", "events.py",
)
_spec = importlib.util.spec_from_file_location(
    "zephyr.governance.drift_detector.events", _events_path,
)
_events_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_events_mod)
DriftEvent = _events_mod.DriftEvent


class DriftFixHandler:
    """漂移自动修复处理器 — G-CT-005 消费端."""

    def on_drift_fix(self, event: DriftEvent) -> dict[str, Any]:
        if not event.auto_fixable:
            event.mark_manual_required()
            return {
                "drift_id": event.drift_id,
                "fixed": False,
                "action": "MANUAL_REQUIRED",
                "reason": "auto_fixable=False",
                "drift_type": event.drift_type.value,
            }

        event.mark_fixed()
        return {
            "drift_id": event.drift_id,
            "fixed": True,
            "action": "AUTO_FIXED",
            "target": event.target,
            "fix_suggestion": event.fix_suggestion,
            "drift_type": event.drift_type.value,
        }
