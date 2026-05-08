from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PromptVersion:
    prompt_id: str
    semantic_version: str
    prompt_text: str

PROMPT_REGRESSION_THRESHOLD: float = 0.05
PROMPT_STORE: dict[str, PromptVersion] = {}
