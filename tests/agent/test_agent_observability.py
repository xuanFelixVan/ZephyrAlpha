# [A_test] module_id: SRC-TST-0288 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_agent_observability
# [INVARIANTS] AgentObservability traces keyed by trace_id; add_span raises KeyError for unknown trace
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] KeyError on add_span with invalid trace_id; empty dict on get_trace with unknown id
# [TESTS] pytest tests/test_agent_observability.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.agent_observability import AgentObservability


class TestAgentObservabilityInit:
    def test_instantiation_creates_empty_traces(self):
        obs = AgentObservability()
        assert obs._traces == {}

    def test_instantiation_traces_is_dict(self):
        obs = AgentObservability()
        assert isinstance(obs._traces, dict)


class TestStartTrace:
    def test_start_trace_returns_trace_id(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-abc")
        assert isinstance(trace_id, str)
        assert "skill-abc" in trace_id

    def test_start_trace_creates_trace_entry(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-xyz")
        trace = obs._traces[trace_id]
        assert trace["skill_id"] == "skill-xyz"
        assert isinstance(trace["spans"], list)
        assert len(trace["spans"]) == 0
        assert "start_time" in trace

    def test_start_trace_multiple_traces(self):
        obs = AgentObservability()
        tid1 = obs.start_trace("skill-a")
        tid2 = obs.start_trace("skill-b")
        assert tid1 != tid2
        assert len(obs._traces) == 2

    def test_start_trace_with_empty_skill_id(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("")
        assert isinstance(trace_id, str)
        assert trace_id.startswith("trace--")


class TestAddSpan:
    def test_add_span_returns_span_dict(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-test")
        span = obs.add_span(trace_id, "span-1")
        assert span["name"] == "span-1"
        assert "timestamp" in span
        assert isinstance(span["metadata"], dict)

    def test_add_span_with_metadata(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-test")
        meta = {"key": "value", "count": 42}
        span = obs.add_span(trace_id, "span-meta", metadata=meta)
        assert span["metadata"] == meta

    def test_add_span_with_none_metadata_defaults_empty(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-test")
        span = obs.add_span(trace_id, "span-none", metadata=None)
        assert span["metadata"] == {}

    def test_add_span_appends_to_spans_list(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-test")
        obs.add_span(trace_id, "span-1")
        obs.add_span(trace_id, "span-2")
        obs.add_span(trace_id, "span-3")
        assert len(obs._traces[trace_id]["spans"]) == 3

    def test_add_span_raises_keyerror_for_unknown_trace(self):
        obs = AgentObservability()
        with pytest.raises(KeyError, match="Trace not found"):
            obs.add_span("nonexistent-trace-id", "span-x")

    def test_add_span_empty_name(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-test")
        span = obs.add_span(trace_id, "")
        assert span["name"] == ""


class TestGetTrace:
    def test_get_trace_returns_trace_data(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-test")
        trace = obs.get_trace(trace_id)
        assert trace["skill_id"] == "skill-test"
        assert "spans" in trace

    def test_get_trace_returns_empty_dict_for_unknown(self):
        obs = AgentObservability()
        result = obs.get_trace("does-not-exist")
        assert result == {}

    def test_get_trace_reflects_added_spans(self):
        obs = AgentObservability()
        trace_id = obs.start_trace("skill-test")
        obs.add_span(trace_id, "span-a", metadata={"x": 1})
        trace = obs.get_trace(trace_id)
        assert len(trace["spans"]) == 1
        assert trace["spans"][0]["name"] == "span-a"
        assert trace["spans"][0]["metadata"]["x"] == 1
