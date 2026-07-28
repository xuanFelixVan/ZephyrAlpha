# [A_test] module_id: MOD-GOV_pipeline_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-544 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.pipeline.test_pipeline_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: pipeline_core"""

import time

from zephyr.infrastructure.pipeline.backpressure_manager import (
    BackpressureManager,
    BpState,
    emit_pause,
    emit_resume,
    emit_throttle,
)
from zephyr.infrastructure.pipeline.backpressure_types import (
    BackpressurePause,
    BackpressureResume,
    BackpressureThrottle,
)
from zephyr.infrastructure.pipeline.models import PipelineOrchestratorConfig


class TestBackpressureManager:
    def test_initial_state_is_empty(self):
        mgr = BackpressureManager()
        stats = mgr.get_stats()
        assert stats["total_tracked_symbols"] == 0
        assert stats["paused_count"] == 0
        assert stats["throttled_count"] == 0

    def test_handle_pause(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-001",
            symbol="BTC-PERP",
            duration_ms=5000,
            reason="queue overload",
            idempotency_key="key-001",
        )
        state = mgr.handle_pause(signal)
        assert state.state == BpState.PAUSED
        assert state.symbol == "BTC-PERP"
        assert state.reason == "queue overload"

    def test_handle_throttle(self):
        mgr = BackpressureManager()
        signal = BackpressureThrottle(
            signal_id="sig-002",
            symbol="ETH-PERP",
            max_rate_per_sec=10,
            reason="queue building up",
            idempotency_key="key-002",
        )
        state = mgr.handle_throttle(signal)
        assert state.state == BpState.THROTTLED
        assert state.max_rate_per_sec == 10

    def test_handle_resume(self):
        mgr = BackpressureManager()
        pause = BackpressurePause(
            signal_id="sig-003",
            symbol="SOL-PERP",
            duration_ms=5000,
            reason="overload",
            idempotency_key="key-003",
        )
        mgr.handle_pause(pause)
        resume = BackpressureResume(
            signal_id="sig-004",
            symbol="SOL-PERP",
            reason="recovered",
            idempotency_key="key-004",
        )
        state = mgr.handle_resume(resume)
        assert state.state == BpState.NORMAL

    def test_is_blocked_when_paused(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-005",
            symbol="DOGE-PERP",
            duration_ms=60000,
            reason="overload",
            idempotency_key="key-005",
        )
        mgr.handle_pause(signal)
        assert mgr.is_blocked("DOGE-PERP") is True

    def test_is_not_blocked_when_normal(self):
        mgr = BackpressureManager()
        assert mgr.is_blocked("UNKNOWN-SYMBOL") is False

    def test_auto_resume_after_timeout(self):
        mgr = BackpressureManager()
        signal = BackpressurePause(
            signal_id="sig-006",
            symbol="XRP-PERP",
            duration_ms=10,
            reason="brief pause",
            idempotency_key="key-006",
        )
        mgr.handle_pause(signal)
        assert mgr.is_blocked("XRP-PERP") is True
        time.sleep(0.02)
        assert mgr.is_blocked("XRP-PERP") is False

    def test_get_state_creates_default(self):
        mgr = BackpressureManager()
        state = mgr.get_state("NEW-SYMBOL")
        assert state.symbol == "NEW-SYMBOL"
        assert state.state == BpState.NORMAL

    def test_get_all_paused(self):
        mgr = BackpressureManager()
        mgr.handle_pause(
            BackpressurePause(
                signal_id="s1",
                symbol="A",
                duration_ms=60000,
                reason="r",
                idempotency_key="k1",
            )
        )
        mgr.handle_pause(
            BackpressurePause(
                signal_id="s2",
                symbol="B",
                duration_ms=60000,
                reason="r",
                idempotency_key="k2",
            )
        )
        paused = mgr.get_all_paused()
        assert len(paused) == 2

    def test_get_all_throttled(self):
        mgr = BackpressureManager()
        mgr.handle_throttle(
            BackpressureThrottle(
                signal_id="s3",
                symbol="C",
                max_rate_per_sec=5,
                reason="r",
                idempotency_key="k3",
            )
        )
        throttled = mgr.get_all_throttled()
        assert len(throttled) == 1
        assert throttled[0].max_rate_per_sec == 5

    def test_stats_tracking(self):
        mgr = BackpressureManager()
        mgr.handle_pause(
            BackpressurePause(
                signal_id="s4",
                symbol="D",
                duration_ms=60000,
                reason="r",
                idempotency_key="k4",
            )
        )
        mgr.handle_throttle(
            BackpressureThrottle(
                signal_id="s5",
                symbol="E",
                max_rate_per_sec=5,
                reason="r",
                idempotency_key="k5",
            )
        )
        stats = mgr.get_stats()
        assert stats["total_tracked_symbols"] == 2
        assert stats["paused_count"] == 1
        assert stats["throttled_count"] == 1
        assert stats["normal_count"] == 0

    def test_callback_on_pause(self):
        mgr = BackpressureManager()
        received = []
        mgr.register_on_pause(lambda s: received.append(s.symbol))
        mgr.handle_pause(
            BackpressurePause(
                signal_id="s6",
                symbol="F",
                duration_ms=60000,
                reason="r",
                idempotency_key="k6",
            )
        )
        assert received == ["F"]

    def test_callback_on_resume(self):
        mgr = BackpressureManager()
        received = []
        mgr.register_on_resume(lambda s: received.append(s.symbol))
        mgr.handle_pause(
            BackpressurePause(
                signal_id="s7",
                symbol="G",
                duration_ms=60000,
                reason="r",
                idempotency_key="k7",
            )
        )
        mgr.handle_resume(
            BackpressureResume(
                signal_id="s8",
                symbol="G",
                reason="recovered",
                idempotency_key="k8",
            )
        )
        assert "G" in received

    def test_callback_on_throttle(self):
        mgr = BackpressureManager()
        received = []
        mgr.register_on_throttle(lambda s: received.append(s.symbol))
        mgr.handle_throttle(
            BackpressureThrottle(
                signal_id="s9",
                symbol="H",
                max_rate_per_sec=5,
                reason="r",
                idempotency_key="k9",
            )
        )
        assert received == ["H"]

    def test_clear_resets_all(self):
        mgr = BackpressureManager()
        mgr.handle_pause(
            BackpressurePause(
                signal_id="s10",
                symbol="I",
                duration_ms=60000,
                reason="r",
                idempotency_key="k10",
            )
        )
        mgr.clear()
        stats = mgr.get_stats()
        assert stats["total_tracked_symbols"] == 0

    def test_emit_pause_helper(self):
        mgr = BackpressureManager()
        state = emit_pause(mgr, "J", 5000, "test")
        assert state.state == BpState.PAUSED
        assert state.symbol == "J"

    def test_emit_throttle_helper(self):
        mgr = BackpressureManager()
        state = emit_throttle(mgr, "K", 10, "test")
        assert state.state == BpState.THROTTLED
        assert state.max_rate_per_sec == 10

    def test_emit_resume_helper(self):
        mgr = BackpressureManager()
        emit_pause(mgr, "L", 5000, "test")
        state = emit_resume(mgr, "L", "recovered")
        assert state.state == BpState.NORMAL


