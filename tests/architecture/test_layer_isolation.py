# [A_test] module_id: SRC-TST-0064 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-222 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.architecture.test_layer_isolation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
架构适应度函数：层隔离性 + 依赖方向
========================================

验证所有域的导入只来自合法来源，依赖方向符合架构定义。

架构不变式
----------
- LF01: 低层不导入高层（低层域不 import 高层域）
- LF02: 跨层数据交换只走 shared/contracts/
- LF03: 层只能导入 shared/ + contracts/ + 自身 + 下层接口

Safety: HIGH（架构基石，违反意味着架构已经腐烂）
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT

LAYER_ORDER = [
    "l00-data-source",
    "l01-infrastructure",
    "l02-alpha-factor",
    "l03-signal-generation",
    "l04-risk-management",
    "l05-portfolio-construction",
    "l06-trade-execution",
    "l07-post-trade-analytics",
    "l08-human-ai-interface",
    "l09-research-innovation",
    "l10-compliance",
    "l11-ml-platform",
    "system-telemetry",
    "l13-experimentation",
]

LAYER_INDEX = {name: i for i, name in enumerate(LAYER_ORDER)}

SHARED_DIRS = {
    "shared",
    "core",
    "context-engine",
    "kb",
    "db",
    "orchestrator",
    "gates",
    "mcp",
    "feedback-loop",
    "llm-security",
    "pipeline",
    "vector-memory",
}

SRC_DIR = REPO_ROOT / "src" / "zephyr"


def _layer_of_file(filepath: Path) -> str | None:
    """返回文件所属的层名，如果不在层目录中则返回 None。"""
    rel = str(filepath.relative_to(SRC_DIR)).replace("\\", "/")
    for layer in LAYER_ORDER:
        if rel.startswith(layer + "/") or rel == layer:
            return layer
    for shared in SHARED_DIRS:
        if rel.startswith(shared + "/") or rel == shared:
            return shared
    return None


def _imports_in_file(filepath: Path) -> list[tuple[str, int]]:
    """提取文件中所有的 import 路径和行号。"""
    imports: list[tuple[str, int]] = []
    source = filepath.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.module, node.lineno))
    return imports


def _all_layer_files() -> list[Path]:
    """返回所有层目录下的 .py 文件。"""
    files: list[Path] = []
    for layer in LAYER_ORDER:
        layer_dir = SRC_DIR / layer
        if not layer_dir.exists():
            continue
        for f in layer_dir.rglob("*.py"):
            if f.is_file() and f.name != "__init__.py":
                files.append(f)
    return files


class TestLayerIsolation:
    """LF01: 层依赖方向正确。"""

    @pytest.mark.parametrize("filepath", _all_layer_files())
    def test_no_upward_dependency(self, filepath: Path):
        current_layer = _layer_of_file(filepath)
        if current_layer is None or current_layer not in LAYER_INDEX:
            pytest.skip(f"非层文件: {filepath}")

        current_idx = LAYER_INDEX[current_layer]
        violations: list[str] = []

        for import_path, lineno in _imports_in_file(filepath):
            normalized = import_path.replace(".", "/")
            for other_layer, other_idx in LAYER_INDEX.items():
                if other_idx > current_idx:
                    layer_in_path = other_layer.replace("_", "/")
                    if layer_in_path in normalized:
                        violations.append(
                            f"行 {lineno}: 低层导入高层 — {current_layer} 不能 import {other_layer} ({import_path})"
                        )

        if violations:
            rel = filepath.relative_to(REPO_ROOT)
            msg = f"{rel}:\n" + "\n".join(f"  - {v}" for v in violations)
            pytest.fail(msg)

    @pytest.mark.parametrize("filepath", _all_layer_files())
    def test_cross_layer_only_via_contracts(self, filepath: Path):
        target_layer = _layer_of_file(filepath)
        if target_layer is None or target_layer not in LAYER_INDEX:
            return

        layer_dir_name = target_layer.replace("_", "/")
        violations: list[str] = []

        for import_path, lineno in _imports_in_file(filepath):
            for other in LAYER_ORDER:
                other_dir = other.replace("_", "/")
                if other_dir != layer_dir_name and other_dir in import_path.replace(".", "/"):
                    if "shared/contracts" not in import_path.replace(".", "/"):
                        violations.append(
                            f"行 {lineno}: 跨层导入未走 contracts/ — "
                            f"{target_layer} import {import_path} 绕过了 CTR 契约"
                        )

        if violations:
            rel = filepath.relative_to(REPO_ROOT)
            pytest.fail(f"{rel}:\n" + "\n".join(f"  - {v}" for v in violations))


class TestNoImportCycles:
    """LF03: 模块间无循环依赖。"""

    def test_no_cycles_in_layer_graph(self):
        import_graph: dict[str, set[str]] = {}

        for filepath in _all_layer_files():
            layer = _layer_of_file(filepath)
            if layer is None:
                continue
            if layer not in import_graph:
                import_graph[layer] = set()
            for import_path, _ in _imports_in_file(filepath):
                normalized = import_path.replace(".", "/")
                for other in LAYER_ORDER:
                    if other.replace("_", "/") in normalized and other != layer:
                        import_graph[layer].add(other)

        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in import_graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for layer in LAYER_ORDER:
            if layer not in visited:
                if has_cycle(layer):
                    pytest.fail(f"检测到循环依赖，涉及层: {sorted(rec_stack)}")
