# [A_test] module_id: SRC-TST-0481 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_canary_controller
# [INVARIANTS] 金丝雀保护不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest;drift_engine;detector_dispatcher;alert_router
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_canary_controller.py
# [TTL] task_bound

import json
import os

from zephyr.gov_drift.canary_controller import (
    CONFIG,
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
    def test_enum_values(self):
        assert CanaryComparison.NEW_FINDING.value == "NEW_FINDING"
        assert CanaryComparison.LOST_FINDING.value == "LOST_FINDING"
        assert CanaryComparison.CHANGED_SEVERITY.value == "CHANGED_SEVERITY"
        assert CanaryComparison.IDENTICAL.value == "IDENTICAL"

    def test_all_members(self):
        members = set(CanaryComparison.__members__.keys())
        assert members == {"NEW_FINDING", "LOST_FINDING", "CHANGED_SEVERITY", "IDENTICAL"}


class TestCanaryResult:
    def test_enum_values(self):
        assert CanaryResult.PROMOTE.value == "PROMOTE"
        assert CanaryResult.REJECT.value == "REJECT"
        assert CanaryResult.PENDING.value == "PENDING"
        assert CanaryResult.AUTO_ROLLBACK.value == "AUTO_ROLLBACK"

    def test_all_members(self):
        members = set(CanaryResult.__members__.keys())
        assert members == {"PROMOTE", "REJECT", "PENDING", "AUTO_ROLLBACK"}


class TestCanaryRun:
    def test_default_fields(self):
        cr = CanaryRun()
        assert cr.run_id.startswith("canary-")
        assert cr.v1_detector_id == ""
        assert cr.v2_detector_id == ""
        assert cr.v1_events == []
        assert cr.v2_events == []
        assert cr.result == CanaryResult.PENDING
        assert cr.review_required is True

    def test_custom_fields(self):
        cr = CanaryRun(
            v1_detector_id="v1-det",
            v2_detector_id="v2-det",
            result=CanaryResult.PROMOTE,
            review_required=False,
        )
        assert cr.v1_detector_id == "v1-det"
        assert cr.v2_detector_id == "v2-det"
        assert cr.result == CanaryResult.PROMOTE
        assert cr.review_required is False

    def test_comparison_default_keys(self):
        cr = CanaryRun()
        assert "NEW_FINDING" in cr.comparison
        assert "LOST_FINDING" in cr.comparison
        assert "CHANGED_SEVERITY" in cr.comparison
        assert "IDENTICAL" in cr.comparison


class TestCanaryConfig:
    def test_default_fields(self):
        cfg = CanaryConfig()
        assert cfg.state_dir == ""
        assert cfg.max_runs_before_review == 5
        assert cfg.fp_threshold == 2.0
        assert cfg.auto_approve_identical_rate == 0.95


class TestClassifyEventId:
    def test_new_finding(self):
        v1_events = [{"event_id": "e1"}]
        v2_events = [{"event_id": "e1"}, {"event_id": "e2"}]
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        classify_event_id("e2", {"e2"}, v1_events, v2_events, classification)
        assert "e2" in classification["NEW_FINDING"]

    def test_lost_finding(self):
        v1_events = [{"event_id": "e1"}, {"event_id": "e2"}]
        v2_events = [{"event_id": "e1"}]
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        classify_event_id("e1", {"e1"}, v1_events, v2_events, classification)
        assert "e2" in classification["LOST_FINDING"]

    def test_changed_severity(self):
        v1_events = [{"event_id": "e1", "severity": "HIGH"}]
        v2_events = [{"event_id": "e1", "severity": "MEDIUM"}]
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        classify_event_id("e1", {"e1"}, v1_events, v2_events, classification)
        assert len(classification["CHANGED_SEVERITY"]) == 1
        assert "e1" in classification["CHANGED_SEVERITY"][0]

    def test_identical(self):
        v1_events = [{"event_id": "e1", "severity": "HIGH"}]
        v2_events = [{"event_id": "e1", "severity": "HIGH"}]
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        classify_event_id("e1", {"e1"}, v1_events, v2_events, classification)
        assert "e1" in classification["IDENTICAL"]

    def test_empty_events(self):
        classification = {"NEW_FINDING": [], "LOST_FINDING": [], "CHANGED_SEVERITY": [], "IDENTICAL": []}
        classify_event_id("e1", set(), [], [], classification)
        assert classification["NEW_FINDING"] == []
        assert classification["LOST_FINDING"] == []


class TestRunCanary:
    def test_identical_events_promote(self):
        events = [{"event_id": "e1", "severity": "HIGH"}]
        cr = run_canary("v1", "v2", lambda: events, lambda: events)
        assert cr.result == CanaryResult.PROMOTE
        assert cr.review_required is False

    def test_new_findings_high_fp_rate_triggers_rollback(self):
        v1_events = [{"event_id": "e1", "severity": "HIGH"}]
        v2_events = [{"event_id": f"new-{i}"} for i in range(10)]
        cr = run_canary("v1", "v2", lambda: v1_events, lambda: v2_events)
        assert cr.result == CanaryResult.AUTO_ROLLBACK

    def test_some_new_findings_pending(self):
        v1_events = [{"event_id": f"e{i}", "severity": "HIGH"} for i in range(10)]
        v2_events = v1_events[:9] + [{"event_id": "new-1", "severity": "MEDIUM"}]
        cr = run_canary("v1", "v2", lambda: v1_events, lambda: v2_events)
        assert cr.result == CanaryResult.PENDING
        assert cr.review_required is True

    def test_empty_v1_events(self):
        v2_events = [{"event_id": "e1"}]
        cr = run_canary("v1", "v2", lambda: [], lambda: v2_events)
        assert cr.result in (CanaryResult.AUTO_ROLLBACK, CanaryResult.PENDING)

    def test_both_empty_events(self):
        cr = run_canary("v1", "v2", lambda: [], lambda: [])
        assert cr.result == CanaryResult.PROMOTE
        assert cr.review_required is False

    def test_run_populates_detector_ids(self):
        cr = run_canary("det-v1", "det-v2", lambda: [], lambda: [])
        assert cr.v1_detector_id == "det-v1"
        assert cr.v2_detector_id == "det-v2"

    def test_lost_findings_pending(self):
        v1_events = [{"event_id": "e1"}, {"event_id": "e2"}]
        v2_events = [{"event_id": "e1"}]
        cr = run_canary("v1", "v2", lambda: v1_events, lambda: v2_events)
        assert cr.result == CanaryResult.PENDING


class TestPromoteDetector:
    def test_promote_pending_run(self):
        cr = run_canary("v1", "v2", lambda: [], lambda: [])
        result = promote_detector(cr)
        assert result is True
        assert cr.result == CanaryResult.PROMOTE

    def test_promote_auto_rollback_blocked(self):
        v1_events = [{"event_id": "e1"}]
        v2_events = [{"event_id": f"new-{i}"} for i in range(10)]
        cr = run_canary("v1", "v2", lambda: v1_events, lambda: v2_events)
        assert cr.result == CanaryResult.AUTO_ROLLBACK
        result = promote_detector(cr)
        assert result is False


class TestRollbackDetector:
    def test_rollback_sets_auto_rollback(self):
        cr = CanaryRun(v1_detector_id="v1", v2_detector_id="v2")
        result = rollback_detector(cr, reason="test rollback")
        assert result is True
        assert cr.result == CanaryResult.AUTO_ROLLBACK

    def test_rollback_default_reason(self):
        cr = CanaryRun(v1_detector_id="v1", v2_detector_id="v2")
        rollback_detector(cr)
        assert cr.result == CanaryResult.AUTO_ROLLBACK


class TestGetCanaryHistory:
    def test_returns_empty_when_no_state(self):
        original_dir = CONFIG.state_dir
        CONFIG.state_dir = ""
        result = get_canary_history()
        assert result == []
        CONFIG.state_dir = original_dir

    def test_returns_empty_for_nonexistent_detector(self):
        original_dir = CONFIG.state_dir
        CONFIG.state_dir = ""
        result = get_canary_history("nonexistent-det")
        assert result == []
        CONFIG.state_dir = original_dir


class TestStatePersistence:
    def test_save_and_load_with_state_dir(self, tmp_path):
        original_dir = CONFIG.state_dir
        CONFIG.state_dir = str(tmp_path)
        try:
            events = [{"event_id": "e1", "severity": "HIGH"}]
            cr = run_canary("v1", "v2", lambda: events, lambda: events)
            assert cr.result == CanaryResult.PROMOTE
            state_file = os.path.join(str(tmp_path), "_canary_state.json")
            assert os.path.exists(state_file)
            with open(state_file, encoding="utf-8") as f:
                state = json.loads(f.read())
            assert state["v1_detector_id"] == "v1"
            assert state["v2_detector_id"] == "v2"
        finally:
            CONFIG.state_dir = original_dir

    def test_no_save_when_no_state_dir(self):
        original_dir = CONFIG.state_dir
        CONFIG.state_dir = ""
        try:
            events = [{"event_id": "e1", "severity": "HIGH"}]
            cr = run_canary("v1", "v2", lambda: events, lambda: events)
            assert cr.result == CanaryResult.PROMOTE
        finally:
            CONFIG.state_dir = original_dir
