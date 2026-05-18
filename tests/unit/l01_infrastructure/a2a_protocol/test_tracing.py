# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_tracing
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Tracing"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_tracing import (
    A2ATracing,
    Span,
)


def test_start_span():
    t = A2ATracing()
    span = t.start_span("trace-1", "span-1", "agent-a", "write", "file.py")
    assert isinstance(span, Span)
    assert span.trace_id == "trace-1"
    assert span.span_id == "span-1"
    assert span.agent_id == "agent-a"
    assert span.action == "write"
    assert span.resource == "file.py"


def test_end_span():
    t = A2ATracing()
    span = t.start_span("trace-1", "span-1", "agent-a", "write", "file.py", start_time=100.0)
    t.end_span(span, end_time=105.0)
    assert span.duration == 5.0


def test_get_trace():
    t = A2ATracing()
    t.start_span("trace-1", "span-1", "agent-a", "write", "file.py")
    t.start_span("trace-1", "span-2", "agent-b", "read", "file.py")
    spans = t.get_trace("trace-1")
    assert len(spans) == 2


def test_get_trace_nonexistent():
    t = A2ATracing()
    assert t.get_trace("nonexistent") == []


def test_summary():
    t = A2ATracing()
    t.start_span("trace-1", "span-1", "agent-a", "write", "file.py", start_time=100.0)
    span2 = t.start_span("trace-1", "span-2", "agent-b", "read", "file.py", start_time=101.0)
    t.end_span(span2, end_time=110.0)
    summary = t.summary("trace-1")
    assert summary["trace_id"] == "trace-1"
    assert summary["span_count"] == 2
    assert "agent-a" in summary["agents"]
