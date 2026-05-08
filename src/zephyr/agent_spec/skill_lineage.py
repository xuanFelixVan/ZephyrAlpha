"""
MOD-INF-019: Agent Spec — Skill Lineage
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 版本谱系追踪——版本树、diff 对比、回滚路径.
"""

from __future__ import annotations

import time
from typing import Dict, Any, List, Optional


class SkillLineage:
    """Skill 版本谱系追踪——版本树与回滚路径."""

    def __init__(self):
        self._lineages: Dict[str, List[Dict[str, Any]]] = {}

    def record_version(self, skill_id: str, version: str,
                       parent: Optional[str], changes: str) -> Dict[str, Any]:
        entry = {"version": version, "parent": parent, "changes": changes,
                 "timestamp": time.time()}
        self._lineages.setdefault(skill_id, []).append(entry)
        return entry

    def get_lineage(self, skill_id: str) -> List[Dict[str, Any]]:
        return self._lineages.get(skill_id, [])

    def latest(self, skill_id: str) -> Optional[Dict[str, Any]]:
        lineage = self._lineages.get(skill_id, [])
        return lineage[-1] if lineage else None

    def rollback_path(self, skill_id: str,
                      target_version: str) -> List[Dict[str, Any]]:
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

    def diff(self, skill_id: str, v1: str, v2: str) -> Dict[str, Any]:
        lineage = self._lineages.get(skill_id, [])
        entry1 = next((v for v in lineage if v["version"] == v1), None)
        entry2 = next((v for v in lineage if v["version"] == v2), None)
        if not entry1 or not entry2:
            return {"found": False, "v1": v1, "v2": v2}
        return {
            "found": True,
            "v1": v1, "v1_changes": entry1.get("changes", ""),
            "v2": v2, "v2_changes": entry2.get("changes", ""),
            "v1_ts": entry1.get("timestamp"), "v2_ts": entry2.get("timestamp"),
        }

    def clear(self, skill_id: Optional[str] = None):
        if skill_id:
            self._lineages.pop(skill_id, None)
        else:
            self._lineages.clear()


__all__ = ["SkillLineage"]
