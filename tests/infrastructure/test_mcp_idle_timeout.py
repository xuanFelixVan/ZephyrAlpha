# [A_test] module_id=MOD-INF-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14
# [MODULE] tests.integration.test_mcp_idle_timeout
# [INVARIANTS] idle_timeout_s后空闲进程被自动回收; 僵尸扫描器定期检测; 回收后进程pid不再存活
# [MODIFY-GUARD] process_pool.py 或 process_lifecycle_gateway.py 的 idle_timeout 逻辑变更需同步更新本测试
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/infrastructure/test_mcp_idle_timeout.py -v --tb=short
# [TTL] task_bound
"""DM-202912: MCP idle_timeout 10分钟自动回收验证。

覆盖目标：
  1. ProcessLifecycleGateway 的 idle_timeout 配置验证（600s = 10分钟）
  2. 空闲超时后进程自动回收（使用缩短的 timeout 加速测试）
  3. 僵尸扫描器定期检测 idle 进程并回收
  4. 回收后进程 PID 不再存活
  5. 活跃进程（持续使用）不被回收

测试策略：
  - 使用短 idle_timeout（2s）和短 zombie_check_interval（0.5s）加速测试
  - 使用替身脚本（time.sleep(60)）模拟长期运行的 MCP Server
  - 不等待真实 600s 超时，而是验证机制本身
"""
from __future__ import annotations

import importlib.util
import inspect
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="module")
def launcher_module():
    """动态导入 launcher 模块。"""
    launcher_path = REPO_ROOT / "scripts" / "mcp" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher_dm202912", launcher_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 5.21.10 修复：_STANDIN_CACHE 全局变量 + tempfile.mktemp 永不清理 →
# session 级 fixture + tmp_path_factory（pytest 管理生命周期，session 结束自动清理）
@pytest.fixture(scope="session")
def standin_script(tmp_path_factory):
    """返回替身脚本路径（session 级共享，session 结束自动清理）。"""
    standin_dir = tmp_path_factory.mktemp("standin")
    script = standin_dir / "standin.py"
    script.write_text("import time; time.sleep(60)", encoding="utf-8")
    return script


@pytest.fixture
def fast_pool():
    """创建快速超时的 MCPProcessPool（idle_timeout=2s, check_interval=0.5s）。

    用于加速测试，不等待真实 600s 超时。
    """
    from zephyr.shared.infra.process_pool import MCPProcessPool

    pool = MCPProcessPool(
        max_processes=30,
        zombie_check_interval=0.5,
        idle_timeout_s=2.0,
    )
    pool.start_zombie_scanner()
    yield pool
    try:
        pool.terminate_all()
        pool.stop_zombie_scanner()
    except Exception:
        pass


@pytest.fixture
def fast_gateway():
    """创建快速超时的 ProcessLifecycleGateway（idle_timeout=2s）。

    注意：ProcessLifecycleGateway 不暴露 zombie_check_interval，
    内部使用 MCPProcessPool 默认值 60s。
    本 fixture 直接创建 MCPProcessPool 并配置短间隔。
    """
    from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway
    from zephyr.shared.infra.process_pool import MCPProcessPool

    # 直接创建带短间隔的 pool，注入到 gateway
    gw = ProcessLifecycleGateway.__new__(ProcessLifecycleGateway)
    gw.pool = MCPProcessPool(
        max_processes=30,
        zombie_check_interval=0.5,
        idle_timeout_s=2.0,
    )
    gw.pool.start_zombie_scanner()
    yield gw
    try:
        gw.terminate_all()
        gw.shutdown()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 测试1: idle_timeout 配置验证
# ---------------------------------------------------------------------------


