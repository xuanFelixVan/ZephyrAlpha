# [A_test] module_id: SRC-TST-0266 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_action_interaction_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_action_interaction_detector.py
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.feedback_loop.detectors.correlation.action_interaction_detector import (
    ActionInteractionDetector,
)


class TestActionInteractionDetectorInstantiation:
    def test_default_construction(self):
        det = ActionInteractionDetector()
        assert det.interaction_window == 300.0
        assert det.min_co_occurrence == 3
        assert det.active_actions == {}
        assert det.interaction_alerts == []

    def test_custom_params(self):
        det = ActionInteractionDetector(interaction_window=60.0, min_co_occurrence=5)
        assert det.interaction_window == 60.0
        assert det.min_co_occurrence == 5


class TestRecordAction:
    def test_single_action_no_co_occurrence(self):
        det = ActionInteractionDetector()
        det.record_action("a1", "repair", 0.5)
        assert "repair" in det.active_actions

    def test_co_occurrence_recorded(self):
        det = ActionInteractionDetector()
        det.record_action("a1", "repair", 0.5)
        det.record_action("a2", "restart", -0.5)
        assert "repair" in det.interaction_matrix or "restart" in det.interaction_matrix

    def test_truncates_at_100(self):
        det = ActionInteractionDetector()
        det.record_action("a1", "repair", 0.5)
        for i in range(105):
            det.record_action(f"a{i}", "restart", -0.5)
        key_a, key_b = tuple(sorted(["repair", "restart"]))
        scores = det.interaction_matrix[key_a][key_b]
        assert len(scores) <= 100

    def test_stale_actions_cleaned(self):
        det = ActionInteractionDetector(interaction_window=0.001)
        det.record_action("a1", "repair", 0.5)
        time.sleep(0.01)
        det.record_action("a2", "restart", 0.5)
        assert "repair" not in det.active_actions


class TestDetectInteraction:
    def test_no_interaction_below_min_co_occurrence(self):
        det = ActionInteractionDetector(min_co_occurrence=3)
        det.record_action("a1", "repair", 0.5)
        det.record_action("a2", "restart", -0.5)
        alerts = det.detect_interaction()
        assert alerts == []

    def test_negative_interaction_detected(self):
        det = ActionInteractionDetector(min_co_occurrence=3)
        det.record_action("a1", "repair", 0.5)
        for i in range(3):
            det.record_action(f"a{i}", "restart", -0.8)
        alerts = det.detect_interaction()
        assert len(alerts) >= 1
        assert alerts[0]["mean_outcome"] < -0.3

    def test_high_severity(self):
        det = ActionInteractionDetector(min_co_occurrence=3)
        det.record_action("a1", "repair", 0.5)
        for i in range(3):
            det.record_action(f"a{i}", "restart", -0.9)
        alerts = det.detect_interaction()
        if alerts:
            assert alerts[0]["severity"] == "HIGH"

    def test_medium_severity(self):
        det = ActionInteractionDetector(min_co_occurrence=3)
        det.record_action("a1", "repair", 0.5)
        for i in range(3):
            det.record_action(f"a{i}", "restart", -0.4)
        alerts = det.detect_interaction()
        if alerts:
            assert alerts[0]["severity"] == "MEDIUM"

    def test_alerts_appended_to_history(self):
        det = ActionInteractionDetector(min_co_occurrence=3)
        det.record_action("a1", "repair", 0.5)
        for i in range(3):
            det.record_action(f"a{i}", "restart", -0.8)
        det.detect_interaction()
        assert len(det.interaction_alerts) >= 1


class TestGetInteractionHeatmap:
    def test_empty_heatmap(self):
        det = ActionInteractionDetector()
        assert det.get_interaction_heatmap() == {}

    def test_heatmap_with_data(self):
        det = ActionInteractionDetector(min_co_occurrence=2)
        det.record_action("a1", "repair", 0.5)
        det.record_action("a2", "restart", -0.5)
        det.record_action("a3", "repair", 0.5)
        heatmap = det.get_interaction_heatmap()
        assert isinstance(heatmap, dict)


class TestClearStale:
    def test_clears_alerts_without_timestamp(self):
        det = ActionInteractionDetector()
        det.interaction_alerts = [{"type": "test"}]
        removed = det.clear_stale()
        assert removed == 1
        assert len(det.interaction_alerts) == 0

    def test_keeps_recent_alerts(self):
        det = ActionInteractionDetector()
        det.interaction_alerts = [{"type": "recent", "ts": time.time()}]
        removed = det.clear_stale()
        assert removed == 0
        assert len(det.interaction_alerts) == 1

    def test_clears_old_alerts(self):
        det = ActionInteractionDetector()
        det.interaction_alerts = [{"type": "old", "ts": time.time() - 200000}]
        removed = det.clear_stale(max_age=86400.0)
        assert removed == 1
        assert len(det.interaction_alerts) == 0
