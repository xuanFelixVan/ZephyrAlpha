# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] zephyr.governance.agent_spec.registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.skill_protocol
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""G-CT-003 契约：Agent Spec -> RBAC 能力检查.

双向桥接：
  1. 通过 SkillRouter API 查询 agent-spec/skill-registry.yaml 中注册的技能
  2. 提供统一的查询接口给 governance gate 使用
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel


class AgentCapability(BaseModel):
    agent_id: str
    capabilities: list[str] = []
    version: str = "1.0.0"
    spec_hash: str = ""


class SpecRegistry:
    """Agent Spec 注册表 — 通过 SkillRouter API 查询."""

    def __init__(self, registry_path: Path | None = None) -> None:
        self._entries: dict[str, AgentCapability] = {}
        self._registry_path = registry_path
        self._load_via_skill_router()

    def _load_via_skill_router(self) -> None:
        try:
            from zephyr.shared.contracts.skill_protocol import create_skill_router

            router = create_skill_router(registry_path=self._registry_path)
            for skill_id, info in router.list_registered_skills().items():
                self._entries[skill_id] = AgentCapability(
                    agent_id=skill_id,
                    capabilities=[
                        info.get("name", skill_id),
                        info.get("category", "unknown"),
                        info.get("description", "")[:80],
                    ],
                    version=info.get("version", "0.1.0"),
                    spec_hash=info.get("spec_hash", ""),
                )
        except Exception:
            self._fallback_load()

    def _fallback_load(self) -> None:
        import yaml

        if self._registry_path and self._registry_path.exists():
            with self._registry_path.open(encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        else:
            _default_path = Path(__file__).resolve().parent.parent.parent / "agent-spec" / "skill-registry.yaml"
            if not _default_path.exists():
                return
            with _default_path.open(encoding="utf-8") as f:
                raw = yaml.safe_load(f)
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

    def list_all(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for sid, cap in self._entries.items():
            result.append(
                {
                    "skill_id": sid,
                    "name": cap.capabilities[0] if cap.capabilities else sid,
                    "category": cap.capabilities[1] if len(cap.capabilities) > 1 else "unknown",
                    "version": cap.version,
                }
            )
        return result

    def list_by_category(self, category: str) -> list[dict[str, Any]]:
        return [e for e in self.list_all() if e["category"] == category]

    def reload(self) -> None:
        self._entries.clear()
        self._raw_cache = None
        self._load_from_skill_registry()
