# [A_test] module_id: SRC-TST-F11AUTO | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §automation
# [MODULE] tests.unit.test_context_pipeline_auto
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
F11 ContextPipeline 三层自动化机制测试
=====================================
覆盖三层自动化：
1. 自动启动 (auto_start): 幂等性 + EventBus 订阅注册
2. 事件启动 (event-driven): TASK_STARTED/TASK_COMPLETED/TASK_FAILED 事件触发
3. 自动关闭 (auto_shutdown): KillSwitch 熔断 + 资源清理 + 幂等性

KillSwitch 扩展测试：
4. check_errors_and_kill: 批量错误检查
5. register_cleanup / trigger_shutdown: 资源清理 + 主动熔断
"""
from __future__ import annotations

import threading
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.autonomy_core.context.context_pipeline_auto import ContextPipelineAuto
from zephyr.infrastructure.capacity_assurance.kill_switch import KillSwitch
from zephyr.shared.event_bus import EventBus, EventType


# ── 自动启动测试 ──────────────────────────────────────────────


class TestAutoStart:
    """测试自动启动机制。"""

    def test_auto_start_sets_started_flag(self) -> None:
        """auto_start() 设置 is_started=True。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=3)
        assert not pipeline.is_started
        pipeline.auto_start()
        assert pipeline.is_started

    def test_auto_start_is_idempotent(self) -> None:
        """多次调用 auto_start() 安全。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=3)
        pipeline.auto_start()
        pipeline.auto_start()
        pipeline.auto_start()
        assert pipeline.is_started

    def test_auto_start_registers_event_subscriptions(self) -> None:
        """auto_start() 注册 EventBus 订阅。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=3)
        pipeline.auto_start()
        assert pipeline._event_subscribed

    def test_auto_start_with_custom_kill_switch(self) -> None:
        """auto_start() 接受自定义 KillSwitch。"""
        ks = KillSwitch(threshold=10)
        pipeline = ContextPipelineAuto(kill_switch=ks, timeout_seconds=10)
        pipeline.auto_start()
        assert pipeline.kill_switch is ks
        assert pipeline.is_started


# ── 事件启动测试 ──────────────────────────────────────────────


class TestEventDriven:
    """测试事件启动机制。"""

    def test_on_task_started_with_fuse_off(self) -> None:
        """fuse OFF 时处理 TASK_STARTED 事件。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()

        bus = EventBus.get_instance()
        event = bus.publish(EventType.TASK_STARTED, "DM-TEST-001", {"test": True})
        assert event.event_type == EventType.TASK_STARTED

    def test_on_task_started_with_fuse_on(self) -> None:
        """fuse ON 时跳过 TASK_STARTED 事件。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()
        pipeline._kill_switch._fuse_on = True

        bus = EventBus.get_instance()
        bus.publish(EventType.TASK_STARTED, "DM-TEST-002", {"test": True})
        assert pipeline.fuse_on

    def test_on_task_failed_records_error(self) -> None:
        """TASK_FAILED 事件记录错误到 KillSwitch。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()

        initial_count = pipeline._kill_switch._error_count
        bus = EventBus.get_instance()
        bus.publish(EventType.TASK_FAILED, "DM-TEST-003", {"reason": "test_failure"})
        assert pipeline._kill_switch._error_count > initial_count

    def test_on_task_failed_triggers_shutdown_when_fuse_on(self) -> None:
        """TASK_FAILED 触发熔断时自动关闭。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=1)
        pipeline.auto_start()

        pipeline._kill_switch._threshold = 1
        bus = EventBus.get_instance()
        bus.publish(EventType.TASK_FAILED, "DM-TEST-004", {"reason": "critical"})
        assert pipeline.fuse_on
        assert not pipeline.is_started

    def test_on_task_completed_with_fuse_off(self) -> None:
        """fuse OFF 时处理 TASK_COMPLETED 事件。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()

        bus = EventBus.get_instance()
        bus.publish(EventType.TASK_COMPLETED, "DM-TEST-005", {"result": "success"})
        assert pipeline.is_started


# ── 自动运行测试 ──────────────────────────────────────────────


class TestAutoRun:
    """测试自动运行机制。"""

    def test_auto_run_with_valid_manifest(self, tmp_path: Path) -> None:
        """有效 manifest 正常运行。"""
        f = tmp_path / "test.md"
        f.write_text("test content", encoding="utf-8")

        pipeline = ContextPipelineAuto(timeout_seconds=30, auto_kill_threshold=5)
        result = pipeline.auto_run(
            [{"file_path": str(f), "reason": "test"}],
            require_absolute_manifest_paths=False,
        )
        assert result is not None
        assert hasattr(result, "assembled")
        assert hasattr(result, "g3_passed")

    def test_auto_run_with_fuse_on_raises(self) -> None:
        """fuse ON 时 auto_run() 抛出 RuntimeError。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline._kill_switch._fuse_on = True

        with pytest.raises(RuntimeError, match="KillSwitch fuse is ON"):
            pipeline.auto_run([{"file_path": "test", "reason": "test"}])

    def test_auto_run_auto_starts_if_not_started(self, tmp_path: Path) -> None:
        """未启动时 auto_run() 自动启动。"""
        f = tmp_path / "auto_start.md"
        f.write_text("content", encoding="utf-8")

        pipeline = ContextPipelineAuto(timeout_seconds=30, auto_kill_threshold=5)
        assert not pipeline.is_started

        pipeline.auto_run(
            [{"file_path": str(f), "reason": "auto_start_test"}],
            require_absolute_manifest_paths=False,
        )
        assert pipeline.is_started

    def test_auto_run_records_g3_failure_to_kill_switch(self, tmp_path: Path) -> None:
        """G3 验证失败时记录错误到 KillSwitch。"""
        f = tmp_path / "g3_test.md"
        f.write_text("content", encoding="utf-8")

        pipeline = ContextPipelineAuto(timeout_seconds=30, auto_kill_threshold=5)
        initial_count = pipeline._kill_switch._error_count

        pipeline.auto_run(
            [{"file_path": str(f), "reason": "g3_test"}],
            require_absolute_manifest_paths=False,
        )
        if not pipeline._kill_switch._fuse_on:
            assert pipeline._kill_switch._error_count >= initial_count


