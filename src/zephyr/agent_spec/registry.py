# [BLUEPRINT] MOD-INF-019 | docs/03_modules/l01_infrastructure/agent-spec/blueprint.md | §3

# [MODULE] zephyr.agent_spec.registry

# [INVARIANTS] skill registration must be atomic; progressive_load must not exceed L3; keyword routing must be O(log N)

# [MODIFY-GUARD] skill_registry.yaml; engine.py; __init__.py

# [CONSUMERS] zephyr.runtime; zephyr.pipeline

# [STABILITY] stable

# [SAFETY] H

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] module import failures degrade gracefully with _AVAILABLE flags; registry load failure returns empty dict

# [TESTS] tests/agent_spec/test_registry.py

"""G-CT-003: Agent Spec -> RBAC capability check.

Bidirectional bridge:
  1. Read 13 skills registered in agent_spec/skill_registry.yaml
  2. Provide unified query interface for governance gate usage
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

_SKILL_REGISTRY_PATH = Path(__file__).resolve().parent / "skill_registry.yaml"

GOVERNANCE_SKILL_TYPES = {
    "domain": ["governor-specialist", "gate-specialist", "contract-enforcer", "script-writer", "audit-specialist",
               "rollback-specialist", "drift-detector", "escalation-specialist", "budget-enforcer", "security-specialist"],
    "role": ["architect", "implementer", "governor"],
}


class AgentCapability(BaseModel):
    agent_id: str
    capabilities: list[str] = []
    version: str = "1.0.0"
    spec_hash: str = ""


class SpecRegistry:
    """Agent Spec registry — interfaces with real skill_registry.yaml."""

    def __init__(self, registry_path: Optional[Path] = None) -> None:
        self._entries: dict[str, AgentCapability] = {}
        self._registry_path = registry_path or _SKILL_REGISTRY_PATH
        self._raw_cache: Optional[Dict[str, Any]] = None
        self._load_from_skill_registry()

    def _load_from_skill_registry(self) -> None:
        if not self._registry_path.exists():
            return
        with self._registry_path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        self._raw_cache = raw
        skills = raw.get("skills", {}) if raw else {}
        for category in ("domain", "role"):
            for sid, info in skills.get(category, {}).items():
                name = info.get("name", sid)
                self._entries[sid] = AgentCapability(
                    agent_id=sid,
                    capabilities=[name, category, info.get("description", "")[:80]],
                    version=info.get("version", "0.1.0"),
                    spec_hash=info.get("spec_hash", ""),
                )

    def register(self, capability: AgentCapability) -> None:
        self._entries[capability.agent_id] = capability

    def get(self, agent_id: str) -> AgentCapability | None:
        return self._entries.get(agent_id)

    def list_all(self) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for sid, cap in self._entries.items():
            result.append({"skill_id": sid, "name": cap.capabilities[0] if cap.capabilities else sid,
                           "category": cap.capabilities[1] if len(cap.capabilities) > 1 else "unknown",
                           "version": cap.version})
        return result

    def list_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [e for e in self.list_all() if e["category"] == category]

    def reload(self) -> None:
        self._entries.clear()
        self._raw_cache = None
        self._load_from_skill_registry()
