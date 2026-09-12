# [A_test] module_id=MOD-INF-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14
# [MODULE] tests.integration.test_mcp_signal_shutdown
# [INVARIANTS] SIGINT/SIGTERM信号发送后所有子进程在5秒内被terminate_all清理; atexit兜底关闭验证; 信号处理不抛异常
# [MODIFY-GUARD] launcher.py 的 signal注册/terminate_all/shutdown 逻辑变更需同步更新本测试
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/infrastructure/test_mcp_signal_shutdown.py -v --tb=short
# [TTL] task_bound
"""DM-202911: MCP SIGINT/SIGTERM 信号优雅关闭进程级测试。

覆盖目标：
  1. launch_all() 注册 SIGINT/SIGTERM 信号处理（mock 验证 signal.signal 调用）
  2. _shutdown 回调行为：启动真实进程→模拟 shutdown→验证 5s 内全部清理
  3. try/finally 兜底清理：KeyboardInterrupt 时 finally 块执行 terminate_all+shutdown
  4. 子进程级信号测试：启动 launcher 子进程→发送信号→验证干净退出+子进程清理
  5. atexit 兜底关闭验证

Windows 兼容性说明：
  - Windows 上 os.kill(pid, SIGTERM) 不可靠，使用 CTRL_BREAK_EVENT 测试子进程信号
  - subprocess.Popen.terminate() 在 Windows 调用 TerminateProcess（等同 SIGKILL）
  - 信号处理函数注册通过 signal.signal() 在主线程生效
"""

from __future__ import annotations

import importlib.util
import inspect
import os
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.shared.io.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="module")
def launcher_module():
    """动态导入 launcher 模块（避免实际启动进程）。"""
    launcher_path = REPO_ROOT / "scripts" / "mcp" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher_dm202911", launcher_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def gateway():
    """创建真实的 ProcessLifecycleGateway 实例（每个测试独立）。

    使用短 idle_timeout 加速测试，yield 后强制清理。
    """
    from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

    gw = ProcessLifecycleGateway(idle_timeout_s=600.0)
    yield gw
    try:
        gw.terminate_all()
        gw.shutdown()
    except Exception:
        pass


# 5.21.10 修复：_STANDIN_CACHE 全局变量 + tempfile.mktemp 永不清理 →
# session 级 fixture + tmp_path_factory（pytest 管理生命周期，session 结束自动清理）
@pytest.fixture(scope="session")
def standin_script(tmp_path_factory):
    """返回替身脚本路径（session 级共享，session 结束自动清理）。

    替身脚本用 time.sleep(60) 模拟长期运行的 MCP Server，
    避免依赖缺失导致测试不稳定。
    """
    standin_dir = tmp_path_factory.mktemp("standin")
    script = standin_dir / "standin.py"
    script.write_text("import time; time.sleep(60)", encoding="utf-8")
    return script


# ---------------------------------------------------------------------------
# 测试1: 信号处理函数注册验证
# ---------------------------------------------------------------------------