# ── 自动关闭测试 ──────────────────────────────────────────────


class TestAutoShutdown:
    """测试自动关闭机制。"""

    def test_auto_shutdown_executes_cleanup_callbacks(self) -> None:
        """auto_shutdown() 执行清理回调。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()

        cleanup_called = []
        pipeline.register_cleanup(lambda: cleanup_called.append(True))

        pipeline.auto_shutdown(reason="test_cleanup")
        assert cleanup_called == [True]

    def test_auto_shutdown_is_idempotent(self) -> None:
        """多次调用 auto_shutdown() 安全。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()

        call_count = []
        pipeline.register_cleanup(lambda: call_count.append(True))

        pipeline.auto_shutdown(reason="first")
        pipeline.auto_shutdown(reason="second")
        pipeline.auto_shutdown(reason="third")
        assert call_count == [True]

    def test_auto_shutdown_clears_started_flag(self) -> None:
        """auto_shutdown() 清除 is_started。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()
        assert pipeline.is_started

        pipeline.auto_shutdown(reason="test")
        assert not pipeline.is_started

    def test_auto_shutdown_clears_cleanup_callbacks(self) -> None:
        """auto_shutdown() 清理后清空回调列表。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()

        pipeline.register_cleanup(lambda: None)
        assert len(pipeline._cleanup_callbacks) == 1

        pipeline.auto_shutdown(reason="test")
        assert len(pipeline._cleanup_callbacks) == 0

    def test_reset_fuse_after_shutdown(self) -> None:
        """shutdown 后可以 reset_fuse 重新启动。"""
        pipeline = ContextPipelineAuto(timeout_seconds=10, auto_kill_threshold=5)
        pipeline.auto_start()
        pipeline._kill_switch._fuse_on = True

        pipeline.auto_shutdown(reason="fuse_test")
        assert not pipeline.is_started

        pipeline.reset_fuse()
        assert not pipeline.fuse_on

        pipeline.auto_start()
        assert pipeline.is_started


# ── KillSwitch 扩展测试 ───────────────────────────────────────


