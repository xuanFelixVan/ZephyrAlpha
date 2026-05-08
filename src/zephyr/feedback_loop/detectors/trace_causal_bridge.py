"""Trace Causal Bridge — v0.6.0 R62

Blindspot: Distributed trace spans disconnected from diagnosis context.
Risk: R62 — Root cause spans multiple services; single-service view misses causal chain.
"""
from dataclasses import dataclass, field

@dataclass
class TraceCausalBridge:
    spans: list[dict] = field(default_factory=list)

    def bridge(self, span: dict) -> None:
        self.spans.append(span)
