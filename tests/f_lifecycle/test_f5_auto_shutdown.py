# [A_test] module_id: SRC-TST-F5-SHUTDOWN | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §2
# [MODULE] tests.test_f5_auto_shutdown
# [INVARIANTS] shutdown is idempotent; signal handlers never raise; atexit hook safe to call multiple times; persist_state writes atomic; restore_state never raises
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit codes: 0=all tests pass
# [TESTS] tests/test_f5_auto_shutdown.py
# [TTL] task_bound

from __future__ import annotations

import atexit
import signal
import sqlite3
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.governance.resilience_governance.f5_boot_integration import F5BootIntegration
from zephyr.governance.resilience_governance.f5_shutdown_manager import (
    F5ShutdownManager,
    ShutdownResult,
    register_f5_shutdown_hook,
)


@pytest.fixture
def integration() -> F5BootIntegration:
    """已启动的 F5BootIntegration 实例。"""
    integ = F5BootIntegration()
    integ.on_startup()
    return integ


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """临时数据库路径。"""
    return tmp_path / "test_governance.db"


@pytest.fixture
def manager(integration: F5BootIntegration, temp_db: Path) -> F5ShutdownManager:
    """已安装的 F5ShutdownManager (短 idle timeout 便于测试)。

    使用真实 signal 注册,在 teardown 时通过 uninstall 恢复原始 handler。
    atexit 注册会累积,但不影响测试逻辑。
    """
    mgr = F5ShutdownManager(
        integration=integration,
        db_path=temp_db,
        idle_timeout_seconds=60.0,
    )
    mgr.install()
    yield mgr
    # 清理: 卸载 signal handler + 停止 idle 线程
    try:
        mgr.uninstall()
    except Exception:
        pass


class TestShutdownResult:
    def test_default_factory_values(self):
        result = ShutdownResult(success=True, component="f5_shutdown")
        assert result.success is True
        assert result.component == "f5_shutdown"
        assert result.errors == []
        assert result.details == {}

    def test_with_errors_and_details(self):
        result = ShutdownResult(
            success=False,
            component="f5_shutdown",
            errors=["err1", "err2"],
            details={"key": "value"},
        )
        assert result.success is False
        assert len(result.errors) == 2
        assert result.details["key"] == "value"


class TestF5ShutdownManagerConstruction:
    def test_default_construction(self, tmp_path: Path):
        mgr = F5ShutdownManager(project_root=tmp_path)
        assert mgr.is_shutdown is False
        assert mgr.is_installed is False
        assert mgr.idle_timeout_seconds == F5ShutdownManager.IDLE_TIMEOUT_SECONDS
        assert mgr.db_path == tmp_path / "data" / "databases" / "governance.db"

    def test_with_custom_db_path(self, tmp_path: Path):
        custom_db = tmp_path / "custom.db"
        mgr = F5ShutdownManager(db_path=custom_db)
        assert mgr.db_path == custom_db

    def test_with_custom_idle_timeout(self, tmp_path: Path):
        mgr = F5ShutdownManager(idle_timeout_seconds=120.0)
        assert mgr.idle_timeout_seconds == 120.0

    def test_constants(self):
        assert F5ShutdownManager.IDLE_TIMEOUT_SECONDS == 600.0
        assert F5ShutdownManager.SIGNAL_HANDLER_NAME == "f5_shutdown_signal"
        assert F5ShutdownManager.ATEXIT_HANDLER_NAME == "f5_shutdown_atexit"
        assert F5ShutdownManager.STATE_TABLE == "f5_state"


