"""No-LLM Degradation Mode — v0.8.0 R94

Blindspot: LLM outage paralyses FLE.
Risk: R94 — LLM API down; FLE cannot diagnose or repair anything.
"""
from dataclasses import dataclass

@dataclass
class NoLLMDegradation:
    rules_engine_active: bool = False
