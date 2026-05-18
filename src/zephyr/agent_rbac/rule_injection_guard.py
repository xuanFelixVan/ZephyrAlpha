# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.rule_injection_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""规则注入守卫——防止权限规则本身被注入绕过逻辑."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RuleInjectionCheck(BaseModel):
    rule_id: str
    rule_content: str
    sanitized: str = ""
    injection_detected: bool = False
    injection_type: str = ""


INJECTION_PATTERNS = [
    "import os", "import subprocess", "import sys",
    "__import__", "eval(", "exec(", "compile(",
    "globals()", "locals()", "getattr(", "setattr(",
    "open(", "write(", "remove(", "rmtree(",
    "shell=True", "popen(", "call(", "check_output(",
]


class RuleInjectionGuard:
    def check(self, rule_id: str, rule_content: str) -> RuleInjectionCheck:
        lower = rule_content.lower()
        for pattern in INJECTION_PATTERNS:
            if pattern.lower() in lower:
                return RuleInjectionCheck(
                    rule_id=rule_id,
                    rule_content=rule_content,
                    injection_detected=True,
                    injection_type=pattern,
                )
        return RuleInjectionCheck(rule_id=rule_id, rule_content=rule_content, sanitized=rule_content)
