# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_di
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
# [A_module] module_id=MOD-ORC_skill_di | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Dependency Injection
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill DI——模块化 Skill 组装与依赖拓扑排序.
"""

from __future__ import annotations

from collections import deque
from typing import Any


class SkillDI:
    """Skill DI——模块化 Skill 组装与依赖解析."""

    _registry: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, skill_id: str, deps: dict[str, Any]) -> dict[str, Any]:
        cls._registry[skill_id] = deps
        return {"skill_id": skill_id, "dependencies_registered": True}

    @classmethod
    def resolve(cls, skill_id: str) -> dict[str, Any]:
        return cls._registry.get(skill_id, {})

    @classmethod
    def inject(cls, skill_id: str, context: dict[str, Any]) -> dict[str, Any]:
        deps = cls._registry.get(skill_id, {})
        injected = dict(context)
        for dep_skill_id, fallback in deps.items():
            if dep_skill_id not in injected:
                resolved = cls.resolve(dep_skill_id)
                injected[dep_skill_id] = resolved.get("default", fallback)
        return injected

    @classmethod
    def topological_order(cls, skill_ids: list[str]) -> list[str]:
        graph: dict[str, list[str]] = {}
        in_degree: dict[str, int] = {}
        for sid in skill_ids:
            graph.setdefault(sid, [])
            in_degree.setdefault(sid, 0)
        for sid in skill_ids:
            deps = cls._registry.get(sid, {})
            for dep in deps:
                if dep in graph:
                    graph.setdefault(dep, []).append(sid)
                    in_degree[sid] = in_degree.get(sid, 0) + 1

        queue = deque([sid for sid in skill_ids if in_degree.get(sid, 0) == 0])
        order: list[str] = []
        visited: set[str] = set()
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            order.append(node)
            for neighbor in graph.get(node, []):
                in_degree[neighbor] = in_degree.get(neighbor, 1) - 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return order

    @classmethod
    def clear(cls):
        cls._registry.clear()


__all__ = ["SkillDI"]
