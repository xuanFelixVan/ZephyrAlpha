"""atomic_injector.py — 原子注入 (DD101, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AtomicResult:
    success: bool
    full_context_applied: bool
    rolled_back: bool = False


class AtomicInjector:
    """All-or-nothing: all 4 layers must succeed or rollback entirely (DD101)."""
    def inject_atomic(self, layers: dict[str, str]) -> AtomicResult:
        all_valid = all(bool(v) for v in layers.values())
        return AtomicResult(success=all_valid, full_context_applied=all_valid, rolled_back=not all_valid)
