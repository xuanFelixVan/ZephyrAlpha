# [A_test] module_id: SRC-TST-0428 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_blast_radius_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_blast_radius_detector.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.blast_radius import BlastRadius


class TestBlastRadiusInstantiation:
    def test_default_construction(self):
        br = BlastRadius()
        assert br.dependency_graph == {}

    def test_with_initial_graph(self):
        graph = {"service_a": ["service_b", "service_c"]}
        br = BlastRadius(dependency_graph=graph)
        assert "service_a" in br.dependency_graph


class TestEstimate:
    def test_unknown_target_returns_empty(self):
        br = BlastRadius()
        assert br.estimate("unknown") == []

    def test_known_target_returns_deps(self):
        graph = {"service_a": ["service_b", "service_c"]}
        br = BlastRadius(dependency_graph=graph)
        result = br.estimate("service_a")
        assert result == ["service_b", "service_c"]

    def test_target_with_no_deps(self):
        graph = {"service_a": []}
        br = BlastRadius(dependency_graph=graph)
        assert br.estimate("service_a") == []

    def test_multiple_targets(self):
        graph = {
            "service_a": ["service_b"],
            "service_b": ["service_c"],
        }
        br = BlastRadius(dependency_graph=graph)
        assert br.estimate("service_a") == ["service_b"]
        assert br.estimate("service_b") == ["service_c"]

    def test_empty_graph(self):
        br = BlastRadius(dependency_graph={})
        assert br.estimate("anything") == []

    def test_graph_mutation_after_construction(self):
        br = BlastRadius()
        br.dependency_graph["service_x"] = ["service_y"]
        assert br.estimate("service_x") == ["service_y"]
