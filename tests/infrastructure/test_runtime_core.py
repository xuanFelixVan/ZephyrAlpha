# [A_test] module_id: MOD-GOV_runtime_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-555 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.runtime.test_runtime_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: runtime_core"""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.shared.lifecycle.resource_optimization_models import (
    OptimizationStrategy,
    ResourceSnapshot,
)
from zephyr.trading.resource_optimization import (
    CircuitBreaker,
    CircuitBreakerState,
    PressureLevel,
    ResourceOptimizationEngine,
    _HysteresisConfig,
    _PressureStateMachine,
)


class TestCircuitBreaker:
    def test_initial_state_is_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_allow_when_closed(self):
        cb = CircuitBreaker()
        assert cb.allow() is True

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_block_when_open(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.allow() is False

    def test_half_open_after_recovery_timeout(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout_s=0.01)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        time.sleep(0.02)
        # 生产跟进（5.91.3）：state getter 不触发迁移，状态转换只在 allow() 内发生
        assert cb.allow() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_success_closes_from_half_open(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout_s=0.01)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.02)
        # 生产跟进（5.91.3）：先 allow() 触发 OPEN→HALF_OPEN 迁移
        assert cb.allow() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_reset_returns_to_closed(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.allow() is True


class TestPressureStateMachine:
    def test_initial_state_is_normal(self):
        sm = _PressureStateMachine()
        assert sm.current == PressureLevel.NORMAL

    def test_escalation_requires_confirmations(self):
        cfg = _HysteresisConfig(confirmation_count=2)
        sm = _PressureStateMachine(cfg)
        result = sm.transition(PressureLevel.WARNING)
        assert result == PressureLevel.NORMAL
        result = sm.transition(PressureLevel.WARNING)
        assert result == PressureLevel.WARNING

    def test_deescalation_after_cooldown(self):
        cfg = _HysteresisConfig(confirmation_count=1, cooldown_seconds=0.01)
        sm = _PressureStateMachine(cfg)
        sm.transition(PressureLevel.WARNING)
        assert sm.current == PressureLevel.WARNING
        time.sleep(0.02)
        sm.transition(PressureLevel.NORMAL)
        assert sm.current == PressureLevel.NORMAL

    def test_same_level_is_noop(self):
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=1))
        sm.transition(PressureLevel.WARNING)
        result = sm.transition(PressureLevel.WARNING)
        assert result == PressureLevel.WARNING


