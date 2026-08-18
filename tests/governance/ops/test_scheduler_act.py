# [A_test] module_id: MOD-GOV_scheduler_act | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_scheduler_act
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] ActPhaseHandler.run_act returns ActResult; run_verify returns verification
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_scheduler_act.py
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from unittest.mock import MagicMock

# 治本：zephyr.ops 已迁移到 zephyr.feedback_loop（ARCH-032，ops/ 74 文件迁移到 trading/feedback_loop/）。
# 子包结构重组：detectors.guard/、diagnosers.reliability/、diagnosers.health/ 等。
from zephyr.feedback_loop.detectors.guard.guard_oscillation_detector import GuardOscillationDetector
from zephyr.feedback_loop.diagnosers.health.self_bottleneck_detector import SelfBottleneckDetector
from zephyr.feedback_loop.diagnosers.reliability.context_window_pressure_manager import ContextWindowPressureManager
from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter
from zephyr.feedback_loop.resilience.graceful_degradation_planner import GracefulDegradationPlanner
from zephyr.feedback_loop.resilience.self_api_throttle_defense import SelfAPIThrottleDefense
from zephyr.feedback_loop.scheduler_act import ActPhaseHandler, ActResult


class TestActResult:
    def test_default_values(self):
        ar = ActResult()
        assert ar.action_record is None
        assert ar.action_type is None
        assert ar.skipped is False

    def test_skipped_result(self):
        ar = ActResult(skipped=True)
        assert ar.skipped is True

    def test_with_action(self):
        ar = ActResult(action_record={"success": True}, action_type="repair")
        assert ar.action_type == "repair"


class TestActPhaseHandlerInit:
    def test_instantiation(self):
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

    def test_no_action_selector_returns_empty(self):
        handler = ActPhaseHandler(
            throttle_defense=SelfAPIThrottleDefense(),
            degradation_planner=GracefulDegradationPlanner(),
            mod_rate_limiter=SelfModificationRateLimiter(),
            guard_oscillation=GuardOscillationDetector(),
            context_pressure=ContextWindowPressureManager(),
            bottleneck_detector=SelfBottleneckDetector(),
        )
        anomaly = MagicMock()
        anomaly.anomaly_id = "a1"
        diagnosis = MagicMock()
        snapshot = MagicMock()
        snapshot.system_cpu = 0.5
        snapshot.memory_usage_pct = 0.5
        result = handler.run_act(anomaly, diagnosis, snapshot, "run1")
        assert isinstance(result, ActResult)
        assert result.action_record is None
        assert result.skipped is False


class TestActPhaseHandlerRunAct:
    def _make_handler(self):
        handler = ActPhaseHandler(
            throttle_defense=SelfAPIThrottleDefense(),
            degradation_planner=GracefulDegradationPlanner(),
            mod_rate_limiter=SelfModificationRateLimiter(),
            guard_oscillation=GuardOscillationDetector(),
            context_pressure=ContextWindowPressureManager(),
            bottleneck_detector=SelfBottleneckDetector(),
        )
        handler.action_selector = MagicMock()
        return handler

    def test_action_selector_selects_and_executes(self):
        handler = self._make_handler()
        handler.throttle_defense = MagicMock()
        handler.throttle_defense.request_action.return_value = {"allowed": True, "queued": False}
        handler.degradation_planner = MagicMock()
        handler.degradation_planner.evaluate_degradation.return_value = {"level": "FULL"}
        handler.oscillation_damping = MagicMock()
        handler.oscillation_damping.is_allowed.return_value = True
        handler.toil_tracker = MagicMock()
        handler.action_decay = MagicMock()
        handler.placebo_detector = MagicMock()
        handler.composition_health = MagicMock()
        handler.cascading_rollback = MagicMock()
        handler.action_selector.select_action.return_value = "REPAIR_CPU"
        mock_record = MagicMock()
        mock_record.success = True
        handler.action_selector.execute.return_value = mock_record

        anomaly = MagicMock()
        anomaly.anomaly_id = "a1"
        anomaly.evidence = {"value": 50.0}
        diagnosis = MagicMock()
        diagnosis.severity_level = 3
        snapshot = MagicMock()
        snapshot.system_cpu = 0.5
        snapshot.memory_usage_pct = 0.5

        result = handler.run_act(anomaly, diagnosis, snapshot, "run1")
        assert result.action_type == "REPAIR_CPU"
        assert result.action_record is mock_record
        assert result.skipped is False

    def test_action_selector_returns_none_type(self):
        handler = self._make_handler()
        handler.action_selector.select_action.return_value = None

        anomaly = MagicMock()
        anomaly.anomaly_id = "a1"
        diagnosis = MagicMock()
        diagnosis.severity_level = 3
        snapshot = MagicMock()
        snapshot.system_cpu = 0.5
        snapshot.memory_usage_pct = 0.5

        result = handler.run_act(anomaly, diagnosis, snapshot, "run1")
        assert result.action_type is None


class TestActPhaseHandlerRunVerify:
    def _make_handler(self):
        handler = ActPhaseHandler(
            throttle_defense=SelfAPIThrottleDefense(),
            degradation_planner=GracefulDegradationPlanner(),
            mod_rate_limiter=SelfModificationRateLimiter(),
            guard_oscillation=GuardOscillationDetector(),
            context_pressure=ContextWindowPressureManager(),
            bottleneck_detector=SelfBottleneckDetector(),
        )
        return handler

    def test_run_verify_returns_verification(self):
        handler = self._make_handler()
        anomaly = MagicMock()
        anomaly.anomaly_id = "a1"
        anomaly.evidence = {"value": 50.0, "metric_name": "cpu"}
        diagnosis = MagicMock()
        diagnosis.root_cause = "cpu_spike"
        diagnosis.confidence = 0.8

        result = handler.run_verify(anomaly, diagnosis, "run1", lambda x: 30.0)
        assert result is not None
