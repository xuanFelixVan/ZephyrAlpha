# [A_test] module_id: MOD-GOV_trace_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_trace_bridge
# [INVARIANTS] getter returns None if unset; writer returns False if unset
# [MODIFY-GUARD] _trace_bridge.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None return when unset; False return when writer unset
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

tb = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.trace_bridge",
    reason="_trace_bridge import failed",
)


@pytest.fixture(autouse=True)
def _reset_bridge():
    tb.span_context_getter = None
    tb.record_writer = None
    yield
    tb.span_context_getter = None
    tb.record_writer = None


class TestSpanContextGetter:
    def test_get_current_span_unset(self):
        result = tb.get_current_span()
        assert result is None

    def test_set_and_get(self):
        tb.set_span_context_getter(lambda: "span_ctx")
        assert tb.get_current_span() == "span_ctx"

    def test_overwrite(self):
        tb.set_span_context_getter(lambda: "first")
        tb.set_span_context_getter(lambda: "second")
        assert tb.get_current_span() == "second"


class TestRecordWriter:
    def test_write_record_unset(self):
        result = tb.write_record({"key": "value"})
        assert result is False

    def test_set_and_write(self):
        tb.set_record_writer(lambda data, labels: True)
        result = tb.write_record({"key": "value"})
        assert result is True

    def test_write_with_labels(self):
        captured = {}

        def _writer(data, labels):
            captured["data"] = data
            captured["labels"] = labels
            return True

        tb.set_record_writer(_writer)
        tb.write_record({"k": "v"}, labels={"type": "test"})
        assert captured["data"] == {"k": "v"}
        assert captured["labels"] == {"type": "test"}

    def test_writer_returns_false(self):
        tb.set_record_writer(lambda data, labels: False)
        result = tb.write_record({"key": "value"})
        assert result is False


class TestBoundary:
    def test_write_record_empty_data(self):
        tb.set_record_writer(lambda data, labels: True)
        result = tb.write_record({})
        assert result is True

    def test_write_record_none_labels(self):
        tb.set_record_writer(lambda data, labels: True)
        result = tb.write_record({"k": "v"}, labels=None)
        assert result is True

    def test_getter_raises(self):
        def _raising():
            raise RuntimeError("no span")

        tb.set_span_context_getter(_raising)
        with pytest.raises(RuntimeError, match="no span"):
            tb.get_current_span()
