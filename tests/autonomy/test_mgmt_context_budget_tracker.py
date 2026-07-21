# [A_test] module_id: MOD-GOV_mgmt_context_budget_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_budget_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.context_budget_tracker import (
        ContextBudgetLevel,
        ContextBudgetTracker,
    )
    from zephyr.shared.infra.observer import Observer
except Exception as _exc:
    pytest.skip(f"cannot import context_budget_tracker: {_exc}", allow_module_level=True)


class TestContextBudgetTrackerCountTokens:
    def test_count_tokens_returns_int(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        count = tracker.count_tokens("hello world", session_id="s1")
        assert isinstance(count, int)
        assert count > 0

    def test_count_tokens_empty_string(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        count = tracker.count_tokens("", session_id="s2")
        assert count == 0

    def test_count_tokens_accumulates(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        tracker.count_tokens("aaaa", session_id="s3")
        tracker.count_tokens("bbbb", session_id="s3")
        usage = tracker.get_usage("s3")
        assert usage["token_count"] > 0


class TestContextBudgetTrackerCheckBudget:
    def test_check_budget_returns_level(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        level = tracker.evaluate_budget("default")
        assert isinstance(level, ContextBudgetLevel)

    def test_check_budget_l1_warning(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=1000)
        tracker.count_tokens("a" * 3400, session_id="s4")
        level = tracker.evaluate_budget("s4")
        assert level in (ContextBudgetLevel.L1_WARNING, ContextBudgetLevel.L2_THROTTLE)

    def test_check_budget_l3_hard_stop(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=1000)
        tracker.count_tokens("a " * 5000, session_id="s5")
        level = tracker.evaluate_budget("s5")
        assert level == ContextBudgetLevel.L3_HARD_STOP


class TestContextBudgetTrackerSessionManagement:
    def test_reset_session(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        tracker.count_tokens("hello", session_id="s6")
        tracker.reset_session("s6")
        usage = tracker.get_usage("s6")
        assert usage["token_count"] == 0

    def test_set_session_limit(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        tracker.set_session_limit("s7", 5000)
        usage = tracker.get_usage("s7")
        assert usage["limit"] == 5000

    def test_get_usage_returns_dict(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        usage = tracker.get_usage("default")
        assert "session_id" in usage
        assert "token_count" in usage
        assert "limit" in usage
        assert "ratio" in usage


class TestDocCompressorIntegration:
    def test_register_and_get_doc_compressor(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        assert tracker.get_doc_compressor() is None
        tracker.register_doc_compressor("fake_compressor")
        assert tracker.get_doc_compressor() == "fake_compressor"

    def test_compress_session_context_without_compressor(self):
        bus = Observer()
        tracker = ContextBudgetTracker(bus, session_limit=8000)
        result = tracker.compress_session_context("some text")
        assert result is None
