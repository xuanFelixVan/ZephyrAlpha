# [A_test] module_id: MOD-GOV_a2a_tracing | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_tracing
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_tracing",
    reason="a2a_tracing module not available",
)


class TestA2ATracing:
    def test_instantiation(self):
        obj = mod.A2ATracing()
        assert obj is not None

    def test_start_span(self):
        obj = mod.A2ATracing()
        now = time.time()
        span = obj.start_span("trace_1", "span_1", "agent1", "read", "file.py", parent_span_id=None, start_time=now)
        assert span is not None

    def test_end_span(self):
        obj = mod.A2ATracing()
        now = time.time()
        span = obj.start_span("trace_1", "span_1", "agent1", "read", "file.py", None, now)
        obj.end_span(span, time.time())

    def test_get_trace(self):
        obj = mod.A2ATracing()
        now = time.time()
        obj.start_span("trace_1", "span_1", "agent1", "read", "file.py", None, now)
        result = obj.get_trace("trace_1")
        assert isinstance(result, list)

    def test_summary(self):
        obj = mod.A2ATracing()
        now = time.time()
        span = obj.start_span("trace_1", "span_1", "agent1", "read", "file.py", None, now)
        obj.end_span(span, time.time())
        result = obj.summary("trace_1")
        assert isinstance(result, dict)

    def test_get_trace_nonexistent(self):
        obj = mod.A2ATracing()
        result = obj.get_trace("nonexistent")
        assert isinstance(result, list)


class TestSpan:
    def test_duration(self):
        span = mod.Span(
            span_id="s1",
            trace_id="t1",
            parent_span_id=None,
            agent_id="a1",
            action="read",
            resource="file.py",
            start_time=time.time(),
            end_time=time.time() + 1.0,
        )
        dur = span.duration
        assert isinstance(dur, float)
