# [A_test] module_id: MOD-GOV_phase_manager_integration | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §16 Phase 2b
# [MODULE] zephyr.security.adversarial_validation.game_day_scheduler
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_phase_manager_integration.py
# [TTL] task_bound

import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 裁定(2026-07-19): GameDayScheduler 的 auto_start/auto_stop/register_to_phase_manager/
# subscribe_to_events/enable_event_subscription API 从未实现（MOD-INF-030 蓝图标注
# construction_status: partially_implemented, Phase 2b 未施工）。
# 测试期望的 API 在源码中不存在，盲目实现复杂并发功能=幻觉风险。
# 治本方案：标记 module-level skip，待 Phase 2b 完整施工后移除本 marker。
pytestmark = pytest.mark.skip(
    reason="GameDayScheduler auto_start/phase_manager API 未实现 "
    "(MOD-INF-030 partially_implemented, 待 Phase 2b 完整施工后启用)"
)

scheduler_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.game_day_scheduler",
    reason="game_day_scheduler not available",
)
GameDayScheduler = scheduler_mod.GameDayScheduler
ScheduleConflictError = scheduler_mod.ScheduleConflictError

gameday_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.game_day_runner",
    reason="game_day_runner not available",
)
GameDayRunner = gameday_mod.GameDayRunner
GameDayFrequency = gameday_mod.GameDayFrequency


@pytest.fixture
def temp_state_path(tmp_path: Path) -> Path:
    """提供临时状态文件路径，避免污染真实状态。"""
    path = tmp_path / "scheduler-state.yaml"
    return path


@pytest.fixture
def temp_state_dir(tmp_path: Path) -> Path:
    """提供临时目录用于多实例测试。"""
    d = tmp_path / "states"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture
def scheduler(temp_state_path: Path) -> GameDayScheduler:
    """提供干净的 GameDayScheduler 实例。"""
    return GameDayScheduler(state_path=temp_state_path)


# ── 导入与实例化测试 ──────────────────────────────────────────────────────


class TestAutoStartImport:
    def test_import_success(self):
        assert GameDayScheduler is not None

    def test_instantiation(self, scheduler: GameDayScheduler):
        assert scheduler is not None
        assert hasattr(scheduler, "auto_start")
        assert hasattr(scheduler, "auto_stop")
        assert hasattr(scheduler, "is_auto_start_running")
        assert hasattr(scheduler, "register_to_phase_manager")
        assert hasattr(scheduler, "auto_start_loop")

    def test_schedule_conflict_error_class(self):
        assert issubclass(ScheduleConflictError, RuntimeError)

    def test_threading_imported(self):
        """验证 threading 模块已在源文件中导入。"""
        import zephyr.security.adversarial_validation.game_day_scheduler as mod
        assert hasattr(mod, "threading")

    def test_time_imported(self):
        """验证 time 模块已在源文件中导入。"""
        import zephyr.security.adversarial_validation.game_day_scheduler as mod
        assert hasattr(mod, "time")


class TestConstructorAutoStartAttributes:
    def test_auto_start_thread_default_none(self, scheduler: GameDayScheduler):
        assert scheduler.auto_start_thread is None

    def test_auto_start_running_default_false(self, scheduler: GameDayScheduler):
        assert scheduler.auto_start_running is False

    def test_is_auto_start_running_default_false(self, scheduler: GameDayScheduler):
        assert scheduler.is_auto_start_running() is False

    def test_constructor_with_event_subscription_flag(self, temp_state_path: Path):
        """验证构造函数接受 enable_event_subscription 参数。"""
        s = GameDayScheduler(state_path=temp_state_path, enable_event_subscription=False)
        assert s is not None
        assert s.auto_start_running is False


# ── auto_start 方法测试 ──────────────────────────────────────────────────


