# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §

# [MODULE] zephyr.agent_spec.skill_kya

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Skill KYA
Author: factory-agent
Version: 0.3.0

Know Your Agent certification
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional


RISKY = {"write_file", "search_replace", "delete_file", "run_command", "execute", "bash"}


class SkillKYA:
    EXPIRE_DAYS = 90

    def __init__(self):
        self._certs: Dict[str, Dict[str, Any]] = {}

    def _assess(self, tools: List[str]) -> str:
        risky = sum(1 for t in tools if t in RISKY)
        total = len(tools)
        if risky >= 5 or total > 15:
            return "privileged"
        if risky >= 2 or total > 10:
            return "advanced"
        if risky >= 1 or total > 5:
            return "intermediate"
        return "basic"

    def certify(self, skill_id: str, tools: Optional[List[str]] = None) -> Dict[str, Any]:
        if tools is None:
            try:
                from zephyr.agent_spec.skill_loader import SkillLoader
                tools = list(SkillLoader().progressive_load(skill_id).get("l1", {}).get("allowed_tools", []))
            except Exception:
                tools = []
        tier = self._assess(tools)
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=self.EXPIRE_DAYS)
        cert = {"skill_id": skill_id, "kya_level": tier, "certified": True,
                "assigned_at": now.isoformat(), "expires_at": expires.isoformat(),
                "expires_in_days": self.EXPIRE_DAYS, "tools_count": len(tools),
                "risky_count": sum(1 for t in tools if t in RISKY)}
        self._certs[skill_id] = cert
        return cert

    def revalidate(self, skill_id: str) -> Dict[str, Any]:
        existing = self._certs.get(skill_id)
        if existing:
            try:
                expires = datetime.fromisoformat(existing.get("expires_at", ""))
                if datetime.now(timezone.utc) < expires:
                    return {"skill_id": skill_id, "status": "still_valid", "expires_in_days": (expires - datetime.now(timezone.utc)).days}
            except (ValueError, TypeError):
                pass
        return self.certify(skill_id)
