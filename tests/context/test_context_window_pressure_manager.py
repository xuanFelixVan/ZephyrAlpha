# [A_test] module_id: SRC-TST-0612 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_context_window_pressure_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.context_window_pressure_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_context_window_pressure_manager.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.context_window_pressure_manager import (
    ContextEntry,
    ContextWindowPressureManager,
)


class TestContextEntry:
    def test_fields(self):
        ce = ContextEntry(content="test", priority=1.0, timestamp=0.0, source="src", token_estimate=10)
        assert ce.content == "test"
        assert ce.priority == 1.0
        assert ce.timestamp == 0.0
        assert ce.source == "src"
        assert ce.token_estimate == 10


class TestContextWindowPressureManagerInstantiation:
    def test_default_params(self):
        cwpm = ContextWindowPressureManager()
        assert cwpm.max_window_tokens == 8000
        assert cwpm.pressure_threshold == 0.7
        assert cwpm.max_entries == 100
        assert cwpm.compress_ratio == 0.5
        assert cwpm.entries == []


class TestContextWindowPressureManagerAddEntry:
    def test_add_entry_increases_count(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("content", priority=1.0, source="test", token_estimate=100)
        assert len(cwpm.entries) == 1

    def test_add_multiple_entries(self):
        cwpm = ContextWindowPressureManager()
        for i in range(5):
            cwpm.add_entry(f"c{i}", priority=1.0, source="s", token_estimate=100)
        assert len(cwpm.entries) == 5

    def test_add_entry_trims_at_max(self):
        cwpm = ContextWindowPressureManager(max_entries=3)
        for i in range(5):
            cwpm.add_entry(f"c{i}", priority=1.0, source="s", token_estimate=100)
        assert len(cwpm.entries) == 3


class TestContextWindowPressureManagerCheckPressure:
    def test_normal_pressure(self):
        cwpm = ContextWindowPressureManager(max_window_tokens=10000)
        cwpm.add_entry("c", priority=1.0, source="s", token_estimate=1000)
        result = cwpm.check_pressure()
        assert result["status"] == "normal"
        assert result["needs_compression"] is False

    def test_pressured_status(self):
        cwpm = ContextWindowPressureManager(max_window_tokens=1000, pressure_threshold=0.7)
        cwpm.add_entry("c", priority=1.0, source="s", token_estimate=750)
        result = cwpm.check_pressure()
        assert result["status"] == "pressured"
        assert result["needs_compression"] is True

    def test_critical_status(self):
        cwpm = ContextWindowPressureManager(max_window_tokens=1000)
        cwpm.add_entry("c", priority=1.0, source="s", token_estimate=950)
        result = cwpm.check_pressure()
        assert result["status"] == "critical"

    def test_empty_entries_normal(self):
        cwpm = ContextWindowPressureManager()
        result = cwpm.check_pressure()
        assert result["status"] == "normal"
        assert result["total_tokens"] == 0


class TestContextWindowPressureManagerCompress:
    def test_compress_removes_entries(self):
        cwpm = ContextWindowPressureManager(max_window_tokens=1000, pressure_threshold=0.5, compress_ratio=0.5)
        for i in range(10):
            cwpm.add_entry(f"c{i}", priority=0.5, source="s", token_estimate=200)
        removed = cwpm.compress()
        assert removed > 0
        assert len(cwpm.entries) < 10

    def test_compress_no_op_when_below_threshold(self):
        cwpm = ContextWindowPressureManager(max_window_tokens=10000)
        cwpm.add_entry("c", priority=1.0, source="s", token_estimate=100)
        removed = cwpm.compress()
        assert removed == 0


class TestContextWindowPressureManagerPrioritize:
    def test_prioritize_keeps_high_priority(self):
        cwpm = ContextWindowPressureManager(max_window_tokens=500)
        cwpm.add_entry("low", priority=0.1, source="s", token_estimate=300)
        cwpm.add_entry("high", priority=1.0, source="s", token_estimate=300)
        cwpm.prioritize()
        assert len(cwpm.entries) == 1
        assert cwpm.entries[0].content == "high"


class TestContextWindowPressureManagerGetSummary:
    def test_summary_keys(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("c", priority=1.0, source="src_a", token_estimate=50)
        summary = cwpm.get_summary()
        assert "total_entries" in summary
        assert "total_tokens" in summary
        assert "avg_priority" in summary
        assert "by_source" in summary

    def test_summary_empty(self):
        cwpm = ContextWindowPressureManager()
        summary = cwpm.get_summary()
        assert summary["total_entries"] == 0
        assert summary["total_tokens"] == 0


class TestContextWindowPressureManagerBoundary:
    def test_zero_token_estimate(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("c", priority=1.0, source="s", token_estimate=0)
        result = cwpm.check_pressure()
        assert result["total_tokens"] == 0

    def test_negative_priority(self):
        cwpm = ContextWindowPressureManager()
        cwpm.add_entry("c", priority=-1.0, source="s", token_estimate=100)
        assert len(cwpm.entries) == 1
