# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §

# [MODULE] zephyr.agent_spec.skill_knowledge_base

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Skill Knowledge Base Integration
Author: factory-agent
Version: 0.3.0

Skill KB bidirectional sync
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set


class SkillKnowledgeBridge:
    def __init__(self):
        self._synced: Set[str] = set()
        self._entities: List[Dict[str, Any]] = []
        self._log: List[Dict[str, Any]] = []
        self._map: Dict[str, str] = {}

    @property
    def kb_synced(self) -> bool:
        return len(self._synced) > 0

    def extract_from_skill(self, skill_id: str, skill_body: str) -> List[Dict[str, Any]]:
        entities: List[Dict[str, Any]] = []
        for entity_type, pattern in [
            ("constraint_rule", r"(?:MUST必须确保|CRITICAL):\s*(.+?)(?:[。\n]|$)"),
            ("forbidden_behavior", r"(?:不可|never|禁止):\s*(.+?)(?:[。\n]|$)"),
            ("allowed_tool", r"`(\w+)`"),
        ]:
            for match in re.finditer(pattern, skill_body, re.IGNORECASE):
                e = {"type": entity_type, "value": match.group(1).strip(), "source": skill_id}
                e["extracted_at"] = datetime.now(timezone.utc).isoformat()
                entities.append(e)
        return entities

    def sync_to_kb(self, skill_id: str, skill_body: str) -> Dict[str, Any]:
        entities = self.extract_from_skill(skill_id, skill_body)
        new = 0
        for e in entities:
            key = f"{e['type']}:{e['value']}"
            if key not in self._map:
                self._map[key] = skill_id
                self._entities.append(e)
                new += 1
        self._synced.add(skill_id)
        self._log.append({"ts": datetime.now(timezone.utc).isoformat(), "action": "sync", "skill": skill_id, "new": new})
        return {"skill_id": skill_id, "entities_extracted": len(entities), "entities_new": new, "kb_synced": True, "total": len(self._entities)}

    def sync_from_kb(self, skill_id: str) -> Dict[str, Any]:
        rel = [e for e in self._entities if e.get("source") != skill_id and skill_id.replace("-specialist", "").replace("-engine", "") in e.get("value", "")]
        return {"skill_id": skill_id, "kb_synced": skill_id in self._synced, "entities": len(rel), "data": rel[:20]}