class TestResourceOptimizationEngine:
    @pytest.fixture(autouse=True)
    def _reset_singleton(self):
        ResourceOptimizationEngine.reset()
        yield
        ResourceOptimizationEngine.reset()

    def test_singleton_creation(self):
        engine1 = ResourceOptimizationEngine()
        engine2 = ResourceOptimizationEngine()
        assert engine1 is engine2

    def test_snapshot_returns_resource_snapshot(self):
        engine = ResourceOptimizationEngine()
        snap = engine.snapshot()
        assert isinstance(snap, ResourceSnapshot)
        assert snap.timestamp > 0

    def test_health_check_returns_result(self):
        engine = ResourceOptimizationEngine()
        hc = engine.health_check()
        assert hasattr(hc, "engine_running")
        assert hasattr(hc, "pressure_level")

    def test_get_pressure_state(self):
        engine = ResourceOptimizationEngine()
        state = engine.get_pressure_state()
        assert state.current_level == PressureLevel.NORMAL

    def test_get_degradation_matrix(self):
        engine = ResourceOptimizationEngine()
        matrix = engine.get_degradation_matrix()
        assert "normal" in matrix.model_fields

    def test_optimize_schedule_adapt(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        assert result.success is True
        assert len(result.actions_taken) > 0

    def test_optimize_memory_compact(self):
        engine = ResourceOptimizationEngine()
        result = engine.optimize(OptimizationStrategy.MEMORY_COMPACT)
        assert result.success is True
        assert len(result.actions_taken) > 0

    def test_optimization_history_recorded(self):
        engine = ResourceOptimizationEngine()
        engine.optimize(OptimizationStrategy.SCHEDULE_ADAPT)
        history = engine.get_optimization_history(limit=10)
        assert len(history) >= 1
        assert history[-1].strategy == OptimizationStrategy.SCHEDULE_ADAPT

    def test_circuit_breaker_status_empty(self):
        engine = ResourceOptimizationEngine()
        status = engine.get_circuit_breaker_status()
        assert isinstance(status, dict)

    def test_on_pressure_callback_registration(self):
        engine = ResourceOptimizationEngine()
        received = []
        engine.on_pressure(lambda level, snap: received.append(level))
        assert len(engine.pressure_callbacks) == 1


class TestAutoRuntimeCoreInit:
    @patch("zephyr.trading.auto_runtime_core.AiAuditLogger")
    @patch("zephyr.trading.auto_runtime_core.CapabilityRegistry")
    @patch("zephyr.trading.auto_runtime_core.NightShiftQueue")
    @patch("zephyr.trading.auto_runtime_core.StopGate")
    @patch("zephyr.trading.auto_runtime_core.DreamCycle")
    @patch("zephyr.trading.auto_runtime_core.FeedbackLoop")
    @patch("zephyr.trading.auto_runtime_core.HealthMonitor")
    @patch("zephyr.trading.auto_runtime_core.IntegrationRegistry")
    @patch("zephyr.trading.auto_runtime_core.WorkOrchestrator")
    @patch("zephyr.trading.auto_runtime_core.Finalizer")
    @patch("zephyr.trading.auto_runtime_core.LifecycleManager")
    @patch("zephyr.trading.auto_runtime_core.ModuleOnboardingScanner")
    @patch("zephyr.trading.auto_runtime_core.AutoIntegrator")
    @patch("zephyr.trading.auto_runtime_core.OrphanDetector")
    @patch("zephyr.trading.auto_runtime_core.StatusDashboard")
    @patch("zephyr.trading.auto_runtime_core.RuntimeConfig")
    def test_init_creates_components(
        self,
        mock_cfg_cls,
        mock_dashboard,
        mock_orphan,
        mock_auto_int,
        mock_scanner,
        mock_lifecycle,
        mock_finalizer,
        mock_work_orch,
        mock_int_reg,
        mock_health,
        mock_feedback,
        mock_dream,
        mock_stop,
        mock_night,
        mock_cap_reg,
        mock_audit,
    ):
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        mock_cfg = MagicMock()
        mock_cfg.audit_log_dir = Path("/tmp/test_audit")
        mock_cfg.capability_card_dir = MagicMock()
        mock_cfg.night_shift_storage_path = Path(
            "/tmp/test_night"
        )  # 生产跟进：ensure_runtime_dirs 取 .parent，契约为 Path
        mock_cfg.dream_archive_dir = Path("/tmp/test_dream")
        mock_cfg.feedback_proposal_dir = Path("/tmp/test_feedback")
        mock_cfg.health_snapshot_dir = Path("/tmp/test_health")
        mock_cfg.work_dag_dir = Path("/tmp/test_dag")
        mock_cfg.max_parallel_l1 = 2
        mock_cfg.max_parallel_l2 = 2
        mock_cfg.max_parallel_l3 = 2
        mock_cfg.max_daily_l3_activations = 5
        mock_cfg.auto_start_l2 = False
        mock_cfg.ollama_base_url = "http://localhost:11434"
        mock_cfg_cls.return_value = mock_cfg
        core = AutoRuntimeCore(config=mock_cfg)
        assert core.booted is False
        assert core.capability_registry is not None
        assert core.integration_registry is not None
        assert core.work_orchestrator is not None
        assert core.stop_gate is not None

    @patch("zephyr.trading.auto_runtime_core.AiAuditLogger")
    @patch("zephyr.trading.auto_runtime_core.CapabilityRegistry")
    @patch("zephyr.trading.auto_runtime_core.NightShiftQueue")
    @patch("zephyr.trading.auto_runtime_core.StopGate")
    @patch("zephyr.trading.auto_runtime_core.DreamCycle")
    @patch("zephyr.trading.auto_runtime_core.FeedbackLoop")
    @patch("zephyr.trading.auto_runtime_core.HealthMonitor")
    @patch("zephyr.trading.auto_runtime_core.IntegrationRegistry")
    @patch("zephyr.trading.auto_runtime_core.WorkOrchestrator")
    @patch("zephyr.trading.auto_runtime_core.Finalizer")
    @patch("zephyr.trading.auto_runtime_core.LifecycleManager")
    @patch("zephyr.trading.auto_runtime_core.ModuleOnboardingScanner")
    @patch("zephyr.trading.auto_runtime_core.AutoIntegrator")
    @patch("zephyr.trading.auto_runtime_core.OrphanDetector")
    @patch("zephyr.trading.auto_runtime_core.StatusDashboard")
    @patch("zephyr.trading.auto_runtime_core.RuntimeConfig")
    def test_learner_summary_when_not_initialized(
        self,
        mock_cfg_cls,
        mock_dashboard,
        mock_orphan,
        mock_auto_int,
        mock_scanner,
        mock_lifecycle,
        mock_finalizer,
        mock_work_orch,
        mock_int_reg,
        mock_health,
        mock_feedback,
        mock_dream,
        mock_stop,
        mock_night,
        mock_cap_reg,
        mock_audit,
    ):
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        mock_cfg = MagicMock()
        mock_cfg.audit_log_dir = Path("/tmp/test_audit")
        mock_cfg.capability_card_dir = MagicMock()
        mock_cfg.night_shift_storage_path = Path(
            "/tmp/test_night"
        )  # 生产跟进：ensure_runtime_dirs 取 .parent，契约为 Path
        mock_cfg.dream_archive_dir = Path("/tmp/test_dream")
        mock_cfg.feedback_proposal_dir = Path("/tmp/test_feedback")
        mock_cfg.health_snapshot_dir = Path("/tmp/test_health")
        mock_cfg.work_dag_dir = Path("/tmp/test_dag")
        mock_cfg.max_parallel_l1 = 2
        mock_cfg.max_parallel_l2 = 2
        mock_cfg.max_parallel_l3 = 2
        mock_cfg.max_daily_l3_activations = 5
        mock_cfg.auto_start_l2 = False
        mock_cfg.ollama_base_url = "http://localhost:11434"
        mock_cfg_cls.return_value = mock_cfg
        core = AutoRuntimeCore(config=mock_cfg)
        summary = core.learner_summary()
        assert "not initialized" in summary

    @patch("zephyr.trading.auto_runtime_core.AiAuditLogger")
    @patch("zephyr.trading.auto_runtime_core.CapabilityRegistry")
    @patch("zephyr.trading.auto_runtime_core.NightShiftQueue")
    @patch("zephyr.trading.auto_runtime_core.StopGate")
    @patch("zephyr.trading.auto_runtime_core.DreamCycle")
    @patch("zephyr.trading.auto_runtime_core.FeedbackLoop")
    @patch("zephyr.trading.auto_runtime_core.HealthMonitor")
    @patch("zephyr.trading.auto_runtime_core.IntegrationRegistry")
    @patch("zephyr.trading.auto_runtime_core.WorkOrchestrator")
    @patch("zephyr.trading.auto_runtime_core.Finalizer")
    @patch("zephyr.trading.auto_runtime_core.LifecycleManager")
    @patch("zephyr.trading.auto_runtime_core.ModuleOnboardingScanner")
    @patch("zephyr.trading.auto_runtime_core.AutoIntegrator")
    @patch("zephyr.trading.auto_runtime_core.OrphanDetector")
    @patch("zephyr.trading.auto_runtime_core.StatusDashboard")
    @patch("zephyr.trading.auto_runtime_core.RuntimeConfig")
    def test_get_task_model_recommendations_empty(
        self,
        mock_cfg_cls,
        mock_dashboard,
        mock_orphan,
        mock_auto_int,
        mock_scanner,
        mock_lifecycle,
        mock_finalizer,
        mock_work_orch,
        mock_int_reg,
        mock_health,
        mock_feedback,
        mock_dream,
        mock_stop,
        mock_night,
        mock_cap_reg,
        mock_audit,
    ):
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        mock_cfg = MagicMock()
        mock_cfg.audit_log_dir = Path("/tmp/test_audit")
        mock_cfg.capability_card_dir = MagicMock()
        mock_cfg.night_shift_storage_path = Path(
            "/tmp/test_night"
        )  # 生产跟进：ensure_runtime_dirs 取 .parent，契约为 Path
        mock_cfg.dream_archive_dir = Path("/tmp/test_dream")
        mock_cfg.feedback_proposal_dir = Path("/tmp/test_feedback")
        mock_cfg.health_snapshot_dir = Path("/tmp/test_health")
        mock_cfg.work_dag_dir = Path("/tmp/test_dag")
        mock_cfg.max_parallel_l1 = 2
        mock_cfg.max_parallel_l2 = 2
        mock_cfg.max_parallel_l3 = 2
        mock_cfg.max_daily_l3_activations = 5
        mock_cfg.auto_start_l2 = False
        mock_cfg.ollama_base_url = "http://localhost:11434"
        mock_cfg_cls.return_value = mock_cfg
        core = AutoRuntimeCore(config=mock_cfg)
        recs = core.get_task_model_recommendations()
        assert recs == []
