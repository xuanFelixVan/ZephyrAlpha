# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_kya
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
# [A_module] module_id=MOD-ORC_skill_kya | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill KYA
Author: factory-agent
Version: 0.3.0

Know Your Agent certification
"""

from datetime import UTC, datetime, timedelta
from typing import Any

RISKY = {"write_file", "search_replace", "delete_file", "run_command", "execute", "bash"}


class SkillKYA:
    EXPIRE_DAYS = 90

    def __init__(self):
        self._certs: dict[str, dict[str, Any]] = {}

    def _assess(self, tools: list[str]) -> str:
        risky = sum(1 for t in tools if t in RISKY)
        total = len(tools)
        if risky >= 5 or total > 15:
            return "privileged"
        if risky >= 2 or total > 10:
            return "advanced"
        if risky >= 1 or total > 5:
            return "intermediate"
        return "basic"

    def certify(self, skill_id: str, tools: list[str] | None = None) -> dict[str, Any]:
        if tools is None:
            try:
                from zephyr.autonomy_core.skills.skill_loader import SkillLoader

                tools = list(SkillLoader().progressive_load(skill_id).get("l1", {}).get("allowed_tools", []))
            except Exception:
                tools = []
        tier = self._assess(tools)
        now = datetime.now(UTC)
        expires = now + timedelta(days=self.EXPIRE_DAYS)
        cert = {
            "skill_id": skill_id,
            "kya_level": tier,
            "certified": True,
            "assigned_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "expires_in_days": self.EXPIRE_DAYS,
            "tools_count": len(tools),
            "risky_count": sum(1 for t in tools if t in RISKY),
        }
        self._certs[skill_id] = cert
        return cert

    def revalidate(self, skill_id: str) -> dict[str, Any]:
        existing = self._certs.get(skill_id)
        if existing:
            try:
                expires = datetime.fromisoformat(existing.get("expires_at", ""))
                if datetime.now(UTC) < expires:
                    return {
                        "skill_id": skill_id,
                        "status": "still_valid",
                        "expires_in_days": (expires - datetime.now(UTC)).days,
                    }
            except (ValueError, TypeError):
                pass
        return self.certify(skill_id)
