"""Knowledge Capture — v0.4.0 R30

Blindspot: Successful diagnoses not captured for future reuse.
Risk: R30 — Repeated diagnosis of same anomaly wastes resources.
"""
from dataclasses import dataclass, field

@dataclass
class KnowledgeCapture:
    captured: list[dict] = field(default_factory=list)

    def capture(self, diagnosis: dict) -> None:
        self.captured.append(diagnosis)
