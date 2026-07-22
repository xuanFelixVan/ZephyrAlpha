# [A_test] module_id: MOD-GOV_blast_radius_red_team | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 9
# [MODULE] tests.semantic_auditor.test_blast_radius_red_team
# [INVARIANTS] adversarial_tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/semantic-auditor/test_blast_radius_red_team.py
# [TTL] task_bound

"""blast_radius 红蓝对抗测试 — 对抗性场景覆盖."""

from __future__ import annotations

from pathlib import Path

import yaml

from zephyr.governance.resilience_governance.blast_radius import (
    BlastRadiusAnalyzer,
    BlastRadiusReport,
)
from zephyr.governance.semantic_audit.models import SemanticAuditFinding, Severity


def _make_finding(
    finding_id: str = "F-SEM-RED-001",
    source_location: str = "",
) -> SemanticAuditFinding:
    return SemanticAuditFinding(
        finding_id=finding_id,
        module="red_team_test",
        severity=Severity.RED,
        dimension="cross_doc_ref_broken",
        description="red team adversarial test",
        source_location=source_location,
    )


def _write_depgraph(path: Path, nodes: dict) -> None:
    data = {"metadata": {"graph_id": "RED-TEAM"}, "nodes": nodes}
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


class TestCyclicDependencyGraph:
    """循环依赖图 — BFS 必须终止，不能无限循环."""

    def test_cyclic_dependency_terminates(self, tmp_path):
        depgraph = tmp_path / "cyclic.yaml"
        nodes = {
            "node_a": {
                "id": "node_a",
                "path": "src/zephyr/a.py",
                "type": "module",
                "imports": ["zephyr.b"],
            },
            "node_b": {
                "id": "node_b",
                "path": "src/zephyr/b.py",
                "type": "module",
                "imports": ["zephyr.c"],
            },
            "node_c": {
                "id": "node_c",
                "path": "src/zephyr/c.py",
                "type": "module",
                "imports": ["zephyr.a"],
            },
        }
        _write_depgraph(depgraph, nodes)
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph, max_depth=5)
        finding = _make_finding(source_location="src/zephyr/a.py")
        report = analyzer.analyze(finding)
        assert report.transitive_dependents >= 0
        assert report.cascade_depth <= 5


class TestSelfReferencingNode:
    """自引用节点 — 文件 import 自身."""

    def test_self_referencing_terminates(self, tmp_path):
        depgraph = tmp_path / "self_ref.yaml"
        nodes = {
            "node_a": {
                "id": "node_a",
                "path": "src/zephyr/a.py",
                "type": "module",
                "imports": ["zephyr.a"],
            },
        }
        _write_depgraph(depgraph, nodes)
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/a.py")
        report = analyzer.analyze(finding)
        assert report.transitive_dependents == 0
        assert report.cascade_depth == 0


class TestEmptyDepgraph:
    """空 depgraph — 零节点."""

    def test_empty_depgraph_returns_zero(self, tmp_path):
        depgraph = tmp_path / "empty.yaml"
        _write_depgraph(depgraph, {})
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/a.py")
        report = analyzer.analyze(finding)
        assert report.direct_dependents == 0
        assert report.transitive_dependents == 0
        assert report.risk_level == "LOW"


class TestSuperDeepChain:
    """超深依赖链 — max_depth 限制必须生效."""

    def test_deep_chain_respects_max_depth(self, tmp_path):
        depgraph = tmp_path / "deep.yaml"
        nodes = {}
        for i in range(20):
            path = f"src/zephyr/layer{i}.py"
            mod = f"zephyr.layer{i}"
            imports = [f"zephyr.layer{i + 1}"] if i < 19 else []
            nodes[f"node_{i}"] = {
                "id": f"node_{i}",
                "path": path,
                "type": "module",
                "imports": imports,
            }
        _write_depgraph(depgraph, nodes)
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph, max_depth=3)
        finding = _make_finding(source_location="src/zephyr/layer0.py")
        report = analyzer.analyze(finding)
        assert report.cascade_depth <= 3


class TestMaliciousSourceLocation:
    """恶意 source_location 注入."""

    def test_path_traversal_attempt(self, tmp_path):
        depgraph = tmp_path / "safe.yaml"
        _write_depgraph(depgraph, {})
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="../../etc/passwd")
        report = analyzer.analyze(finding)
        assert report.risk_level == "LOW"

    def test_null_bytes_in_location(self, tmp_path):
        depgraph = tmp_path / "safe.yaml"
        _write_depgraph(depgraph, {})
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/a.py\x00evil")
        report = analyzer.analyze(finding)
        assert isinstance(report, BlastRadiusReport)

    def test_extremely_long_location(self, tmp_path):
        depgraph = tmp_path / "safe.yaml"
        _write_depgraph(depgraph, {})
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        long_path = "src/zephyr/" + "a/" * 1000 + "x.py"
        finding = _make_finding(source_location=long_path)
        report = analyzer.analyze(finding)
        assert isinstance(report, BlastRadiusReport)

    def test_sql_injection_in_location(self, tmp_path):
        depgraph = tmp_path / "safe.yaml"
        _write_depgraph(depgraph, {})
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="'; DROP TABLE nodes; --")
        report = analyzer.analyze(finding)
        assert isinstance(report, BlastRadiusReport)


class TestCorruptedDepgraph:
    """损坏的 depgraph 数据."""

    def test_node_with_missing_path(self, tmp_path):
        depgraph = tmp_path / "no_path.yaml"
        nodes = {
            "node_a": {
                "id": "node_a",
                "type": "module",
                "imports": ["zephyr.b"],
            },
        }
        _write_depgraph(depgraph, nodes)
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/a.py")
        report = analyzer.analyze(finding)
        assert isinstance(report, BlastRadiusReport)

    def test_node_with_non_dict_value(self, tmp_path):
        depgraph = tmp_path / "bad_node.yaml"
        nodes = {
            "node_a": "not_a_dict",
        }
        _write_depgraph(depgraph, nodes)
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/a.py")
        report = analyzer.analyze(finding)
        assert isinstance(report, BlastRadiusReport)

    def test_imports_not_a_list(self, tmp_path):
        depgraph = tmp_path / "bad_imports.yaml"
        nodes = {
            "node_a": {
                "id": "node_a",
                "path": "src/zephyr/a.py",
                "type": "module",
                "imports": "not_a_list",
            },
        }
        _write_depgraph(depgraph, nodes)
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/a.py")
        report = analyzer.analyze(finding)
        assert isinstance(report, BlastRadiusReport)
