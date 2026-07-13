# [A_test] module_id: SRC-TST-0999 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_scheduler_act
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.scheduler_act
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_scheduler_act.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.scheduler_act import ActPhaseHandler, ActResult


class TestActResult:
    def test_creates_with_defaults(self):
        result = ActResult()
        assert result.action_record is None
        assert result.action_type is None
        assert result.skipped is False

    def test_creates_with_skipped(self):
        result = ActResult(skipped=True)
        assert result.skipped is True


class TestActPhaseHandlerInstantiation:
    def test_creates_with_dependencies(self):
        from zephyr.feedback_loop.detectors.guard.guard_oscillation_detector import GuardOscillationDetector
        from zephyr.feedback_loop.diagnosers.reliability.context_window_pressure_manager import ContextWindowPressureManager
        from zephyr.feedback_loop.diagnosers.health.self_bottleneck_detector import SelfBottleneckDetector
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter
        from zephyr.feedback_loop.resilience.graceful_degradation_planner import GracefulDegradationPlanner
        from zephyr.feedback_loop.resilience.self_api_throttle_defense import SelfAPIThrottleDefense

        handler = ActPhaseHandler(
            throttle_defense=SelfAPIThrottleDefense(),
            degradation_planner=GracefulDegradationPlanner(),
            mod_rate_limiter=SelfModificationRateLimiter(),
            guard_oscillation=GuardOscillationDetector(),
            context_pressure=ContextWindowPressureManager(),
            bottleneck_detector=SelfBottleneckDetector(),
        )
        assert handler.action_selector is None
        assert handler.verification_engine is not None


class TestActPhaseHandlerRunAct:
    def test_skips_without_action_selector(self):
        from zephyr.feedback_loop.detectors.guard.guard_oscillation_detector import GuardOscillationDetector
        from zephyr.feedback_loop.diagnosers.reliability.context_window_pressure_manager import ContextWindowPressureManager
        from zephyr.feedback_loop.diagnosers.health.self_bottleneck_detector import SelfBottleneckDetector
        from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter
        from zephyr.feedback_loop.resilience.graceful_degradation_planner import GracefulDegradationPlanner
        from zephyr.feedback_loop.resilience.self_api_throttle_defense import SelfAPIThrottleDefense

        handler = ActPhaseHandler(
            throttle_defense=SelfAPIThrottleDefense(),
            degradation_planner=GracefulDegradationPlanner(),
            mod_rate_limiter=SelfModificationRateLimiter(),
            guard_oscillation=GuardOscillationDetector(),
            context_pressure=ContextWindowPressureManager(),
            bottleneck_detector=SelfBottleneckDetector(),
        )
        from unittest.mock import MagicMock

        anomaly = MagicMock()
        anomaly.anomaly_id = "a1"
        diagnosis = MagicMock()
        snapshot = MagicMock()
        result = handler.run_act(anomaly, diagnosis, snapshot, "run1")
        assert result.action_record is None