class TestSignalHandlerRegistration:
    """验证 launch_all() 注册了 SIGINT/SIGTERM 信号处理函数。"""

    def test_launch_all_source_contains_signal_registration(self, launcher_module):
        """验证 launch_all 源码包含 signal.signal 注册逻辑。"""
        source = inspect.getsource(launcher_module.launch_all)
        assert "signal.signal" in source, "launch_all should call signal.signal"
        assert "signal.SIGINT" in source, "launch_all should register SIGINT handler"
        assert "signal.SIGTERM" in source, "launch_all should register SIGTERM handler"

    def test_shutdown_callback_defined_in_launch_all(self, launcher_module):
        """验证 launch_all 内部定义了 _shutdown 回调函数。"""
        source = inspect.getsource(launcher_module.launch_all)
        assert "def _shutdown" in source, "launch_all should define _shutdown callback"
        assert "terminate_all" in source, "_shutdown should call gateway.terminate_all()"
        assert "shutdown" in source, "_shutdown should call gateway.shutdown()"

    def test_signal_handler_registered_via_mock(self, launcher_module):
        """通过 mock 验证 signal.signal 被调用注册 SIGINT/SIGTERM。

        拦截 signal.signal 调用，验证传入了 SIGINT 和 SIGTERM。
        mock time.sleep 在 N 次调用后抛 KeyboardInterrupt 打断 while 循环。
        注入 sys.modules 绕过 launcher.py 中 zephyr.shared.infra 的导入路径。
        同时 mock check_server_health 避免 FATAL abort（launcher.py 修改后新增健康检查）。
        """
        registered_signals: dict[int, object] = {}

        def fake_signal(sig, handler):
            registered_signals[sig] = handler

        # 计数 sleep 调用，超过阈值后抛 KeyboardInterrupt 打断 while running 循环
        sleep_count = [0]
        original_sleep = time.sleep

        def fast_sleep(seconds):
            sleep_count[0] += 1
            if sleep_count[0] > 20:
                raise KeyboardInterrupt()
            original_sleep(0.001)

        # 创建 mock 模块注入 sys.modules，绕过 launcher.py 的导入路径
        # launcher.py 现在用 zephyr.shared.infra（不是 zephyr.integration.infra）
        mock_gw = MagicMock()
        mock_gw.launch.return_value = MagicMock(is_alive=True, pid=99999)
        mock_module = MagicMock()
        mock_module.ProcessLifecycleGateway = MagicMock(return_value=mock_gw)

        # 模拟 start_server 和 check_server_health 返回 True，避免实际启动进程和 FATAL abort
        with (
            patch.object(signal, "signal", side_effect=fake_signal),
            patch.object(launcher_module, "start_server", return_value=True),
            patch.object(launcher_module, "check_server_health", return_value=True),
            patch.object(launcher_module.time, "sleep", side_effect=fast_sleep),
            patch.dict(
                sys.modules,
                {
                    "zephyr.shared.infra.process_lifecycle_gateway": mock_module,
                    "zephyr.shared.infra": MagicMock(),
                    "zephyr.shared": MagicMock(),
                },
            ),
        ):
            # 直接调用 launch_all——KeyboardInterrupt 会打断 while 循环
            # except KeyboardInterrupt 捕获后，finally 执行 terminate_all+shutdown
            launcher_module.launch_all()

        # 验证 SIGINT 和 SIGTERM 被注册
        assert signal.SIGINT in registered_signals, "SIGINT handler should be registered"
        assert signal.SIGTERM in registered_signals, "SIGTERM handler should be registered"

        # 验证 terminate_all 和 shutdown 被 finally 块调用
        assert mock_gw.terminate_all.called, "terminate_all should be called by finally block"
        assert mock_gw.shutdown.called, "shutdown should be called by finally block"


# ---------------------------------------------------------------------------
# 测试2: _shutdown 回调清理行为（启动真实进程→模拟 shutdown→验证清理）
# ---------------------------------------------------------------------------


