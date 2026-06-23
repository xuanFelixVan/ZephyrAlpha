# [A_test] module_id=MOD-INF-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp_servers/blueprint.md | §14
# [MODULE] tests.integration.test_mcp_health_check_cron
# [INVARIANTS] mcp_health_check cron job已注册; gateway=None时跳过; 死亡进程自动重启; 多进程死亡全部恢复
# [MODIFY-GUARD] boot_cron_jobs.py 的 _mcp_health_check 注册逻辑变更需同步更新本测试
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/integration/test_mcp_health_check_cron.py -v --tb=short --timeout=60
"""DM-202915: MCP定时健康检查接入CircadianScheduler集成测试。

覆盖目标：
  1. cron job 注册：register_task_system_cron_jobs 调用后 mcp_health_check 被注册
  2. _mcp_health_check 函数行为：
     - gateway=None 时跳过（MCP集群未启动）
     - 进程健康时不重启
     - 进程死亡时自动重启
     - 多个进程死亡时全部恢复
  3. 红蓝对抗极端场景：launcher缺失/异常处理/全部死亡/部分死亡

测试策略：
  - mock CircadianScheduler.register_task 捕获注册的 callback
  - 调用 register_task_system_cron_jobs() 后从捕获的 callbacks 找到 mcp_health_check
  - 直接调用 callback，mock launcher 模块验证行为
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _is_pid_alive(pid: int) -> bool:
    """跨平台检查 PID 是否存活。"""
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
                capture_output=True,
                timeout=2.0,
            )
            return str(pid).encode("ascii") in result.stdout
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    except OSError:
        return False


def _get_standin_script() -> Path:
    """返回替身脚本路径（模拟 MCP Server）。"""
    tmp = Path(tempfile.mktemp(suffix=".py"))
    tmp.write_text("import time; time.sleep(60)", encoding="utf-8")
    return tmp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def captured_cron_tasks():
    """捕获 CircadianScheduler.register_task 的注册调用。

    register_task_system_cron_jobs 接收 circadian_scheduler 作为参数，
    传入 mock scheduler 捕获所有 register_task 调用。

    Returns:
        dict[name, callback] 注册的任务名到回调函数的映射
    """
    tasks: dict[str, object] = {}

    from zephyr.trading import boot_cron_jobs

    # 创建 mock scheduler 和 orchestrator
    mock_scheduler = MagicMock()

    def fake_register(hour, name, layer, callback, **kwargs):
        tasks[name] = callback
        return True

    mock_scheduler.register_task = fake_register
    mock_orchestrator = MagicMock()
    project_root = REPO_ROOT

    # 调用 register_boot_cron_jobs
    boot_cron_jobs.register_boot_cron_jobs(
        mock_scheduler, mock_orchestrator, project_root
    )

    yield tasks


@pytest.fixture
def launcher_module():
    """动态导入 launcher 模块。"""
    launcher_path = REPO_ROOT / "scripts" / "mcp" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher_cron_test", launcher_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def gateway():
    """创建真实的 ProcessLifecycleGateway 实例。"""
    from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

    gw = ProcessLifecycleGateway(idle_timeout_s=600.0)
    yield gw
    try:
        gw.terminate_all()
        gw.shutdown()
    except Exception:
        pass


@pytest.fixture
def standin_script():
    """返回替身脚本路径，测试后清理。"""
    script = _get_standin_script()
    yield script
    try:
        script.unlink()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 测试1: cron job 注册验证
# ---------------------------------------------------------------------------


class TestCronJobRegistration:
    """验证 mcp_health_check cron job 被正确注册。"""

    def test_mcp_health_check_registered(self, captured_cron_tasks):
        """mcp_health_check 应被注册到 CircadianScheduler。"""
        assert "mcp_health_check" in captured_cron_tasks, "mcp_health_check should be registered"

    def test_mcp_health_check_callback_callable(self, captured_cron_tasks):
        """mcp_health_check 的 callback 应可调用。"""
        callback = captured_cron_tasks.get("mcp_health_check")
        assert callback is not None
        assert callable(callback)

    def test_mcp_health_check_registered_with_other_tasks(self, captured_cron_tasks):
        """mcp_health_check 应与其他 cron job 一起注册。"""
        # 至少应有 mcp_health_check 和 stale_task_recovery
        assert "mcp_health_check" in captured_cron_tasks
        assert "stale_task_recovery" in captured_cron_tasks

    def test_all_expected_cron_jobs_registered(self, captured_cron_tasks):
        """验证所有预期的 cron job 都被注册。"""
        expected_jobs = [
            "mcp_health_check",
            "stale_task_recovery",
        ]
        for job in expected_jobs:
            assert job in captured_cron_tasks, f"{job} should be registered"


# ---------------------------------------------------------------------------
# 测试2: _mcp_health_check 函数行为
# ---------------------------------------------------------------------------


class TestMcpHealthCheckBehavior:
    """验证 _mcp_health_check 函数的行为。"""

    def test_skip_when_gateway_is_none(self, captured_cron_tasks):
        """gateway=None 时应跳过（MCP集群未启动）。"""
        callback = captured_cron_tasks["mcp_health_check"]

        # mock launcher 模块，_gateway=None
        mock_mod = MagicMock()
        mock_mod._gateway = None
        mock_mod.SERVER_SCRIPTS = {"srv1": "path1"}

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                # 不应抛异常
                callback()

    def test_skip_when_server_scripts_empty(self, captured_cron_tasks):
        """SERVER_SCRIPTS 为空时应跳过。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {}

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                callback()

    def test_healthy_servers_no_restart(self, captured_cron_tasks):
        """所有进程健康时不调用 restart_server。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1", "srv2": "p2", "srv3": "p3"}
        mock_mod.check_server_health.return_value = True

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                callback()

        # check_server_health 被调用 3 次
        assert mock_mod.check_server_health.call_count == 3
        # restart_server 不应被调用
        mock_mod.restart_server.assert_not_called()

    def test_dead_server_triggers_restart(self, captured_cron_tasks):
        """死亡进程触发 restart_server。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1", "srv2": "p2"}
        # srv1 健康，srv2 死亡
        mock_mod.check_server_health.side_effect = [True, False]
        mock_mod.restart_server.return_value = True

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                callback()

        # restart_server 只对 srv2 调用一次
        mock_mod.restart_server.assert_called_once_with("srv2", mock_mod._gateway)

    def test_all_dead_all_restarted(self, captured_cron_tasks):
        """所有进程死亡时全部触发 restart_server。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1", "srv2": "p2", "srv3": "p3"}
        mock_mod.check_server_health.return_value = False
        mock_mod.restart_server.return_value = True

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                callback()

        assert mock_mod.restart_server.call_count == 3

    def test_restart_failure_logged(self, captured_cron_tasks):
        """restart_server 返回 False 时不抛异常（只记录日志）。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1"}
        mock_mod.check_server_health.return_value = False
        mock_mod.restart_server.return_value = False

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                # 不应抛异常
                callback()

        mock_mod.restart_server.assert_called_once()

    def test_check_server_health_exception_handled(self, captured_cron_tasks):
        """check_server_health 抛异常时不影响其他 server 检查。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1", "srv2": "p2"}
        # srv1 抛异常，srv2 健康
        mock_mod.check_server_health.side_effect = [Exception("check failed"), True]

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                # 不应抛异常
                callback()

        # 两个 server 都被检查
        assert mock_mod.check_server_health.call_count == 2


# ---------------------------------------------------------------------------
# 测试3: 真实进程崩溃恢复（E2E）
# ---------------------------------------------------------------------------


class TestRealProcessCrashRecovery:
    """验证真实进程崩溃后的自动恢复（通过 _mcp_health_check callback）。"""

    def test_real_dead_process_recovered_by_callback(
        self, captured_cron_tasks, gateway, standin_script, launcher_module
    ):
        """启动真实进程→杀死→调用 _mcp_health_check callback→验证恢复。"""
        callback = captured_cron_tasks["mcp_health_check"]

        # 启动 2 个真实进程
        entry1 = gateway.launch("mcp-cron1", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        entry2 = gateway.launch("mcp-cron2", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        assert entry1 is not None and entry2 is not None
        pid1 = entry1.pid

        # 杀死第一个进程
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/PID", str(pid1)], capture_output=True, timeout=3.0)
        else:
            os.kill(pid1, 9)
        time.sleep(0.5)

        # 设置 launcher 模块的 _gateway 和 SERVER_SCRIPTS
        original_gateway = launcher_module._gateway
        original_scripts = launcher_module.SERVER_SCRIPTS
        launcher_module._gateway = gateway
        launcher_module.SERVER_SCRIPTS = {"cron1": "fake1", "cron2": "fake2"}

        # fake start_server：真正调用 gateway.launch 启动替身脚本
        def fake_start_server(server_id, gw):
            entry = gw.launch(
                f"mcp-{server_id}",
                [sys.executable, str(standin_script)],
                idle_timeout_s=600.0,
            )
            if entry is None:
                return False
            time.sleep(0.3)
            return entry.is_alive

        try:
            # mock importlib.util 使 _mcp_health_check 内部加载的 mod 返回 launcher_module
            # 这样 mod._gateway 和 mod.SERVER_SCRIPTS 使用测试中设置的值
            mock_spec = MagicMock()
            mock_spec.loader.exec_module = MagicMock(return_value=None)
            with (
                patch("importlib.util.spec_from_file_location", return_value=mock_spec),
                patch("importlib.util.module_from_spec", return_value=launcher_module),
                patch.object(launcher_module, "start_server", side_effect=fake_start_server),
            ):
                # 调用 _mcp_health_check callback
                callback()

            # 验证 cron1 被恢复（新进程存活）
            new_entry = gateway._pool._pool.get("mcp-cron1")
            assert new_entry is not None, "cron1 should be recovered"
            assert new_entry.is_alive, "recovered cron1 should be alive"
            assert new_entry.pid != pid1, "recovered process should have new PID"

            # cron2 仍然存活
            entry2_after = gateway._pool._pool.get("mcp-cron2")
            assert entry2_after is not None
            assert entry2_after.is_alive
        finally:
            launcher_module._gateway = original_gateway
            launcher_module.SERVER_SCRIPTS = original_scripts

    def test_real_all_dead_recovered_by_callback(
        self, captured_cron_tasks, gateway, standin_script, launcher_module
    ):
        """所有真实进程死亡→调用 callback→全部恢复。"""
        callback = captured_cron_tasks["mcp_health_check"]

        # 启动 3 个真实进程
        pids = []
        for name in ["mcp-all1", "mcp-all2", "mcp-all3"]:
            entry = gateway.launch(name, [sys.executable, str(standin_script)], idle_timeout_s=600.0)
            assert entry is not None
            pids.append(entry.pid)

        # 杀死所有进程
        for pid in pids:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=3.0)
            else:
                os.kill(pid, 9)
        time.sleep(0.5)

        original_gateway = launcher_module._gateway
        original_scripts = launcher_module.SERVER_SCRIPTS
        launcher_module._gateway = gateway
        launcher_module.SERVER_SCRIPTS = {"all1": "f1", "all2": "f2", "all3": "f3"}

        # fake start_server：真正调用 gateway.launch 启动替身脚本
        def fake_start_server(server_id, gw):
            entry = gw.launch(
                f"mcp-{server_id}",
                [sys.executable, str(standin_script)],
                idle_timeout_s=600.0,
            )
            if entry is None:
                return False
            time.sleep(0.3)
            return entry.is_alive

        try:
            mock_spec = MagicMock()
            mock_spec.loader.exec_module = MagicMock(return_value=None)
            with (
                patch("importlib.util.spec_from_file_location", return_value=mock_spec),
                patch("importlib.util.module_from_spec", return_value=launcher_module),
                patch.object(launcher_module, "start_server", side_effect=fake_start_server),
            ):
                callback()

            # 验证全部恢复
            for name in ["mcp-all1", "mcp-all2", "mcp-all3"]:
                entry = gateway._pool._pool.get(name)
                assert entry is not None, f"{name} should be recovered"
                assert entry.is_alive, f"{name} should be alive"
        finally:
            launcher_module._gateway = original_gateway
            launcher_module.SERVER_SCRIPTS = original_scripts


# ---------------------------------------------------------------------------
# 测试4: 红蓝对抗极端场景
# ---------------------------------------------------------------------------


class TestRedBlueExtremeScenarios:
    """红蓝对抗极端测试。"""

    def test_launcher_not_found(self, captured_cron_tasks, tmp_path):
        """launcher.py 不存在时不抛异常。"""
        callback = captured_cron_tasks["mcp_health_check"]

        # mock project_root 使 launcher_path 不存在
        with patch("pathlib.Path.exists", return_value=False):
            # 不应抛异常
            callback()

    def test_spec_creation_failure(self, captured_cron_tasks):
        """launcher spec 创建失败时不抛异常。"""
        callback = captured_cron_tasks["mcp_health_check"]

        with patch("importlib.util.spec_from_file_location", return_value=None):
            # 不应抛异常
            callback()

    def test_module_load_exception_handled(self, captured_cron_tasks):
        """模块加载异常时不抛异常。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_spec = MagicMock()
        mock_spec.loader.exec_module.side_effect = Exception("load failed")

        with patch("importlib.util.spec_from_file_location", return_value=mock_spec):
            # 不应抛异常
            callback()

    def test_partial_dead_with_exception(self, captured_cron_tasks):
        """部分进程死亡且 check_server_health 抛异常时，其他进程仍被检查。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1", "srv2": "p2", "srv3": "p3"}
        # srv1 抛异常，srv2 死亡，srv3 健康
        mock_mod.check_server_health.side_effect = [
            Exception("error"),
            False,
            True,
        ]
        mock_mod.restart_server.return_value = True

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                callback()

        # 3 个 server 都被检查
        assert mock_mod.check_server_health.call_count == 3
        # 只有 srv2 触发 restart
        mock_mod.restart_server.assert_called_once_with("srv2", mock_mod._gateway)

    def test_all_restart_failures_handled(self, captured_cron_tasks):
        """所有 restart_server 都失败时不抛异常。"""
        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1", "srv2": "p2"}
        mock_mod.check_server_health.return_value = False
        mock_mod.restart_server.return_value = False

        with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
            with patch("importlib.util.module_from_spec", return_value=mock_mod):
                # 不应抛异常
                callback()

        assert mock_mod.restart_server.call_count == 2

    def test_concurrent_health_check_calls(self, captured_cron_tasks):
        """并发调用 _mcp_health_check 不应产生竞争条件。"""
        import threading

        callback = captured_cron_tasks["mcp_health_check"]

        mock_mod = MagicMock()
        mock_mod._gateway = MagicMock()
        mock_mod.SERVER_SCRIPTS = {"srv1": "p1", "srv2": "p2"}
        mock_mod.check_server_health.return_value = True

        errors: list[Exception] = []

        def run_check():
            try:
                with patch("importlib.util.spec_from_file_location", return_value=MagicMock()):
                    with patch("importlib.util.module_from_spec", return_value=mock_mod):
                        callback()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=run_check) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        assert len(errors) == 0, f"Concurrent errors: {errors}"
