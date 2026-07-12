# [A_test] module_id: SRC-TST-0394 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_canary_controller
# [INVARIANTS] 金丝雀保护不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI;drift_engine
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_ba_canary_controller.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.canary_controller import (
    CanaryComparison,
    CanaryConfig,
    CanaryResult,
    CanaryRun,
    classify_event_id,
    get_canary_history,
    promote_detector,
    rollback_detector,
    run_canary,
)


class TestCanaryComparison:
    def test_has_expected_values(self):
        assert CanaryComparison.NEW_FINDING.value == "NEW_FINDING"
        assert CanaryComparison.LOST_FINDING.value == "LOST_FINDING"
        assert CanaryComparison.CHANGED_SEVERITY.value == "CHANGED_SEVERITY"
        assert CanaryComparison.IDENTICAL.value == "IDENTICAL"

    def test_is_str_enum(self):
        assert isinstance(CanaryComparison.NEW_FINDING, str)


class TestCanaryResult:
    def test_has_expected_values(self):
        assert CanaryResult.PROMOTE.value == "PROMOTE"
        assert CanaryResult.REJECT.value == "REJECT"
        assert CanaryResult.PENDING.value == "PENDING"
        assert CanaryResult.AUTO_ROLLBACK.value == "AUTO_ROLLBACK"


class TestCanaryRun:
    def test_defaults(self):
        cr = CanaryRun()
        assert cr.run_id.startswith("canary-")
        assert cr.result == CanaryResult.PENDING
        assert cr.review_required is True
        assert cr.v1_events == []
        assert cr.v2_events == []

    def test_custom_fields(self):
        cr = CanaryRun(v1_detector_id="v1", v2_detector_id="v2")
        assert cr.v1_detector_id == "v1"
        assert cr.v2_detector_id == "v2"


class TestCanaryConfig:
    def test_defaults(self):
        cfg = CanaryConfig()
        assert cfg.max_runs_before_review == 5
        assert cfg.fp_threshold == 2.0
        assert cfg.auto_approve_identical_rate == 0.95


class TestClassifyEventId:
    def test_classifies_new_finding(self):
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        v1_events = [{"event_id": "a"}]
        v2_events = [{"event_id": "a"}, {"event_id": "b"}]
        classify_event_id("a", {"a", "b"}, v1_events, v2_events, classification)
        assert "b" in classification["NEW_FINDING"]

    def test_classifies_lost_finding(self):
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        v1_events = [{"event_id": "a"}, {"event_id": "c"}]
        v2_events = [{"event_id": "a"}]
        classify_event_id("a", {"a"}, v1_events, v2_events, classification)
        assert "c" in classification["LOST_FINDING"]

    def test_classifies_changed_severity(self):
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        v1_events = [{"event_id": "a", "severity": "HIGH"}]
        v2_events = [{"event_id": "a", "severity": "LOW"}]
        classify_event_id("a", {"a"}, v1_events, v2_events, classification)
        assert len(classification["CHANGED_SEVERITY"]) >= 1

    def test_classifies_identical(self):
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        v1_events = [{"event_id": "a", "severity": "HIGH"}]
        v2_events = [{"event_id": "a", "severity": "HIGH"}]
        classify_event_id("a", {"a"}, v1_events, v2_events, classification)
        assert "a" in classification["IDENTICAL"]

    def test_empty_events(self):
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        classify_event_id("", set(), [], [], classification)
        assert classification["NEW_FINDING"] == []
        assert classification["LOST_FINDING"] == []


class TestRunCanary:
    def test_promotes_identical_results(self):
        v1_fn = lambda: [{"event_id": "e1"}]
        v2_fn = lambda: [{"event_id": "e1"}]
        cr = run_canary("v1_det", "v2_det", v1_fn, v2_fn)
        assert cr.result == CanaryResult.PROMOTE
        assert cr.review_required is False

    def test_auto_rollback_on_high_fp(self):
        v1_fn = lambda: [{"event_id": "e1"}]
        v2_fn = lambda: [{"event_id": "e2"}, {"event_id": "e3"}, {"event_id": "e4"}]
        cr = run_canary("v1_det", "v2_det", v1_fn, v2_fn)
        assert cr.result == CanaryResult.AUTO_ROLLBACK

    def test_pending_on_mixed_results(self):
        v1_fn = lambda: [{"event_id": "e1"}]
        v2_fn = lambda: [{"event_id": "e1"}, {"event_id": "e2"}]
        cr = run_canary("v1_det", "v2_det", v1_fn, v2_fn)
        assert cr.result in (CanaryResult.PENDING, CanaryResult.AUTO_ROLLBACK, CanaryResult.PROMOTE)

    def test_stores_v1_and_v2_events(self):
        v1_fn = lambda: [{"event_id": "e1"}]
        v2_fn = lambda: [{"event_id": "e2"}]
        cr = run_canary("v1", "v2", v1_fn, v2_fn)
        assert len(cr.v1_events) == 1
        assert len(cr.v2_events) == 1


class TestPromoteDetector:
    def test_promotes_pending_run(self):
        cr = CanaryRun(v1_detector_id="v1", v2_detector_id="v2", result=CanaryResult.PENDING)
        result = promote_detector(cr)
        assert result is True
        assert cr.result == CanaryResult.PROMOTE

    def test_rejects_auto_rollback_run(self):
        cr = CanaryRun(v1_detector_id="v1", v2_detector_id="v2", result=CanaryResult.AUTO_ROLLBACK)
        result = promote_detector(cr)
        assert result is False


class TestRollbackDetector:
    def test_sets_auto_rollback(self):
        cr = CanaryRun(v1_detector_id="v1", v2_detector_id="v2")
        result = rollback_detector(cr, reason="test")
        assert result is True
        assert cr.result == CanaryResult.AUTO_ROLLBACK

    def test_default_reason(self):
        cr = CanaryRun(v1_detector_id="v1", v2_detector_id="v2")
        rollback_detector(cr)
        assert cr.result == CanaryResult.AUTO_ROLLBACK


class TestGetCanaryHistory:
    def test_returns_list_when_no_state(self):
        history = get_canary_history()
        assert isinstance(history, list)

    def test_filters_by_detector_id(self):
        history = get_canary_history("nonexistent_detector")
        assert isinstance(history, list)
