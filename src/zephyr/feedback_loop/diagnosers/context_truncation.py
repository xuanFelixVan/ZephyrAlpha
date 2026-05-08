"""Context Truncation Detector — v0.9.0 R122

Blindspot: LLM context window overflow silently drops critical diagnostic evidence.
Risk: R122 — Truncated context causes misdiagnosis on complex multi-factor anomalies.
"""
from dataclasses import dataclass


@dataclass
class ContextTruncation:
    max_tokens: int = 8192

    def check(self, token_count: int) -> bool:
        return token_count > self.max_tokens