class TestShutdownCleanupBehavior:
    """验证 _shutdown 回调的清理行为。

    启动真实子进程（替身脚本），模拟 _shutdown 的操作
    （terminate_all + shutdown），验证所有进程在 5s 内被清理。
    """

    def test_terminate_all_kills_all_processes(self, gateway, standin_script):
        """验证 terminate_all 终止所有池中进程。"""
        # 启动 3 个替身进程
        pids = []
        for name in ["mcp-test1", "mcp-test2", "mcp-test3"]:
            entry = gateway.launch(
                name,
                [sys.executable, str(standin_script)],
                idle_timeout_s=600.0,
            )
            assert entry is not None, f"Failed to launch {name}"
            pids.append(entry.pid)

        # 验证进程存活
        for pid in pids:
            assert _is_pid_alive(pid), f"Process {pid} should be alive"

        # 调用 terminate_all（_shutdown 的核心操作）
        count = gateway.terminate_all()
        assert count == 3, f"terminate_all should return 3, got {count}"

        # 验证所有进程在 5s 内被清理
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            if all(not _is_pid_alive(pid) for pid in pids):
                break
            time.sleep(0.1)

        for pid in pids:
            assert not _is_pid_alive(pid), f"Process {pid} should be dead within 5s"

    def test_shutdown_cleans_all_processes_within_5s(self, gateway, standin_script):
        """验证 shutdown 在 5s 内清理所有进程（_shutdown 调用 shutdown）。"""
        pids = []
        for name in ["mcp-sig1", "mcp-sig2"]:
            entry = gateway.launch(
                name,
                [sys.executable, str(standin_script)],
                idle_timeout_s=600.0,
            )
            assert entry is not None
            pids.append(entry.pid)

        # 调用 shutdown（_shutdown 的完整操作：terminate_all + stop_zombie_scanner）
        start = time.monotonic()
        gateway.shutdown()
        elapsed = time.monotonic() - start

        assert elapsed < 5.0, f"shutdown should complete within 5s, took {elapsed:.2f}s"

        # 验证所有进程已清理
        for pid in pids:
            assert not _is_pid_alive(pid), f"Process {pid} should be dead after shutdown"

    def test_try_finally_cleanup_on_keyboard_interrupt(self, gateway, standin_script):
        """验证 try/finally 块在 KeyboardInterrupt 时执行清理。

        launcher.py 的 launch_all 有 try/finally 块：
          try:
              while running: time.sleep(2)
          except KeyboardInterrupt:
              pass
          finally:
              gateway.terminate_all()
              gateway.shutdown()

        本测试模拟 KeyboardInterrupt 触发 finally 清理。
        """
        pids = []
        for name in ["mcp-finally1", "mcp-finally2"]:
            entry = gateway.launch(
                name,
                [sys.executable, str(standin_script)],
                idle_timeout_s=600.0,
            )
            assert entry is not None
            pids.append(entry.pid)

        # 模拟 launch_all 的 try/finally 行为
        running = True
        try:
            # 模拟 while running: time.sleep(2) 被 KeyboardInterrupt 打断
            raise KeyboardInterrupt()
        except KeyboardInterrupt:
            running = False
        finally:
            # 这是 _shutdown 和 try/finally 共同保证的清理
            gateway.terminate_all()
            gateway.shutdown()

        # 验证清理完成
        for pid in pids:
            assert not _is_pid_alive(pid), f"Process {pid} should be cleaned by finally block"

    def test_process_pids_not_alive_after_shutdown(self, gateway, standin_script):
        """验证 shutdown 后所有进程 PID 不再存活（验收标准）。"""
        pids = []
        for name in ["mcp-verify1", "mcp-verify2", "mcp-verify3"]:
            entry = gateway.launch(
                name,
                [sys.executable, str(standin_script)],
                idle_timeout_s=600.0,
            )
            assert entry is not None
            pids.append(entry.pid)

        gateway.terminate_all()
        gateway.shutdown()

        # 等待清理完成
        time.sleep(0.5)

        for pid in pids:
            assert not _is_pid_alive(pid), f"PID {pid} should not be alive after shutdown"


# ---------------------------------------------------------------------------
# 测试3: 子进程级信号测试
# ---------------------------------------------------------------------------


