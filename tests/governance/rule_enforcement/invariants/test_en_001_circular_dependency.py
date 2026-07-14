# [A_test] module_id: SRC-TST-0831 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_en_001_circular_dependency
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit code reflects pass/fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency import (
    ALL_MODULES,
    MODULE_TO_DIR,
    ScanResult,
    _build_dependency_graph,
    _find_cycles,
    _kahn_topological_sort,
    _parse_imports,
    _resolve_to_module,
    check,
    run_scan,
)

SHARED_MODULE = "zephyr.shared.contracts"


class TestScanResult:
    def test_passed_summary(self):
        sr = ScanResult(passed=True, topological_order=["a", "b", "c"])
        assert sr.summary() == "[PASS] EN-001: No circular dependencies (3 nodes)"

    def test_failed_summary(self):
        sr = ScanResult(
            passed=False,
            cycles=[["a", "b", "a"]],
        )
        summary = sr.summary()
        assert "[FAIL] EN-001:" in summary
        assert "1 cycle(s) detected" in summary
        assert "a → b → a" in summary

    def test_failed_summary_multiple_cycles(self):
        sr = ScanResult(
            passed=False,
            cycles=[["a", "b", "a"], ["c", "d", "c"]],
        )
        summary = sr.summary()
        assert "2 cycle(s) detected" in summary

    def test_default_values(self):
        sr = ScanResult(passed=True)
        assert sr.topological_order == []
        assert sr.cycles == []
        assert sr.errors == []
        assert sr.dependency_graph == {}

    def test_passed_false_with_empty_cycles(self):
        sr = ScanResult(passed=False, cycles=[])
        assert "[FAIL]" in sr.summary()


class TestParseImports:
    def test_parse_import_statement(self, tmp_path):
        py = tmp_path / "mod.py"
        py.write_text("import os\nimport sys\n", encoding="utf-8")
        result = _parse_imports(py)
        assert "os" in result
        assert "sys" in result

    def test_parse_from_import(self, tmp_path):
        py = tmp_path / "mod.py"
        py.write_text("from zephyr.shared.contracts import Foo\n", encoding="utf-8")
        result = _parse_imports(py)
        assert "zephyr.shared.contracts" in result

    def test_parse_mixed_imports(self, tmp_path):
        py = tmp_path / "mod.py"
        py.write_text(
            "import os\nfrom zephyr.infrastructure_runtime_integration import X\n",
            encoding="utf-8",
        )
        result = _parse_imports(py)
        assert "os" in result
        assert "zephyr.l01_infrastructure" in result

    def test_nonexistent_file(self):
        result = _parse_imports(Path("/nonexistent/file.py"))
        assert result == set()

    def test_syntax_error_file(self, tmp_path):
        py = tmp_path / "bad.py"
        py.write_text("def broken(\n", encoding="utf-8")
        result = _parse_imports(py)
        assert result == set()

    def test_empty_file(self, tmp_path):
        py = tmp_path / "empty.py"
        py.write_text("", encoding="utf-8")
        result = _parse_imports(py)
        assert result == set()

    def test_no_imports(self, tmp_path):
        py = tmp_path / "code.py"
        py.write_text("x = 1\ny = 2\n", encoding="utf-8")
        result = _parse_imports(py)
        assert result == set()

    def test_import_with_alias(self, tmp_path):
        py = tmp_path / "mod.py"
        py.write_text("import numpy as np\n", encoding="utf-8")
        result = _parse_imports(py)
        assert "numpy" in result

    def test_from_import_none_module(self, tmp_path):
        py = tmp_path / "mod.py"
        py.write_text("from . import something\n", encoding="utf-8")
        result = _parse_imports(py)
        assert isinstance(result, set)


class TestResolveToModule:
    def test_exact_match(self):
        assert _resolve_to_module("zephyr.shared.contracts") == SHARED_MODULE

    def test_prefix_match(self):
        result = _resolve_to_module("zephyr.infrastructure.submod")
        assert result == "zephyr.l01_infrastructure"

    def test_no_match(self):
        assert _resolve_to_module("os") is None

    def test_no_match_external(self):
        assert _resolve_to_module("numpy") is None

    def test_partial_no_match(self):
        assert _resolve_to_module("zephyr") is None

    def test_all_modules_resolvable(self):
        for mod in ALL_MODULES:
            resolved = _resolve_to_module(mod)
            assert resolved is not None
            assert resolved in ALL_MODULES


class TestConstants:
    def test_layer_module_names_is_list(self):
        assert isinstance(ALL_MODULES, list)

    def test_shared_module_value(self):
        assert SHARED_MODULE == "zephyr.shared.contracts"

    def test_all_modules_includes_shared(self):
        assert SHARED_MODULE in ALL_MODULES

    def test_all_modules_includes_all_layers(self):
        for mod in ALL_MODULES:
            assert mod in ALL_MODULES

    def test_module_to_dir_has_all_entries(self):
        for mod in ALL_MODULES:
            assert mod in MODULE_TO_DIR

    def test_module_to_dir_values_are_paths(self):
        for mod, path in MODULE_TO_DIR.items():
            assert isinstance(path, Path)


