# [A_test] module_id: SRC-TST-0317 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_anomaly_clustering
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_anomaly_clustering.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.anomaly_clustering import AnomalyClustering


class TestAnomalyClusteringInstantiation:
    def test_default_construction(self):
        ac = AnomalyClustering()
        assert ac.clusters == {}

    def test_with_initial_clusters(self):
        ac = AnomalyClustering(clusters={"g1": ["a1", "a2"]})
        assert "g1" in ac.clusters


class TestCluster:
    def test_empty_anomalies(self):
        ac = AnomalyClustering()
        result = ac.cluster([])
        assert result == {"default": []}

    def test_single_anomaly(self):
        ac = AnomalyClustering()
        result = ac.cluster([{"id": "anom_1"}])
        assert result == {"default": ["anom_1"]}

    def test_multiple_anomalies(self):
        ac = AnomalyClustering()
        anomalies = [{"id": "anom_1"}, {"id": "anom_2"}, {"id": "anom_3"}]
        result = ac.cluster(anomalies)
        assert result["default"] == ["anom_1", "anom_2", "anom_3"]

    def test_missing_id_key(self):
        ac = AnomalyClustering()
        result = ac.cluster([{"type": "cpu_spike"}])
        assert result["default"] == [""]

    def test_preserves_order(self):
        ac = AnomalyClustering()
        anomalies = [{"id": "c"}, {"id": "a"}, {"id": "b"}]
        result = ac.cluster(anomalies)
        assert result["default"] == ["c", "a", "b"]
