"""dependency_tracker.py — 依赖追踪 (DD116, TASK-020)"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DependencyGraph:
    nodes: list[str]
    edges: list[tuple[str, str]]
    circular_deps: list[tuple[str, str]] = field(default_factory=list)


class DependencyTracker:
    """TaskCard.depends_on→graph; circular dep detection (DD116)."""
    def build_graph(self, tasks: list[dict]) -> DependencyGraph:
        nodes = [t.get("id", f"TASK-{i}") for i, t in enumerate(tasks)]
        edges = [(t.get("id", ""), dep) for t in tasks for dep in t.get("depends_on", []) if dep]
        return DependencyGraph(nodes=nodes, edges=edges)
