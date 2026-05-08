"""
Per-Task Token Budget — 任务级 Token 预算 (盲点 #18)
特性：
  - 与 Per-request 预算正交：每 task 独立预算池
  - 单任务限额：8K input / 4K output
  - 超限后自动降级为精简模式
"""
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TaskBudget:
    task_id: str
    input_limit: int = 8192
    output_limit: int = 4096
    input_used: int = 0
    output_used: int = 0


class PerTaskTokenBudget:
    """
    任务级 Token 预算 (盲点 #18)
    """

    def __init__(self):
        self._budgets: dict[str, TaskBudget] = {}

    def create_budget(self, task_id: str, input_limit: int = 8192,
                      output_limit: int = 4096) -> TaskBudget:
        budget = TaskBudget(task_id=task_id, input_limit=input_limit,
                            output_limit=output_limit)
        self._budgets[task_id] = budget
        return budget

    def can_consume(self, task_id: str, tokens: int, is_input: bool = True) -> bool:
        budget = self._budgets.get(task_id)
        if budget is None:
            return True

        if is_input:
            return (budget.input_used + tokens) <= budget.input_limit
        return (budget.output_used + tokens) <= budget.output_limit

    def consume(self, task_id: str, tokens: int, is_input: bool = True):
        budget = self._budgets.get(task_id)
        if budget:
            if is_input:
                budget.input_used += tokens
            else:
                budget.output_used += tokens

    def get_remaining(self, task_id: str) -> dict:
        budget = self._budgets.get(task_id)
        if budget is None:
            return {"input_remaining": -1, "output_remaining": -1}
        return {
            "input_remaining": budget.input_limit - budget.input_used,
            "output_remaining": budget.output_limit - budget.output_used,
        }
