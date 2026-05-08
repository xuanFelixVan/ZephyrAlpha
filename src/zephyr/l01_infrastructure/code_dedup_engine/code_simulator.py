"""代码模拟器——播放录制的克隆演化序列，stress-test AST/baseline归一化."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimStep:
    iteration: int
    operation: str
    content: str
    expected_hash: str = ""
    tolerance: float = 0.0


@dataclass
class CodeSimulator:
    steps: list[SimStep] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    current_content: str = ""

    def load_sequence(self, base: str, steps: list[tuple[str, str]]) -> None:
        self.current_content = base
        for i, (op, content) in enumerate(steps):
            self.steps.append(SimStep(iteration=i, operation=op, content=content))

    def run(self) -> list[dict[str, Any]]:
        for step in self.steps:
            self.current_content = step.content
            self.history.append({
                "iteration": step.iteration,
                "operation": step.operation,
                "content_len": len(self.current_content),
            })
        return self.history

    def get_final(self) -> str:
        return self.current_content
