"""Teacher Transfer — v0.6.0 R53

Blindspot: New FLE instances learn from scratch.
Risk: R53 — New instance repeats all mistakes previous instance learned from.
"""
from dataclasses import dataclass

@dataclass
class TeacherTransfer:
    transferred: bool = False

    def transfer(self, source: dict) -> dict:
        self.transferred = True
        return dict(source)
