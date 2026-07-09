# [A_test] module_id: SRC-TST-0739 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_dependency
# [INVARIANTS] DependencyExtractor.extract returns list[DependencyEdge]; build_dependency_graph produces DependencyGraph
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SyntaxError in source code returns empty list
# [TESTS] tests/test_dependency_root.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.asset_inventory.dependency import (
    DependencyEdge,
    DependencyExtractor,
    DependencyGraph,
    DependencyNode,
    _infer_layer,
    build_dependency_graph,
    priority_from_dependency,
)


class TestDependencyNode:
    def test_create(self):
        n = DependencyNode(file_path="src/test.py")
        assert n.layer == "cross_layer"
        assert n.imported_by_count == 0
        assert n.is_leaf is False
        assert n.is_root is True


class TestDependencyEdge:
    def test_create(self):
        e = DependencyEdge(from_file="a.py", to_module="os", import_type="stdlib", line_number=1)
        assert e.from_file == "a.py"
        assert e.to_module == "os"
        assert e.import_type == "stdlib"


class TestDependencyGraph:
    def test_create(self):
        g = DependencyGraph()
        assert g.nodes == {}
        assert g.edges == []
        assert g.circular_dependencies == []
        assert g.orphan_imports == []


class TestDependencyExtractorInstantiation:
    def test_create(self):
        ext = DependencyExtractor()
        assert ext is not None


class TestDependencyExtractorExtract:
    def test_extract_import(self):
        code = "import os\nimport sys\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        assert len(edges) >= 2
        assert any(e.to_module == "os" for e in edges)

    def test_extract_from_import(self):
        code = "from pathlib import Path\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        assert len(edges) >= 1
        assert any("pathlib" in e.to_module for e in edges)

    def test_extract_syntax_error(self):
        code = "def broken(\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        assert edges == []

    def test_extract_empty_code(self):
        ext = DependencyExtractor()
        edges = ext.extract("test.py", "")
        assert edges == []

    def test_extract_no_imports(self):
        code = "x = 1\ny = 2\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        assert edges == []

    def test_extract_relative_import(self):
        code = "from . import sibling\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        assert len(edges) >= 1
        assert any("sibling" in e.to_module for e in edges)

    def test_extract_project_import(self):
        code = "from zephyr.infrastructure.asset_inventory.models import AssetType\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        project_edges = [e for e in edges if e.import_type == "absolute"]
        assert len(project_edges) >= 1

    def test_extract_third_party_import(self):
        code = "import requests\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        third_party = [e for e in edges if e.import_type == "third_party"]
        assert len(third_party) >= 1

    def test_extract_stdlib_import(self):
        code = "import os\n"
        ext = DependencyExtractor()
        edges = ext.extract("test.py", code)
        stdlib = [e for e in edges if e.import_type == "stdlib"]
        assert len(stdlib) >= 1


class TestInferLayer:
    def test_infrastructure(self):
        assert _infer_layer("src/zephyr/infrastructure/db.py") == "L0_infrastructure"

    def test_shared(self):
        assert _infer_layer("src/zephyr/shared/events/bus.py") == "L0_infrastructure"

    def test_governance(self):
        assert _infer_layer("src/zephyr/governance/check.py") == "L1_foundation"

    def test_integration(self):
        assert _infer_layer("src/zephyr/integration/mcp_server.py") == "L1_foundation"

    def test_domain(self):
        assert _infer_layer("src/zephyr/factor/base.py") == "L2_domain"

    def test_scripts(self):
        assert _infer_layer("scripts/scan.py") == "L1_foundation"

    def test_tests(self):
        assert _infer_layer("tests/test_foo.py") == "cross_layer"

    def test_config(self):
        assert _infer_layer("config/settings.yaml") == "L0_infrastructure"

    def test_docs(self):
        assert _infer_layer("docs/guide.md") == "cross_layer"

    def test_unknown(self):
        assert _infer_layer("random/file.txt") == "cross_layer"


class TestPriorityFromDependency:
    def test_p0(self):
        assert priority_from_dependency(5) == "P0"
        assert priority_from_dependency(10) == "P0"

    def test_p1(self):
        assert priority_from_dependency(2) == "P1"
        assert priority_from_dependency(4) == "P1"

    def test_p2(self):
        assert priority_from_dependency(1) == "P2"

    def test_p3(self):
        assert priority_from_dependency(0) == "P3"


class TestBuildDependencyGraph:
    def test_empty_entries(self, tmp_path):
        graph = build_dependency_graph([], tmp_path)
        assert isinstance(graph, DependencyGraph)
        assert graph.total_files == 0

    def test_with_dict_entries(self, tmp_path):
        subdir = tmp_path / "src"
        subdir.mkdir()
        f = subdir / "mod.py"
        f.write_text("import os\n", encoding="utf-8")
        entries = [{"relative_path": "src/mod.py"}]
        graph = build_dependency_graph(entries, tmp_path)
        assert graph.total_files == 1
        assert len(graph.edges) >= 1

    def test_nonexistent_files_skipped(self, tmp_path):
        entries = [{"relative_path": "nonexistent.py"}]
        graph = build_dependency_graph(entries, tmp_path)
        assert graph.total_files == 1
        assert len(graph.edges) == 0
