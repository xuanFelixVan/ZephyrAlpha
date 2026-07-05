# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_lineage
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
# [A_module] module_id=MOD-ORC_skill_lineage | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Lineage
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 版本谱系追踪——版本树、diff 对比、回滚路径.
"""

from __future__ import annotations

import time
from typing import Any


class SkillLineage:
    """Skill 版本谱系追踪——版本树与回滚路径."""

    def __init__(self):
        self._lineages: dict[str, list[dict[str, Any]]] = {}

    def record_version(self, skill_id: str, version: str, parent: str | None, changes: str) -> dict[str, Any]:
        entry = {"version": version, "parent": parent, "changes": changes, "timestamp": time.time()}
        self._lineages.setdefault(skill_id, []).append(entry)
        return entry

    def get_lineage(self, skill_id: str) -> list[dict[str, Any]]:
        return self._lineages.get(skill_id, [])

    def latest(self, skill_id: str) -> dict[str, Any] | None:
        lineage = self._lineages.get(skill_id, [])
        return lineage[-1] if lineage else None

    def rollback_path(self, skill_id: str, target_version: str) -> list[dict[str, Any]]:
        lineage = self._lineages.get(skill_id, [])
        path = []
        current = lineage[-1] if lineage else None
        while current and current["version"] != target_version:
            path.append(current)
            parent = current.get("parent")
            if not parent:
                break
            current = next((v for v in lineage if v["version"] == parent), None)
        path.append(current) if current else None
        return path

    def diff(self, skill_id: str, v1: str, v2: str) -> dict[str, Any]:
        lineage = self._lineages.get(skill_id, [])
        entry1 = next((v for v in lineage if v["version"] == v1), None)
        entry2 = next((v for v in lineage if v["version"] == v2), None)
        if not entry1 or not entry2:
            return {"found": False, "v1": v1, "v2": v2}
        return {
            "found": True,
            "v1": v1,
            "v1_changes": entry1.get("changes", ""),
            "v2": v2,
            "v2_changes": entry2.get("changes", ""),
            "v1_ts": entry1.get("timestamp"),
            "v2_ts": entry2.get("timestamp"),
        }

    def clear(self, skill_id: str | None = None):
        if skill_id:
            self._lineages.pop(skill_id, None)
        else:
            self._lineages.clear()


__all__ = ["SkillLineage"]
