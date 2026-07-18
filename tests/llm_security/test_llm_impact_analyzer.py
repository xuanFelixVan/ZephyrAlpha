# [A_test] module_id: SRC-TST-1234 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-403 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_llm_impact_analyzer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.impact.llm_impact_analyzer import (
    DependencyCluster,
    ImpactAssessment,
    LLMImpactAnalyzer,
)


class TestImpactAssessment:
    def test_defaults(self):
        ia = ImpactAssessment(
            task_id="T-001",
            files_affected=["a.py"],
            risk_level="LOW",
            blast_radius=1,
        )
        assert ia.requires_rollback_sim is False
        assert ia.recommendation == ""

    def test_custom_fields(self):
        ia = ImpactAssessment(
            task_id="T-002",
            files_affected=["a.py", "b.py"],
            risk_level="CRITICAL",
            blast_radius=12,
            requires_rollback_sim=True,
            recommendation="Run rollback simulation",
        )
        assert ia.requires_rollback_sim is True
        assert ia.recommendation == "Run rollback simulation"


class TestDependencyCluster:
    def test_fields(self):
        dc = DependencyCluster(
            cluster_id="CLUSTER-1",
            tasks=["T-001"],
            shared_files=["a.py"],
            cluster_risk="LOW",
        )
        assert dc.cluster_id == "CLUSTER-1"
        assert dc.tasks == ["T-001"]


class TestLLMImpactAnalyzerInit:
    def test_default_project_root(self):
        analyzer = LLMImpactAnalyzer()
        assert analyzer._project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        assert analyzer._project_root == tmp_path

    def test_none_project_root(self):
        analyzer = LLMImpactAnalyzer(project_root=None)
        assert analyzer._project_root == Path.cwd()


class TestAnalyzeImpact:
    def test_low_risk(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-200",
            "downstream_outputs": [{"path": "a.py"}],
            "depends_on": [],
            "blocked_by": [],
        }
        result = analyzer.analyze_impact(task_card)
        assert isinstance(result, ImpactAssessment)
        assert result.task_id == "T-200"
        assert result.risk_level == "LOW"
        assert result.blast_radius == 1
        assert result.requires_rollback_sim is False
        assert "Safe to execute" in result.recommendation

    def test_medium_risk(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-201",
            "downstream_outputs": [{"path": f"f{i}.py"} for i in range(3)],
            "depends_on": [],
            "blocked_by": [],
        }
        result = analyzer.analyze_impact(task_card)
        assert result.risk_level == "MEDIUM"
        assert result.blast_radius == 3

    def test_high_risk(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-202",
            "downstream_outputs": [{"path": f"f{i}.py"} for i in range(4)],
            "depends_on": ["d1", "d2"],
            "blocked_by": [],
        }
        result = analyzer.analyze_impact(task_card)
        assert result.risk_level == "HIGH"
        assert result.blast_radius == 6

    def test_critical_risk(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-203",
            "downstream_outputs": [{"path": f"f{i}.py"} for i in range(8)],
            "depends_on": ["d1", "d2", "d3"],
            "blocked_by": ["b1"],
        }
        result = analyzer.analyze_impact(task_card)
        assert result.risk_level == "CRITICAL"
        assert result.blast_radius == 12
        assert result.requires_rollback_sim is True
        assert "rollback simulation" in result.recommendation

    def test_empty_task_card(self):
        analyzer = LLMImpactAnalyzer()
        result = analyzer.analyze_impact({})
        assert result.task_id == ""
        assert result.files_affected == []
        assert result.risk_level == "LOW"
        assert result.blast_radius == 0

    def test_boundary_blast_radius_2(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-204",
            "downstream_outputs": [{"path": "a.py"}, {"path": "b.py"}],
            "depends_on": [],
            "blocked_by": [],
        }
        result = analyzer.analyze_impact(task_card)
        assert result.blast_radius == 2
        assert result.risk_level == "LOW"

    def test_boundary_blast_radius_3(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-205",
            "downstream_outputs": [{"path": "a.py"}, {"path": "b.py"}, {"path": "c.py"}],
            "depends_on": [],
            "blocked_by": [],
        }
        result = analyzer.analyze_impact(task_card)
        assert result.blast_radius == 3
        assert result.risk_level == "MEDIUM"

    def test_boundary_blast_radius_6(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-206",
            "downstream_outputs": [{"path": f"f{i}.py"} for i in range(4)],
            "depends_on": ["d1", "d2"],
            "blocked_by": [],
        }
        result = analyzer.analyze_impact(task_card)
        assert result.blast_radius == 6
        assert result.risk_level == "HIGH"

    def test_boundary_blast_radius_11(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-207",
            "downstream_outputs": [{"path": f"f{i}.py"} for i in range(9)],
            "depends_on": ["d1", "d2"],
            "blocked_by": [],
        }
        result = analyzer.analyze_impact(task_card)
        assert result.blast_radius == 11
        assert result.risk_level == "CRITICAL"

    def test_downstream_missing_path_key(self):
        analyzer = LLMImpactAnalyzer()
        task_card = {
            "task_id": "T-208",
            "downstream_outputs": [{"path": "a.py"}, {}],
        }
        result = analyzer.analyze_impact(task_card)
        assert "" in result.files_affected


