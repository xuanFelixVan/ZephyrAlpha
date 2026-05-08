"""Checkpoint Manager — v0.3.0 R18

Blindspot: FLE state lost on crash; no recovery checkpoint.
Risk: R18 — Crash during repair leaves system in inconsistent state.
"""
from dataclasses import dataclass, field

@dataclass
class CheckpointManager:
    checkpoints: list[dict] = field(default_factory=list)

    def save(self, state: dict) -> int:
        self.checkpoints.append(dict(state))
        return len(self.checkpoints) - 1
