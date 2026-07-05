# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.dependency
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.asset_inventory.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_dependency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MOD-INF-026 §18 — 资产依赖图。

DependencyExtractor：从 Python AST 提取 import 关系。
DependencyGraph：项目级依赖图 + 环路检测（DFS）+ 优先级联动。
"""

import ast
import sys
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field


class DependencyNode(BaseModel):
    file_path: str
    layer: str = "cross_layer"
    imported_by_count: int = 0
    imports_count: int = 0
    is_leaf: bool = False
    is_root: bool = True


class DependencyEdge(BaseModel):
    from_file: str
    to_module: str
    import_type: str = "absolute"
    line_number: int = 0


class DependencyGraph(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    based_on_scan: str = ""
    total_files: int = 0
    total_edges: int = 0
    nodes: dict[str, DependencyNode] = Field(default_factory=dict)
    edges: list[DependencyEdge] = Field(default_factory=list)
    most_depended_upon: list[str] = Field(default_factory=list)
    circular_dependencies: list[list[str]] = Field(default_factory=list)
    orphan_imports: list[str] = Field(default_factory=list)


_STDLIB_MODULES: set[str] = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()


class DependencyExtractor:
    def extract(self, file_path: str, source_code: str) -> list[DependencyEdge]:
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []

        edges: list[DependencyEdge] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(self._to_edge(file_path, alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    edges.append(self._to_edge(file_path, full_name, node.lineno or 0))

        return edges

    def _to_edge(self, file_path: str, imported: str, lineno: int) -> DependencyEdge:
        return DependencyEdge(
            from_file=file_path,
            to_module=imported,
            import_type=self._classify_import(imported),
            line_number=lineno,
        )

    def _classify_import(self, imported: str) -> str:
        top_level = imported.split(".")[0]
        if top_level in _STDLIB_MODULES:
            return "stdlib"
        known_project_prefixes = ("zephyr", "scripts", "tests", "config", "docs")
        if any(imported.startswith(p) for p in known_project_prefixes):
            return "absolute"
        if imported.startswith("."):
            return "relative"
        return "third_party"


def build_dependency_graph(scan_entries: list, project_root: Path) -> DependencyGraph:
    extractor = DependencyExtractor()
    graph = DependencyGraph()
    graph.based_on_scan = "DEP-001"
    graph.total_files = len(scan_entries)

    importer_count: dict[str, int] = {}
    importee_count: dict[str, int] = {}
    adjacency: dict[str, set[str]] = {}
    module_to_file: dict[str, str] = {}
    resolved_adjacency: dict[str, set[str]] = {}

    for entry in scan_entries:
        if isinstance(entry, dict):
            fp = entry.get("relative_path", "")
        else:
            fp = getattr(entry, "relative_path", str(entry))
        if not fp.endswith(".py"):
            continue

        full_path = project_root / fp
        if not full_path.exists():
            continue

        try:
            code = full_path.read_text(encoding="utf-8")
        except (OSError, PermissionError, UnicodeDecodeError):
            continue

        edges = extractor.extract(fp, code)
        graph.edges.extend(edges)

        modules_imported: set[str] = set()
        for e in edges:
            modules_imported.add(e.to_module)
            importer_count[e.to_module] = importer_count.get(e.to_module, 0) + 1

        importee_count[fp] = len(modules_imported)
        adjacency[fp] = modules_imported

    for entry in scan_entries:
        if isinstance(entry, dict):
            fp = entry.get("relative_path", "")
        else:
            fp = getattr(entry, "relative_path", str(entry))
        if not fp.endswith(".py"):
            continue
        layer = _infer_layer(fp)
        graph.nodes[fp] = DependencyNode(
            file_path=fp,
            layer=layer,
            imported_by_count=importer_count.get(fp, 0),
            imports_count=importee_count.get(fp, 0),
            is_leaf=importee_count.get(fp, 0) == 0,
            is_root=importer_count.get(fp, 0) == 0,
        )

    graph.total_edges = len(graph.edges)
    graph.most_depended_upon = sorted(
        [n.file_path for n in graph.nodes.values() if n.imported_by_count > 0],
        key=lambda fp: graph.nodes[fp].imported_by_count,
        reverse=True,
    )[:10]

    unresolved: set[str] = set()
    for e in graph.edges:
        top = e.to_module.split(".")[0]
        resolved = False
        for fp in graph.nodes:
            if fp.endswith(e.to_module.replace(".", "/") + ".py") or fp.endswith(
                e.to_module.replace(".", "/") + "/__init__.py"
            ):
                resolved = True
                break
            if top == fp.split("/")[-1].replace(".py", ""):
                resolved = True
                break
        if not resolved:
            unresolved.add(e.to_module)
    graph.orphan_imports = sorted(unresolved)

    graph.circular_dependencies = _detect_cycles(graph.nodes, resolved_adjacency)

    return graph


def _resolve_module_to_file(module_name: str, module_to_file: dict[str, str]) -> str | None:
    if module_name in module_to_file:
        return module_to_file[module_name]
    parts = module_name.split(".")
    for i in range(len(parts) - 1, 0, -1):
        prefix = ".".join(parts[:i])
        if prefix in module_to_file:
            return module_to_file[prefix]
    return None


def _infer_layer(file_path: str) -> str:
    if file_path.startswith("src/zephyr/gates/"):
        return "L02_gates"
    if file_path.startswith("src/zephyr/governance/"):
        return "L01_governance"
    if file_path.startswith("src/zephyr/"):
        return "L00_core"
    if file_path.startswith("scripts/"):
        return "L03_scripts"
    if file_path.startswith("tests/"):
        return "L04_tests"
    if file_path.startswith("config/"):
        return "L05_config"
    if file_path.startswith("docs/"):
        return "L06_docs"
    return "cross_layer"


def _detect_cycles(nodes: dict[str, DependencyNode], adjacency: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {fp: WHITE for fp in nodes}
    stack: list[str] = []

    def dfs(fp: str) -> None:
        color[fp] = GRAY
        stack.append(fp)

        for imported in adjacency.get(fp, set()):
            if imported not in color:
                continue
            if color[imported] == GRAY:
                try:
                    start = stack.index(imported)
                    cycle = stack[start:] + [imported]
                    cycles.append(cycle)
                except ValueError:
                    pass
            elif color[imported] == WHITE:
                dfs(imported)

        stack.pop()
        color[fp] = BLACK

    for fp in nodes:
        if color[fp] == WHITE:
            dfs(fp)

    return cycles


def priority_from_dependency(imported_by_count: int) -> str:
    if imported_by_count >= 5:
        return "P0"
    if imported_by_count >= 2:
        return "P1"
    if imported_by_count == 1:
        return "P2"
    return "P3"
