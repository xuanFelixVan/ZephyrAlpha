# [BLUEPRINT] MOD-INF-005 | scripts/governance/dependency_graph.py | §
# [MODULE] scripts.governance.dependency_graph
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""治理域有向依赖图 — 扫描 governance/ 下所有 import 生成依赖图."""

from __future__ import annotations

__manifest__ = """
args: []
description: 治理域有向依赖图 — 扫描 governance/ 下所有 import 生成依赖图.
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

SRC_DIR = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC_DIR))


def build_dependency_graph(package_path: str | Path | None = None) -> dict[str, list[str]]:
    """扫描 governance/ 下所有 .py 文件的 import → 返回有向邻接表."""
    if package_path is None:
        package_path = Path("src/zephyr/governance")
    pkg = Path(package_path)

    graph: dict[str, list[str]] = {}

    for py_file in sorted(pkg.rglob("*.py")):
        module_name = str(py_file.relative_to(Path("src/zephyr"))).replace("\\", ".").replace(".py", "")
        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        deps: list[str] = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("from zephyr.governance."):
                parts = line.split()
                if len(parts) >= 2:
                    dep = parts[1]
                    dep = dep.split(".")[:3]  # module.sub_module only
                    dep_name = ".".join(dep)
                    deps.append(dep_name)
            elif line.startswith("import zephyr.governance."):
                parts = line.split()
                if len(parts) >= 2:
                    deps.append(parts[1])

        if deps:
            graph[module_name] = sorted(set(deps))

    return graph


def has_cycle(graph: dict[str, list[str]]) -> tuple[bool, list[str] | None]:
    """DFS 检测有向图中是否存在环."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {node: WHITE for node in graph}

    path: list[str] = []

    def dfs(node: str) -> bool:
        """dfs implementation."""
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, []):
            # Simplify neighbor to check partial matches
            for key in graph:
                if key.endswith(neighbor) or neighbor.endswith(key):
                    if color.get(key) == GRAY:
                        return True
                    if color.get(key) == WHITE:
                        if dfs(key):
                            return True
        path.pop()
        color[node] = BLACK
        return False

    for node in graph:
        if color.get(node) == WHITE:
            if dfs(node):
                return True, path

    return False, None


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    graph = build_dependency_graph()
    print("=== 治理域依赖图 ===")
    if not graph:
        print("No internal dependencies detected.")
        return EXIT_PASS

    for module, deps in sorted(graph.items()):
        print(f"  {module} → {deps}")

    cyclic, cycle_path = has_cycle(graph)
    if cyclic:
        print(f"FAIL: 循环依赖检测到: {cycle_path}")
        return EXIT_FINDINGS

    print("PASS: 依赖图无环")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
