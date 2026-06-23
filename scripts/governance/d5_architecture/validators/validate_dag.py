# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_dag.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_dag
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""
对标 dimension_audit_matrix.md §4.3：
  校验代码级 import 依赖图无循环，与 detect_depends_on_cycles.py（YAML 级）互补。

检测方式：
  - 扫描 src/zephyr/ 下所有 .py 文件的 import 语句
  - 构建 层级→层级 的有向图
  - 使用 DFS 检测环

exit: 0=pass (无环), 1=cycle found, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 代码级 import 依赖 DAG 无循环校验（dimension-audit-matrix §4.3 — D5依赖方向）
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, SRC_DIR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

LAYER_PREFIX = "l"
EXCLUDE_DIRS = {"__pycache__", ".git", "tests", "docs", "shared", "pipeline"}


def extract_layer_from_path(py_file: Path) -> str | None:
    """extract_layer_from_path implementation."""
    parts = py_file.relative_to(SRC_DIR).parts
    if not parts:
        return None
    first = parts[0]
    if first.startswith("l") and first[1:2].isdigit():
        return first.split("_")[0]
    if first in ("shared", "pipeline"):
        return first
    return None


def extract_imports(content: str, own_layer: str) -> set[str]:
    """extract_imports implementation."""
    imports = set()
    for match in re.finditer(r"(?:from|import)\s+(zephyr\.)(\w+)", content):
        module = match.group(2)
        if module.startswith("l") and module[1:2].isdigit():
            layer = module.split("_")[0]
            if layer != own_layer:
                imports.add(layer)
    return imports


def build_dependency_graph() -> dict[str, set[str]]:
    """build_dependency_graph implementation."""
    graph: dict[str, set[str]] = defaultdict(set)
    if not SRC_DIR.exists():
        return graph
    for py_file in SRC_DIR.rglob("*.py"):
        if any(excl in py_file.parts for excl in EXCLUDE_DIRS):
            continue
        own_layer = extract_layer_from_path(py_file)
        if not own_layer:
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        deps = extract_imports(content, own_layer)
        for dep in deps:
            graph[own_layer].add(dep)
    return graph


def detect_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Detect issues in target and report findings."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = defaultdict(int)
    cycles: list[list[str]] = []
    path: list[str] = []

    def dfs(node: str) -> None:
        """dfs implementation."""
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, set()):
            if color[neighbor] == GRAY:
                idx = path.index(neighbor)
                cycles.append(path[idx:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor)
        path.pop()
        color[node] = BLACK

    for node in sorted(graph.keys()):
        if color[node] == WHITE:
            dfs(node)
    return cycles


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if not SRC_DIR.exists():
        print("src/zephyr/ 目录不存在 — 跳过 DAG 校验")
        return EXIT_PASS
    graph = build_dependency_graph()

    print("层级依赖图:")
    for layer in sorted(graph.keys()):
        deps = sorted(graph[layer])
        if deps:
            print(f"  {layer} → {', '.join(deps)}")
        else:
            print(f"  {layer} → (无外部依赖)")

    cycles = detect_cycles(graph)

    if cycles:
        print(f"\n[FAIL] 发现 {len(cycles)} 个循环依赖:")
        for cycle in cycles:
            print(f"  {' → '.join(cycle)}")
        print("\n循环依赖违反分层架构原则——上层不得依赖下层，同层不得互相依赖。")
        return EXIT_FINDINGS
    print(f"\n[OK] DAG 无循环 — {len(graph)} 个层级节点已校验")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
