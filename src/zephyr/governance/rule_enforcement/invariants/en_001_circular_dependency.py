# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.invariants.en_001_circular_dependency
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_en_001_circular_dependency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODEGEN:EN-001 ====
"""
EN-001 — Circular Dependency Scanner

Kahn's algorithm topological sort over the module import DAG.
Detects cycles across all module directories + shared/contracts.

SSoT: cross_layer_contracts.yaml v3.0 — partition.cross-cutting-contracts
Architecture Decision:  (LPC 双轨)
"""

from __future__ import annotations

from typing import Final
import ast
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from zephyr.shared.io.paths import REPO_ROOT
SRC_ROOT: Final[Path] = REPO_ROOT / "src" / "zephyr"

_YAML_PATH = Path(__file__).parent / "en_001_circular_dependency.yaml"


def _load_module_names() -> list[str]:
    """从 YAML 真源加载扫描目标（SSoT 收敛，消除 py/yaml 双真源分叉）。"""
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    targets: list[str] = []
    for check in data.get("checks", []):
        targets.extend(check.get("params", {}).get("scan_targets", []))
    return targets


# MODULE_NAMES 从 YAML scan_targets 派生（含 zephyr.shared.contracts）
MODULE_NAMES: Final[Any] = _load_module_names()

ALL_MODULES: Final[Any] = MODULE_NAMES

MODULE_TO_DIR: Final[dict[str, Path]] = {}
for mod in MODULE_NAMES:
    suffix = mod.replace("zephyr.", "").replace(".", "/")
    MODULE_TO_DIR[mod] = SRC_ROOT / suffix


@dataclass
class ScanResult:
    passed: bool
    topological_order: list[str] = field(default_factory=list)
    cycles: list[list[str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dependency_graph: dict[str, set[str]] = field(default_factory=dict)

    def summary(self) -> str:
        if self.passed:
            return f"[PASS] EN-001: No circular dependencies ({len(self.topological_order)} nodes)"
        return f"[FAIL] EN-001: {len(self.cycles)} cycle(s) detected\n" + "\n".join(
            f"  Cycle: {' → '.join(c)}" for c in self.cycles
        )


def _parse_imports(file_path: Path) -> set[str]:
    imports: set[str] = set()
    if not file_path.exists():
        return imports
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def _resolve_to_module(import_name: str) -> str | None:
    for mod in ALL_MODULES:
        if import_name == mod or import_name.startswith(mod + "."):
            return mod
    return None


def _build_dependency_graph() -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {mod: set() for mod in ALL_MODULES}

    for mod, directory in MODULE_TO_DIR.items():
        if not directory.exists():
            continue
        all_imports: set[str] = set()
        for py_file in directory.rglob("*.py"):
            all_imports.update(_parse_imports(py_file))
        for imp in all_imports:
            resolved = _resolve_to_module(imp)
            if resolved and resolved != mod:
                graph[mod].add(resolved)

    return graph


def _kahn_topological_sort(graph: dict[str, set[str]]) -> tuple[list[str], list[str]]:
    in_degree: dict[str, int] = {node: 0 for node in graph}
    for node, deps in graph.items():
        for dep in deps:
            in_degree[dep] = in_degree.get(dep, 0) + 1

    queue: deque[str] = deque(n for n, d in in_degree.items() if d == 0)
    order: list[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, set()):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    remaining = [n for n, d in in_degree.items() if d > 0]
    return order, remaining


def _find_cycles(graph: dict[str, set[str]], nodes_in_cycle: list[str]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visited: set[str] = set()
    stack: list[str] = []
    path_set: set[str] = set()

    def dfs(node: str) -> None:
        if node in path_set:
            cycle_start = stack.index(node)
            cycles.append(stack[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path_set.add(node)
        stack.append(node)
        for neighbor in graph.get(node, set()):
            dfs(neighbor)
        stack.pop()
        path_set.discard(node)

    for node in nodes_in_cycle:
        if node not in visited:
            dfs(node)

    return cycles


def run_scan() -> ScanResult:
    errors: list[str] = []
    graph = _build_dependency_graph()

    order, remaining = _kahn_topological_sort(graph)

    if remaining:
        cycles = _find_cycles(graph, remaining)
        return ScanResult(
            passed=False,
            topological_order=order,
            cycles=cycles,
            errors=errors,
            dependency_graph=graph,
        )

    return ScanResult(
        passed=True,
        topological_order=order,
        dependency_graph=graph,
    )


def check() -> tuple[bool, str]:
    result = run_scan()
    return result.passed, result.summary()


if __name__ == "__main__":
    ok, msg = check()
    print(msg)
    sys.exit(0 if ok else 1)

# ==== END CODEGEN:EN-001 ====