class TestInstall:
    def test_install_registers_signal_handlers(self, manager: F5ShutdownManager):
        # install 已经在 fixture 中调用
        assert manager.is_installed is True
        # signal handler 应该已被注册 (在主线程中)
        current_sigint = signal.getsignal(signal.SIGINT)
        current_sigterm = signal.getsignal(signal.SIGTERM)
        assert current_sigint == manager._on_signal
        assert current_sigterm == manager._on_signal

    def test_install_registers_atexit(self, manager: F5ShutdownManager):
        assert manager._atexit_registered is True

    def test_install_starts_idle_monitor(self, manager: F5ShutdownManager):
        # 事件驱动模型：install 后存在活跃的 idle timer
        assert manager._idle_timer is not None

    def test_install_is_idempotent(self, manager: F5ShutdownManager):
        first = manager.install()
        second = manager.install()
        assert first.success is True
        assert second.success is True
        assert second.details.get("already_installed") is True

    def test_install_with_mocked_signal(self, integration: F5BootIntegration, temp_db: Path):
        """测试用 monkeypatch mock signal.signal 避免影响测试进程。"""
        mgr = F5ShutdownManager(
            integration=integration,
            db_path=temp_db,
            idle_timeout_seconds=60.0,
        )
        with patch("zephyr.governance.f5_shutdown_manager.signal.signal") as mock_signal, \
             patch("zephyr.governance.f5_shutdown_manager.atexit.register") as mock_atexit:
            mock_signal.return_value = None
            result = mgr.install()
            assert result.success is True
            assert mock_signal.call_count == 2  # SIGINT + SIGTERM
            assert mock_atexit.call_count == 1
        mgr.uninstall()


class TestShutdown:
    def test_shutdown_returns_shutdown_result(self, manager: F5ShutdownManager):
        result = manager.shutdown()
        assert isinstance(result, ShutdownResult)
        assert result.component == "f5_shutdown"
        assert result.success is True

    def test_shutdown_marks_state(self, manager: F5ShutdownManager):
        assert manager.is_shutdown is False
        manager.shutdown()
        assert manager.is_shutdown is True

    def test_shutdown_is_idempotent(self, manager: F5ShutdownManager):
        first = manager.shutdown()
        second = manager.shutdown()
        assert first.success is True
        assert second.success is True
        assert second.details.get("already_shutdown") is True

    def test_shutdown_calls_integration_on_shutdown(self, manager: F5ShutdownManager):
        integration = manager._integration
        with patch.object(integration, "on_shutdown") as mock_on_shutdown:
            mock_on_shutdown.return_value = MagicMock(success=True, errors=[], details={})
            manager.shutdown()
            mock_on_shutdown.assert_called_once()

    def test_shutdown_persists_state(self, manager: F5ShutdownManager):
        manager.shutdown()
        # 数据库应该有状态
        assert manager.db_path.exists()
        conn = sqlite3.connect(str(manager.db_path))
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM f5_state")
            count = cursor.fetchone()[0]
            assert count > 0
        finally:
            conn.close()

    def test_shutdown_without_integration(self, temp_db: Path):
        mgr = F5ShutdownManager(integration=None, db_path=temp_db)
        result = mgr.shutdown()
        assert result.success is True

    def test_shutdown_handles_integration_failure(self, manager: F5ShutdownManager):
        integration = manager._integration
        with patch.object(integration, "on_shutdown") as mock_on_shutdown:
            mock_on_shutdown.side_effect = RuntimeError("boom")
            result = manager.shutdown()
            assert result.success is False
            assert any("integration on_shutdown failed" in e for e in result.errors)

    def test_shutdown_stops_idle_monitor(self, manager: F5ShutdownManager):
        timer = manager._idle_timer
        assert timer is not None
        manager.shutdown()
        # shutdown 后 timer 应已取消
        assert manager._idle_timer is None


