# [A_test] module_id: SRC-TST-1121 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_infinite_loop_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_infinite_loop_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.anomaly.infinite_loop_detector import (
    InfiniteLoopDetector,
    LoopAction,
)


class TestLoopAction:
    def test_creation(self):
        action = LoopAction(action_signature="repair_metric_X")
        assert action.action_signature == "repair_metric_X"
        assert action.timestamp > 0


class TestInfiniteLoopDetector:
    def test_default_construction(self):
        det = InfiniteLoopDetector()
        assert len(det.recent_actions) == 0
        assert det.loop_threshold == 3
        assert det.cooldown_seconds == 300.0
        assert det.active_loops == set()

    def test_custom_construction(self):
        det = InfiniteLoopDetector(loop_threshold=5, cooldown_seconds=60.0)
        assert det.loop_threshold == 5
        assert det.cooldown_seconds == 60.0

    def test_track_no_loop(self):
        det = InfiniteLoopDetector(loop_threshold=3)
        assert det.track("action_A") is False
        assert det.track("action_A") is False

    def test_track_detects_loop(self):
        det = InfiniteLoopDetector(loop_threshold=3, cooldown_seconds=3600.0)
        det.track("action_A")
        det.track("action_A")
        result = det.track("action_A")
        assert result is True
        assert "action_A" in det.active_loops

    def test_track_different_actions_no_loop(self):
        det = InfiniteLoopDetector(loop_threshold=3)
        det.track("action_A")
        det.track("action_B")
        det.track("action_C")
        assert len(det.active_loops) == 0

    def test_track_deque_maxlen(self):
        det = InfiniteLoopDetector(loop_threshold=3)
        for i in range(60):
            det.track(f"action_{i}")
        assert len(det.recent_actions) <= 50

    def test_clear_specific_loop(self):
        det = InfiniteLoopDetector(loop_threshold=3, cooldown_seconds=3600.0)
        det.track("action_A")
        det.track("action_A")
        det.track("action_A")
        assert "action_A" in det.active_loops
        det.clear("action_A")
        assert "action_A" not in det.active_loops

    def test_clear_nonexistent_loop(self):
        det = InfiniteLoopDetector()
        det.clear("nonexistent")
        assert len(det.active_loops) == 0

    def test_track_multiple_loops(self):
        det = InfiniteLoopDetector(loop_threshold=3, cooldown_seconds=3600.0)
        for _ in range(3):
            det.track("action_A")
        for _ in range(3):
            det.track("action_B")
        assert "action_A" in det.active_loops
        assert "action_B" in det.active_loops

    def test_empty_detector_no_active_loops(self):
        det = InfiniteLoopDetector()
        assert len(det.active_loops) == 0
