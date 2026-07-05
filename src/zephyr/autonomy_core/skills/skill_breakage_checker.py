# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_breakage_checker
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
# [A_module] module_id=MOD-ORC_skill_breakage_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Breakage Checker
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 破坏性变更检测 —— 向后兼容
"""

from __future__ import annotations

import difflib
import re
from typing import Any


class SkillBreakageChecker:
    TOOL_PATTERN = re.compile(r"`(\w+)`\s*[(:]")

    CONSTRAINT_PATTERNS = [
        (r"MUST\s+(NOT\s+)?\w+", "must_directive"),
        (r"CRITICAL", "critical_label"),
        (r"不可\s+\w+", "forbidden_action"),
        (r"禁止\s+\w+", "prohibited_action"),
        (r"always\s+\w+", "always_directive"),
        (r"never\s+\w+", "never_directive"),
    ]

    def _extract_tools(self, content: str) -> set[str]:
        return set(self.TOOL_PATTERN.findall(content))

    def _extract_constraints(self, content: str) -> set[str]:
        return {
            match.group()[:80]
            for pattern, _ in self.CONSTRAINT_PATTERNS
            for match in re.finditer(pattern, content, re.IGNORECASE)
        }

    def check(self, old_content: str, new_content: str) -> dict[str, Any]:
        old_tools = self._extract_tools(old_content)
        new_tools = self._extract_tools(new_content)
        old_constraints = self._extract_constraints(old_content)
        new_constraints = self._extract_constraints(new_content)

        breaking = []
        removed = old_tools - new_tools
        if removed:
            breaking.append({"type": "tools_removed", "severity": "high", "detail": f"Removed: {sorted(removed)}"})

        lost = old_constraints - new_constraints
        if lost:
            breaking.append(
                {
                    "type": "constraints_removed",
                    "severity": "critical",
                    "detail": f"Removed {len(lost)} constraints: {list(lost)[:5]}",
                }
            )

        sim = difflib.SequenceMatcher(None, old_content, new_content).ratio()
        return {
            "breaking_changes": breaking,
            "compatible": len(breaking) == 0,
            "similarity": round(sim, 3),
            "change_type": "breaking" if breaking else ("minor" if sim < 0.9 else "patch"),
        }
