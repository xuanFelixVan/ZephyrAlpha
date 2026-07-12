# [A_test] module_id: SRC-TST-1738 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_thematic_clusterer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_thematic_clusterer.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.thematic_clusterer import ThematicClusterer


class TestThematicClusterer:
    def test_instantiation(self):
        tc = ThematicClusterer()
        assert tc is not None

    def test_cluster_empty(self):
        tc = ThematicClusterer()
        result = tc.cluster([])
        assert result["total_clustered"] == 0
        assert result["noise_ratio"] == 0.0

    def test_cluster_test_patterns(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("tests/test_a.py", ""), ("tests/test_b.py", "")]},
            {"members": [("tests/test_c.py", ""), ("tests/test_d.py", "")]},
        ]
        result = tc.cluster(groups)
        assert "Test Patterns" in result["themes"]
        assert result["total_clustered"] == 2

    def test_cluster_shared_library(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("src/shared/utils.py", ""), ("src/shared/helpers.py", "")]},
        ]
        result = tc.cluster(groups)
        assert "Shared Library" in result["themes"]

    def test_cluster_infrastructure(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("src/l01-infrastructure/engine.py", ""), ("src/l01-infrastructure/scanner.py", "")]},
        ]
        result = tc.cluster(groups)
        assert "Infrastructure" in result["themes"]

    def test_cluster_pipeline(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("src/pipeline/step1.py", ""), ("src/workflow/step2.py", "")]},
        ]
        result = tc.cluster(groups)
        assert "Pipeline" in result["themes"]

    def test_cluster_general(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("src/utils/a.py", ""), ("src/utils/b.py", "")]},
        ]
        result = tc.cluster(groups)
        assert "General" in result["themes"]

    def test_cluster_max_clusters(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("tests/a.py", "")]},
            {"members": [("shared/b.py", "")]},
            {"members": [("l01-infrastructure/c.py", "")]},
            {"members": [("pipeline/d.py", "")]},
            {"members": [("other/e.py", "")]},
            {"members": [("another/f.py", "")]},
        ]
        result = tc.cluster(groups, max_clusters=3)
        assert len(result["themes"]) <= 3

    def test_cluster_noise_ratio(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("tests/a.py", "")]},
            {"members": [("random/x.py", "")]},
            {"members": [("random/y.py", "")]},
            {"members": [("random/z.py", "")]},
            {"members": [("random/w.py", "")]},
        ]
        result = tc.cluster(groups, max_clusters=1)
        assert result["noise_ratio"] >= 0.0
        assert result["noise_ratio"] <= 1.0

    def test_cluster_recommendation(self):
        tc = ThematicClusterer()
        groups = [
            {"members": [("tests/a.py", "")]},
            {"members": [("tests/b.py", "")]},
        ]
        result = tc.cluster(groups)
        assert "themes cover" in result["recommendation"]

    def test_classify_static(self):
        assert ThematicClusterer._classify(["tests/a.py"]) == "Test Patterns"
        assert ThematicClusterer._classify(["shared/b.py"]) == "Shared Library"
        assert ThematicClusterer._classify(["l01-infrastructure/c.py"]) == "Infrastructure"
        assert ThematicClusterer._classify(["pipeline/d.py"]) == "Pipeline"
        assert ThematicClusterer._classify(["random/x.py"]) == "General"
