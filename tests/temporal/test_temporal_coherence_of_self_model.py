# [A_test] module_id: SRC-TST-1731 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_temporal_coherence_of_self_model
# [INVARIANTS] check_coherence needs >=2 snapshots; coherence = avg of cap/limit/health similarity
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_temporal_coherence_of_self_model.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.temporal_coherence_of_self_model import (
    SelfModelSnapshot,
    TemporalCoherenceOfSelfModel,
)


class TestSelfModelSnapshot:
    def test_instantiation(self):
        snap = SelfModelSnapshot(
            timestamp=1000.0,
            capabilities={"cpu": 0.9},
            limits={"max_rps": 1000.0},
            health_score=0.95,
        )
        assert snap.timestamp == 1000.0
        assert snap.capabilities == {"cpu": 0.9}
        assert snap.limits == {"max_rps": 1000.0}
        assert snap.health_score == 0.95

    def test_default_hash(self):
        snap = SelfModelSnapshot(timestamp=0.0, capabilities={}, limits={}, health_score=0.0)
        assert snap.hash == ""


class TestTemporalCoherenceOfSelfModelInstantiation:
    def test_default_params(self):
        obj = TemporalCoherenceOfSelfModel()
        assert obj.snapshots == []
        assert obj.max_snapshots == 30
        assert obj.coherence_threshold == 0.7

    def test_custom_params(self):
        obj = TemporalCoherenceOfSelfModel(max_snapshots=10, coherence_threshold=0.5)
        assert obj.max_snapshots == 10
        assert obj.coherence_threshold == 0.5


class TestTemporalCoherenceOfSelfModelRecordSnapshot:
    def test_record_returns_hash(self):
        obj = TemporalCoherenceOfSelfModel()
        h = obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        assert isinstance(h, str)
        assert len(h) > 0

    def test_record_appends_snapshot(self):
        obj = TemporalCoherenceOfSelfModel()
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        assert len(obj.snapshots) == 1

    def test_record_multiple_snapshots(self):
        obj = TemporalCoherenceOfSelfModel()
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        obj.record_snapshot({"cpu": 0.8}, {"max_rps": 900.0}, 0.90)
        assert len(obj.snapshots) == 2

    def test_record_trims_to_max_snapshots(self):
        obj = TemporalCoherenceOfSelfModel(max_snapshots=3)
        for i in range(5):
            obj.record_snapshot({"v": float(i)}, {"l": float(i)}, float(i) / 10.0)
        assert len(obj.snapshots) == 3

    def test_record_same_data_same_hash(self):
        obj = TemporalCoherenceOfSelfModel()
        h1 = obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        h2 = obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        assert h1 == h2


class TestTemporalCoherenceOfSelfModelCheckCoherence:
    def test_insufficient_data(self):
        obj = TemporalCoherenceOfSelfModel()
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        result = obj.check_coherence()
        assert result["status"] == "insufficient_data"
        assert result["coherence_score"] == 1.0

    def test_coherent_snapshots(self):
        obj = TemporalCoherenceOfSelfModel()
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        obj.record_snapshot({"cpu": 0.91}, {"max_rps": 1005.0}, 0.96)
        result = obj.check_coherence()
        assert result["status"] == "normal"
        assert result["coherence_score"] > obj.coherence_threshold

    def test_divergent_capabilities(self):
        obj = TemporalCoherenceOfSelfModel(coherence_threshold=0.7)
        obj.record_snapshot({"cpu": 0.9, "mem": 0.8}, {"max_rps": 1000.0}, 0.95)
        obj.record_snapshot({"cpu": 0.1, "mem": 0.1}, {"max_rps": 1000.0}, 0.95)
        result = obj.check_coherence()
        assert "capability_drift" in result["inconsistencies"]

    def test_divergent_limits(self):
        obj = TemporalCoherenceOfSelfModel(coherence_threshold=0.7)
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0, "max_conn": 500.0}, 0.95)
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 100.0, "max_conn": 50.0}, 0.95)
        result = obj.check_coherence()
        assert "limit_drift" in result["inconsistencies"]

    def test_health_score_jump(self):
        obj = TemporalCoherenceOfSelfModel(coherence_threshold=0.7)
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.1)
        result = obj.check_coherence()
        assert "health_score_jump" in result["inconsistencies"]

    def test_critical_severity_multiple_inconsistencies(self):
        obj = TemporalCoherenceOfSelfModel(coherence_threshold=0.7)
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        obj.record_snapshot({"cpu": 0.1}, {"max_rps": 100.0}, 0.1)
        result = obj.check_coherence()
        assert result["status"] == "critical"

    def test_result_has_hash_fields(self):
        obj = TemporalCoherenceOfSelfModel()
        obj.record_snapshot({"cpu": 0.9}, {"max_rps": 1000.0}, 0.95)
        obj.record_snapshot({"cpu": 0.91}, {"max_rps": 1005.0}, 0.96)
        result = obj.check_coherence()
        assert "previous_hash" in result
        assert "current_hash" in result


class TestTemporalCoherenceComputeDictSimilarity:
    def test_identical_dicts(self):
        result = TemporalCoherenceOfSelfModel._compute_dict_similarity({"a": 1.0, "b": 2.0}, {"a": 1.0, "b": 2.0})
        assert result == 1.0

    def test_empty_dicts(self):
        result = TemporalCoherenceOfSelfModel._compute_dict_similarity({}, {})
        assert result == 1.0

    def test_completely_different(self):
        result = TemporalCoherenceOfSelfModel._compute_dict_similarity({"a": 100.0}, {"a": 1.0})
        assert result < 0.5

    def test_one_empty_one_not(self):
        result = TemporalCoherenceOfSelfModel._compute_dict_similarity({"a": 1.0}, {})
        assert result < 1.0