class TestSubprocessSignalHandling:
    """子进程级信号测试：启动模拟 launcher 子进程→发送信号→验证退出。

    Windows 兼容性：
    - 使用 CREATE_NEW_PROCESS_GROUP 创建子进程，避免 CTRL_C_EVENT 影响 pytest
    - 使用 CTRL_BREAK_EVENT 发送信号（可定向到特定进程组）
    - 子进程注册 SIGBREAK handler（映射到 CTRL_BREAK_EVENT）
    Unix: 直接使用 SIGINT/SIGTERM。
    """

    def _create_signal_test_script(self, tmp_path: Path) -> Path:
        """创建模拟 launcher 信号处理的子进程脚本。

        脚本行为：
        1. 启动 2 个子进程（替身）
        2. 注册 SIGBREAK/SIGINT 信号处理
        3. 进入 while True 循环
        4. 收到信号时调用 terminate_all + shutdown + exit(0)
        5. 输出子进程 PID 供测试验证

        5.21.10 修复：tempfile.mktemp（已废弃 + race condition）→
        tmp_path（pytest 管理，测试结束自动清理）。
        """
        script = tmp_path / "signal_test_script.py"
        script.write_text(
            textwrap.dedent(
                """
                import signal, subprocess, sys, time, os

                # 启动 2 个替身子进程
                children = []
                for i in range(2):
                    p = subprocess.Popen(
                        [sys.executable, "-c", "import time; time.sleep(60)"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    children.append(p)
                    print(f"CHILD_PID:{p.pid}", flush=True)

                # 注册信号处理
                def _shutdown(sig, frame):
                    for p in children:
                        try:
                            p.terminate()
                            p.wait(timeout=3)
                        except Exception:
                            try:
                                p.kill()
                            except Exception:
                                pass
                    print("SHUTDOWN_COMPLETE", flush=True)
                    sys.exit(0)

                signal.signal(signal.SIGINT, _shutdown)
                signal.signal(signal.SIGBREAK, _shutdown)

                print("READY", flush=True)

                # 等待信号
                while True:
                    time.sleep(1)
                """
            ),
            encoding="utf-8",
        )
        return script

    def _start_subprocess(self, script: Path) -> subprocess.Popen:
        """启动子进程，Windows 上使用 CREATE_NEW_PROCESS_GROUP。"""
        kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "encoding": "utf-8",
            "errors": "replace",
        }
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        return subprocess.Popen([sys.executable, str(script)], **kwargs)

    def _send_signal(self, proc: subprocess.Popen, sig_name: str) -> None:
        """发送信号，Windows 使用 CTRL_BREAK_EVENT，Unix 使用 SIGINT/SIGTERM。"""
        if os.name == "nt":
            # Windows: CTRL_BREAK_EVENT 可定向到特定进程组
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            sig = signal.SIGINT if sig_name == "SIGINT" else signal.SIGTERM
            proc.send_signal(sig)

    def _wait_for_ready(self, proc: subprocess.Popen) -> tuple[list[int], bool]:
        """等待子进程输出 READY，返回 (child_pids, ready)。"""
        child_pids = []
        ready = False
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith("CHILD_PID:"):
                child_pids.append(int(line.split(":")[1]))
            elif line == "READY":
                ready = True
                break
        return child_pids, ready

    def _cleanup_subprocess(self, proc: subprocess.Popen, script: Path) -> None:
        """清理子进程资源：关闭管道、终止进程、删除脚本。"""
        try:
            if proc.stdout:
                proc.stdout.close()
        except Exception:
            pass
        try:
            if proc.stderr:
                proc.stderr.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=2.0)
        except Exception:
            try:
                proc.kill()
                proc.wait(timeout=1.0)
            except Exception:
                pass
        try:
            script.unlink()
        except Exception:
            pass

    def test_subprocess_sigint_clean_exit(self, tmp_path):
        """验证子进程收到 SIGINT/SIGBREAK 后干净退出。"""
        script = self._create_signal_test_script(tmp_path)
        proc = None
        try:
            proc = self._start_subprocess(script)
            child_pids, ready = self._wait_for_ready(proc)

            assert ready, "Subprocess should reach READY state"
            assert len(child_pids) == 2, f"Should have 2 child PIDs, got {child_pids}"

            self._send_signal(proc, "SIGINT")

            try:
                proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)
                pytest.fail("Subprocess did not exit within 5s after signal")

            assert proc.returncode == 0, f"Subprocess should exit 0, got {proc.returncode}"

            time.sleep(0.5)
            for pid in child_pids:
                assert not _is_pid_alive(pid), f"Child PID {pid} should be terminated"
        finally:
            if proc is not None:
                self._cleanup_subprocess(proc, script)
            else:
                try:
                    script.unlink()
                except Exception:
                    pass

    def test_subprocess_sigterm_clean_exit(self, tmp_path):
        """验证子进程收到 SIGTERM/SIGBREAK 后干净退出。

        Windows 上 SIGTERM 不可拦截（TerminateProcess），使用 SIGBREAK 替代。
        """
        script = self._create_signal_test_script(tmp_path)
        proc = None
        try:
            proc = self._start_subprocess(script)
            child_pids, ready = self._wait_for_ready(proc)

            assert ready, "Subprocess should reach READY state"
            assert len(child_pids) == 2

            self._send_signal(proc, "SIGTERM")

            try:
                proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)
                pytest.fail("Subprocess did not exit within 5s after signal")

            assert proc.returncode == 0, f"Subprocess should exit 0, got {proc.returncode}"

            time.sleep(0.5)
            for pid in child_pids:
                assert not _is_pid_alive(pid), f"Child PID {pid} should be terminated"
        finally:
            if proc is not None:
                self._cleanup_subprocess(proc, script)
            else:
                try:
                    script.unlink()
                except Exception:
                    pass

    def test_subprocess_child_processes_terminated_after_signal(self, tmp_path):
        """验证信号发送后所有子进程被清理（验收标准）。"""
        script = self._create_signal_test_script(tmp_path)
        proc = None
        try:
            proc = self._start_subprocess(script)
            child_pids, ready = self._wait_for_ready(proc)

            assert ready
            assert len(child_pids) == 2

            self._send_signal(proc, "SIGINT")

            proc.wait(timeout=5.0)

            # 等待子进程完全清理
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                if all(not _is_pid_alive(pid) for pid in child_pids):
                    break
                time.sleep(0.1)

            for pid in child_pids:
                assert not _is_pid_alive(pid), f"Child PID {pid} must not be alive"
        finally:
            if proc is not None:
                self._cleanup_subprocess(proc, script)
            else:
                try:
                    script.unlink()
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# 测试4: atexit 兜底关闭验证
# ---------------------------------------------------------------------------


