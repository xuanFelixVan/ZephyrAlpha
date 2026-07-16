# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_compliance
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Compliance
Author: factory-agent
Version: 0.3.0

GDPR/SOC2/ISO27001 compliance checks
"""

import re
from typing import Any

PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
    (r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "credit_card"),
]


class SkillCompliance:
    @classmethod
    def _check_pii(cls, content: str) -> dict[str, Any]:
        findings = []
        for pat, ptype in PII_PATTERNS:
            for m in re.finditer(pat, content):
                findings.append({"type": ptype, "value": m.group()[:30] + "..."})
        return {"pii_detected": len(findings) > 0, "findings": findings}

    @classmethod
    def check(cls, skill_id: str, content: str | None = None) -> dict[str, Any]:
        pii = cls._check_pii(content or "")
        violations = []
        if pii["pii_detected"]:
            violations.append({"policy": "GDPR", "check": "no_pii_storage", "detail": str(pii["findings"])})
        return {"skill_id": skill_id, "compliant": len(violations) == 0, "pii_check": pii, "violations": violations}
