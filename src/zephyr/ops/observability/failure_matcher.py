# [BLUEPRINT] SRC-124 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.observability.failure_matcher
# [DOMAIN] D-OPS
# [DEPENDENCIES] zephyr.ops.observability.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_failure_matcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
Failure Matcher — 失败模式分类与根因匹配。

依据：
    蓝图 MOD-INF-006 §6.3.3 + v0.6.0
    任务卡 TASK-INF-0109 (Part 3/5)
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class FailureCategory(str, Enum):
    NETWORK = "network"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    PERMISSION = "permission"
    DISK_SPACE = "disk_space"
    DEPENDENCY = "dependency"
    SYNTAX = "syntax"
    LOGIC = "logic"
    UNKNOWN = "unknown"


@dataclass
class FailureMatch:
    category: FailureCategory
    probability: float
    pattern: str
    suggestion: str


FAILURE_PATTERNS: list[tuple[str, FailureCategory, str]] = [
    (r"connection\s+(refused|reset|timed\s*out)", FailureCategory.NETWORK, "Check network connectivity"),
    (r"timed?\s*out|deadline\s+exceeded", FailureCategory.TIMEOUT, "Increase timeout or add retry with backoff"),
    (r"validation\s+(failed|error)|invalid\s+\w+", FailureCategory.VALIDATION, "Verify input data format"),
    (r"permission\s+denied|access\s+denied|unauthorized", FailureCategory.PERMISSION, "Check file/API permissions"),
    (r"no\s+space\s+left|disk\s+full|ENOSPC", FailureCategory.DISK_SPACE, "Free disk space"),
    (r"(module|import)\s+not\s+found|no\s+module\s+named", FailureCategory.DEPENDENCY, "Install missing dependency"),
    (r"SyntaxError|IndentationError|EOL\s+while\s+scanning", FailureCategory.SYNTAX, "Fix syntax error"),
    (r"AssertionError|assert\s+.*\s*failed", FailureCategory.LOGIC, "Check assertion condition"),
]


class FailureMatcher:
    def match(self, error_message: str) -> FailureMatch:
        error_lower = error_message.lower()

        best_match: FailureMatch | None = None
        best_probability = 0.0

        for pattern, category, suggestion in FAILURE_PATTERNS:
            if re.search(pattern, error_lower, re.IGNORECASE):
                prob = 0.7 + 0.3 * (len(pattern) / 100)
                if prob > best_probability:
                    best_probability = prob
                    best_match = FailureMatch(
                        category=category,
                        probability=round(prob, 2),
                        pattern=pattern,
                        suggestion=suggestion,
                    )

        if best_match is None:
            return FailureMatch(
                category=FailureCategory.UNKNOWN,
                probability=0.3,
                pattern="",
                suggestion="Manual investigation required",
            )

        return best_match

    def categorize(self, exception: Exception) -> FailureMatch:
        error_msg = f"{type(exception).__name__}: {exception!s}"
        return self.match(error_msg)

    def aggregate_failures(self, records: list[dict[str, Any]]) -> dict[FailureCategory, int]:
        counts: dict[FailureCategory, int] = {cat: 0 for cat in FailureCategory}

        for record in records:
            error = record.get("error", "")
            if error:
                result = self.match(error)
                counts[result.category] += 1

        return counts
