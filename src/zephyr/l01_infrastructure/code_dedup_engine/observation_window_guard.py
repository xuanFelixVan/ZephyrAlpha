"""提取后稳定观察期守护 — 对标SDP 14天观察."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta


class ObservationWindowGuard:
    """14天稳定观察期."""

    _WINDOW_DAYS: int = 14

    def check(self, extraction_date: str) -> tuple[bool, int, str]:
        """检查提取是否已过14天观察期."""
        try:
            dt = datetime.fromisoformat(extraction_date.replace("Z", "+00:00"))
        except ValueError:
            return False, 0, "invalid_date"

        age = (datetime.now(timezone.utc) - dt.replace(tzinfo=timezone.utc)).days
        if age >= self._WINDOW_DAYS:
            return True, age, f"观察期通过：{age}天/14天"
        return False, age, f"观察期进行中：{age}天/14天，剩余{self._WINDOW_DAYS-age}天"
