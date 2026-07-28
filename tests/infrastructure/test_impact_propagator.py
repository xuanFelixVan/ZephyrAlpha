# [A_test] module_id: MOD-GOV_impact_propagator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-395 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_impact_propagator
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

from zephyr.infrastructure.impact.impact_propagator import ImpactPath, ImpactPropagator, PropagationReport


class TestImpactPath:
    def test_default_impact_type(self):
        ip = ImpactPath(source_file="a.py", target_file="b.py", path_length=1, intermediate_nodes=[])
        assert ip.impact_type == "direct"

    def test_custom_impact_type(self):
        ip = ImpactPath(
            source_file="a.py", target_file="b.py", path_length=2, intermediate_nodes=["c.py"], impact_type="transitive"
        )
        assert ip.impact_type == "transitive"
        assert ip.path_length == 2
        assert ip.intermediate_nodes == ["c.py"]


class TestPropagationReport:
    def test_fields(self):
        report = PropagationReport(
            task_id="T-001",
            source_files=["a.py"],
            affected_files=["b.py"],
            propagation_depth=1,
            paths=[],
            critical_paths=[],
        )
        assert report.task_id == "T-001"
        assert report.source_files == ["a.py"]
        assert report.affected_files == ["b.py"]
        assert report.propagation_depth == 1


class TestImpactPropagatorInit:
    def test_default_project_root(self):
        prop = ImpactPropagator()
        assert prop.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        prop = ImpactPropagator(project_root=tmp_path)
        assert prop.project_root == tmp_path

    def test_none_project_root(self):
        prop = ImpactPropagator(project_root=None)
        assert prop.project_root == Path.cwd()


class TestAnalyzePropagation:
    def test_basic_propagation(self):
        prop = ImpactPropagator()
        task_card = {
            "task_id": "T-100",
            "downstream_outputs": [{"path": "src/a.py"}, {"path": "src/b.py"}],
            "depends_on": ["dep_x", "dep_y"],
        }
        report = prop.analyze_propagation(task_card)
        assert isinstance(report, PropagationReport)
        assert report.task_id == "T-100"
        assert report.source_files == ["src/a.py", "src/b.py"]
        assert set(report.affected_files) == {"dep_x", "dep_y"}
        assert report.propagation_depth >= 1

    def test_direct_paths_created(self):
        prop = ImpactPropagator()
        task_card = {
            "task_id": "T-101",
            "downstream_outputs": [{"path": "a.py"}],
            "depends_on": ["b.py"],
        }
        report = prop.analyze_propagation(task_card)
        direct_paths = [p for p in report.paths if p.impact_type == "direct"]
        assert len(direct_paths) == 1
        assert direct_paths[0].source_file == "a.py"
        assert direct_paths[0].target_file == "b.py"

    def test_inter_source_paths(self):
        prop = ImpactPropagator()
        task_card = {
            "task_id": "T-102",
            "downstream_outputs": [{"path": "a.py"}, {"path": "b.py"}],
            "depends_on": [],
        }
        report = prop.analyze_propagation(task_card)
        inter = [p for p in report.paths if p.impact_type == "inter_source"]
        assert len(inter) == 2
        pairs = {(p.source_file, p.target_file) for p in inter}
        assert ("a.py", "b.py") in pairs
        assert ("b.py", "a.py") in pairs

    def test_critical_paths_are_short(self):
        prop = ImpactPropagator()
        task_card = {
            "task_id": "T-103",
            "downstream_outputs": [{"path": "a.py"}],
            "depends_on": ["b.py"],
        }
        report = prop.analyze_propagation(task_card)
        for cp in report.critical_paths:
            assert cp.path_length <= 1

    def test_empty_task_card(self):
        prop = ImpactPropagator()
        report = prop.analyze_propagation({})
        assert report.task_id == ""
        assert report.source_files == []
        assert report.affected_files == []
        assert report.paths == []
        assert report.critical_paths == []
        assert report.propagation_depth == 0

    def test_missing_keys_partial(self):
        prop = ImpactPropagator()
        task_card = {"task_id": "T-104"}
        report = prop.analyze_propagation(task_card)
        assert report.task_id == "T-104"
        assert report.source_files == []
        assert report.affected_files == []
        assert report.propagation_depth == 0

    def test_no_depends_on(self):
        prop = ImpactPropagator()
        task_card = {
            "task_id": "T-105",
            "downstream_outputs": [{"path": "a.py"}],
        }
        report = prop.analyze_propagation(task_card)
        direct = [p for p in report.paths if p.impact_type == "direct"]
        assert len(direct) == 0

    def test_downstream_missing_path_key(self):
        prop = ImpactPropagator()
        task_card = {
            "task_id": "T-106",
            "downstream_outputs": [{"path": "a.py"}, {}],
            "depends_on": ["d.py"],
        }
        report = prop.analyze_propagation(task_card)
        assert "" in report.source_files


class TestEstimateBlastRadius:
    def test_basic_calculation(self):
        prop = ImpactPropagator()
        task_card = {
            "downstream_outputs": [{"path": "a.py"}, {"path": "b.py"}],
            "depends_on": ["d1"],
            "blocked_by": ["b1"],
        }
        result = prop.estimate_blast_radius(task_card)
        assert result == 2 * 2 + 1 + 1

    def test_empty_task_card(self):
        prop = ImpactPropagator()
        result = prop.estimate_blast_radius({})
        assert result == 0

    def test_only_downstream(self):
        prop = ImpactPropagator()
        task_card = {"downstream_outputs": [{"path": "a.py"}]}
        result = prop.estimate_blast_radius(task_card)
        assert result == 2

    def test_only_depends_on(self):
        prop = ImpactPropagator()
        task_card = {"depends_on": ["x", "y", "z"]}
        result = prop.estimate_blast_radius(task_card)
        assert result == 3

    def test_only_blocked_by(self):
        prop = ImpactPropagator()
        task_card = {"blocked_by": ["q"]}
        result = prop.estimate_blast_radius(task_card)
        assert result == 1

    def test_large_blast_radius(self):
        prop = ImpactPropagator()
        task_card = {
            "downstream_outputs": [{"path": f"f{i}.py"} for i in range(10)],
            "depends_on": [f"d{i}" for i in range(5)],
            "blocked_by": [f"b{i}" for i in range(3)],
        }
        result = prop.estimate_blast_radius(task_card)
        assert result == 10 * 2 + 5 + 3
