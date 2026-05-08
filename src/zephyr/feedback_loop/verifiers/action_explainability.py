"""Action Explainability — v0.3.0 R15

Blindspot: FLE actions opaque; owner cannot understand why a repair was chosen.
Risk: R15 — Trust eroded; owner overrides correct repairs due to lack of explainability.
"""
from dataclasses import dataclass

@dataclass
class ActionExplainability:

    def explain(self, action: dict) -> str:
        return f"Action: {action.get('type')} — Reason: {action.get('reason')}"
