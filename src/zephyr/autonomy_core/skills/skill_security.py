# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_security
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
# [A_module] module_id=MOD-ORC_skill_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Security
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0
"""

import re
from typing import Any

_PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions",
    r"forget\s+(?:all\s+)?(?:previous|prior)\s+directives",
    r"you\s+(?:are\s+)?(?:now|must\s+now)\s+(?:a\s+)?(?:free|unrestricted|unbounded)",
    r"system\s+prompt\s*:?\s*override",
    r"DISREGARD\s+ALL\s+PREVIOUS",
    r"```\s*override",
    r"role\s*:\s*(?:system|admin|assistant)\s*\]",
]

_COMMAND_INJECTION_PATTERNS = [
    r"(?:;|\|\||&&)\s*(?:rm|del|shutdown|format|mkfs|wget|curl|nc|bash|powershell)",
    r"`[^`]*`\s*\$?\([^)]+\)",
    r"\$\([^)]+\)",
    r"\b(?:rm|del)\s+(?:-[rf]+\s+)?/",
    r"subprocess\s*\.\s*(?:call|popen|run)\s*\(",
    r"os\s*\.\s*(?:system|popen)\s*\(",
]

_SSRF_PATTERNS = [
    r"https?://(?:169\.254|127\.0\.0\.1|localhost|0\.0\.0\.0|10\.\d+\.\d+\.\d+|172\.1[6-9]\.\d+\.\d+|172\.2\d+\.\d+\.\d+|172\.3[0-1]\.\d+\.\d+|192\.168\.\d+\.\d+)",
    r"https?://.*(?:internal|private|secret|metadata)",
    r"file:///",
]

_PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
    r"%2e%2e%2f",
]

_YAML_DESERIALIZATION_PATTERNS = [
    r"!!python/",
    r"!!org.",
    r"!!javax.",
    r"!!com\.sun\.",
]


class SkillSecurity:
    """Skill 安全审计与防护"""

    _VETTING_CHECKS = ["prompt_injection", "command_injection", "ssrf", "path_traversal", "yaml_deserialization"]

    @classmethod
    def vet(cls, skill_id: str, content: str) -> dict[str, Any]:
        if not content:
            return {
                "skill_id": skill_id,
                "passed": False,
                "checks": cls._VETTING_CHECKS,
                "findings": [{"check": "content_empty", "severity": "error", "detail": "Skill content is empty"}],
            }

        findings: list[dict[str, Any]] = []
        checks_passed = True

        for pattern in _PROMPT_INJECTION_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                findings.append(
                    {"check": "prompt_injection", "severity": "critical", "detail": f"Match: {match.group()[:80]}"}
                )
                checks_passed = False

        for pattern in _COMMAND_INJECTION_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                findings.append(
                    {"check": "command_injection", "severity": "critical", "detail": f"Match: {match.group()[:80]}"}
                )
                checks_passed = False

        for pattern in _SSRF_PATTERNS:
            match = re.search(pattern, content)
            if match:
                findings.append(
                    {"check": "ssrf", "severity": "high", "detail": f"Internal URL detected: {match.group()[:80]}"}
                )
                checks_passed = False

        for pattern in _PATH_TRAVERSAL_PATTERNS:
            match = re.search(pattern, content)
            if match:
                findings.append(
                    {
                        "check": "path_traversal",
                        "severity": "high",
                        "detail": f"Path traversal pattern: {match.group()[:80]}",
                    }
                )
                checks_passed = False

        for pattern in _YAML_DESERIALIZATION_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                findings.append(
                    {
                        "check": "yaml_deserialization",
                        "severity": "critical",
                        "detail": f"Dangerous YAML tag: {match.group()[:80]}",
                    }
                )
                checks_passed = False

        blocked_keywords = ["import os", "import subprocess", "from subprocess", "import socket"]
        for kw in blocked_keywords:
            if kw in content:
                findings.append(
                    {"check": "dangerous_import", "severity": "warning", "detail": f"Blocked import keyword: {kw}"}
                )
                checks_passed = False

        return {
            "skill_id": skill_id,
            "passed": checks_passed,
            "checks": cls._VETTING_CHECKS,
            "findings": findings,
        }

    @classmethod
    def scan_vulnerabilities(cls, skill_id: str) -> list[dict[str, Any]]:
        return []