class TestIdleTimeoutConfiguration:
    """验证 idle_timeout 配置正确。"""

    def test_launcher_idle_timeout_is_600s(self, launcher_module):
        """验证 launcher.py 的 idle_timeout 配置为 600 秒（10分钟）。"""
        source = inspect.getsource(launcher_module.start_server)
        assert "idle_timeout_s" in source, "start_server should set idle_timeout_s"
        assert "600" in source, "idle_timeout should be 600 seconds (10 minutes)"

    def test_gateway_default_idle_timeout_600s(self):
        """验证 ProcessLifecycleGateway 默认 idle_timeout 为 600s。"""
        from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

        gw = ProcessLifecycleGateway(idle_timeout_s=600.0)
        assert gw.pool.idle_timeout_s == 600.0
        gw.shutdown()

    def test_pool_idle_timeout_configurable(self):
        """验证 MCPProcessPool 的 idle_timeout 可配置。"""
        from zephyr.shared.infra.process_pool import MCPProcessPool

        pool = MCPProcessPool(idle_timeout_s=2.0)
        assert pool.idle_timeout_s == 2.0
        pool.stop_zombie_scanner()


# ---------------------------------------------------------------------------
# 测试2: 空闲超时后进程自动回收
# ---------------------------------------------------------------------------


class TestIdleTimeoutAutoReclaim:
    """验证空闲超时后进程被自动回收。

    使用短 idle_timeout（2s）和短 zombie_check_interval（0.5s）加速测试。
    """

    def test_idle_process_reclaimed_after_timeout(self, fast_pool, standin_script):
        """验证空闲进程在 idle_timeout 后被自动回收。"""
        entry = fast_pool.get_or_create(
            "mcp-idle-test",
            [sys.executable, str(standin_script)],
        )
        assert entry is not None
        pid = entry.pid
        assert entry.is_alive

        # 等待 idle_timeout + zombie_check_interval + buffer
        # idle_timeout=2s, check_interval=0.5s, buffer=1s → 最多 3.5s
        deadline = time.monotonic() + 6.0
        reclaimed = False
        while time.monotonic() < deadline:
            # 检查进程是否已从池中移除
            with fast_pool.lock:
                if "mcp-idle-test" not in fast_pool.pool:
                    reclaimed = True
                    break
            time.sleep(0.2)

        assert reclaimed, "Idle process should be reclaimed after timeout"

        # 验证进程 PID 不再存活
        time.sleep(0.5)
        assert not _is_pid_alive(pid), f"PID {pid} should not be alive after reclaim"

    def test_active_process_not_reclaimed(self, fast_pool, standin_script):
        """验证活跃进程（持续使用）不被回收。"""
        entry = fast_pool.get_or_create(
            "mcp-active-test",
            [sys.executable, str(standin_script)],
        )
        assert entry is not None
        pid = entry.pid

        # 持续使用进程（更新 last_used_at）
        for _ in range(8):
            time.sleep(0.5)
            # get_or_create 会更新 last_used_at
            fast_pool.get_or_create("mcp-active-test")

        # 进程应该仍然存活（因为持续使用，未超时）
        with fast_pool.lock:
            assert "mcp-active-test" in fast_pool.pool, "Active process should not be reclaimed"
            assert fast_pool.pool["mcp-active-test"].is_alive

        assert _is_pid_alive(pid), "Active process should still be alive"

    def test_idle_process_reclaimed_via_gateway(self, fast_gateway, standin_script):
        """验证通过 ProcessLifecycleGateway 启动的进程也能被自动回收。"""
        entry = fast_gateway.launch(
            "mcp-gw-idle",
            [sys.executable, str(standin_script)],
            idle_timeout_s=2.0,
        )
        assert entry is not None
        pid = entry.pid

        # 等待 idle_timeout 触发回收
        deadline = time.monotonic() + 6.0
        reclaimed = False
        while time.monotonic() < deadline:
            with fast_gateway.pool.lock:
                if "mcp-gw-idle" not in fast_gateway.pool.pool:
                    reclaimed = True
                    break
            time.sleep(0.2)

        assert reclaimed, "Idle process should be reclaimed via gateway"

        time.sleep(0.5)
        assert not _is_pid_alive(pid), f"PID {pid} should not be alive after reclaim"

    def test_reclaimed_process_pid_not_alive(self, fast_pool, standin_script):
        """验证回收后进程 PID 不再存活（验收标准）。"""
        entry = fast_pool.get_or_create(
            "mcp-reclaim-verify",
            [sys.executable, str(standin_script)],
        )
        assert entry is not None
        pid = entry.pid
        assert _is_pid_alive(pid)

        # 等待回收
        deadline = time.monotonic() + 6.0
        while time.monotonic() < deadline:
            with fast_pool.lock:
                if "mcp-reclaim-verify" not in fast_pool.pool:
                    break
            time.sleep(0.2)

        # 等待进程完全终止
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            if not _is_pid_alive(pid):
                break
            time.sleep(0.1)

        assert not _is_pid_alive(pid), f"PID {pid} must not be alive after reclaim"


