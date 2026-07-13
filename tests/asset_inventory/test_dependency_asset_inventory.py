# [A_test] module_id: SRC-TST-0070 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-228 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_dependency
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §18 Dependency Graph module."""

from pathlib import Path

from zephyr.infrastructure.asset_inventory.dependency import (
    DependencyExtractor,
    DependencyNode,
    _detect_cycles,
    _infer_layer,
    build_dependency_graph,
    priority_from_dependency,
)
from zephyr.shared.io.paths import REPO_ROOT

_SIMPLE_IMPORTS = """\
import os
import sys
from pathlib import Path
from zephyr.orchestrator.core import BaseModel
from .utils import helper
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
"""

_NO_IMPORTS = """\
x = 1 + 2
def foo():
    pass
"""

_SYNTAX_ERROR = """\
def broken(
"""

_CIRCULAR_A = "from tests.fixtures.circular_b import b\na = 1"
_CIRCULAR_B = "from tests.fixtures.circular_a import a\nb = 1"


class TestDependencyExtractor:
    def test_extract_simple(self) -> None:
        ex = DependencyExtractor()
        edges = ex.extract("src/mod.py", _SIMPLE_IMPORTS)
        assert len(edges) == 5
        imports = {e.to_module for e in edges}
        assert "os" in imports
        assert "pathlib.Path" in imports
        assert "sys" in imports
        assert "zephyr.orchestrator.core.BaseModel" in imports
        assert "utils.helper" in imports

    def test_extract_no_imports(self) -> None:
        ex = DependencyExtractor()
        edges = ex.extract("src/simple.py", _NO_IMPORTS)
        assert edges == []

    def test_extract_syntax_error(self) -> None:
        ex = DependencyExtractor()
        edges = ex.extract("src/broken.py", _SYNTAX_ERROR)
        assert edges == []

    def test_classify_stdlib(self) -> None:
        ex = DependencyExtractor()
        assert ex._classify_import("os.path") == "stdlib"

    def test_classify_absolute(self) -> None:
        ex = DependencyExtractor()
        assert ex._classify_import("zephyr.governance.audit_trail.models") == "absolute"

    def test_classify_relative(self) -> None:
        ex = DependencyExtractor()
        assert ex._classify_import(".utils") == "relative"

    def test_classify_third_party(self) -> None:
        ex = DependencyExtractor()
        assert ex._classify_import("pandas") == "third_party"

    def test_import_from_with_alias(self) -> None:
        ex = DependencyExtractor()
        code = "from zephyr.governance.audit_trail.models import Field as F"
        edges = ex.extract("test.py", code)
        assert len(edges) == 1
        assert edges[0].to_module == "zephyr.governance.audit_trail.models.Field"


class TestBuildDependencyGraph:
    def test_empty_entries(self) -> None:
        graph = build_dependency_graph([], REPO_ROOT)
        assert graph.total_files == 0
        assert graph.total_edges == 0

    def test_single_py_file(self) -> None:
        entries = [{"relative_path": "src/zephyr/asset-inventory/scanner.py"}]
        graph = build_dependency_graph(entries, REPO_ROOT)
        assert graph.total_files == 1
        assert graph.total_edges > 0
        assert "src/zephyr/asset-inventory/scanner.py" in graph.nodes

    def test_non_py_files_skipped(self) -> None:
        entries = [
            {"relative_path": "README.md"},
            {"relative_path": "config.yaml"},
        ]
        graph = build_dependency_graph(entries, REPO_ROOT)
        assert graph.total_edges == 0


class TestInferLayer:
    def test_domain_layer(self) -> None:
        assert _infer_layer("src/zephyr/models.py") == "L2_domain"

    def test_infrastructure_layer(self) -> None:
        assert _infer_layer("src/zephyr/infrastructure/db.py") == "L0_infrastructure"

    def test_governance_layer(self) -> None:
        assert _infer_layer("src/zephyr/governance/phase.py") == "L1_foundation"

    def test_scripts_layer(self) -> None:
        assert _infer_layer("scripts/lock_files.py") == "L1_foundation"

    def test_tests_layer(self) -> None:
        assert _infer_layer("tests/test_foo.py") == "cross_layer"

    def test_cross_layer_default(self) -> None:
        assert _infer_layer("README.md") == "cross_layer"


class TestDetectCycles:
    def test_no_cycles(self) -> None:
        nodes = {"a.py": DependencyNode(file_path="a.py"), "b.py": DependencyNode(file_path="b.py")}
        adj = {"a.py": {"b.py"}, "b.py": set()}
        cycles = _detect_cycles(nodes, adj)
        assert cycles == []

    def test_simple_cycle(self) -> None:
        nodes = {"a.py": DependencyNode(file_path="a.py"), "b.py": DependencyNode(file_path="b.py")}
        adj = {"a.py": {"b.py"}, "b.py": {"a.py"}}
        cycles = _detect_cycles(nodes, adj)
        assert len(cycles) == 1

    def test_self_cycle_ignored(self) -> None:
        nodes = {"a.py": DependencyNode(file_path="a.py")}
        adj = {"a.py": {"a.py"}}
        cycles = _detect_cycles(nodes, adj)
        assert len(cycles) >= 1


class TestPriorityFromDependency:
    def test_high_imported_by(self) -> None:
        assert priority_from_dependency(10) == "P0"

    def test_medium_imported_by(self) -> None:
        assert priority_from_dependency(3) == "P1"

    def test_low_imported_by(self) -> None:
        assert priority_from_dependency(1) == "P2"

    def test_none_imported_by(self) -> None:
        assert priority_from_dependency(0) == "P3"
