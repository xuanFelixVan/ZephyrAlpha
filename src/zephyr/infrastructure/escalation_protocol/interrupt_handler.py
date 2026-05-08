"""Interrupt Handler — D-022-06 硬中断处理器: Owner紧急中断+优雅停止+状态保存。"""
from __future__ import annotations
from enum import Enum

class InterruptSignal(Enum):
    OWNER_OVERRIDE="owner_override"
    SAFETY_BREACH="safety_breach"
    HARD_TIMEOUT="hard_timeout"

class InterruptHandler:
    def __init__(self):
        self._interrupted=False
        self._signal:InterruptSignal|None=None

    def interrupt(self, signal:InterruptSignal)->None:
        self._interrupted=True
        self._signal=signal

    @property
    def interrupted(self)->bool:
        return self._interrupted

    def save_state(self)->dict:
        return {"interrupted":self._interrupted,"signal":self._signal.value if self._signal else None}

    def resume(self)->bool:
        self._interrupted=False
        self._signal=None
        return True
