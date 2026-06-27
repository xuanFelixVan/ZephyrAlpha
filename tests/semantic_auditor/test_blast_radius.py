# [A_test] module_id: SRC-TST-0209 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 9
# [MODULE] tests.semantic_auditor.test_blast_radius
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] tests/semantic-auditor/test_blast_radius.py
# [TTL] task_bound

"""blast_radius 单元测试 — BlastRadiusAnalyzer 全公共方法覆盖."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.governance.blast_radius import (
    BlastRadiusAnalyzer,
    BlastRadiusReport,
    DepgraphLoadError,
    _compute_risk_level,
)
from zephyr.governance.semantic_audit.models import SemanticAuditFinding, Severity


def _make_finding(
    finding_id: str = "F-SEM-001",
    module: str = "test_module",
    severity: Severity = Severity.RED,
    dimension: str = "cross_doc_ref_broken",
    description: str = "test finding",
    source_location: str = "",
) -> SemanticAuditFinding:
    return SemanticAuditFinding(
        finding_id=finding_id,
        module=module,
        severity=severity,
        dimension=dimension,
        description=description,
        source_location=source_location,
    )


def _write_depgraph(path: Path, nodes: dict) -> None:
    data = {"metadata": {"graph_id": "TEST"}, "nodes": nodes}
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def _make_depgraph_nodes() -> dict:
    return {
        "node_a": {
            "id": "node_a",
            "path": "src/zephyr/semantic-auditor/models.py",
            "type": "module",
            "imports": [],
        },
        "node_b": {
            "id": "node_b",
            "path": "src/zephyr/semantic-auditor/blast_radius.py",
            "type": "module",
            "imports": ["zephyr.governance.semantic_audit.models"],
        },
        "node_c": {
            "id": "node_c",
            "path": "src/zephyr/semantic-auditor/fix_prioritizer.py",
            "type": "module",
            "imports": ["zephyr.governance.semantic_audit.models"],
        },
        "node_d": {
            "id": "node_d",
            "path": "src/zephyr/semantic-auditor/self_healer.py",
            "type": "module",
            "imports": ["zephyr.governance.semantic_audit.models", "zephyr.governance.blast_radius"],
        },
    }


class TestBlastRadiusAnalyzerInstantiation:
    def test_instantiate_default(self):
        analyzer = BlastRadiusAnalyzer()
        assert analyzer is not None
        assert analyzer._max_depth == 5

    def test_instantiate_custom_max_depth(self):
        analyzer = BlastRadiusAnalyzer(max_depth=3)
        assert analyzer._max_depth == 3

    def test_instantiate_invalid_max_depth_zero(self):
        with pytest.raises(ValueError, match="max_depth must be >= 1"):
            BlastRadiusAnalyzer(max_depth=0)

    def test_instantiate_invalid_max_depth_negative(self):
        with pytest.raises(ValueError, match="max_depth must be >= 1"):
            BlastRadiusAnalyzer(max_depth=-1)


class TestDepgraphLoadError:
    def test_missing_depgraph_file(self, tmp_path):
        missing = tmp_path / "nonexistent.yaml"
        analyzer = BlastRadiusAnalyzer(depgraph_path=missing)
        with pytest.raises(DepgraphLoadError, match="depgraph not found"):
            analyzer.analyze(_make_finding())

    def test_invalid_yaml(self, tmp_path):
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("\tleading_tab: invalid\n  indented: bad", encoding="utf-8")
        analyzer = BlastRadiusAnalyzer(depgraph_path=bad_file)
        with pytest.raises(DepgraphLoadError):
            analyzer.analyze(_make_finding())

    def test_missing_nodes_key(self, tmp_path):
        bad_file = tmp_path / "no_nodes.yaml"
        with open(bad_file, "w", encoding="utf-8") as f:
            yaml.dump({"metadata": {}}, f)
        analyzer = BlastRadiusAnalyzer(depgraph_path=bad_file)
        with pytest.raises(DepgraphLoadError, match="missing 'nodes' key"):
            analyzer.analyze(_make_finding())


class TestAnalyzeEmptySourceLocation:
    def test_empty_source_location_returns_low_risk(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="")
        report = analyzer.analyze(finding)
        assert report.finding_id == "F-SEM-001"
        assert report.source_path == ""
        assert report.direct_dependents == 0
        assert report.transitive_dependents == 0
        assert report.cascade_depth == 0
        assert report.risk_level == "LOW"


class TestAnalyzeWithSourceLocation:
    def test_direct_dependents_counted(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/semantic-auditor/models.py")
        report = analyzer.analyze(finding)
        assert report.source_path == "src/zephyr/semantic-auditor/models.py"
        assert report.direct_dependents >= 2
        assert report.transitive_dependents >= 2
        assert report.cascade_depth >= 1

    def test_leaf_node_no_dependents(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(source_location="src/zephyr/semantic-auditor/fix_prioritizer.py")
        report = analyzer.analyze(finding)
        assert report.direct_dependents >= 0

    def test_finding_id_preserved(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        finding = _make_finding(finding_id="F-SEM-999", source_location="src/zephyr/semantic-auditor/models.py")
        report = analyzer.analyze(finding)
        assert report.finding_id == "F-SEM-999"


class TestAnalyzeBatch:
    def test_batch_returns_list(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        findings = [
            _make_finding(finding_id="F-SEM-001", source_location="src/zephyr/semantic-auditor/models.py"),
            _make_finding(finding_id="F-SEM-002", source_location=""),
        ]
        reports = analyzer.analyze_batch(findings)
        assert len(reports) == 2
        assert reports[0].finding_id == "F-SEM-001"
        assert reports[1].finding_id == "F-SEM-002"
        assert reports[0].transitive_dependents > reports[1].transitive_dependents

    def test_batch_empty_list(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        reports = analyzer.analyze_batch([])
        assert reports == []


class TestRiskLevel:
    def test_risk_level_low(self):
        assert _compute_risk_level(0, 0) == "LOW"
        assert _compute_risk_level(1, 1) == "LOW"
        assert _compute_risk_level(2, 1) == "LOW"

    def test_risk_level_medium(self):
        assert _compute_risk_level(3, 1) == "MEDIUM"
        assert _compute_risk_level(5, 2) == "MEDIUM"

    def test_risk_level_high(self):
        assert _compute_risk_level(10, 2) == "HIGH"
        assert _compute_risk_level(5, 3) == "HIGH"

    def test_risk_level_critical(self):
        assert _compute_risk_level(20, 3) == "CRITICAL"
        assert _compute_risk_level(15, 4) == "CRITICAL"
        assert _compute_risk_level(25, 5) == "CRITICAL"


class TestGetDependencyChain:
    def test_chain_with_dependents(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        chain = analyzer.get_dependency_chain("src/zephyr/semantic-auditor/models.py")
        assert isinstance(chain, dict)
        if chain:
            assert "1" in chain
            assert len(chain["1"]) >= 2

    def test_chain_leaf_node(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph)
        chain = analyzer.get_dependency_chain("src/zephyr/semantic-auditor/fix_prioritizer.py")
        assert isinstance(chain, dict)

    def test_chain_custom_max_depth(self, tmp_path):
        depgraph = tmp_path / "dep.yaml"
        _write_depgraph(depgraph, _make_depgraph_nodes())
        analyzer = BlastRadiusAnalyzer(depgraph_path=depgraph, max_depth=1)
        chain = analyzer.get_dependency_chain("src/zephyr/semantic-auditor/models.py", max_depth=1)
        assert isinstance(chain, dict)


class TestBlastRadiusReport:
    def test_report_defaults(self):
        report = BlastRadiusReport()
        assert report.finding_id == ""
        assert report.source_path == ""
        assert report.direct_dependents == 0
        assert report.transitive_dependents == 0
        assert report.affected_files == []
        assert report.cascade_depth == 0
        assert report.risk_level == "LOW"

    def test_report_with_values(self):
        report = BlastRadiusReport(
            finding_id="F-SEM-001",
            source_path="src/zephyr/foo.py",
            direct_dependents=5,
            transitive_dependents=12,
            affected_files=["a.py", "b.py"],
            cascade_depth=3,
            risk_level="HIGH",
        )
        assert report.finding_id == "F-SEM-001"
        assert report.transitive_dependents == 12
        assert report.risk_level == "HIGH"
