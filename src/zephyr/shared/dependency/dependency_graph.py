# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.dependency.dependency_graph
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_dependency_graph | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Dependency Graph — 任务卡依赖关系管理。

依据：
    蓝图 MOD-TASK_SYSTEM §5 依赖项 + v0.6.0
    任务卡 TASK-INF-0107

功能：
    - depends_on/blocked_by 格式校验
    - 环检测（DFS cycle detection）
    - 依赖浅深分析 + 硬杀伤链构建
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DependencyNode:
    task_id: str
    depends_on: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)
    all_dependencies: list[str] = field(default_factory=list)


@dataclass
class CycleDetection:
    has_cycle: bool
    cycle_path: list[str]
    message: str = ""


@dataclass
class KillChain:
    task_id: str
    chain_depth: int
    chain_path: list[str]
    direct_deps: int
    transitive_deps: int


class DependencyGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, DependencyNode] = {}

    def add_node(
        self, task_id: str, depends_on: list[str] | None = None, blocked_by: list[str] | None = None
    ) -> DependencyNode:
        if task_id not in self._nodes:
            self._nodes[task_id] = DependencyNode(task_id=task_id)

        node = self._nodes[task_id]
        if depends_on is not None:
            node.depends_on = list(depends_on)
        if blocked_by is not None:
            node.blocked_by = list(blocked_by)

        node.all_dependencies = self._resolve_all_deps(task_id)

        return node

    def detect_cycles(self) -> list[CycleDetection]:
        cycles: list[CycleDetection] = []
        visited: set[str] = set()
        in_stack: set[str] = set()
        path: list[str] = []

        def dfs(tid: str) -> None:
            if tid in in_stack:
                cycle_start = path.index(tid)
                cycles.append(
                    CycleDetection(
                        has_cycle=True,
                        cycle_path=path[cycle_start:] + [tid],
                        message=f"Dependency cycle detected: {' -> '.join(path[cycle_start:] + [tid])}",
                    )
                )
                return

            if tid in visited or tid not in self._nodes:
                return

            visited.add(tid)
            in_stack.add(tid)
            path.append(tid)

            for dep in self._nodes[tid].depends_on:
                dfs(dep)

            path.pop()
            in_stack.discard(tid)

        for tid in self._nodes:
            if tid not in visited:
                dfs(tid)

        return cycles

    def build_kill_chain(self, task_id: str) -> KillChain | None:
        if task_id not in self._nodes:
            return None

        node = self._nodes[task_id]
        all_deps = self._resolve_all_deps(task_id)
        chain_path = self._depth_first_path(task_id)

        return KillChain(
            task_id=task_id,
            chain_depth=len(chain_path) - 1,
            chain_path=chain_path,
            direct_deps=len(node.depends_on),
            transitive_deps=len(all_deps),
        )

    def validate_task_deps(self, task_card: dict[str, Any]) -> tuple[bool, str]:
        depends_on = task_card.get("depends_on", [])
        blocked_by = task_card.get("blocked_by", [])

        if not isinstance(depends_on, list) or not isinstance(blocked_by, list):
            return False, "depends_on and blocked_by must be lists"

        all_ids = set(depends_on + blocked_by)
        for tid in all_ids:
            if tid == task_card.get("task_id"):
                return False, f"Self-dependency detected: {tid}"
            if tid in depends_on and tid in blocked_by:
                return False, f"Conflicting dependency: {tid} in both depends_on and blocked_by"

        return True, "Dependencies valid"

    def _resolve_all_deps(self, task_id: str, visited: set[str] | None = None) -> list[str]:
        if visited is None:
            visited = set()

        if task_id in visited or task_id not in self._nodes:
            return []

        visited.add(task_id)
        all_deps: set[str] = set()

        for dep in self._nodes[task_id].depends_on:
            all_deps.add(dep)
            all_deps.update(self._resolve_all_deps(dep, visited))

        return sorted(all_deps)

    def _depth_first_path(self, task_id: str) -> list[str]:
        node = self._nodes.get(task_id)
        if node is None:
            return [task_id]

        path = [task_id]
        for dep in node.depends_on:
            sub_path = self._depth_first_path(dep)
            for item in sub_path:
                if item not in path:
                    path.append(item)
        return path
