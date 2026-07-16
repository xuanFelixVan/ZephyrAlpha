# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_contract
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Contract
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 契约验证 —— I/O Schema + 副作用 + 依赖
"""

from __future__ import annotations

import re
from typing import Any


class SkillContract:
    _CONTRACT_TYPES = ["input_schema", "output_schema", "side_effects", "dependencies"]

    @classmethod
    def _parse_contracts(cls, body: str) -> dict[str, Any]:
        contracts = {}
        for key, pattern in [
            ("input_schema", r"(?:输入|input|parameters|args?)[：:]\s*\n(.+?)(?:\n\n|\n#|\Z)"),
            ("output_schema", r"(?:输出|output|return|returns?|回应)[：:]\s*\n(.+?)(?:\n\n|\n#|\Z)"),
            ("side_effects", r"(?:副作用|side_?effects?)[：:]\s*\n(.+?)(?:\n\n|\n#|\Z)"),
            ("dependencies", r"(?:依赖|dependenc(?:y|ies))[：:]\s*\n(.+?)(?:\n\n|\n#|\Z)"),
        ]:
            m = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
            if m:
                contracts[key] = m.group(1).strip()[:500]
        return contracts

    @classmethod
    def validate_contracts(cls, skill_id: str, body: str | None = None) -> dict[str, Any]:
        if body is None:
            try:
                from zephyr.autonomy_core.skills.skill_loader import SkillLoader

                body = SkillLoader().progressive_load(skill_id).get("l2", "")
            except Exception:
                return {
                    "skill_id": skill_id,
                    "contracts_valid": False,
                    "error": "load_failed",
                    "violations": ["skill_load_failed"],
                    "contracts_found": [],
                }

        contracts = cls._parse_contracts(body)
        violations = []
        for ct in ("input_schema", "output_schema"):
            if ct not in contracts:
                violations.append(
                    {
                        "type": "missing_contract",
                        "contract": ct,
                        "severity": "high" if ct == "output_schema" else "warning",
                    }
                )
        for ct, content in contracts.items():
            if len(content) < 10:
                violations.append({"type": "contract_too_short", "contract": ct, "severity": "warning"})

        block = any(v.get("severity") == "critical" for v in violations)
        return {
            "skill_id": skill_id,
            "contracts_valid": not block and len(violations) == 0,
            "contracts_found": list(contracts.keys()),
            "contracts_missing": [c for c in cls._CONTRACT_TYPES if c not in contracts],
            "violations": violations,
            "contract_details": contracts,
        }