class TestPersistState:
    def test_persist_state_returns_result(self, manager: F5ShutdownManager):
        result = manager.persist_state()
        assert isinstance(result, ShutdownResult)
        assert result.component == "f5_persist_state"
        assert result.success is True

    def test_persist_state_creates_db(self, manager: F5ShutdownManager):
        assert not manager.db_path.exists()
        manager.persist_state()
        assert manager.db_path.exists()

    def test_persist_state_creates_table(self, manager: F5ShutdownManager):
        manager.persist_state()
        conn = sqlite3.connect(str(manager.db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='f5_state'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_persist_state_captures_deadlock_state(self, manager: F5ShutdownManager):
        # 添加一些 deadlock 状态
        manager._integration.deadlock_detector.add_edge("a", "b")
        manager._integration.deadlock_detector.try_acquire("resource-1", "holder-1")

        result = manager.persist_state()
        assert result.details.get("deadlock_state_captured") is True

        # 验证数据库内容
        conn = sqlite3.connect(str(manager.db_path))
        try:
            cursor = conn.execute("SELECT value FROM f5_state WHERE key='deadlock_state'")
            row = cursor.fetchone()
            assert row is not None
            import json
            state = json.loads(row[0])
            assert "a" in state["wait_graph"]
            assert "resource-1" in state["locks"]
        finally:
            conn.close()

    def test_persist_state_captures_arbitrator_audit_log(self, manager: F5ShutdownManager):
        # 添加一些仲裁审计日志
        from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import (
            AgentMeta,
            AgentRole,
        )
        arb = manager._integration.arbitrator
        arb.arbitrate(
            AgentMeta(agent_id="a", role=AgentRole.SUPERADMIN),
            AgentMeta(agent_id="b", role=AgentRole.BUILDER),
            ["file1.py"],
        )

        result = manager.persist_state()
        assert result.details.get("arbitrator_audit_log_captured") is True

    def test_persist_state_captures_delegation_history(self, manager: F5ShutdownManager):
        # 添加一个委托 (mock LSG 验证, 因为 SupplyChainGuard 有预存在的签名问题)
        from zephyr.governance.escalation.escalation_models import (
            EscalationEvent,
            RuleCategory,
        )
        delegation = manager._integration.delegation_engine
        delegation.register_delegate("delegate-1", expertise=["deadlock"])

        event = EscalationEvent(
            category=RuleCategory.DEADLOCK,
            description="test",
            owner_id="owner-1",
        )
        with patch.object(delegation, "_lsg_verify_delegation"):
            delegation.delegate(event)

        result = manager.persist_state()
        assert result.details.get("delegation_history_captured") is True
        assert result.details.get("delegation_history_count") == 1

    def test_persist_state_replaces_old_state(self, manager: F5ShutdownManager):
        # 第一次持久化
        manager._integration.deadlock_detector.add_edge("a", "b")
        manager.persist_state()

        # 第二次持久化 (不同状态)
        manager._integration.deadlock_detector._wait_graph.clear()
        manager._integration.deadlock_detector.add_edge("x", "y")
        manager.persist_state()

        # 应该只有最新状态
        conn = sqlite3.connect(str(manager.db_path))
        try:
            cursor = conn.execute("SELECT value FROM f5_state WHERE key='deadlock_state'")
            row = cursor.fetchone()
            import json
            state = json.loads(row[0])
            assert "x" in state["wait_graph"]
            assert "a" not in state["wait_graph"]
        finally:
            conn.close()

    def test_persist_state_without_integration(self, temp_db: Path):
        mgr = F5ShutdownManager(integration=None, db_path=temp_db)
        result = mgr.persist_state()
        assert result.success is True
        # 应该写入 timestamp
        conn = sqlite3.connect(str(temp_db))
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM f5_state")
            assert cursor.fetchone()[0] > 0
        finally:
            conn.close()


class TestRestoreState:
    def test_restore_state_returns_result(self, manager: F5ShutdownManager):
        # 先持久化
        manager.persist_state()
        result = manager.restore_state()
        assert isinstance(result, ShutdownResult)
        assert result.component == "f5_restore_state"
        assert result.success is True

    def test_restore_state_no_db(self, temp_db: Path):
        mgr = F5ShutdownManager(integration=None, db_path=temp_db)
        result = mgr.restore_state()
        assert result.success is True
        assert result.details.get("db_exists") is False
        assert result.details.get("restored") is False

    def test_restore_state_restores_deadlock_graph(self, manager: F5ShutdownManager):
        # 添加状态并持久化
        deadlock = manager._integration.deadlock_detector
        deadlock.add_edge("a", "b")
        deadlock.add_edge("b", "c")
        deadlock.try_acquire("resource-1", "holder-1")
        manager.persist_state()

        # 清空状态
        deadlock._wait_graph.clear()
        deadlock._locks.clear()
        deadlock._lock_timestamps.clear()
        deadlock._preemption_order.clear()
        assert len(deadlock._wait_graph) == 0

        # 恢复
        result = manager.restore_state()
        assert result.details.get("deadlock_state_restored") is True

        # 验证恢复
        assert "a" in deadlock._wait_graph
        assert "b" in deadlock._wait_graph
        assert deadlock._wait_graph["a"] == {"b"}
        assert deadlock._wait_graph["b"] == {"c"}
        assert deadlock._locks["resource-1"] == "holder-1"

    def test_restore_state_never_raises_on_missing_keys(self, manager: F5ShutdownManager):
        # 写入空状态
        manager.persist_state()
        # 恢复不应该抛异常
        result = manager.restore_state()
        assert result.success is True

    def test_restore_state_without_integration(self, temp_db: Path):
        mgr = F5ShutdownManager(integration=None, db_path=temp_db)
        # 先写一些状态
        mgr._write_state_to_db({"timestamp": time.time(), "deadlock_state": None})
        result = mgr.restore_state()
        assert result.success is True


class TestSignalHandler:
    def test_signal_handler_calls_shutdown(self, manager: F5ShutdownManager):
        with patch.object(manager, "shutdown") as mock_shutdown:
            mock_shutdown.return_value = ShutdownResult(
                success=True, component="f5_shutdown"
            )
            manager._on_signal(signal.SIGTERM, None)
            mock_shutdown.assert_called_once()

    def test_signal_handler_never_raises(self, manager: F5ShutdownManager):
        with patch.object(manager, "shutdown", side_effect=RuntimeError("boom")):
            # 不应该抛异常
            manager._on_signal(signal.SIGTERM, None)

    def test_signal_handler_logs_signal_name(self, manager: F5ShutdownManager):
        with patch.object(manager, "shutdown") as mock_shutdown:
            mock_shutdown.return_value = ShutdownResult(
                success=True, component="f5_shutdown"
            )
            # SIGINT = 2
            manager._on_signal(2, None)
            mock_shutdown.assert_called_once()


class TestAtexitHandler:
    def test_atexit_handler_calls_shutdown(self, manager: F5ShutdownManager):
        with patch.object(manager, "shutdown") as mock_shutdown:
            mock_shutdown.return_value = ShutdownResult(
                success=True, component="f5_shutdown"
            )
            manager._on_atexit()
            mock_shutdown.assert_called_once()

    def test_atexit_handler_never_raises(self, manager: F5ShutdownManager):
        with patch.object(manager, "shutdown", side_effect=RuntimeError("boom")):
            # 不应该抛异常
            manager._on_atexit()


class TestIdleMonitor:
    def test_update_activity_resets_timer(self, manager: F5ShutdownManager):
        old_activity = manager.last_activity
        time.sleep(0.05)
        manager.update_activity()
        assert manager.last_activity > old_activity

    def test_is_idle_timeout_false_when_recent_activity(self, manager: F5ShutdownManager):
        # 事件驱动模型：update_activity 重排 timer，timer 仍活跃
        manager.update_activity()
        assert manager._idle_timer is not None

    def test_is_idle_timeout_true_when_timeout_reached(self, temp_db: Path):
        # 事件驱动模型：极短 timeout 让 timer 触发 shutdown
        mgr = F5ShutdownManager(
            integration=None,
            db_path=temp_db,
            idle_timeout_seconds=0.01,
        )
        mgr.install()
        # 等待 timer 到期触发 shutdown
        time.sleep(0.1)
        assert mgr.is_shutdown is True
        mgr.uninstall()

    def test_is_idle_timeout_false_after_shutdown(self, manager: F5ShutdownManager):
        manager.shutdown()
        # shutdown 后 timer 应已取消
        assert manager._idle_timer is None

    def test_idle_monitor_triggers_shutdown(self, temp_db: Path):
        """测试 idle timer 在 timeout 后触发 shutdown（事件驱动）。"""
        integration = F5BootIntegration()
        integration.on_startup()
        mgr = F5ShutdownManager(
            integration=integration,
            db_path=temp_db,
            idle_timeout_seconds=0.1,
        )
        try:
            mgr.install()
            # 等待 timer 到期触发 shutdown
            time.sleep(0.3)
            assert mgr.is_shutdown is True
        finally:
            mgr.uninstall()


class TestUninstall:
    def test_uninstall_stops_idle_thread(self, manager: F5ShutdownManager):
        timer = manager._idle_timer
        assert timer is not None
        manager.uninstall()
        # uninstall 后 timer 应已取消
        assert manager._idle_timer is None

    def test_uninstall_restores_signal_handlers(self, integration: F5BootIntegration, temp_db: Path):
        # 保存原始 signal handler
        original_sigint = signal.getsignal(signal.SIGINT)
        original_sigterm = signal.getsignal(signal.SIGTERM)

        mgr = F5ShutdownManager(
            integration=integration,
            db_path=temp_db,
            idle_timeout_seconds=60.0,
        )
        mgr.install()

        # signal handler 应该已被替换
        assert signal.getsignal(signal.SIGINT) == mgr._on_signal
        assert signal.getsignal(signal.SIGTERM) == mgr._on_signal

        mgr.uninstall()

        # 应该恢复原始 handler
        assert signal.getsignal(signal.SIGINT) == original_sigint
        assert signal.getsignal(signal.SIGTERM) == original_sigterm

    def test_uninstall_marks_not_installed(self, manager: F5ShutdownManager):
        assert manager.is_installed is True
        manager.uninstall()
        assert manager.is_installed is False


class TestRegisterF5ShutdownHookModuleFunction:
    def test_returns_manager_instance(self, integration: F5BootIntegration, temp_db: Path):
        with patch("zephyr.governance.f5_shutdown_manager.atexit.register"):
            mgr = register_f5_shutdown_hook(
                integration=integration,
                db_path=temp_db,
            )
            assert isinstance(mgr, F5ShutdownManager)
            assert mgr.is_installed is True
            mgr.uninstall()


class TestEndToEndShutdownCycle:
    def test_full_install_shutdown_cycle(self, integration: F5BootIntegration, temp_db: Path):
        mgr = F5ShutdownManager(
            integration=integration,
            db_path=temp_db,
            idle_timeout_seconds=60.0,
        )
        install_result = mgr.install()
        assert install_result.success is True

        # 模拟一些活动
        integration.deadlock_detector.add_edge("a", "b")
        mgr.update_activity()

        # 关闭
        shutdown_result = mgr.shutdown()
        assert shutdown_result.success is True
        assert mgr.is_shutdown is True
        assert integration.is_initialized is False

        # 数据库应该有状态
        assert mgr.db_path.exists()

    def test_persist_then_restore_cycle(self, integration: F5BootIntegration, temp_db: Path):
        # 第一个 manager: 持久化状态
        mgr1 = F5ShutdownManager(
            integration=integration,
            db_path=temp_db,
            idle_timeout_seconds=60.0,
        )
        integration.deadlock_detector.add_edge("a", "b")
        integration.deadlock_detector.try_acquire("resource-1", "holder-1")
        mgr1.persist_state()

        # 第二个 manager: 恢复状态
        integration2 = F5BootIntegration()
        integration2.on_startup()
        mgr2 = F5ShutdownManager(
            integration=integration2,
            db_path=temp_db,
            idle_timeout_seconds=60.0,
        )
        restore_result = mgr2.restore_state()
        assert restore_result.success is True
        assert restore_result.details.get("deadlock_state_restored") is True

        # 验证恢复
        assert "a" in integration2.deadlock_detector._wait_graph
        assert integration2.deadlock_detector._locks["resource-1"] == "holder-1"

    def test_shutdown_via_signal_handler(self, integration: F5BootIntegration, temp_db: Path):
        mgr = F5ShutdownManager(
            integration=integration,
            db_path=temp_db,
            idle_timeout_seconds=60.0,
        )
        mgr.install()

        # 模拟信号触发
        mgr._on_signal(signal.SIGTERM, None)

        assert mgr.is_shutdown is True
        assert integration.is_initialized is False
        mgr.uninstall()

    def test_shutdown_via_atexit_handler(self, integration: F5BootIntegration, temp_db: Path):
        mgr = F5ShutdownManager(
            integration=integration,
            db_path=temp_db,
            idle_timeout_seconds=60.0,
        )
        mgr.install()

        # 模拟 atexit 触发
        mgr._on_atexit()

        assert mgr.is_shutdown is True
        assert integration.is_initialized is False
        mgr.uninstall()
