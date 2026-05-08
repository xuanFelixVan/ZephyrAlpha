"""
MOD-INF-019: Agent Spec — Skill Ontology
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
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
from typing import Any, Dict, List, Optional, Tuple


class SkillOntology:
    """Skill 本体对齐器"""

    ENTITY_PATTERNS = [
        (r"MOD-INF-(\d{3})", "module"),
        (r"GATE-(\d+)", "gate"),
        (r"SKILL-[A-Z]+-\d+", "skill"),
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
    def extract_entities(cls, content: str) -> List[Dict[str, str]]:
        entities: List[Dict[str, str]] = []
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
        extracted: List[Dict[str, str]],
        kb_entities: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        kb_set: set = set()
        if kb_entities:
            kb_set = {f"{e.get('type', '')}:{e.get('value', '')}" for e in kb_entities}

        matched: List[Dict[str, str]] = []
        unmatched: List[Dict[str, str]] = []
        novel: List[Dict[str, str]] = []

        for entity in extracted:
            key = f"{entity['type']}:{entity['value']}"
            if kb_entities is None:
                matched.append(entity)
            elif key in kb_set:
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
        kb_entities: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        entities = cls.extract_entities(skill_body)
        match_result = cls.match_entities(entities, kb_entities)

        gaps: List[Dict[str, str]] = []
        for novel in match_result.get("novel_entities", []):
            kata_type = cls._KATA_MAP.get(novel["type"], "Unknown")
            gaps.append({
                "entity": novel["value"],
                "type": novel["type"],
                "kb_category": kata_type,
                "action": f"Create {kata_type} entity '{novel['value']}' in KB",
            })

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
