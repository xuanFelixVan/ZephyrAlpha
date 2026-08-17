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
# [A_module] module_id=MOD-INF-005 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
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


import ast
import sys
from pathlib import Path

# bootstrap sys.path: _shared lives at scripts/governance/_shared/
# Path(__file__).resolve() = scripts/governance/d5_architecture/dependency_graph.py
# parents[0] = d5_architecture/, parents[1] = governance/, parents[2] = scripts/
_GOV_DIR = str(Path(__file__).resolve().parents[1])
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402

SRC_DIR = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC_DIR))

# 依赖图模块名基准：相对于 src/zephyr/ 的路径去掉 .py 后缀（如 governance.__init__、
# governance.capability_lookup）。import 语句中 `zephyr.governance.xxx` 需去掉
# `zephyr.` 前缀以与模块名格式对齐，使 has_cycle 可用精确匹配。
_GOV_PREFIX = "zephyr.governance."


def _normalize_dep(module: str) -> str | None:
    """将 `zephyr.governance.xxx.yyy` 归一化为 `governance.xxx.yyy`（取前 3 段）。

    非 governance 子模块（如 `zephyr.shared.io.paths`）返回 None。
    """
    if not module or not module.startswith(_GOV_PREFIX):
        return None
    rest = module[len(_GOV_PREFIX):]
    # 与历史行为一致：只保留 `governance.<sub>.<subsub>` 三段
    parts = ("governance." + rest).split(".")[:3]
    return ".".join(parts)


def _iter_load_time_imports(tree: ast.Module):
    """遍历模块加载时执行的 import（跳过函数体内的 lazy import）。

    静态依赖分析只关心 load-time import：模块级、class body、if/try/with 块内的
    import 在模块加载时执行，可能形成 load-time 循环依赖；函数体内的 import 是
    runtime lazy import，不会造成 load-time 循环（Python import 系统允许）。
    """
    def _walk(node: ast.AST):
        """_walk implementation."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue  # 跳过函数体（lazy import）
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                yield child
            yield from _walk(child)
    yield from _walk(tree)


def build_dependency_graph(package_path: str | Path | None = None) -> dict[str, list[str]]:
    """扫描 governance/ 下所有 .py 文件的 import → 返回有向邻接表.

    使用 AST 解析跳过 docstring/注释中的伪 import，并只统计模块加载时执行的
    import（函数体内的 lazy import 不计入静态依赖图）。
    """
    if package_path is None:
        package_path = Path("src/zephyr/governance")
    pkg = Path(package_path)

    graph: dict[str, list[str]] = {}

    for py_file in sorted(pkg.rglob("*.py")):
        module_name = str(
            py_file.relative_to(Path("src/zephyr"))
        ).replace("\\", ".").replace(".py", "")
        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        deps: list[str] = []
        try:
            tree = ast.parse(content, filename=str(py_file))
        except SyntaxError:
            continue
        for node in _iter_load_time_imports(tree):
            if isinstance(node, ast.ImportFrom):
                normalized = _normalize_dep(node.module or "")
                if normalized:
                    deps.append(normalized)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    normalized = _normalize_dep(alias.name)
                    if normalized:
                        deps.append(normalized)

        if deps:
            graph[module_name] = sorted(set(deps))

    return graph


def has_cycle(graph: dict[str, list[str]]) -> tuple[bool, list[str] | None]:
    """DFS 检测有向图中是否存在环（精确匹配，无 endswith 模糊匹配）."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {node: WHITE for node in graph}

    path: list[str] = []

    def dfs(node: str) -> bool:
        """dfs implementation."""
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, []):
            # 精确匹配：依赖必须在图中（同包内）才构成环
            if neighbor not in graph:
                continue
            if color.get(neighbor) == GRAY:
                return True
            if color.get(neighbor) == WHITE:
                if dfs(neighbor):
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
