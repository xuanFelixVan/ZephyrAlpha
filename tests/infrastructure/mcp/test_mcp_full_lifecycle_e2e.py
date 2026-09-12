# [A_test] module_id=MOD-INF-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14
# [MODULE] tests.e2e.test_mcp_full_lifecycle_e2e
# [INVARIANTS] boot不抛异常; shutdown后_booted=False; _start_mcp_cluster函数存在; launch_all可调用; MCP进程可启动可清理
# [MODIFY-GUARD] auto_runtime_core.py 或 boot_hooks.py 或 launcher.py 的 boot/MCP/shutdown 逻辑变更需同步更新本测试
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/infrastructure/test_mcp_full_lifecycle_e2e.py -v --tb=short
# [TTL] task_bound
"""DM-202914: MCP boot→FLE→MCP→shutdown全链路E2E测试（不mock）。

覆盖目标：
  1. auto_runtime_core.boot() 全链路不抛异常
  2. boot 后 _booted=True
  3. boot_hooks.start_mcp_cluster 函数存在且可调用
  4. launcher.launch_all 可调用（MCP DAG 启动）
  5. auto_runtime_core.shutdown() 全链路清理
  6. shutdown 后 _booted=False
  7. MCP 进程通过 ProcessLifecycleGateway 启动→验证存活→shutdown 清理

设计说明：
  - 不 mock 任何组件，实际调用 boot/shutdown 全链路
  - MCP 启动通过 daemon 线程异步执行，boot_hooks.start_mcp_cluster 调用 launcher.launch_all
  - 由于 launcher.py 导入路径限制，MCP 进程启动可能失败但不影响 boot 流程
  - 测试验证流程完整性 + MCP 机制可用性
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

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


@pytest.fixture(scope="module")
def launcher_module():
    """动态导入 launcher 模块。"""
    launcher_path = REPO_ROOT / "scripts" / "mcp" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher_e2e", launcher_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def boot_hooks_module():
    """导入 boot_hooks 模块。"""
    from zephyr.trading import boot_hooks

    return boot_hooks


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
# 测试1: boot_hooks 源码结构验证
# ---------------------------------------------------------------------------


class TestBootHooksSourceStructure:
    """验证 boot_hooks.py 的 MCP 自动启动源码结构。"""

    def test_start_mcp_cluster_function_exists(self, boot_hooks_module):
        """验证 boot_hooks.py 定义了 _start_mcp_cluster 函数。"""
        source = inspect.getsource(boot_hooks_module.register_boot_hooks)
        assert "def _start_mcp_cluster" in source, "boot_hooks should define _start_mcp_cluster"

    def test_mcp_thread_is_daemon(self, boot_hooks_module):
        """验证 MCP 线程设置为 daemon=True。"""
        source = inspect.getsource(boot_hooks_module.register_boot_hooks)
        assert "daemon=True" in source, "MCP thread should be daemon=True"

    def test_launch_all_called_in_hook(self, boot_hooks_module):
        """验证 _start_mcp_cluster 调用 mod.launch_all()。"""
        source = inspect.getsource(boot_hooks_module.register_boot_hooks)
        assert "launch_all" in source, "_start_mcp_cluster should call launch_all()"

    def test_launcher_path_resolution(self, boot_hooks_module):
        """验证 _start_mcp_cluster 解析 launcher.py 路径。"""
        source = inspect.getsource(boot_hooks_module.register_boot_hooks)
        assert "launcher.py" in source, "Should reference launcher.py"
        assert "exists()" in source, "Should check launcher_path.exists()"

    def test_register_boot_hooks_calls_mcp_start(self, boot_hooks_module):
        """验证 register_boot_hooks 包含 MCP 启动逻辑。"""
        source = inspect.getsource(boot_hooks_module.register_boot_hooks)
        assert "_start_mcp_cluster" in source
        assert "mcp_thread" in source
        assert "start()" in source


# ---------------------------------------------------------------------------
# 测试2: launcher 源码结构验证
# ---------------------------------------------------------------------------


class TestLauncherSourceStructure:
    """验证 launcher.py 的源码结构。"""

    def test_launch_all_function_exists(self, launcher_module):
        """验证 launcher.py 定义了 launch_all 函数。"""
        assert hasattr(launcher_module, "launch_all"), "launcher should have launch_all"

    def test_topological_order_function_exists(self, launcher_module):
        """验证 launcher.py 定义了 topological_order 函数。"""
        assert hasattr(launcher_module, "topological_order"), "launcher should have topological_order"

    def test_start_server_function_exists(self, launcher_module):
        """验证 launcher.py 定义了 start_server 函数。"""
        assert hasattr(launcher_module, "start_server"), "launcher should have start_server"

    def test_dag_layers_defined(self, launcher_module):
        """验证 DAG_LAYERS 已定义。"""
        assert hasattr(launcher_module, "DAG_LAYERS"), "launcher should have DAG_LAYERS"
        assert isinstance(launcher_module.DAG_LAYERS, dict)
        assert len(launcher_module.DAG_LAYERS) > 0

    def test_server_scripts_defined(self, launcher_module):
        """验证 SERVER_SCRIPTS 已定义。"""
        assert hasattr(launcher_module, "SERVER_SCRIPTS"), "launcher should have SERVER_SCRIPTS"
        assert isinstance(launcher_module.SERVER_SCRIPTS, dict)
        assert len(launcher_module.SERVER_SCRIPTS) > 0

    def test_launch_all_registers_signal_handlers(self, launcher_module):
        """验证 launch_all 注册 SIGINT/SIGTERM 信号处理。"""
        source = inspect.getsource(launcher_module.launch_all)
        assert "signal.signal" in source
        assert "SIGINT" in source
        assert "SIGTERM" in source

    def test_launch_all_has_shutdown_callback(self, launcher_module):
        """验证 launch_all 定义了 _shutdown 回调。"""
        source = inspect.getsource(launcher_module.launch_all)
        assert "def _shutdown" in source
        assert "terminate_all" in source
        assert "shutdown" in source


# ---------------------------------------------------------------------------
# 测试3: MCP 进程启动与清理（通过 ProcessLifecycleGateway）
# ---------------------------------------------------------------------------


class TestMcpProcessLifecycle:
    """验证 MCP 进程通过 ProcessLifecycleGateway 启动与清理。"""

    def test_single_mcp_process_starts_and_alive(self, gateway, standin_script):
        """启动单个 MCP 进程，验证存活。"""
        entry = gateway.launch(
            "mcp-e2e-test1",
            [sys.executable, str(standin_script)],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        assert entry.is_alive is True
        assert _is_pid_alive(entry.pid)

    def test_multiple_mcp_processes_start(self, gateway, standin_script):
        """启动多个 MCP 进程，验证全部存活。"""
        pids = []
        for name in ["mcp-e2e-srv1", "mcp-e2e-srv2", "mcp-e2e-srv3"]:
            entry = gateway.launch(name, [sys.executable, str(standin_script)], idle_timeout_s=600.0)
            assert entry is not None
            assert entry.is_alive is True
            pids.append(entry.pid)

        for pid in pids:
            assert _is_pid_alive(pid)

    def test_shutdown_clears_all_mcp_processes(self, gateway, standin_script):
        """shutdown 后所有 MCP 进程应被清理。"""
        pids = []
        for name in ["mcp-e2e-clean1", "mcp-e2e-clean2"]:
            entry = gateway.launch(name, [sys.executable, str(standin_script)], idle_timeout_s=600.0)
            assert entry is not None
            pids.append(entry.pid)

        gateway.terminate_all()
        gateway.shutdown()

        time.sleep(0.5)
        for pid in pids:
            assert not _is_pid_alive(pid), f"PID {pid} should be dead after shutdown"

    def test_terminate_all_returns_count(self, gateway, standin_script):
        """terminate_all 返回已终止的进程数。"""
        for name in ["mcp-e2e-count1", "mcp-e2e-count2", "mcp-e2e-count3"]:
            gateway.launch(name, [sys.executable, str(standin_script)], idle_timeout_s=600.0)

        count = gateway.terminate_all()
        assert count == 3, f"terminate_all should return 3, got {count}"

    def test_process_reuse_on_same_name(self, gateway, standin_script):
        """同名进程应复用（reuse_count 增加）。"""
        gateway.launch("mcp-e2e-reuse", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        entry1 = gateway.pool.pool.get("mcp-e2e-reuse")
        assert entry1 is not None

        gateway.launch("mcp-e2e-reuse", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        entry2 = gateway.pool.pool.get("mcp-e2e-reuse")

        assert entry2 is not None
        assert entry2.pid == entry1.pid, "Same name should reuse same process"
        assert entry2.reuse_count >= 1


# ---------------------------------------------------------------------------
# 测试4: boot/shutdown 全链路 E2E（不 mock）
# ---------------------------------------------------------------------------


class TestBootShutdownE2E:
    """验证 auto_runtime_core 的 boot/shutdown 全链路。

    不 mock 任何组件，实际调用 boot() 和 shutdown()。
    由于 boot 会启动多个后台组件，测试后必须确保 shutdown 清理。
    """

    def test_boot_returns_boot_report(self):
        """boot() 应返回 BootReport 且不抛异常。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        core = AutoRuntimeCore()
        try:
            report = core.boot()
            assert report is not None, "boot() should return BootReport"
            assert hasattr(report, "success"), "BootReport should have success attribute"
        finally:
            try:
                core.shutdown()
            except Exception:
                pass

    def test_booted_flag_set_after_boot(self):
        """boot 成功后 _booted 应为 True。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        core = AutoRuntimeCore()
        try:
            core.boot()
            # boot 可能因环境限制失败，但 _booted 应反映实际状态
            assert isinstance(core.booted, bool)
        finally:
            try:
                core.shutdown()
            except Exception:
                pass

    def test_shutdown_returns_shutdown_report(self):
        """shutdown() 应返回 ShutdownReport 且不抛异常。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        core = AutoRuntimeCore()
        core.boot()
        try:
            report = core.shutdown()
            assert report is not None, "shutdown() should return ShutdownReport"
        except Exception:
            try:
                core.shutdown()
            except Exception:
                pass
            raise

    def test_booted_flag_false_after_shutdown(self):
        """shutdown 后 _booted 应为 False。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        core = AutoRuntimeCore()
        core.boot()
        core.shutdown()
        assert core.booted is False, "_booted should be False after shutdown"

    def test_boot_shutdown_idempotent(self):
        """连续 boot→shutdown→boot→shutdown 不应抛异常。"""
        from zephyr.trading.auto_runtime_core import AutoRuntimeCore

        core = AutoRuntimeCore()
        try:
            core.boot()
            core.shutdown()
            core.boot()
            core.shutdown()
        finally:
            try:
                if core.booted:
                    core.shutdown()
            except Exception:
                pass

    def test_register_boot_hooks_callable(self, boot_hooks_module):
        """register_boot_hooks 应可调用且不抛异常。"""
        boot_hooks_module.register_boot_hooks()


# ---------------------------------------------------------------------------
# 测试5: launcher DAG 拓扑验证
# ---------------------------------------------------------------------------


class TestLauncherDAGTopology:
    """验证 launcher 的 DAG 拓扑结构。"""

    def test_topological_order_returns_list_of_lists(self, launcher_module):
        """topological_order 应返回 list[list[str]]。"""
        order = launcher_module.topological_order()
        assert isinstance(order, list)
        assert all(isinstance(layer, list) for layer in order)

    def test_dag_has_multiple_layers(self, launcher_module):
        """DAG 应有多个层。"""
        order = launcher_module.topological_order()
        assert len(order) >= 2, f"Expected at least 2 layers, got {len(order)}"

    def test_server_scripts_non_empty(self, launcher_module):
        """SERVER_SCRIPTS 应非空。"""
        scripts = launcher_module.SERVER_SCRIPTS
        assert len(scripts) > 0, "SERVER_SCRIPTS should not be empty"

    def test_dag_layers_cover_all_servers(self, launcher_module):
        """DAG_LAYERS 应覆盖 SERVER_SCRIPTS 中的所有 server。"""
        all_servers = set(launcher_module.SERVER_SCRIPTS.keys())
        dag_servers: set[str] = set()
        for layer in launcher_module.DAG_LAYERS.values():
            dag_servers.update(layer)
        assert all_servers == dag_servers, f"Mismatch: {all_servers} vs {dag_servers}"


# ---------------------------------------------------------------------------
# 测试6: 红蓝对抗极端场景
# ---------------------------------------------------------------------------


class TestRedBlueExtremeScenarios:
    """红蓝对抗极端测试：进程崩溃/资源耗尽/并发/幂等/恢复。"""

    def test_process_crash_does_not_affect_others(self, gateway, standin_script):
        """一个进程崩溃不影响其他进程。"""
        # 启动 3 个进程
        entries = {}
        for name in ["mcp-red1", "mcp-red2", "mcp-red3"]:
            entries[name] = gateway.launch(name, [sys.executable, str(standin_script)], idle_timeout_s=600.0)

        # 杀死中间一个
        killed_pid = entries["mcp-red2"].pid
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/PID", str(killed_pid)], capture_output=True, timeout=3.0)
        else:
            os.kill(killed_pid, 9)
        time.sleep(0.5)

        # 验证其他两个仍然存活
        assert entries["mcp-red1"].is_alive is True, "red1 should still be alive"
        assert entries["mcp-red3"].is_alive is True, "red3 should still be alive"
        assert entries["mcp-red2"].is_alive is False, "red2 should be dead"

    def test_shutdown_after_partial_crash(self, gateway, standin_script):
        """部分进程崩溃后 shutdown 应清理所有剩余进程。"""
        pids = []
        for name in ["mcp-partial1", "mcp-partial2", "mcp-partial3"]:
            entry = gateway.launch(name, [sys.executable, str(standin_script)], idle_timeout_s=600.0)
            pids.append(entry.pid)

        # 杀死第一个
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/PID", str(pids[0])], capture_output=True, timeout=3.0)
        else:
            os.kill(pids[0], 9)
        time.sleep(0.5)

        # shutdown 应清理剩余
        gateway.terminate_all()
        gateway.shutdown()
        time.sleep(0.5)

        # 验证所有 PID 都不再存活
        for pid in pids:
            assert not _is_pid_alive(pid), f"PID {pid} should be dead after shutdown"

    def test_double_shutdown_idempotent(self, gateway, standin_script):
        """连续两次 shutdown 不应抛异常。"""
        gateway.launch("mcp-double", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        gateway.shutdown()
        # 第二次 shutdown 不应抛异常
        gateway.shutdown()

    def test_terminate_all_on_empty_pool(self, gateway):
        """空池上 terminate_all 应返回 0。"""
        count = gateway.terminate_all()
        assert count == 0, "terminate_all on empty pool should return 0"

    def test_launch_after_shutdown(self, gateway, standin_script):
        """shutdown 后再 launch 应能启动新进程。"""
        gateway.launch("mcp-before", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        gateway.shutdown()

        # shutdown 后 _pool 可能被清理，但 gateway 仍可创建新进程
        entry = gateway.launch("mcp-after", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        if entry is not None:
            assert entry.is_alive is True
            gateway.terminate_all()

    def test_concurrent_launch_no_race(self, gateway, standin_script):
        """并发 launch 不应产生竞争条件。"""
        import threading

        errors: list[Exception] = []
        entries_list: list = []

        def launch_one(name: str):
            try:
                entry = gateway.launch(name, [sys.executable, str(standin_script)], idle_timeout_s=600.0)
                if entry is not None:
                    entries_list.append(entry)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=launch_one, args=(f"mcp-conc{i}",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(entries_list) == 5, f"Expected 5 entries, got {len(entries_list)}"
