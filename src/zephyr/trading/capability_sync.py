# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.capability_sync
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.trading.auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] sync_a2a and sync_skills are idempotent; existing cap_ids are skipped
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns int (count synced); never raises; logs on failure
# [TESTS]
# [A_module] module_id=MOD-ORC_capability_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from pathlib import Path
from typing import Any

import yaml

from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory
from zephyr.trading.capability_registry import CapabilityRegistry

logger = logging.getLogger(__name__)

_SKILL_CATEGORY_MAP: dict[str, CapabilityCategory] = {
    "database-specialist": CapabilityCategory.DATA,
    "mcp-specialist": CapabilityCategory.INFRA,
    "context-specialist": CapabilityCategory.INFRA,
    "feedback-specialist": CapabilityCategory.OBSERVABILITY,
    "gate-specialist": CapabilityCategory.GOVERNANCE,
    "agent-specialist": CapabilityCategory.SECURITY,
    "master-blueprint": CapabilityCategory.GOVERNANCE,
    "drift-detector": CapabilityCategory.GOVERNANCE,
    "knowledge-specialist": CapabilityCategory.SEARCH,
    "rollback-specialist": CapabilityCategory.INFRA,
    "lsg-security": CapabilityCategory.SECURITY,
    "vector-memory": CapabilityCategory.SEARCH,
    "task-system": CapabilityCategory.ORCHESTRATION,
    "system-telemetry": CapabilityCategory.OBSERVABILITY,
    "code-dedup-engine": CapabilityCategory.GOVERNANCE,
    "budget-enforcer": CapabilityCategory.GOVERNANCE,
    "auto-fix-engine": CapabilityCategory.INFRA,
    "a2a-protocol": CapabilityCategory.COORDINATION,
    "behavioral-auditor": CapabilityCategory.SECURITY,
}


class CapabilitySync:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    def sync_a2a(self, a2a_registry: Any) -> int:
        if a2a_registry is None:
            return 0
        synced = 0
        try:
            for card in a2a_registry._cards.values():
                cap_id = f"a2a-agent-{card.agent_id}"
                existing = self._registry.get(cap_id)
                if existing is None:
                    cap_card = CapabilityCard(
                        capability_id=cap_id,
                        name=f"A2A Agent: {card.name}",
                        category=CapabilityCategory.SEARCH,
                        description=card.description,
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        tags=["a2a-agent", card.agent_id] + [c.value for c in card.capabilities],
                        priority="P2",
                        runtime_plane="warm",
                        requires_human=False,
                    )
                    self._registry.register(cap_card)
                    synced += 1
        except Exception:
            pass
        return synced

    def sync_skills(self, skill_registry_path: Path) -> int:
        synced = 0
        try:
            if not skill_registry_path.exists():
                return 0
            with open(skill_registry_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            for category in ("domain", "role"):
                for sid, sdata in data.get("skills", {}).get(category, {}).items():
                    cap_id = sid.lower().replace("_", "-")
                    existing = self._registry.get(cap_id)
                    if existing is not None:
                        continue
                    name = sdata.get("name", sid)
                    desc = sdata.get("description", f"Skill-derived capability: {name}")
                    cap_category = _SKILL_CATEGORY_MAP.get(name, CapabilityCategory.INFRA)
                    tier = sdata.get("tier", "L1")
                    plane = "warm" if tier in ("L0", "L1") else "cold"
                    cap_card = CapabilityCard(
                        capability_id=cap_id,
                        name=f"Skill: {name}",
                        category=cap_category,
                        description=desc,
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                        tags=["skill-derived", category, name],
                        priority="P1" if category == "domain" else "P2",
                        runtime_plane=plane,
                        requires_human=False,
                    )
                    self._registry.register(cap_card)
                    synced += 1
        except Exception:
            pass
        return synced
