# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_ontology
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
# [A_module] module_id=MOD-ORC_skill_ontology | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Ontology
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 本体对齐引擎
==================
对齐 Skill 与项目知识图谱(KB)中的本体概念:
  1. EntityExtraction: 从 Skill body 抽取领域实体
  2. OntologyMatch: 匹配到 KB 中已有实体
  3. GapDetection: 发现 Skill 引用了 KB 中不存在的概念
  4. AlignmentScore: 计算本体对齐度
"""

from __future__ import annotations

import re
from typing import Any


class SkillOntology:
    """Skill 本体对齐器"""

    ENTITY_PATTERNS = [
        (r"(MOD-INF-\d{3})", "module"),
        (r"\b(G\d+)\b", "gate"),
        (r"(SKILL-[A-Z]+-[A-Z]+-\d+)", "skill"),
        (r"(?:MODULE|模块):?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", "module_name"),
        (r"Phase\s*[:#]?\s*(\w+)", "phase"),
        (r"(?:Table|表|table):?\s*`?(\w+)`?", "database_table"),
        (r"(?:API|endpoint|接口):?\s*`?([/\w]+)`?", "api_endpoint"),
        (r"(?:Agent|agent):?\s*`?([\w-]+)`?", "agent"),
    ]

    _KATA_MAP = {
        "module": "Module",
        "gate": "Gate",
        "skill": "Skill",
        "phase": "Phase",
        "database_table": "Table",
        "api_endpoint": "API",
        "agent": "Agent",
        "module_name": "Module",
    }

    @classmethod
    def extract_entities(cls, content: str) -> list[dict[str, str]]:
        entities: list[dict[str, str]] = []
        seen: set = set()

        for pattern, entity_type in cls.ENTITY_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                value = match.group(1).strip()
                key = f"{entity_type}:{value}"
                if key not in seen:
                    seen.add(key)
                    entities.append({"type": entity_type, "value": value})

        return entities

    @classmethod
    def match_entities(
        cls,
        extracted: list[dict[str, str]],
        kb_entities: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        kb_set: set = set()
        if kb_entities:
            kb_set = {f"{e.get('type', '')}:{e.get('value', '')}" for e in kb_entities}

        matched: list[dict[str, str]] = []
        unmatched: list[dict[str, str]] = []
        novel: list[dict[str, str]] = []

        for entity in extracted:
            key = f"{entity['type']}:{entity['value']}"
            if kb_entities is None or key in kb_set:
                matched.append(entity)
            else:
                unmatched.append(entity)
                novel.append(entity)

        total = len(extracted)
        match_rate = (len(matched) / max(total, 1)) * 100.0

        return {
            "total_extracted": total,
            "matched_entities": matched,
            "matched_count": len(matched),
            "unmatched_count": len(unmatched),
            "novel_entities": novel,
            "match_rate": round(match_rate, 1),
            "confidence": round(match_rate / 100.0, 2),
        }

    @classmethod
    def detect_gaps(
        cls,
        skill_id: str,
        skill_body: str,
        kb_entities: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        entities = cls.extract_entities(skill_body)
        match_result = cls.match_entities(entities, kb_entities)

        gaps: list[dict[str, str]] = []
        for novel in match_result.get("novel_entities", []):
            kata_type = cls._KATA_MAP.get(novel["type"], "Unknown")
            gaps.append(
                {
                    "entity": novel["value"],
                    "type": novel["type"],
                    "kb_category": kata_type,
                    "action": f"Create {kata_type} entity '{novel['value']}' in KB",
                }
            )

        score = match_result["match_rate"]

        return {
            "skill_id": skill_id,
            "entities_extracted": match_result["total_extracted"],
            "entities_matched": match_result["matched_count"],
            "gaps_found": len(gaps),
            "gaps": gaps,
            "alignment_score": score,
            "aligned": score >= 70.0,
        }