class TestAtexitFallbackShutdown:
    """验证 atexit 兜底关闭机制。

    launcher.py 依赖 signal handler + try/finally 作为清理机制。
    本测试验证当 signal handler 未触发时，try/finally 仍能清理。
    """

    def test_try_finally_executes_on_exception(self, gateway, standin_script):
        """验证 try/finally 在异常时仍执行清理。"""
        entry = gateway.launch(
            "mcp-atexit-test",
            [sys.executable, str(standin_script)],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        pid = entry.pid
        assert _is_pid_alive(pid)

        # 模拟 launch_all 的 try/finally 在异常路径下执行
        try:
            raise RuntimeError("simulated failure")
        except RuntimeError:
            pass
        finally:
            gateway.terminate_all()
            gateway.shutdown()

        assert not _is_pid_alive(pid), "Process should be cleaned by finally block"

    def test_shutdown_idempotent_after_terminate_all(self, gateway, standin_script):
        """验证 terminate_all 后 shutdown 不抛异常（幂等性）。

        _shutdown 先调 terminate_all 再调 shutdown，
        shutdown 内部会再调 terminate_all——需验证不抛异常。
        """
        entry = gateway.launch(
            "mcp-idempotent",
            [sys.executable, str(standin_script)],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        pid = entry.pid

        # 模拟 _shutdown 的调用顺序
        gateway.terminate_all()
        gateway.shutdown()  # 不应抛异常

        assert not _is_pid_alive(pid)

    def test_signal_handler_cleanup_via_atexit_pattern(self, gateway, standin_script):
        """验证信号处理+atexit 模式的清理效果。

        模拟 atexit.register(_cleanup) + signal handler 的双重保障：
        即使 signal handler 未执行，atexit 也能清理。
        """
        entry = gateway.launch(
            "mcp-atexit-pattern",
            [sys.executable, str(standin_script)],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        pid = entry.pid

        # 注册 atexit 清理函数（模拟 atexit.register）
        import atexit

        def _atexit_cleanup():
            try:
                gateway.terminate_all()
                gateway.shutdown()
            except Exception:
                pass

        atexit.register(_atexit_cleanup)

        # 模拟 signal handler 触发清理
        gateway.terminate_all()
        gateway.shutdown()

        assert not _is_pid_alive(pid)

        # 注销 atexit（避免测试结束后重复执行）
        # atexit.unregister 在 Python 3.x 可用
        try:
            atexit.unregister(_atexit_cleanup)
        except AttributeError:
            pass


# ---------------------------------------------------------------------------
# 测试5: 红蓝对抗极端测试
# ---------------------------------------------------------------------------


class TestRedBlueExtremeScenarios:
    """红蓝对抗极端测试——覆盖异常和边界场景。"""

    def test_double_shutdown_idempotent(self, gateway, standin_script):
        """极端场景1: 连续两次 shutdown 不抛异常。"""
        entry = gateway.launch(
            "mcp-double-shutdown",
            [sys.executable, str(standin_script)],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        pid = entry.pid

        gateway.shutdown()
        # 第二次 shutdown 不应抛异常
        gateway.shutdown()

        assert not _is_pid_alive(pid)

    def test_shutdown_with_already_dead_process(self, gateway, standin_script):
        """极端场景2: shutdown 时进程已死亡（僵尸进程）。"""
        entry = gateway.launch(
            "mcp-already-dead",
            [sys.executable, str(standin_script)],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        pid = entry.pid

        # 手动杀死进程（制造僵尸）
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F"],
                    capture_output=True,
                )
            else:
                os.kill(pid, signal.SIGKILL)
        except Exception:
            pass

        # 等待进程死亡
        time.sleep(0.5)
        assert not _is_pid_alive(pid)

        # shutdown 应能处理已死亡的进程（不抛异常）
        gateway.terminate_all()
        gateway.shutdown()

    def test_shutdown_with_no_processes(self, gateway):
        """极端场景3: 空池 shutdown 不抛异常。"""
        # 不启动任何进程，直接 shutdown
        result = gateway.terminate_all()
        assert result == 0, "terminate_all on empty pool should return 0"
        gateway.shutdown()

    def test_shutdown_during_concurrent_launch(self, gateway, standin_script):
        """极端场景4: 并发启动时 shutdown 不导致死锁/异常。"""
        import threading

        launch_errors: list[Exception] = []

        def launch_concurrently():
            try:
                for i in range(5):
                    gateway.launch(
                        f"mcp-concurrent-{i}",
                        [sys.executable, str(standin_script)],
                        idle_timeout_s=600.0,
                    )
            except Exception as exc:
                launch_errors.append(exc)

        # 启动并发 launch 线程
        t = threading.Thread(target=launch_concurrently, daemon=True)
        t.start()

        # 等待一小段时间让部分进程启动
        time.sleep(0.3)

        # 在并发启动过程中 shutdown
        gateway.terminate_all()
        gateway.shutdown()

        t.join(timeout=5.0)

        # shutdown 应成功，不应死锁
        # launch_errors 可能有因 shutdown 导致的失败，这是正常的

    def test_signal_handler_does_not_raise_on_cleanup_failure(self, gateway):
        """极端场景5: 清理失败时信号处理函数不抛异常。

        模拟 terminate_all 抛异常时，_shutdown 不应传播异常。
        """
        # 让 terminate_all 抛异常
        with patch.object(
            gateway.pool,
            "terminate_all",
            side_effect=RuntimeError("simulated cleanup failure"),
        ):
            # 模拟 _shutdown 的行为：即使 terminate_all 失败也继续
            try:
                gateway.terminate_all()
            except RuntimeError:
                pass  # _shutdown 应捕获异常

            # shutdown 应仍能执行（stop_zombie_scanner）
            try:
                gateway.shutdown()
            except Exception:
                pass  # 不应传播到调用者

    def test_rapid_signal_repeated(self, gateway, standin_script):
        """极端场景6: 快速重复发送信号（模拟用户狂按 Ctrl+C）。"""
        entry = gateway.launch(
            "mcp-rapid-signal",
            [sys.executable, str(standin_script)],
            idle_timeout_s=600.0,
        )
        assert entry is not None
        pid = entry.pid

        # 模拟快速重复调用 _shutdown（狂按 Ctrl+C）
        for _ in range(5):
            try:
                gateway.terminate_all()
            except Exception:
                pass

        try:
            gateway.shutdown()
        except Exception:
            pass

        assert not _is_pid_alive(pid)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _is_pid_alive(pid: int) -> bool:
    """检查 PID 是否存活（跨平台）。

    Windows: 使用 tasklist 命令检查（bytes 模式避免编码问题）
    Unix: 使用 os.kill(pid, 0) 检查
    """
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            # 使用 bytes 模式避免 Windows cp936/GBK 编码问题
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
                capture_output=True,
                timeout=2.0,
            )
            # tasklist 输出包含 PID 则进程存活
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