class TestPipelineOrchestratorConfig:
    def test_default_config(self):
        cfg = PipelineOrchestratorConfig()
        assert cfg.max_retries >= 1
        assert cfg.claude_rescue_threshold >= 1

    def test_custom_config(self):
        cfg = PipelineOrchestratorConfig(max_retries=5, claude_rescue_threshold=2)
        assert cfg.max_retries == 5
        assert cfg.claude_rescue_threshold == 2


class TestPipelineOrchestratorInit:
    def test_init_with_defaults(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        orc = PipelineOrchestrator()
        assert orc._cfg is not None
        assert orc._failure_log == {}
        assert orc._active_dispatches == set()

    def test_init_with_custom_config(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        cfg = PipelineOrchestratorConfig(max_retries=7)
        orc = PipelineOrchestrator(config=cfg)
        assert orc._cfg.max_retries == 7

    def test_health_check_returns_dict(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        orc = PipelineOrchestrator()
        hc = orc.health_check()
        assert isinstance(hc, dict)
        assert "module" in hc
        assert "status" in hc

    def test_save_and_load_state(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        orc = PipelineOrchestrator()
        orc._failure_log["test"] = 3
        state = orc.save_state()
        assert "failure_log" in state
        assert state["failure_log"]["test"] == 3

    def test_get_telemetry_snapshot(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        orc = PipelineOrchestrator()
        snap = orc.get_telemetry_snapshot()
        assert "metrics" in snap
        assert "latency_samples" in snap

    def test_get_cost_summary(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        orc = PipelineOrchestrator()
        summary = orc.get_cost_summary()
        assert isinstance(summary, dict)

    def test_set_token_budget(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        orc = PipelineOrchestrator()
        orc.set_token_budget(500_000)
        assert orc._token_budget_total == 500_000

    def test_text_similarity(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        sim = PipelineOrchestrator.text_similarity("hello world foo", "hello world bar")
        assert 0.0 < sim < 1.0

    def test_text_similarity_identical(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        sim = PipelineOrchestrator.text_similarity("hello world test", "hello world test")
        assert sim == 1.0

    def test_text_similarity_empty(self):
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        assert PipelineOrchestrator.text_similarity("", "hello") == 0.0
        assert PipelineOrchestrator.text_similarity("hello", "") == 0.0

    def test_determine_status_all_success(self):
        from zephyr.infrastructure.pipeline.models import ModuleResult, ModuleStatus, PipelineStatus
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        results = [
            ModuleResult(
                module_id="M1",
                pipeline="A",
                model="deepseek",
                status=ModuleStatus.SUCCESS,
                output={},
                started_at="",
                finished_at="",
            ),
        ]
        assert PipelineOrchestrator.determine_status(results) == PipelineStatus.SUCCESS

    def test_determine_status_all_failure(self):
        from zephyr.infrastructure.pipeline.models import ModuleResult, ModuleStatus, PipelineStatus
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        results = [
            ModuleResult(
                module_id="M1",
                pipeline="A",
                model="deepseek",
                status=ModuleStatus.FAILURE,
                output={},
                errors=["err"],
                started_at="",
                finished_at="",
            ),
        ]
        assert PipelineOrchestrator.determine_status(results) == PipelineStatus.FAILURE

    def test_determine_status_empty(self):
        from zephyr.infrastructure.pipeline.models import PipelineStatus
        from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator

        assert PipelineOrchestrator.determine_status([]) == PipelineStatus.FAILURE
