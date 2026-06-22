# [A_module] module_id=MOD-SHR_ai_understandability_constraint | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UnderstandabilityResult:
    content: str
    score: float
    passed: bool
    violations: list[str]


class AiUnderstandabilityConstraint:
    def __init__(self, max_line_length: int = 120, max_nesting: int = 4, min_comment_ratio: float = 0.0):
        self._max_line_length = max_line_length
        self._max_nesting = max_nesting
        self._min_comment_ratio = min_comment_ratio

    def check(self, content: str) -> UnderstandabilityResult:
        violations = []
        lines = content.split("\n")
        long_lines = sum(1 for l in lines if len(l) > self._max_line_length)
        if long_lines > 0:
            violations.append(f"{long_lines} lines exceed {self._max_line_length} chars")
        max_depth = 0
        for line in lines:
            if line.strip():
                depth = (len(line) - len(line.lstrip())) // 4
                max_depth = max(max_depth, depth)
        if max_depth > self._max_nesting:
            violations.append(f"nesting depth {max_depth} exceeds {self._max_nesting}")
        score = max(0.0, 1.0 - len(violations) * 0.3)
        return UnderstandabilityResult(content, score, len(violations) == 0, violations)
