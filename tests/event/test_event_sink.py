# [A_test] module_id: MOD-GOV_event_sink | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] tests.test_event_sink
# [INVARIANTS] ring buffer capped at _EVENT_RING_MAX; ErrorContext validation; AIBehaviorEvent snapshot
# [MODIFY-GUARD] ai_behavior/event_sink.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeatureFlag OFF→noop; ring buffer full→discard oldest
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

es = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.ai_behavior.event_sink",
    reason="event_sink import failed",
)


@pytest.fixture(autouse=True)
def _clear_ring():
    with es._ring_lock:
        es._event_ring.clear()
    yield
    with es._ring_lock:
        es._event_ring.clear()


class TestErrorContext:
    def test_creation(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="transient",
            source="server",
        )
        assert ctx.error_type == "timeout"
        assert ctx.persistence == "transient"
        assert ctx.source == "server"

    def test_snapshot(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="transient",
            source="server",
        )
        snap = ctx.snapshot()
        assert snap["error_type"] == "timeout"
        assert "persistence" in snap
        assert "detail" not in snap


class TestValidateErrorContext:
    def test_valid_context(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="transient",
            source="server",
        )
        issues = es.validate_error_context(ctx)
        assert issues == []

    def test_invalid_persistence(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="invalid",
            source="server",
        )
        issues = es.validate_error_context(ctx)
        assert len(issues) > 0
        assert any("persistence" in i for i in issues)

    def test_invalid_source(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="transient",
            source="invalid",
        )
        issues = es.validate_error_context(ctx)
        assert len(issues) > 0

    def test_invalid_severity(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="transient",
            source="server",
            severity="invalid",
        )
        issues = es.validate_error_context(ctx)
        assert len(issues) > 0

    def test_all_invalid(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="bad",
            source="bad",
            expectation="bad",
            severity="bad",
        )
        issues = es.validate_error_context(ctx)
        assert len(issues) == 4


class TestAIBehaviorEvent:
    def test_creation(self):
        event = es.AIBehaviorEvent(
            model_name="gpt-4",
            task_type="code_gen",
            module_id="test_mod",
        )
        assert event.model_name == "gpt-4"
        assert event.task_type == "code_gen"

    def test_total_tokens(self):
        event = es.AIBehaviorEvent(input_tokens=100, output_tokens=50)
        assert event.total_tokens == 150

    def test_token_efficiency(self):
        event = es.AIBehaviorEvent(input_tokens=100, output_tokens=50)
        assert event.token_efficiency == 0.5

    def test_token_efficiency_zero_input(self):
        event = es.AIBehaviorEvent(input_tokens=0, output_tokens=50)
        assert event.token_efficiency == 0.0

    def test_is_suspicious_clean(self):
        event = es.AIBehaviorEvent(
            input_tokens=100,
            output_tokens=50,
            factual_consistency_score=0.9,
            backtrack_count=0,
        )
        assert event.is_suspicious is False

    def test_is_suspicious_flags(self):
        event = es.AIBehaviorEvent(
            input_tokens=1000,
            output_tokens=10,
            factual_consistency_score=0.5,
            backtrack_count=5,
        )
        assert event.is_suspicious is True

    def test_snapshot(self):
        event = es.AIBehaviorEvent(model_name="gpt-4", task_type="code_gen")
        snap = event.snapshot()
        assert snap["model"]["name"] == "gpt-4"
        assert snap["task"]["type"] == "code_gen"
        assert "event_id" in snap


class TestEmitAIBehaviorEvent:
    def test_emits_event(self):
        event = es.emit_ai_behavior_event(
            model_name="gpt-4",
            task_type="code_gen",
            module_id="test_mod",
        )
        assert isinstance(event, es.AIBehaviorEvent)
        assert event.model_name == "gpt-4"

    def test_appends_to_ring(self):
        es.emit_ai_behavior_event(model_name="gpt-4", task_type="test")
        with es._ring_lock:
            assert len(es._event_ring) >= 1

    def test_ring_cap(self):
        for i in range(es._EVENT_RING_MAX + 50):
            es.emit_ai_behavior_event(model_name=f"model-{i}", task_type="test")
        with es._ring_lock:
            assert len(es._event_ring) <= es._EVENT_RING_MAX


class TestBoundary:
    def test_emit_with_empty_strings(self):
        event = es.emit_ai_behavior_event(
            model_name="",
            task_type="",
            module_id="",
        )
        assert event.model_name == ""

    def test_emit_with_error_context(self):
        ctx = es.ErrorContext(
            error_type="timeout",
            persistence="transient",
            source="server",
        )
        event = es.emit_ai_behavior_event(
            model_name="gpt-4",
            error_context=ctx,
        )
        assert event.error_context is not None

    def test_event_default_id(self):
        event = es.AIBehaviorEvent()
        assert event.event_id != ""
        assert len(event.event_id) > 0
