"""
MOD-INF-019: Agent Spec — Skill Dependency Injection
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill DI——模块化 Skill 组装与依赖拓扑排序.
"""

from __future__ import annotations

from typing import Dict, Any, List, Set

from collections import deque


class SkillDI:
    """Skill DI——模块化 Skill 组装与依赖解析."""

    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, skill_id: str,
                 deps: Dict[str, Any]) -> Dict[str, Any]:
        cls._registry[skill_id] = deps
        return {"skill_id": skill_id, "dependencies_registered": True}

    @classmethod
    def resolve(cls, skill_id: str) -> Dict[str, Any]:
        return cls._registry.get(skill_id, {})

    @classmethod
    def inject(cls, skill_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        deps = cls._registry.get(skill_id, {})
        injected = dict(context)
        for dep_skill_id, fallback in deps.items():
            if dep_skill_id not in injected:
                resolved = cls.resolve(dep_skill_id)
                injected[dep_skill_id] = resolved.get("default", fallback)
        return injected

    @classmethod
    def topological_order(cls, skill_ids: List[str]) -> List[str]:
        graph: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {}
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
        order: List[str] = []
        visited: Set[str] = set()
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
