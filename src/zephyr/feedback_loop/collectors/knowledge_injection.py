"""Knowledge Injection — v0.8.0 R102

Blindspot: Human expert knowledge cannot be injected into FLE KB.
Risk: R102 — FLE relearns what owner already knows.
"""
from dataclasses import dataclass, field

@dataclass
class KnowledgeInjection:
    injected: list[dict] = field(default_factory=list)

    def inject(self, knowledge: dict) -> None:
        self.injected.append(knowledge)
