# [A_test] module_id: SRC-TST-0500 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_causal_inference_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.causal_inference_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_causal_inference_engine.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.diagnosis.causal_inference_engine import (
    CausalGraph,
    CausalInferenceEngine,
)


class TestCausalGraph:
    def test_default_construction(self):
        graph = CausalGraph()
        assert graph.nodes == {}

    def test_custom_nodes(self):
        graph = CausalGraph(nodes={"timeout": ["resource_contention"]})
        assert "timeout" in graph.nodes

    def test_find_root_cause_existing(self):
        graph = CausalGraph(nodes={"timeout": ["resource_contention", "deadlock"]})
        result = graph.find_root_cause("timeout")
        assert result == ["resource_contention", "deadlock"]

    def test_find_root_cause_missing(self):
        graph = CausalGraph()
        result = graph.find_root_cause("unknown_symptom")
        assert result == []

    def test_find_root_cause_empty_list(self):
        graph = CausalGraph(nodes={"timeout": []})
        result = graph.find_root_cause("timeout")
        assert result == []

    def test_find_root_cause_multiple_symptoms(self):
        graph = CausalGraph(
            nodes={
                "timeout": ["resource_contention"],
                "error_spike": ["config_drift"],
            }
        )
        assert graph.find_root_cause("timeout") == ["resource_contention"]
        assert graph.find_root_cause("error_spike") == ["config_drift"]


class TestCausalInferenceEngine:
    def test_instantiation_default(self):
        engine = CausalInferenceEngine()
        assert engine.graph is not None
        assert isinstance(engine.graph, CausalGraph)

    def test_instantiation_custom_graph(self):
        graph = CausalGraph(nodes={"symptom_a": ["root_x"]})
        engine = CausalInferenceEngine(graph=graph)
        assert engine.graph is graph

    def test_infer_returns_list(self):
        engine = CausalInferenceEngine()
        result = engine.infer("symptom", {})
        assert isinstance(result, list)

    def test_infer_with_known_symptom(self):
        graph = CausalGraph(nodes={"latency_spike": ["db_overload"]})
        engine = CausalInferenceEngine(graph=graph)
        result = engine.infer("latency_spike", {"region": "us-east"})
        assert "db_overload" in result

    def test_infer_with_unknown_symptom(self):
        graph = CausalGraph(nodes={"latency_spike": ["db_overload"]})
        engine = CausalInferenceEngine(graph=graph)
        result = engine.infer("unknown_symptom", {})
        assert result == []

    def test_infer_empty_evidence(self):
        graph = CausalGraph(nodes={"symptom": ["cause"]})
        engine = CausalInferenceEngine(graph=graph)
        result = engine.infer("symptom", {})
        assert result == ["cause"]

    def test_infer_evidence_not_used(self):
        graph = CausalGraph(nodes={"symptom": ["cause_a"]})
        engine = CausalInferenceEngine(graph=graph)
        result = engine.infer("symptom", {"extra_key": "extra_value"})
        assert result == ["cause_a"]

    def test_infer_multiple_causes(self):
        graph = CausalGraph(nodes={"symptom": ["cause_a", "cause_b", "cause_c"]})
        engine = CausalInferenceEngine(graph=graph)
        result = engine.infer("symptom", {})
        assert len(result) == 3

    def test_infer_empty_string_symptom(self):
        engine = CausalInferenceEngine()
        result = engine.infer("", {})
        assert result == []

    def test_infer_with_empty_graph(self):
        engine = CausalInferenceEngine(graph=CausalGraph())
        result = engine.infer("anything", {})
        assert result == []
