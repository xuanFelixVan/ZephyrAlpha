"""Last Resort Watchdog — v0.8.0 终极逃生舱: 所有escalation失败后的final fallback+shutdown。"""
from __future__ import annotations

class LastResortWatchdog:
    def __init__(self):
        self._activated=False

    def activate(self)->None:
        self._activated=True

    @property
    def active(self)->bool:
        return self._activated

    def emergency_shutdown(self)->dict:
        self._activated=True
        return {"action":"EMERGENCY_SHUTDOWN","reason":"last_resort_activated","safe_mode":True}