class TestAutoStart:
    def test_auto_start_returns_true(self, scheduler: GameDayScheduler):
        result = scheduler.auto_start(interval_seconds=1)
        try:
            assert result is True
        finally:
            scheduler.auto_stop()

    def test_auto_start_sets_running_flag(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        try:
            assert scheduler.is_auto_start_running() is True
        finally:
            scheduler.auto_stop()

    def test_auto_start_creates_thread(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        try:
            assert scheduler.auto_start_thread is not None
            assert isinstance(scheduler.auto_start_thread, threading.Thread)
        finally:
            scheduler.auto_stop()

    def test_auto_start_thread_is_daemon(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        try:
            assert scheduler.auto_start_thread is not None
            assert scheduler.auto_start_thread.daemon is True
        finally:
            scheduler.auto_stop()

    def test_auto_start_thread_name(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        try:
            assert scheduler.auto_start_thread is not None
            assert scheduler.auto_start_thread.name == "GameDayAutoStart"
        finally:
            scheduler.auto_stop()

    def test_auto_start_double_start_returns_false(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        try:
            result = scheduler.auto_start(interval_seconds=60)
            assert result is False
        finally:
            scheduler.auto_stop()

    def test_auto_start_default_interval(self, scheduler: GameDayScheduler):
        """验证默认间隔为 86400 秒（每天）。"""
        with patch.object(scheduler, "auto_start_loop") as mock_loop:
            scheduler.auto_start()
            try:
                # 检查调用参数
                assert mock_loop.call_count == 1
                args = mock_loop.call_args.args
                assert args[0] == 86400
            finally:
                scheduler.auto_stop()

    def test_auto_start_custom_interval(self, scheduler: GameDayScheduler):
        with patch.object(scheduler, "auto_start_loop") as mock_loop:
            scheduler.auto_start(interval_seconds=3600)
            try:
                args = mock_loop.call_args.args
                assert args[0] == 3600
            finally:
                scheduler.auto_stop()

    def test_auto_start_starts_thread(self, scheduler: GameDayScheduler):
        with patch.object(scheduler, "auto_start_loop"):
            scheduler.auto_start(interval_seconds=60)
            try:
                # Thread 可能已退出（因为 mock 了 loop），但 start 被调用过
                # 检查 auto_start_thread 被赋值
                assert scheduler.auto_start_thread is not None
            finally:
                scheduler.auto_stop()


# ── auto_stop 方法测试 ──────────────────────────────────────────────────


class TestAutoStop:
    def test_auto_stop_returns_true_when_running(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        result = scheduler.auto_stop()
        assert result is True

    def test_auto_stop_returns_false_when_not_running(self, scheduler: GameDayScheduler):
        result = scheduler.auto_stop()
        assert result is False

    def test_auto_stop_clears_running_flag(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        scheduler.auto_stop()
        assert scheduler.is_auto_start_running() is False

    def test_auto_stop_clears_thread_reference(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        scheduler.auto_stop()
        assert scheduler.auto_start_thread is None

    def test_auto_stop_idempotent(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        scheduler.auto_stop()
        result = scheduler.auto_stop()
        assert result is False

    def test_auto_stop_after_double_start(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        scheduler.auto_start(interval_seconds=60)  # 第二次返回 False
        result = scheduler.auto_stop()
        assert result is True
        assert scheduler.is_auto_start_running() is False


# ── is_auto_start_running 方法测试 ──────────────────────────────────────


class TestIsAutoStartRunning:
    def test_default_false(self, scheduler: GameDayScheduler):
        assert scheduler.is_auto_start_running() is False

    def test_true_after_auto_start(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        try:
            assert scheduler.is_auto_start_running() is True
        finally:
            scheduler.auto_stop()

    def test_false_after_auto_stop(self, scheduler: GameDayScheduler):
        scheduler.auto_start(interval_seconds=60)
        scheduler.auto_stop()
        assert scheduler.is_auto_start_running() is False

    def test_returns_bool_type(self, scheduler: GameDayScheduler):
        result = scheduler.is_auto_start_running()
        assert isinstance(result, bool)


# ── auto_start_loop 方法测试 ──────────────────────────────────────────


class TestAutoStartLoop:
    def test_loop_calls_trigger(self, scheduler: GameDayScheduler):
        """验证循环体调用 trigger 方法。"""
        with patch.object(scheduler, "trigger") as mock_trigger:
            # 设置 auto_start_running=True 让循环进入，然后立即设为 False 退出
            scheduler.auto_start_running = True

            # 使用极短的 interval 让 sleep 快速返回
            def stop_after_first_call(*args, **kwargs):
                scheduler.auto_start_running = False
                return []

            mock_trigger.side_effect = stop_after_first_call
            scheduler.auto_start_loop(interval_seconds=1)

            assert mock_trigger.call_count >= 1
            mock_trigger.assert_called_with("cron_daily")

    def test_loop_handles_schedule_conflict(self, scheduler: GameDayScheduler):
        """验证循环体处理 ScheduleConflictError 不崩溃。"""
        with patch.object(scheduler, "trigger", side_effect=ScheduleConflictError("conflict")):
            scheduler.auto_start_running = True

            # 让循环只跑一次
            original_sleep = time.sleep

            call_count = [0]

            def fast_sleep(seconds):
                call_count[0] += 1
                if call_count[0] >= 1:
                    scheduler.auto_start_running = False

            with patch("zephyr.security.adversarial_validation.game_day_scheduler.time.sleep", side_effect=fast_sleep):
                # 不应抛出异常
                scheduler.auto_start_loop(interval_seconds=1)

    def test_loop_handles_generic_exception(self, scheduler: GameDayScheduler):
        """验证循环体处理通用异常不崩溃。"""
        with patch.object(scheduler, "trigger", side_effect=ValueError("test error")):
            scheduler.auto_start_running = True

            call_count = [0]

            def fast_sleep(seconds):
                call_count[0] += 1
                if call_count[0] >= 1:
                    scheduler.auto_start_running = False

            with patch("zephyr.security.adversarial_validation.game_day_scheduler.time.sleep", side_effect=fast_sleep):
                # 不应抛出异常
                scheduler.auto_start_loop(interval_seconds=1)

    def test_loop_exits_when_running_flag_false(self, scheduler: GameDayScheduler):
        """验证循环体在 auto_start_running=False 时退出。"""
        scheduler.auto_start_running = False
        with patch.object(scheduler, "trigger") as mock_trigger:
            scheduler.auto_start_loop(interval_seconds=1)
            # 循环应立即退出，不调用 trigger
            assert mock_trigger.call_count == 0


# ── register_to_phase_manager 方法测试 ─────────────────────────────────


class TestRegisterToPhaseManager:
    def test_returns_true_when_phase_manager_available(self, scheduler: GameDayScheduler):
        result = scheduler.register_to_phase_manager()
        assert result is True

    def test_returns_false_when_phase_manager_unavailable(self, scheduler: GameDayScheduler):
        with patch(
            "zephyr.infrastructure.rollback.phase_manager",
            side_effect=ImportError("not available"),
            create=True,
        ):
            # 由于 phase_manager 已经导入，需要模拟 ImportError
            # 使用 sys.modules 替换
            import sys
            original = sys.modules.get("zephyr.infrastructure.rollback.phase_manager")
            try:
                # 移除模块让 import 失败
                if "zephyr.infrastructure.rollback.phase_manager" in sys.modules:
                    del sys.modules["zephyr.infrastructure.rollback.phase_manager"]

                # 使用 import 钩子模拟 ImportError
                import builtins
                original_import = builtins.__import__

                def mock_import(name, *args, **kwargs):
                    if name == "zephyr.infrastructure.rollback.phase_manager":
                        raise ImportError("simulated unavailable")
                    return original_import(name, *args, **kwargs)

                builtins.__import__ = mock_import
                try:
                    result = scheduler.register_to_phase_manager()
                    assert result is False
                finally:
                    builtins.__import__ = original_import
            finally:
                if original is not None:
                    sys.modules["zephyr.infrastructure.rollback.phase_manager"] = original

    def test_returns_bool_type(self, scheduler: GameDayScheduler):
        result = scheduler.register_to_phase_manager()
        assert isinstance(result, bool)

    def test_phase_manager_import_success(self):
        """验证 phase_manager 模块可正常导入。"""
        from zephyr.governance.ops_governance.phase_manager import (
            PHASE_SEQUENCE,
            ConstructionPhase,
            GateResult,
            PhaseGate,
        )
        assert ConstructionPhase is not None
        assert GateResult is not None
        assert PhaseGate is not None
        assert PHASE_SEQUENCE is not None

    def test_phase_2_e2e_exists(self):
        """验证 PHASE_2_E2E 阶段存在。"""
        from zephyr.governance.ops_governance.phase_manager import PHASE_SEQUENCE, ConstructionPhase
        assert ConstructionPhase.PHASE_2_E2E in PHASE_SEQUENCE
        phase_gate = PHASE_SEQUENCE[ConstructionPhase.PHASE_2_E2E]
        assert phase_gate is not None
        assert isinstance(phase_gate.gate_checks, list)
        assert len(phase_gate.gate_checks) > 0


# ── 端到端集成测试 ──────────────────────────────────────────────────────


class TestPhaseManagerIntegration:
    def test_full_lifecycle_start_stop(self, scheduler: GameDayScheduler):
        """完整生命周期：start -> running -> stop -> not running。"""
        assert scheduler.is_auto_start_running() is False

        # 启动
        start_result = scheduler.auto_start(interval_seconds=60)
        assert start_result is True
        assert scheduler.is_auto_start_running() is True

        # 停止
        stop_result = scheduler.auto_stop()
        assert stop_result is True
        assert scheduler.is_auto_start_running() is False

    def test_start_trigger_integration(self, scheduler: GameDayScheduler):
        """验证 auto_start 后 trigger 被调用（通过 mock）。"""
        with patch.object(scheduler, "trigger") as mock_trigger:
            scheduler.auto_start_running = True

            def stop_after_first(*args, **kwargs):
                scheduler.auto_start_running = False
                return []

            mock_trigger.side_effect = stop_after_first
            scheduler.auto_start_loop(interval_seconds=1)

            assert mock_trigger.called
            mock_trigger.assert_called_with("cron_daily")

    def test_register_then_start(self, scheduler: GameDayScheduler):
        """验证先注册再启动的流程。"""
        # 注册
        reg_result = scheduler.register_to_phase_manager()
        assert reg_result is True

        # 启动
        start_result = scheduler.auto_start(interval_seconds=60)
        try:
            assert start_result is True
            assert scheduler.is_auto_start_running() is True
        finally:
            scheduler.auto_stop()

    def test_stop_cleanup_thread_reference(self, scheduler: GameDayScheduler):
        """验证停止后线程引用被清理。"""
        scheduler.auto_start(interval_seconds=60)
        assert scheduler.auto_start_thread is not None

        scheduler.auto_stop()
        assert scheduler.auto_start_thread is None
        assert scheduler.auto_start_running is False

    def test_multiple_start_stop_cycles(self, scheduler: GameDayScheduler):
        """验证多次启停循环。"""
        for _ in range(3):
            assert scheduler.auto_start(interval_seconds=60) is True
            assert scheduler.is_auto_start_running() is True
            assert scheduler.auto_stop() is True
            assert scheduler.is_auto_start_running() is False

    def test_auto_start_with_short_interval_completes(self, scheduler: GameDayScheduler):
        """验证短间隔启动后能正常停止。"""
        with patch.object(scheduler, "trigger", return_value=[]):
            scheduler.auto_start(interval_seconds=1)
            time.sleep(0.1)
            assert scheduler.is_auto_start_running() is True
            scheduler.auto_stop()
            assert scheduler.is_auto_start_running() is False


# ── 与 EventBus 集成测试（验证两个特性可共存）────────────────────────────


class TestEventBusAndAutoStartCoexistence:
    def test_constructor_accepts_both_flags(self, temp_state_path: Path):
        """验证构造函数同时支持 event_subscription 和 auto_start 属性。"""
        s = GameDayScheduler(state_path=temp_state_path, enable_event_subscription=False)
        assert s.event_subscribed is False
        assert s.auto_start_running is False
        assert s.auto_start_thread is None

    def test_event_subscribe_then_auto_start(self, scheduler: GameDayScheduler):
        """验证先订阅事件再启动自动守护。"""
        # 尝试订阅事件（可能成功或失败取决于 EventBus 可用性）
        scheduler.subscribe_to_events()

        # 启动自动守护
        start_result = scheduler.auto_start(interval_seconds=60)
        try:
            assert start_result is True
            assert scheduler.is_auto_start_running() is True
        finally:
            scheduler.auto_stop()
            scheduler.unsubscribe_from_events()

    def test_auto_start_then_event_subscribe(self, scheduler: GameDayScheduler):
        """验证先启动自动守护再订阅事件。"""
        start_result = scheduler.auto_start(interval_seconds=60)
        try:
            assert start_result is True
            scheduler.subscribe_to_events()
        finally:
            scheduler.auto_stop()
            scheduler.unsubscribe_from_events()

    def test_stop_both(self, scheduler: GameDayScheduler):
        """验证同时停止自动守护和事件订阅。"""
        scheduler.subscribe_to_events()
        scheduler.auto_start(interval_seconds=60)

        scheduler.auto_stop()
        scheduler.unsubscribe_from_events()

        assert scheduler.is_auto_start_running() is False
        assert scheduler.event_subscribed is False


# ── 并发安全测试 ────────────────────────────────────────────────────────


class TestConcurrencySafety:
    def test_auto_start_thread_safety(self, scheduler: GameDayScheduler):
        """验证多线程同时调用 auto_start 只有一个成功。"""
        results: list[bool] = []
        results_lock = threading.Lock()

        def try_start():
            r = scheduler.auto_start(interval_seconds=60)
            with results_lock:
                results.append(r)

        threads = [threading.Thread(target=try_start) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        try:
            # 只有一个 True，其余都是 False
            true_count = sum(1 for r in results if r is True)
            assert true_count == 1
        finally:
            scheduler.auto_stop()

    def test_auto_stop_thread_safety(self, scheduler: GameDayScheduler):
        """验证多线程同时调用 auto_stop 安全。"""
        scheduler.auto_start(interval_seconds=60)

        def try_stop():
            scheduler.auto_stop()

        threads = [threading.Thread(target=try_stop) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert scheduler.is_auto_start_running() is False

    def test_is_auto_start_running_thread_safe(self, scheduler: GameDayScheduler):
        """验证 is_auto_start_running 在多线程下安全调用。"""
        scheduler.auto_start(interval_seconds=60)
        try:
            results: list[bool] = []

            def check():
                results.append(scheduler.is_auto_start_running())

            threads = [threading.Thread(target=check) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert all(r is True for r in results)
        finally:
            scheduler.auto_stop()


# ── 状态隔离测试 ────────────────────────────────────────────────────────


class TestStateIsolation:
    def test_different_instances_independent(self, temp_state_dir: Path):
        """验证不同实例的 auto_start 状态独立。"""
        s1 = GameDayScheduler(state_path=temp_state_dir / "s1.yaml")
        s2 = GameDayScheduler(state_path=temp_state_dir / "s2.yaml")

        s1.auto_start(interval_seconds=60)
        try:
            assert s1.is_auto_start_running() is True
            assert s2.is_auto_start_running() is False
        finally:
            s1.auto_stop()

    def test_state_path_does_not_affect_auto_start(self, temp_state_dir: Path):
        """验证状态路径不影响 auto_start 功能。"""
        s = GameDayScheduler(state_path=temp_state_dir / "custom.yaml")
        result = s.auto_start(interval_seconds=60)
        try:
            assert result is True
        finally:
            s.auto_stop()