class TestComputeFileSimilarity:
    def test_identical_files(self, tmp_path):
        content = "line1\nline2\nline3\n"
        fa = tmp_path / "a.py"
        fb = tmp_path / "b.py"
        fa.write_text(content, encoding="utf-8")
        fb.write_text(content, encoding="utf-8")
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        result = analyzer.compute_file_similarity("a.py", "b.py")
        assert result == 1.0

    def test_completely_different_files(self, tmp_path):
        fa = tmp_path / "a.py"
        fb = tmp_path / "b.py"
        fa.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
        fb.write_text("delta\nepsilon\nzeta\n", encoding="utf-8")
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        result = analyzer.compute_file_similarity("a.py", "b.py")
        assert result == 0.0

    def test_partial_overlap(self, tmp_path):
        fa = tmp_path / "a.py"
        fb = tmp_path / "b.py"
        fa.write_text("shared\nonly_a\n", encoding="utf-8")
        fb.write_text("shared\nonly_b\n", encoding="utf-8")
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        result = analyzer.compute_file_similarity("a.py", "b.py")
        assert 0.0 < result < 1.0
        expected = 1 / 3
        assert abs(result - expected) < 1e-9

    def test_nonexistent_file_a(self, tmp_path):
        fb = tmp_path / "b.py"
        fb.write_text("content\n", encoding="utf-8")
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        result = analyzer.compute_file_similarity("nonexistent.py", "b.py")
        assert result == 0.0

    def test_nonexistent_file_b(self, tmp_path):
        fa = tmp_path / "a.py"
        fa.write_text("content\n", encoding="utf-8")
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        result = analyzer.compute_file_similarity("a.py", "nonexistent.py")
        assert result == 0.0

    def test_both_nonexistent(self, tmp_path):
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        result = analyzer.compute_file_similarity("x.py", "y.py")
        assert result == 0.0

    def test_empty_file_returns_zero(self, tmp_path):
        fa = tmp_path / "a.py"
        fb = tmp_path / "b.py"
        fa.write_text("", encoding="utf-8")
        fb.write_text("content\n", encoding="utf-8")
        analyzer = LLMImpactAnalyzer(project_root=tmp_path)
        result = analyzer.compute_file_similarity("a.py", "b.py")
        assert result == 0.0


class TestClusterDependencies:
    def test_single_task(self):
        analyzer = LLMImpactAnalyzer()
        tasks = [
            {"task_id": "T-300", "downstream_outputs": [{"path": "a.py"}]},
        ]
        clusters = analyzer.cluster_dependencies(tasks)
        assert len(clusters) == 1
        assert clusters[0].cluster_id == "CLUSTER-1"
        assert clusters[0].tasks == ["T-300"]
        assert clusters[0].shared_files == ["a.py"]
        assert clusters[0].cluster_risk == "LOW"

    def test_merging_shared_files(self):
        analyzer = LLMImpactAnalyzer()
        tasks = [
            {"task_id": "T-301", "downstream_outputs": [{"path": "shared.py"}, {"path": "a.py"}]},
            {"task_id": "T-302", "downstream_outputs": [{"path": "shared.py"}, {"path": "b.py"}]},
        ]
        clusters = analyzer.cluster_dependencies(tasks)
        assert len(clusters) == 1
        assert "T-301" in clusters[0].tasks
        assert "T-302" in clusters[0].tasks
        assert clusters[0].cluster_risk == "MEDIUM"

    def test_separate_clusters(self):
        analyzer = LLMImpactAnalyzer()
        tasks = [
            {"task_id": "T-303", "downstream_outputs": [{"path": "a.py"}]},
            {"task_id": "T-304", "downstream_outputs": [{"path": "b.py"}]},
        ]
        clusters = analyzer.cluster_dependencies(tasks)
        assert len(clusters) == 2

    def test_empty_tasks_list(self):
        analyzer = LLMImpactAnalyzer()
        clusters = analyzer.cluster_dependencies([])
        assert clusters == []

    def test_task_with_empty_downstream(self):
        analyzer = LLMImpactAnalyzer()
        tasks = [
            {"task_id": "T-305", "downstream_outputs": []},
        ]
        clusters = analyzer.cluster_dependencies(tasks)
        assert len(clusters) == 1
        assert clusters[0].shared_files == []

    def test_critical_cluster_risk(self):
        analyzer = LLMImpactAnalyzer()
        tasks = [{"task_id": f"T-{i}", "downstream_outputs": [{"path": "shared.py"}]} for i in range(6)]
        clusters = analyzer.cluster_dependencies(tasks)
        assert len(clusters) == 1
        assert clusters[0].cluster_risk == "CRITICAL"

    def test_high_cluster_risk(self):
        analyzer = LLMImpactAnalyzer()
        tasks = [{"task_id": f"T-{i}", "downstream_outputs": [{"path": "shared.py"}]} for i in range(4)]
        clusters = analyzer.cluster_dependencies(tasks)
        assert len(clusters) == 1
        assert clusters[0].cluster_risk == "HIGH"

    def test_task_missing_task_id(self):
        analyzer = LLMImpactAnalyzer()
        tasks = [
            {"downstream_outputs": [{"path": "a.py"}]},
        ]
        clusters = analyzer.cluster_dependencies(tasks)
        assert len(clusters) == 1
        assert clusters[0].tasks == [""]
