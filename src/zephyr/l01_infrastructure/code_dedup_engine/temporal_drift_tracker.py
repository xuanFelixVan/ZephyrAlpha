"""时态签名漂移追踪器 — 渐进类型化检测."""

from __future__ import annotations

from datetime import datetime, timezone


class TemporalDriftTracker:
    """时态漂移追踪."""

    _DRIFT_THRESHOLD: int = 3

    def __init__(self) -> None:
        self._events: dict[str, list[dict]] = {}

    def record(self, function_name: str, event_type: str, detail: str = "") -> None:
        self._events.setdefault(function_name, []).append({
            "type": event_type,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def is_drifting(self, function_name: str) -> tuple[bool, int]:
        events = self._events.get(function_name, [])
        count = len(events)
        return count >= self._DRIFT_THRESHOLD, count

    def get_drift_report(self) -> list[dict]:
        reports = []
        for fname, events in self._events.items():
            drifting, count = self.is_drifting(fname)
            if drifting:
                reports.append({"function": fname, "events": count, "drifting": True, "locked": True})
        return reports
