"""Retirement Planner — v0.10.0 R139

Blindspot: Outdated diagnostic rules persist forever without retirement.
Risk: R139 — Obsolete diagnostic rules cause false positives on evolved systems.
"""
from dataclasses import dataclass, field

@dataclass
class RetirementPlanner:
    rules: dict[str, float] = field(default_factory=dict)

    def mark_for_retirement(self, rule_id: str) -> None:
        self.rules[rule_id] = -1.0
