"""Maintenance Window Adapter — v0.10.0 计划维护窗口适配器。"""
from __future__ import annotations

class MaintenanceWindowAdapter:
    def __init__(self):
        self._in_maintenance=False

    def start_maintenance(self)->None:
        self._in_maintenance=True

    def end_maintenance(self)->None:
        self._in_maintenance=False

    @property
    def in_maintenance(self)->bool:
        return self._in_maintenance

    def adjust_escalation(self, original_level:str)->str:
        if self._in_maintenance and original_level=="auto_guard":
            return "autonomous"
        return original_level
