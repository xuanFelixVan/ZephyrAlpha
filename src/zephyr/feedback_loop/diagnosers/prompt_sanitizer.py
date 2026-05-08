"""Prompt Sanitizer — v0.10.0 R133

Blindspot: External data injected into prompts can carry injection attacks.
Risk: R133 — Prompt injection through diagnosis evidence compromises LLM output.
"""
from dataclasses import dataclass

@dataclass
class PromptSanitizer:
    def sanitize(self, text: str) -> str:
        return text.replace("ignore previous", "[FILTERED]")