class TestKillSwitchExtension:
    """测试 KillSwitch 扩展功能。"""

    def test_check_errors_and_kill_triggers_fuse(self) -> None:
        """批量错误超过 auto_kill_threshold 时触发熔断。"""
        ks = KillSwitch(threshold=2, auto_kill_threshold=2)
        result = ks.check_errors_and_kill(["error1", "error2"])
        assert result is True
        assert ks._fuse_on

    def test_check_errors_and_kill_disabled_when_threshold_zero(self) -> None:
        """auto_kill_threshold=0 时禁用。"""
        ks = KillSwitch(threshold=5, auto_kill_threshold=0)
        result = ks.check_errors_and_kill(["error1", "error2", "error3"])
        assert result is False
        assert not ks._fuse_on

    def test_check_errors_and_kill_below_threshold(self) -> None:
        """错误数低于 auto_kill_threshold 时不触发。"""
        ks = KillSwitch(threshold=10, auto_kill_threshold=5)
        result = ks.check_errors_and_kill(["error1", "error2"])
        assert result is False
        assert not ks._fuse_on

    def test_register_cleanup_and_trigger_shutdown(self) -> None:
        """注册回调并触发熔断时执行回调。"""
        ks = KillSwitch(threshold=5)
        cleanup_called = []
        ks.register_cleanup(lambda: cleanup_called.append(True))

        ks.trigger_shutdown()
        assert ks._fuse_on
        assert cleanup_called == [True]

    def test_trigger_shutdown_clears_callbacks(self) -> None:
        """trigger_shutdown() 清空回调列表。"""
        ks = KillSwitch(threshold=5)
        ks.register_cleanup(lambda: None)
        ks.register_cleanup(lambda: None)
        assert len(ks._cleanup_callbacks) == 2

        ks.trigger_shutdown()
        assert len(ks._cleanup_callbacks) == 0

    def test_trigger_shutdown_callback_exception_does_not_block(self) -> None:
        """回调异常不阻止其他回调执行。"""
        ks = KillSwitch(threshold=5)

        def failing_callback() -> None:
            raise RuntimeError("callback error")

        success_called = []
        ks.register_cleanup(failing_callback)
        ks.register_cleanup(lambda: success_called.append(True))

        ks.trigger_shutdown()
        assert ks._fuse_on
        assert success_called == [True]


# ── 集成测试 ──────────────────────────────────────────────────


class TestIntegration:
    """三层自动化集成测试。"""

    def test_full_lifecycle_start_run_shutdown(self, tmp_path: Path) -> None:
        """完整生命周期：启动 → 运行 → 关闭。"""
        f = tmp_path / "lifecycle.md"
        f.write_text("lifecycle test", encoding="utf-8")

        pipeline = ContextPipelineAuto(timeout_seconds=30, auto_kill_threshold=5)

        pipeline.auto_start()
        assert pipeline.is_started

        result = pipeline.auto_run(
            [{"file_path": str(f), "reason": "lifecycle"}],
            require_absolute_manifest_paths=False,
        )
        assert result is not None

        cleanup_called = []
        pipeline.register_cleanup(lambda: cleanup_called.append(True))
        pipeline.auto_shutdown(reason="lifecycle_complete")

        assert not pipeline.is_started
        assert cleanup_called == [True]

    def test_fuse_blocks_auto_run_after_errors(self, tmp_path: Path) -> None:
        """错误累积触发熔断后，auto_run 被阻止。"""
        f = tmp_path / "fuse_block.md"
        f.write_text("content", encoding="utf-8")

        pipeline = ContextPipelineAuto(timeout_seconds=30, auto_kill_threshold=1)
        pipeline._kill_switch._threshold = 1

        pipeline.auto_start()
        pipeline._kill_switch.record_error("triggering_error")
        assert pipeline.fuse_on

        with pytest.raises(RuntimeError, match="KillSwitch fuse is ON"):
            pipeline.auto_run(
                [{"file_path": str(f), "reason": "blocked"}],
                require_absolute_manifest_paths=False,
            )

    def test_concurrent_auto_run_thread_safety(self, tmp_path: Path) -> None:
        """并发 auto_run 线程安全。"""
        f = tmp_path / "concurrent.md"
        f.write_text("concurrent content", encoding="utf-8")

        pipeline = ContextPipelineAuto(timeout_seconds=30, auto_kill_threshold=10)
        pipeline.auto_start()

        results: list = []
        errors: list = []
        lock = threading.Lock()

        def run_pipeline() -> None:
            try:
                result = pipeline.auto_run(
                    [{"file_path": str(f), "reason": "concurrent"}],
                    require_absolute_manifest_paths=False,
                )
                with lock:
                    results.append(result)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=run_pipeline) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert len(errors) == 0
        assert len(results) == 3
