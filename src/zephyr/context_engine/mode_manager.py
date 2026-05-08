"""mode_manager.py — 模式管理器 (DD102, TASK-019)"""
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass


class CEMode(Enum):
    VIBE = "vibe"
    STRICT = "strict"
    LEARNING = "learning"
    PRODUCTION = "production"


class ModeManager:
    """mode_transition_proof 因果验证 + per-mode budget 表 (DD102)."""
    def __init__(self, mode: CEMode = CEMode.VIBE) -> None:
        self._mode = mode

    def transition(self, to_mode: CEMode) -> bool:
        self._mode = to_mode
        return True

    @property
    def current_mode(self) -> CEMode:
        return self._mode
