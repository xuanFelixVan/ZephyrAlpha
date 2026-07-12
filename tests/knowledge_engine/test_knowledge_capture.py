# [A_test] module_id: SRC-TST-1192 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_knowledge_capture
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.knowledge_capture
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_knowledge_capture.py
# [TTL] task_bound


from zephyr.feedback_loop.collectors.knowledge_capture import KnowledgeCapture


class TestKnowledgeCaptureInstantiation:
    def test_default_captured_is_empty_list(self):
        kc = KnowledgeCapture()
        assert kc.captured == []
        assert isinstance(kc.captured, list)

    def test_captured_is_independent_per_instance(self):
        kc1 = KnowledgeCapture()
        kc2 = KnowledgeCapture()
        kc1.capture({"id": "1"})
        assert len(kc1.captured) == 1
        assert len(kc2.captured) == 0


class TestKnowledgeCaptureCapture:
    def test_capture_appends_diagnosis(self):
        kc = KnowledgeCapture()
        diagnosis = {"anomaly_id": "anom-001", "root_cause": "cpu_spike"}
        kc.capture(diagnosis)
        assert len(kc.captured) == 1
        assert kc.captured[0] == diagnosis

    def test_capture_multiple_diagnoses(self):
        kc = KnowledgeCapture()
        d1 = {"anomaly_id": "anom-001", "root_cause": "cpu_spike"}
        d2 = {"anomaly_id": "anom-002", "root_cause": "mem_leak"}
        kc.capture(d1)
        kc.capture(d2)
        assert len(kc.captured) == 2
        assert kc.captured[0] == d1
        assert kc.captured[1] == d2

    def test_capture_preserves_reference(self):
        kc = KnowledgeCapture()
        diagnosis = {"anomaly_id": "anom-003"}
        kc.capture(diagnosis)
        assert kc.captured[0] is diagnosis

    def test_capture_empty_dict(self):
        kc = KnowledgeCapture()
        kc.capture({})
        assert len(kc.captured) == 1
        assert kc.captured[0] == {}

    def test_capture_dict_with_nested_structure(self):
        kc = KnowledgeCapture()
        diagnosis = {
            "anomaly_id": "anom-004",
            "evidence": {"metric": "cpu", "threshold": 95.0},
            "tags": ["critical", "infra"],
        }
        kc.capture(diagnosis)
        assert kc.captured[0]["evidence"]["threshold"] == 95.0
        assert kc.captured[0]["tags"] == ["critical", "infra"]

    def test_capture_does_not_deduplicate(self):
        kc = KnowledgeCapture()
        diagnosis = {"anomaly_id": "anom-001", "root_cause": "cpu_spike"}
        kc.capture(diagnosis)
        kc.capture(diagnosis)
        assert len(kc.captured) == 2
