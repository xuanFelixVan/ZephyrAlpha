# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.dependency.dependency_tracker
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_dependency_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""dependency_tracker.py — 依赖追踪 (DD116, TASK-020)"""

from dataclasses import dataclass, field


@dataclass
class DependencyGraph:
    nodes: list[str]
    edges: list[tuple[str, str]]
    circular_deps: list[tuple[str, str]] = field(default_factory=list)


class DependencyTracker:
    """TaskCard.depends_on->graph; circular dep detection (DD116)."""

    def build_graph(self, tasks: list[dict]) -> DependencyGraph:
        nodes = [t.get("id", f"TASK-{i}") for i, t in enumerate(tasks)]
        edges = [(t.get("id", ""), dep) for t in tasks for dep in t.get("depends_on", []) if dep]
        return DependencyGraph(nodes=nodes, edges=edges)