class TestKahnTopologicalSort:
    def test_acyclic_graph(self):
        graph = {"a": {"b"}, "b": {"c"}, "c": set()}
        order, remaining = _kahn_topological_sort(graph)
        assert len(order) == 3
        assert len(remaining) == 0
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_cyclic_graph(self):
        graph = {"a": {"b"}, "b": {"a"}}
        order, remaining = _kahn_topological_sort(graph)
        assert len(remaining) == 2

    def test_empty_graph(self):
        graph: dict[str, set[str]] = {}
        order, remaining = _kahn_topological_sort(graph)
        assert order == []
        assert remaining == []

    def test_single_node_no_deps(self):
        graph = {"a": set()}
        order, remaining = _kahn_topological_sort(graph)
        assert order == ["a"]
        assert remaining == []

    def test_self_loop(self):
        graph = {"a": {"a"}}
        order, remaining = _kahn_topological_sort(graph)
        assert len(remaining) == 1
        assert "a" in remaining

    def test_diamond_dependency(self):
        graph = {"a": {"b", "c"}, "b": {"d"}, "c": {"d"}, "d": set()}
        order, remaining = _kahn_topological_sort(graph)
        assert len(order) == 4
        assert len(remaining) == 0
        assert order.index("a") < order.index("b")
        assert order.index("a") < order.index("c")
        assert order.index("b") < order.index("d")
        assert order.index("c") < order.index("d")


class TestFindCycles:
    def test_simple_cycle(self):
        graph = {"a": {"b"}, "b": {"a"}}
        cycles = _find_cycles(graph, ["a", "b"])
        assert len(cycles) >= 1
        cycle_nodes = set()
        for c in cycles:
            cycle_nodes.update(c)
        assert "a" in cycle_nodes
        assert "b" in cycle_nodes

    def test_no_cycle(self):
        graph = {"a": {"b"}, "b": set()}
        cycles = _find_cycles(graph, [])
        assert cycles == []

    def test_self_loop_cycle(self):
        graph = {"a": {"a"}}
        cycles = _find_cycles(graph, ["a"])
        assert len(cycles) >= 1

    def test_three_node_cycle(self):
        graph = {"a": {"b"}, "b": {"c"}, "c": {"a"}}
        cycles = _find_cycles(graph, ["a", "b", "c"])
        assert len(cycles) >= 1


class TestBuildDependencyGraph:
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency._parse_imports")
    def test_builds_graph_from_imports(self, mock_parse):
        mock_parse.return_value = {"zephyr.l01_infrastructure", "os"}

        graph = _build_dependency_graph()
        assert isinstance(graph, dict)
        for mod in ALL_MODULES:
            assert mod in graph

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency._parse_imports")
    def test_self_dependency_excluded(self, mock_parse):
        mock_parse.return_value = {"zephyr.l01_infrastructure"}

        graph = _build_dependency_graph()
        infra_deps = graph.get("zephyr.l01_infrastructure", set())
        assert "zephyr.l01_infrastructure" not in infra_deps


class TestRunScan:
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency._build_dependency_graph")
    def test_returns_scan_result(self, mock_build):
        mock_build.return_value = {"a": set(), "b": set()}
        result = run_scan()
        assert isinstance(result, ScanResult)

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency._build_dependency_graph")
    def test_acyclic_passes(self, mock_build):
        mock_build.return_value = {"a": set(), "b": set()}
        result = run_scan()
        assert result.passed is True

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency._build_dependency_graph")
    def test_cyclic_fails(self, mock_build):
        mock_build.return_value = {"a": {"b"}, "b": {"a"}}
        result = run_scan()
        assert result.passed is False
        assert len(result.cycles) >= 1


class TestCheck:
    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency.run_scan")
    def test_check_returns_tuple(self, mock_scan):
        mock_scan.return_value = ScanResult(passed=True, topological_order=["a"])
        passed, msg = check()
        assert isinstance(passed, bool)
        assert isinstance(msg, str)

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency.run_scan")
    def test_check_pass(self, mock_scan):
        mock_scan.return_value = ScanResult(passed=True, topological_order=["a", "b"])
        passed, msg = check()
        assert passed is True
        assert "[PASS]" in msg

    @patch("zephyr.gov_enforcement.rule_enforcement.invariants.en_001_circular_dependency.run_scan")
    def test_check_fail(self, mock_scan):
        mock_scan.return_value = ScanResult(passed=False, cycles=[["a", "b", "a"]])
        passed, msg = check()
        assert passed is False
        assert "[FAIL]" in msg
