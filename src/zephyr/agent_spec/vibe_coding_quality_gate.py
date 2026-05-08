"""
MOD-INF-019: Agent Spec — Vibe Coding Quality Gate
Author: factory-agent
Version: 0.3.0

AI-generated code quality guard
"""
from __future__ import annotations

import ast
import re
from typing import Any, Dict, List


SECRET_PATTERNS = [
    (r"(?:api_?key|API_?KEY)\s*=\s*[\"'][A-Za-z0-9_-]{12,}[\"']", "hardcoded_key"),
    (r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "hardcoded_ip"),
]


class VibeCodingQualityGate:

    @classmethod
    def validate(cls, skill_id: str, code: str) -> Dict[str, Any]:
        syntax = cls._check_syntax(code)
        security = cls._scan_security(code)
        results = {"syntax_check": syntax, "security_scan": security}
        all_pass = all(r["passed"] for r in results.values())
        return {"skill_id": skill_id, "passed": all_pass, "checks": {k: v["passed"] for k, v in results.items()}}

    @classmethod
    def _check_syntax(cls, code: str) -> Dict[str, Any]:
        try:
            ast.parse(code)
            return {"passed": True, "issues": []}
        except SyntaxError as e:
            return {"passed": False, "issues": [str(e)]}

    @classmethod
    def _scan_security(cls, code: str) -> Dict[str, Any]:
        findings = []
        for pat, cat in SECRET_PATTERNS:
            for m in re.finditer(pat, code):
                findings.append({"category": cat, "line": code[:m.start()].count("\n") + 1})
        return {"passed": len(findings) == 0, "findings": findings}