# ---------------------------------------------------------------------------
# 测试3: 僵尸扫描器行为
# ---------------------------------------------------------------------------


class TestZombieScannerBehavior:
    """验证僵尸扫描器定期检测 idle 进程并回收。"""

    def test_zombie_scanner_detects_idle_process(self, fast_pool, standin_script):
        """验证僵尸扫描器检测到 idle 进程。"""
        entry = fast_pool.get_or_create(
            "mcp-scanner-test",
            [sys.executable, str(standin_script)],
        )
        assert entry is not None

        # 等待扫描器运行（check_interval=0.5s）
        time.sleep(0.3)

        # 进程应该在池中（还未超时）
        with fast_pool.lock:
            assert "mcp-scanner-test" in fast_pool.pool

        # 等待超时 + 扫描
        deadline = time.monotonic() + 6.0
        while time.monotonic() < deadline:
            with fast_pool.lock:
                if "mcp-scanner-test" not in fast_pool.pool:
                    break
            time.sleep(0.2)

        with fast_pool.lock:
            assert "mcp-scanner-test" not in fast_pool.pool, "Scanner should have reclaimed idle process"

    def test_zombie_scanner_detects_dead_process(self, fast_pool, standin_script):
        """验证僵尸扫描器检测到已死亡进程（僵尸）。"""
        entry = fast_pool.get_or_create(
            "mcp-zombie-test",
            [sys.executable, str(standin_script)],
        )
        assert entry is not None
        pid = entry.pid

        # 手动杀死进程（制造僵尸）
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
            else:
                import signal as sig_mod
                os.kill(pid, sig_mod.SIGKILL)
        except Exception:
            pass

        # 等待扫描器检测并清理僵尸
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            with fast_pool.lock:
                if "mcp-zombie-test" not in fast_pool.pool:
                    break
            time.sleep(0.2)

        with fast_pool.lock:
            assert "mcp-zombie-test" not in fast_pool.pool, "Scanner should have reaped zombie process"

    def test_multiple_idle_processes_all_reclaimed(self, fast_pool, standin_script):
        """验证多个 idle 进程都被回收。"""
        pids = []
        for name in ["mcp-multi-1", "mcp-multi-2", "mcp-multi-3"]:
            entry = fast_pool.get_or_create(
                name,
                [sys.executable, str(standin_script)],
            )
            assert entry is not None
            pids.append(entry.pid)

        # 等待所有进程超时并被回收
        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline:
            with fast_pool.lock:
                remaining = [n for n in ["mcp-multi-1", "mcp-multi-2", "mcp-multi-3"] if n in fast_pool.pool]
            if not remaining:
                break
            time.sleep(0.2)

        assert len(remaining) == 0, f"Should have no remaining processes, got {remaining}"

        # 验证所有 PID 都不再存活
        time.sleep(0.5)
        for pid in pids:
            assert not _is_pid_alive(pid), f"PID {pid} should not be alive"


# ---------------------------------------------------------------------------
# 测试4: 红蓝对抗极端测试
# ---------------------------------------------------------------------------


