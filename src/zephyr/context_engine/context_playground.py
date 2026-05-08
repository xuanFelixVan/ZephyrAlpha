"""context_playground.py — 上下文沙箱 dry-run (B5, DD79, TASK-015 beta v)"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class DryRunResult:
    task_summary: str
    ke_ids_selected: list[str]
    total_tokens: int
    decision_trace: list[str]


class ContextPlayground:
    """dry-run CLI /sc:dry-run <task> — 展示 build 全链路 (DD79)."""
    def dry_run(self, task_description: str) -> DryRunResult:
        return DryRunResult(task_summary=task_description, ke_ids_selected=[], total_tokens=0, decision_trace=[])


def playground_cli(task: str) -> DryRunResult:
    return ContextPlayground().dry_run(task)
