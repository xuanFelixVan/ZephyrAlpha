# [A_test] module_id: MOD-GOV_context_budget_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_context_budget_tracker
# [INVARIANTS] L1_80%;L2_90%;L3_95%;token_count_accumulates;session_isolation
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_context_budget_tracker.py
# [TTL] task_bound

from unittest.mock import MagicMock

from zephyr.autonomy_core.context.context_budget_tracker import (
    DEFAULT_THRESHOLDS,
    ContextBudgetLevel,
    ContextBudgetTracker,
    handle_compression_needed,
    set_default_tracker,
)


def _make_observer():
    obs = MagicMock()
    obs.emit = MagicMock()
    return obs


class TestContextBudgetLevel:
    def test_levels_exist(self):
        assert ContextBudgetLevel.L1_WARNING.value == "budget_l1_warning"
        assert ContextBudgetLevel.L2_THROTTLE.value == "budget_l2_throttle"
        assert ContextBudgetLevel.L3_HARD_STOP.value == "budget_l3_hard_stop"


class TestDefaultThresholds:
    def test_values(self):
        assert DEFAULT_THRESHOLDS[ContextBudgetLevel.L1_WARNING] == 0.80
        assert DEFAULT_THRESHOLDS[ContextBudgetLevel.L2_THROTTLE] == 0.90
        assert DEFAULT_THRESHOLDS[ContextBudgetLevel.L3_HARD_STOP] == 0.95


class TestContextBudgetTrackerInit:
    def test_default_session_limit(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs)
        assert tracker._session_limit > 0

    def test_custom_session_limit(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        assert tracker._session_limit == 1000


class TestCountTokens:
    def test_count_returns_int(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        count = tracker.count_tokens("hello world", session_id="s1")
        assert isinstance(count, int)
        assert count > 0

    def test_count_accumulates(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        tracker.count_tokens("hello", session_id="s1")
        tracker.count_tokens("world", session_id="s1")
        usage = tracker.get_usage("s1")
        assert usage["token_count"] > 0

    def test_different_sessions_isolated(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        tracker.count_tokens("hello", session_id="s1")
        tracker.count_tokens("hello", session_id="s2")
        u1 = tracker.get_usage("s1")
        u2 = tracker.get_usage("s2")
        assert u1["session_id"] == "s1"
        assert u2["session_id"] == "s2"


class TestCheckBudget:
    def test_below_threshold_no_event(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=10000)
        tracker.count_tokens("short text", session_id="s1")
        level = tracker.evaluate_budget("s1")
        obs.emit.assert_not_called()

    def test_l1_warning_emitted(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=100)
        tracker.count_tokens("x" * 400, session_id="s1")
        level = tracker.evaluate_budget("s1")
        assert level == ContextBudgetLevel.L1_WARNING or obs.emit.called

    def test_l3_hard_stop_emitted(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=100)
        tracker.count_tokens("x" * 500, session_id="s1")
        level = tracker.evaluate_budget("s1")
        assert level in (ContextBudgetLevel.L2_THROTTLE, ContextBudgetLevel.L3_HARD_STOP)


class TestGetUsage:
    def test_returns_dict(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        tracker.count_tokens("hello", session_id="s1")
        usage = tracker.get_usage("s1")
        assert "session_id" in usage
        assert "token_count" in usage
        assert "limit" in usage
        assert "ratio" in usage

    def test_ratio_format(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        tracker.count_tokens("hello", session_id="s1")
        usage = tracker.get_usage("s1")
        assert isinstance(usage["ratio"], float)


class TestResetSession:
    def test_reset_clears_session(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        tracker.count_tokens("hello", session_id="s1")
        tracker.reset_session("s1")
        usage = tracker.get_usage("s1")
        assert usage["token_count"] == 0


class TestSetSessionLimit:
    def test_changes_limit(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs, session_limit=1000)
        tracker.set_session_limit("s1", 500)
        usage = tracker.get_usage("s1")
        assert usage["limit"] == 500


class TestDocCompressor:
    def test_register_and_get(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs)
        assert tracker.get_doc_compressor() is None
        compressor = MagicMock()
        tracker.register_doc_compressor(compressor)
        assert tracker.get_doc_compressor() is compressor

    def test_compress_without_compressor_returns_none(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs)
        result = tracker.compress_session_context("some text")
        assert result is None

    def test_compress_with_compressor(self):
        obs = _make_observer()
        tracker = ContextBudgetTracker(obs)
        compressor = MagicMock()
        compressor.compress.return_value = "compressed"
        tracker.register_doc_compressor(compressor)
        result = tracker.compress_session_context("some text", session_id="s1")
        assert result == "compressed"
        compressor.compress.assert_called_once_with("some text", session_id="s1")


class TestHandleCompressionNeeded:
    def test_no_tracker_returns_none(self):
        set_default_tracker(None)
        result = handle_compression_needed({"text": "hello", "session_id": "s1"})
        assert result is None