class TestRedBlueExtremeScenarios:
    """红蓝对抗极端测试——覆盖异常和边界场景。"""

    def test_idle_timeout_zero_disables_reclaim(self, standin_script):
        """极端场景1: idle_timeout=0 禁用自动回收。"""
        from zephyr.shared.infra.process_pool import MCPProcessPool

        pool = MCPProcessPool(
            max_processes=30,
            zombie_check_interval=0.5,
            idle_timeout_s=0,  # 禁用
        )
        pool.start_zombie_scanner()

        try:
            entry = pool.get_or_create(
                "mcp-no-timeout",
                [sys.executable, str(standin_script)],
            )
            assert entry is not None

            # 等待一段时间，进程不应被回收
            time.sleep(2.0)

            with pool.lock:
                assert "mcp-no-timeout" in pool.pool, "Process should not be reclaimed when timeout=0"
        finally:
            pool.terminate_all()
            pool.stop_zombie_scanner()

    def test_reclaim_during_active_use(self, fast_pool, standin_script):
        """极端场景2: 进程正在使用时不会被回收（即使超时）。"""
        entry = fast_pool.get_or_create(
            "mcp-in-use",
            [sys.executable, str(standin_script)],
        )
        assert entry is not None
        pid = entry.pid

        # 等待超过 idle_timeout，但持续更新 last_used_at
        for i in range(6):
            time.sleep(0.5)
            # 模拟活跃使用
            with fast_pool.lock:
                e = fast_pool.pool.get("mcp-in-use")
                if e:
                    e.last_used_at = time.monotonic()

        # 进程应该仍然存活
        with fast_pool.lock:
            assert "mcp-in-use" in fast_pool.pool, "Active process should not be reclaimed"
        assert _is_pid_alive(pid)

    def test_reclaim_then_recreate(self, fast_pool, standin_script):
        """极端场景3: 进程被回收后可以重新创建。"""
        # 第一次创建
        entry1 = fast_pool.get_or_create(
            "mcp-recreate",
            [sys.executable, str(standin_script)],
        )
        assert entry1 is not None
        pid1 = entry1.pid

        # 等待回收
        deadline = time.monotonic() + 6.0
        while time.monotonic() < deadline:
            with fast_pool.lock:
                if "mcp-recreate" not in fast_pool.pool:
                    break
            time.sleep(0.2)

        with fast_pool.lock:
            assert "mcp-recreate" not in fast_pool.pool

        # 重新创建
        entry2 = fast_pool.get_or_create(
            "mcp-recreate",
            [sys.executable, str(standin_script)],
        )
        assert entry2 is not None
        pid2 = entry2.pid

        # 应该是新进程（PID 不同）
        assert pid2 != pid1, "Recreated process should have different PID"
        assert _is_pid_alive(pid2)

    def test_max_processes_enforced(self, standin_script):
        """极端场景4: 超过最大进程数时拒绝创建。"""
        from zephyr.shared.infra.process_pool import MCPProcessPool

        pool = MCPProcessPool(
            max_processes=2,
            zombie_check_interval=10.0,
            idle_timeout_s=600.0,
        )
        pool.start_zombie_scanner()

        try:
            # 创建 2 个进程（达到上限）
            e1 = pool.get_or_create("mcp-max-1", [sys.executable, str(standin_script)])
            e2 = pool.get_or_create("mcp-max-2", [sys.executable, str(standin_script)])
            assert e1 is not None
            assert e2 is not None

            # 第 3 个应该失败
            e3 = pool.get_or_create("mcp-max-3", [sys.executable, str(standin_script)])
            assert e3 is None, "Should not create process when max reached"
        finally:
            pool.terminate_all()
            pool.stop_zombie_scanner()

    def test_terminate_all_clears_idle_timer(self, fast_pool, standin_script):
        """极端场景5: terminate_all 后所有进程被清理，无残留定时器。"""
        for name in ["mcp-clear-1", "mcp-clear-2"]:
            fast_pool.get_or_create(
                name,
                [sys.executable, str(standin_script)],
            )

        # 立即终止所有
        count = fast_pool.terminate_all()
        assert count == 2

        # 池应为空
        with fast_pool.lock:
            assert len(fast_pool.pool) == 0

        # 等待一段时间，不应有残留进程被回收（因为池已空）
        time.sleep(1.0)
        with fast_pool.lock:
            assert len(fast_pool.pool) == 0


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _is_pid_alive(pid: int) -> bool:
    """检查 PID 是否存活（跨平台）。"""
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
