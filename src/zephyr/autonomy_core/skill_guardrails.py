# [A_module] module_id=MOD-ORC_skill_guardrails | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md

# [MODULE] zephyr.orchestration.agent_lifecycle.skill_guardrails

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Skill Guardrails
Author: factory-agent
Version: 0.3.0

Runtime guardrails: budget/mutation/output checks
"""

from typing import Any, Callable, Dict, List, Optional

DESTRUCTIVE = {"rm -rf": "critical", "DROP TABLE": "critical", "TRUNCATE": "high", "DELETE FROM": "high",
               "format c:": "critical", "rmdir /s": "high"}

class SkillGuardrails:
    MIN_OUTPUT = 5

    def __init__(self):
        self._violations: List[Dict[str, Any]] = []
        self._active = True

    @property
    def allowed(self) -> bool:
        return self._active and len(self._violations) == 0

    def check_pre_execution(self, skill_id: str, operation: str, budget_remaining: Optional[int] = None) -> Dict[str, Any]:
        v = []
        if budget_remaining is not None and budget_remaining <= 0:
            v.append({"type": "budget_exhausted", "severity": "blocking"})
        op_upper = operation.upper()
        for pat, sev in DESTRUCTIVE.items():
            if pat.upper() in op_upper:
                v.append({"type": "destructive", "severity": sev, "detail": operation[:100]})
        self._violations.extend(v)
        return {"allowed": len(v) == 0, "skill_id": skill_id, "operation": operation[:200], "violations": v}

    def check_output(self, skill_id: str, output: str) -> Dict[str, Any]:
        v = []
        if len(output.strip()) < self.MIN_OUTPUT:
            v.append({"type": "too_short", "severity": "warning"})
        self._violations.extend(v)
        return {"allowed": len(v) == 0, "skill_id": skill_id, "violations": v}
