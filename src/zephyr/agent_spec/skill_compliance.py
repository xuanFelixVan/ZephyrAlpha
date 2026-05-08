"""
MOD-INF-019: Agent Spec — Skill Compliance
Author: factory-agent
Version: 0.3.0

GDPR/SOC2/ISO27001 compliance checks
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


PII_PATTERNS = [(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
                (r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "credit_card")]


class SkillCompliance:

    @classmethod
    def _check_pii(cls, content: str) -> Dict[str, Any]:
        findings = []
        for pat, ptype in PII_PATTERNS:
            for m in re.finditer(pat, content):
                findings.append({"type": ptype, "value": m.group()[:30] + "..."})
        return {"pii_detected": len(findings) > 0, "findings": findings}

    @classmethod
    def check(cls, skill_id: str, content: Optional[str] = None) -> Dict[str, Any]:
        pii = cls._check_pii(content or "")
        violations = []
        if pii["pii_detected"]:
            violations.append({"policy": "GDPR", "check": "no_pii_storage", "detail": str(pii["findings"])})
        return {"skill_id": skill_id, "compliant": len(violations) == 0,
                "pii_check": pii, "violations": violations}
