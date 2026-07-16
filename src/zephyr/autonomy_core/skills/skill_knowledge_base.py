# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_knowledge_base
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
MOD-INF-019: Agent Spec — Skill Knowledge Base Integration
Author: factory-agent
Version: 0.3.0

Skill KB bidirectional sync
"""

import re
from datetime import UTC, datetime
from typing import Any


class SkillKnowledgeBridge:
    def __init__(self):
        self._synced: set[str] = set()
        self._entities: list[dict[str, Any]] = []
        self._log: list[dict[str, Any]] = []
        self._map: dict[str, str] = {}

    @property
    def kb_synced(self) -> bool:
        return len(self._synced) > 0

    def extract_from_skill(self, skill_id: str, skill_body: str) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        for entity_type, pattern in [
            ("constraint_rule", r"(?:MUST必须确保|CRITICAL):\s*(.+?)(?:[。\n]|$)"),
            ("forbidden_behavior", r"(?:不可|never|禁止):\s*(.+?)(?:[。\n]|$)"),
            ("allowed_tool", r"`(\w+)`"),
        ]:
            for match in re.finditer(pattern, skill_body, re.IGNORECASE):
                e = {"type": entity_type, "value": match.group(1).strip(), "source": skill_id}
                e["extracted_at"] = datetime.now(UTC).isoformat()
                entities.append(e)
        return entities

    def sync_to_kb(self, skill_id: str, skill_body: str) -> dict[str, Any]:
        entities = self.extract_from_skill(skill_id, skill_body)
        new = 0
        for e in entities:
            key = f"{e['type']}:{e['value']}"
            if key not in self._map:
                self._map[key] = skill_id
                self._entities.append(e)
                new += 1
        self._synced.add(skill_id)
        self._log.append({"ts": datetime.now(UTC).isoformat(), "action": "sync", "skill": skill_id, "new": new})
        return {
            "skill_id": skill_id,
            "entities_extracted": len(entities),
            "entities_new": new,
            "kb_synced": True,
            "total": len(self._entities),
        }

    def sync_from_kb(self, skill_id: str) -> dict[str, Any]:
        rel = [
            e
            for e in self._entities
            if e.get("source") != skill_id
            and skill_id.replace("-specialist", "").replace("-engine", "") in e.get("value", "")
        ]
        return {"skill_id": skill_id, "kb_synced": skill_id in self._synced, "entities": len(rel), "data": rel[:20]}
