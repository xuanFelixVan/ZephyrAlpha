"""Failure Replay — v0.7.0 R77

Blindspot: Past failures not replayed for training.
Risk: R77 — FLE forgets failure patterns; repeats same mistakes.
"""
from dataclasses import dataclass, field

@dataclass
class FailureReplay:
    failures: list[dict] = field(default_factory=list)

    def record(self, failure: dict) -> None:
        self.failures.append(failure)
