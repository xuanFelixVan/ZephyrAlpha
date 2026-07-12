# [A_test] module_id: SRC-TST-1757 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_trace_causal_bridge
# [INVARIANTS] TraceCausalBridge.spans is list[dict]; bridge appends span
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_trace_causal_bridge.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.trace_causal_bridge import TraceCausalBridge


class TestTraceCausalBridgeInstantiation:
    def test_default_spans_empty(self):
        obj = TraceCausalBridge()
        assert obj.spans == []

    def test_custom_spans(self):
        initial = [{"span_id": "s1", "service": "svc-a"}]
        obj = TraceCausalBridge(spans=initial)
        assert obj.spans == initial

    def test_spans_is_list_type(self):
        obj = TraceCausalBridge()
        assert isinstance(obj.spans, list)


class TestTraceCausalBridgeBridge:
    def test_bridge_appends_span(self):
        obj = TraceCausalBridge()
        obj.bridge({"span_id": "s1", "service": "svc-a"})
        assert len(obj.spans) == 1
        assert obj.spans[0]["span_id"] == "s1"

    def test_bridge_multiple_spans(self):
        obj = TraceCausalBridge()
        obj.bridge({"span_id": "s1"})
        obj.bridge({"span_id": "s2"})
        obj.bridge({"span_id": "s3"})
        assert len(obj.spans) == 3

    def test_bridge_preserves_order(self):
        obj = TraceCausalBridge()
        obj.bridge({"order": 1})
        obj.bridge({"order": 2})
        assert obj.spans[0]["order"] == 1
        assert obj.spans[1]["order"] == 2

    def test_bridge_empty_dict(self):
        obj = TraceCausalBridge()
        obj.bridge({})
        assert len(obj.spans) == 1
        assert obj.spans[0] == {}

    def test_bridge_nested_dict(self):
        obj = TraceCausalBridge()
        span = {"span_id": "s1", "context": {"trace_id": "t1", "parent": None}}
        obj.bridge(span)
        assert obj.spans[0]["context"]["trace_id"] == "t1"

    def test_separate_instances_independent(self):
        a = TraceCausalBridge()
        b = TraceCausalBridge()
        a.bridge({"id": "a1"})
        assert len(b.spans) == 0
