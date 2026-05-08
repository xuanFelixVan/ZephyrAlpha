"""ce_bootstrap.py — CE 自举架构 (B1, DD75, TASK-015 beta v)"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class CEBootstrapLevel(Enum):
    CE_MVP = "ce_mvp"
    FUNCTIONAL = "functional"
    FULL_CE = "full_ce"


@dataclass
class BootstrapGate:
    level: CEBootstrapLevel
    required_ke_count: int = 0
    required_test_pass_rate: float = 0.9
    passed: bool = False
    graduation_log: list[str] = field(default_factory=list)


class CEBootstrap:
    """三级递进建造序列: CE-MVP → Functional → FullCE (DD75)."""
    def __init__(self) -> None:
        self._level = CEBootstrapLevel.CE_MVP
        self._gates: dict[CEBootstrapLevel, BootstrapGate] = {}

    @property
    def current_level(self) -> CEBootstrapLevel:
        return self._level

    def graduate(self, target: CEBootstrapLevel) -> BootstrapGate:
        return BootstrapGate(level=target)


ce_bootstrap_default = CEBootstrap()
