"""LLM Cost Accounting — v0.4.0 R35

Blindspot: LLM API costs unaccounted; budget invisible.
Risk: R35 — Surprise bill from runaway LLM calls.
"""
from dataclasses import dataclass

@dataclass
class LLMCostAccounting:
    total_cost: float = 0.0

    def record(self, model: str, tokens: int) -> None:
        self.total_cost += tokens * 0.00001
