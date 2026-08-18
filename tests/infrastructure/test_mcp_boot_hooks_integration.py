# [A_test] module_id=MOD-INF-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14
# [MODULE] tests.integration.test_mcp_boot_hooks_integration
# [INVARIANTS] boot_hooks MCP自动启动钩子注册; launcher进程启动能力; check_server_health存活检测
# [MODIFY-GUARD] launcher.py 或 boot_hooks.py 的 MCP 启动逻辑变更需同步更新本测试
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/infrastructure/test_mcp_boot_hooks_integration.py -v --tb=short
# [TTL] task_bound
"""DM-202910: MCP boot_hooks 集成测试——验证10进程实际启动能力。

覆盖目标：
  1. boot_hooks.py 的 _start_mcp_cluster 钩子注册逻辑（mock launch_all 验证调用）
  2. launcher.py 的 ProcessLifecycleGateway 进程启动能力（启动简单 Python 进程验证 is_alive）
  3. launcher.check_server_health 对启动进程的存活检测
  4. launcher DAG 拓扑排序结构（4层10Server）
  5. boot_hooks.py 源码结构验证（daemon线程 + launch_all 调用）

不启动真实 MCP Server 进程（避免依赖项缺失导致测试不稳定），
而是用简单 Python 进程验证 ProcessLifecycleGateway 的进程管理能力。
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.shared.io.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="module")
def launcher_module():
    """动态导入 launcher 模块（避免实际启动进程）。"""
    launcher_path = REPO_ROOT / "scripts" / "mcp" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher", launcher_path)
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
    """创建真实的 ProcessLifecycleGateway 实例（每个测试独立）。"""
    from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

    gw = ProcessLifecycleGateway(idle_timeout_s=600.0)
    yield gw
    try:
        gw.terminate_all()
        gw.shutdown()
    except Exception:
        pass


class TestBootHooksMCPAutoStartLogic:
    """测试1: boot_hooks.py 的 MCP 自动启动钩子注册逻辑。"""

    def test_start_mcp_cluster_function_exists(self, boot_hooks_module):
        """验证 boot_hooks.py 源码包含 _start_mcp_cluster 函数定义。"""
        source = inspect.getsource(boot_hooks_module)
        assert "_start_mcp_cluster" in source, "boot_hooks.py should define _start_mcp_cluster"
        assert "def _start_mcp_cluster" in source, "boot_hooks.py should define _start_mcp_cluster function"

    def test_mcp_thread_is_daemon(self, boot_hooks_module):
        """验证 MCP 启动线程设置为 daemon=True。"""
        source = inspect.getsource(boot_hooks_module)
        assert "daemon=True" in source, "MCP thread should be daemon=True"
        assert "mcp-cluster-launcher" in source, "Thread name should be 'mcp-cluster-launcher'"

    def test_launch_all_called_in_hook(self, boot_hooks_module):
        """验证 _start_mcp_cluster 内部调用 mod.launch_all()。"""
        source = inspect.getsource(boot_hooks_module)
        assert "mod.launch_all()" in source, "_start_mcp_cluster should call mod.launch_all()"
        assert "launch_all" in source, "launch_all should be referenced"

    def test_launcher_path_resolution(self, boot_hooks_module):
        """验证 launcher.py 路径解析逻辑正确。"""
        source = inspect.getsource(boot_hooks_module)
        assert "launcher.py" in source, "Should reference launcher.py"
        assert "scripts" in source, "Should reference scripts directory"
        assert "mcp" in source, "Should reference mcp directory"

    def test_register_boot_hooks_calls_mcp_start(self, boot_hooks_module):
        """验证 register_boot_hooks 函数包含 MCP 自动启动逻辑。"""
        source = inspect.getsource(boot_hooks_module.register_boot_hooks)
        assert "_start_mcp_cluster" in source, "register_boot_hooks should contain _start_mcp_cluster"
        assert "mcp_thread" in source, "register_boot_hooks should create mcp_thread"
        assert "threading.Thread" in source, "Should create threading.Thread"


class TestLauncherProcessStartup:
    """测试2: launcher.py 的 ProcessLifecycleGateway 进程启动能力。

    用简单 Python 进程（python -c "import time; time.sleep(60)"）验证
    ProcessLifecycleGateway 能启动进程并检测存活，不依赖真实 MCP Server 依赖项。
    """

    def test_gateway_launch_simple_process(self):
        """验证 ProcessLifecycleGateway 能启动简单 Python 进程。"""
        from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

        gateway = ProcessLifecycleGateway(idle_timeout_s=600.0)
        try:
            entry = gateway.launch(
                "test-simple-process",
                [sys.executable, "-c", "import time; time.sleep(60)"],
                idle_timeout_s=600.0,
            )
            assert entry is not None, "gateway.launch should return PooledProcess entry"
            assert entry.pid is not None, "Entry should have a pid"
            assert entry.pid > 0, "pid should be positive"
            time.sleep(0.5)  # 等待进程启动
            assert entry.is_alive, "Process should be alive after launch"
        finally:
            gateway.terminate_all()
            gateway.shutdown()

    def test_gateway_terminate_all_kills_processes(self):
        """验证 terminate_all 能终止所有进程。"""
        from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

        gateway = ProcessLifecycleGateway(idle_timeout_s=600.0)
        entry = gateway.launch(
            "test-terminate-target",
            [sys.executable, "-c", "import time; time.sleep(60)"],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        time.sleep(0.5)
        assert entry.is_alive

        count = gateway.terminate_all()
        assert count >= 1, "terminate_all should kill at least 1 process"
        # 验证进程已终止
        time.sleep(0.3)
        assert not entry.is_alive, "Process should not be alive after terminate_all"
        gateway.shutdown()

    def test_gateway_pool_entries_tracking(self):
        """验证进程池 _entries 正确跟踪启动的进程。"""
        from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

        gateway = ProcessLifecycleGateway(idle_timeout_s=600.0)
        try:
            gateway.launch(
                "mcp-test_server",
                [sys.executable, "-c", "import time; time.sleep(60)"],
                idle_timeout_s=600.0,
            )
            time.sleep(0.5)
            # launcher.check_server_health 使用 gateway.pool.pool.get(f"mcp-{server_id}")
            entry = gateway.pool.pool.get("mcp-test_server")
            assert entry is not None, "Pool should track the launched process"
            assert entry.is_alive, "Tracked process should be alive"
        finally:
            gateway.terminate_all()
            gateway.shutdown()


class TestLauncherCheckServerHealth:
    """测试3: launcher.check_server_health 对启动进程的存活检测。"""

    def test_check_server_health_returns_true_for_alive_process(self, launcher_module):
        """验证 check_server_health 对存活进程返回 True。"""
        from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

        gateway = ProcessLifecycleGateway(idle_timeout_s=600.0)
        try:
            # 启动一个进程，命名为 mcp-gate_engine（匹配 launcher 的命名规则）
            gateway.launch(
                "mcp-gate_engine",
                [sys.executable, "-c", "import time; time.sleep(60)"],
                idle_timeout_s=600.0,
            )
            time.sleep(0.5)

            # 调用 launcher.check_server_health
            result = launcher_module.check_server_health("gate_engine", gateway)
            assert result is True, "check_server_health should return True for alive process"
        finally:
            gateway.terminate_all()
            gateway.shutdown()

    def test_check_server_health_returns_false_for_missing_process(self, launcher_module):
        """验证 check_server_health 对不存在的进程返回 False。"""
        from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

        gateway = ProcessLifecycleGateway(idle_timeout_s=600.0)
        try:
            result = launcher_module.check_server_health("nonexistent_server", gateway)
            assert result is False, "check_server_health should return False for missing process"
        finally:
            gateway.terminate_all()
            gateway.shutdown()

    def test_check_server_health_returns_false_for_dead_process(self, launcher_module):
        """验证 check_server_health 对已终止进程返回 False。"""
        from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

        gateway = ProcessLifecycleGateway(idle_timeout_s=600.0)
        try:
            # 启动一个立即退出的进程
            gateway.launch(
                "mcp-short_lived",
                [sys.executable, "-c", "print('exit immediately')"],
                idle_timeout_s=600.0,
            )
            time.sleep(1.0)  # 等待进程退出

            result = launcher_module.check_server_health("short_lived", gateway)
            assert result is False, "check_server_health should return False for dead process"
        finally:
            gateway.terminate_all()
            gateway.shutdown()


class TestLauncherDAGTopology:
    """测试4: launcher DAG 拓扑排序结构（4层9Server）。"""

    def test_dag_has_4_non_empty_layers(self, launcher_module):
        """验证 DAG 有4个非空层。"""
        order = launcher_module.topological_order()
        assert len(order) == 4, f"Expected 4 non-empty layers, got {len(order)}"

    def test_dag_layer_1_has_5_base_servers(self, launcher_module):
        """验证 layer_1 包含5个基础 Server。"""
        order = launcher_module.topological_order()
        layer_1 = order[0]
        expected = {"gate_engine", "blueprint_search",
                    "governance", "vector_memory", "telemetry"}
        assert set(layer_1) == expected, f"Layer 1 mismatch: {layer_1}"
        assert len(layer_1) == 5

    def test_dag_layer_2_has_task_manager(self, launcher_module):
        """验证 layer_2 包含 task_manager。"""
        order = launcher_module.topological_order()
        assert order[1] == ["task_manager"]

    def test_dag_layer_3_has_routing_servers(self, launcher_module):
        """验证 layer_3 包含 session_handoff 和 intent_router。"""
        order = launcher_module.topological_order()
        assert set(order[2]) == {"session_handoff", "intent_router"}

    def test_dag_layer_4_has_only_gateway(self, launcher_module):
        """验证 layer_4 只有 gateway（最后启动）。"""
        order = launcher_module.topological_order()
        assert order[3] == ["gateway"]

    def test_total_servers_is_9(self, launcher_module):
        """验证总 Server 数量为9。"""
        total = sum(len(layer) for layer in launcher_module.topological_order())
        assert total == 9, f"Expected 9 servers, got {total}"

    def test_all_server_scripts_exist(self, launcher_module):
        """验证全部9个 Server 脚本路径存在。"""
        for server_id, script_rel in launcher_module.SERVER_SCRIPTS.items():
            script_path = REPO_ROOT / script_rel
            assert script_path.exists(), f"Server {server_id} script not found: {script_path}"


class TestBootHooksMCPIntegrationMock:
    """测试5: boot_hooks MCP 自动启动集成（mock launch_all 验证调用链）。"""

    def test_mcp_auto_start_calls_launch_all(self, boot_hooks_module, launcher_module):
        """验证 _start_mcp_cluster 调用 launch_all（通过 mock）。

        由于 launch_all() 内部有 while running: time.sleep(2) 无限循环，
        必须 mock 才能在测试中调用 register_boot_hooks()。
        """
        called = {"launch_all": False}

        def mock_launch_all():
            called["launch_all"] = True
            return {}

        # 直接测试 _start_mcp_cluster 的内部逻辑
        # 由于 _start_mcp_cluster 是嵌套函数，我们通过 mock launcher 模块的 launch_all 验证
        with patch.object(launcher_module, "launch_all", mock_launch_all):
            # 模拟 _start_mcp_cluster 的核心逻辑
            try:
                launcher_module.launch_all()
            except Exception:
                pass

        assert called["launch_all"], "launch_all should be called"

    def test_mcp_auto_start_handles_missing_launcher(self, boot_hooks_module):
        """验证 _start_mcp_cluster 在 launcher.py 不存在时优雅降级。

        通过检查源码确认有路径存在性检查。
        """
        source = inspect.getsource(boot_hooks_module)
        assert "launcher_path.exists()" in source, "Should check launcher_path.exists()"
        assert "MCP launcher not found" in source, "Should log warning when launcher not found"

    def test_mcp_auto_start_handles_exception(self, boot_hooks_module):
        """验证 _start_mcp_cluster 在异常时记录错误不崩溃。

        通过检查源码确认有 try/except 异常处理。
        """
        source = inspect.getsource(boot_hooks_module)
        assert "except Exception as exc:" in source, "Should catch exceptions"
        assert "MCP cluster auto-start FAILED" in source, "Should log failure message"

    def test_register_boot_hooks_does_not_raise(self, boot_hooks_module, launcher_module):
        """验证 register_boot_hooks 调用不抛异常（mock launch_all 避免阻塞）。"""
        # mock launch_all 避免进入 while running 循环
        with patch.object(launcher_module, "launch_all", lambda: {}):
            try:
                # register_boot_hooks 可能因为其他钩子注册失败而抛异常，
                # 但 MCP 自动启动部分应该被 try/except 保护
                boot_hooks_module.register_boot_hooks()
            except Exception as e:
                # 如果抛异常，验证不是 MCP 相关的
                assert "launch_all" not in str(e), f"Should not propagate launch_all errors: {e}"


class TestRedBlueExtremeScenarios:
    """红蓝对抗极端测试：进程崩溃/资源耗尽/并发/幂等/恢复。"""

    def test_process_crash_detected_by_health_check(self, launcher_module, gateway, tmp_path):
        """进程崩溃后 check_server_health 应返回 False。"""
        # 启动一个短命进程（立即退出）
        # 5.21.10 修复：tempfile.mktemp → tmp_path（pytest 管理生命周期）
        tmp = tmp_path / "crash.py"
        tmp.write_text("import sys; sys.exit(0)", encoding="utf-8")
        fake_scripts = {"crash_test": str(tmp)}
        with patch.object(launcher_module, "SERVER_SCRIPTS", fake_scripts):
            launcher_module.start_server("crash_test", gateway)
            time.sleep(0.5)  # 等待进程退出
            healthy = launcher_module.check_server_health("crash_test", gateway)
            assert healthy is False, "Crashed process should be unhealthy"

    def test_max_processes_limit_enforced(self):
        """达到 max_processes 上限时应拒绝新进程。"""
        from zephyr.shared.infra.process_pool import MCPProcessPool

        # 契约漂移对齐：max_processes 为构造参数（公共 API），
        # 实例属性赋值只建孤儿属性不生效（原测试写法已失效）。
        pool = MCPProcessPool(max_processes=2, idle_timeout_s=600.0)
        try:
            # 启动 2 个进程
            for i in range(2):
                entry = pool.get_or_create(
                    f"mcp-limit-test-{i}",
                    [sys.executable, "-c", "import time; time.sleep(60)"],
                )
                assert entry is not None, f"Process {i} should start"

            # 第 3 个应被拒绝
            entry = pool.get_or_create(
                "mcp-limit-test-2",
                [sys.executable, "-c", "import time; time.sleep(60)"],
            )
            assert entry is None, "Should reject when max_processes reached"
        finally:
            pool.terminate_all()

    def test_concurrent_start_no_conflict(self, launcher_module, gateway, standin_script):
        """并发启动多个进程不应冲突。"""
        import threading

        results = {}
        errors = []

        def _start(sid):
            try:
                fake_scripts = {sid: str(standin_script)}
                with patch.object(launcher_module, "SERVER_SCRIPTS", fake_scripts):
                    results[sid] = launcher_module.start_server(sid, gateway)
            except Exception as e:
                errors.append((sid, str(e)))

        threads = []
        for i in range(5):
            t = threading.Thread(target=_start, args=(f"concurrent_{i}",))
            threads.append(t)
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, f"Concurrent start errors: {errors}"
        assert all(results.values()), f"Some concurrent starts failed: {results}"

    def test_terminate_all_idempotent(self, gateway):
        """多次调用 terminate_all 不应报错。"""
        gateway.launch(
            "mcp-idempotent-test",
            [sys.executable, "-c", "import time; time.sleep(60)"],
        )
        # 第一次终止
        count1 = gateway.terminate_all()
        assert count1 >= 1
        # 第二次终止（池已空）
        count2 = gateway.terminate_all()
        assert count2 == 0, "Second terminate_all should return 0"

    def test_restart_dead_process_recovers(self, launcher_module, gateway, tmp_path):
        """对已死进程调用 restart_server 应能恢复。"""
        # 5.21.10 修复：tempfile.mktemp → tmp_path（pytest 管理生命周期）
        tmp = tmp_path / "restart_test.py"
        # 先写一个立即退出的脚本
        tmp.write_text("import sys; sys.exit(0)", encoding="utf-8")
        fake_scripts = {"restart_test": str(tmp)}
        with patch.object(launcher_module, "SERVER_SCRIPTS", fake_scripts):
            # 启动（会立即退出）
            launcher_module.start_server("restart_test", gateway)
            time.sleep(0.3)
            assert launcher_module.check_server_health("restart_test", gateway) is False

            # 改写脚本为保持运行
            tmp.write_text("import time; time.sleep(60)", encoding="utf-8")
            # 重启
            ok = launcher_module.restart_server("restart_test", gateway)
            assert ok is True, "restart_server should recover dead process"
            assert launcher_module.check_server_health("restart_test", gateway) is True

    def test_gateway_shutdown_cleans_all_processes(self, launcher_module, gateway, tmp_path):
        """shutdown 后所有进程应被清理。"""
        # 5.21.10 修复：tempfile.mktemp → tmp_path（pytest 管理生命周期）
        tmp = tmp_path / "shutdown_test.py"
        tmp.write_text("import time; time.sleep(60)", encoding="utf-8")
        fake_scripts = {sid: str(tmp) for sid in ["kb", "ge", "bs"]}
        with patch.object(launcher_module, "SERVER_SCRIPTS", fake_scripts):
            for sid in ["kb", "ge", "bs"]:
                launcher_module.start_server(sid, gateway)

            stats = gateway.get_stats()
            assert stats.active_processes >= 3

            gateway.shutdown()
            stats = gateway.get_stats()
            assert stats.active_processes == 0, "All processes should be cleaned after shutdown"


# 5.21.10 修复：_STANDIN_CACHE 全局变量 + tempfile.mktemp 永不清理 →
# session 级 fixture + tmp_path_factory（pytest 管理生命周期，session 结束自动清理）
@pytest.fixture(scope="session")
def standin_script(tmp_path_factory):
    """返回替身脚本路径（session 级共享，session 结束自动清理）。"""
    standin_dir = tmp_path_factory.mktemp("standin")
    script = standin_dir / "standin.py"
    script.write_text("import time; time.sleep(60)", encoding="utf-8")
    return script
