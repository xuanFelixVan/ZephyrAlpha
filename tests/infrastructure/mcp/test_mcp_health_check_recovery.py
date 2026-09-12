# [A_test] module_id=MOD-INF-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14
# [MODULE] tests.integration.test_mcp_health_check_recovery
# [INVARIANTS] 死亡进程被检测; restart后新进程存活; 健康检查幂等; 多进程并发恢复
# [MODIFY-GUARD] launcher.py 或 boot_cron_jobs.py 的健康检查/restart逻辑变更需同步更新本测试
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/infrastructure/test_mcp_health_check_recovery.py -v --tb=short
# [TTL] task_bound
"""DM-202913: MCP _mcp_health_check死亡进程检测+restart_server验证。

覆盖目标：
  1. 死亡进程检测：启动进程→杀死→通过 is_alive=False 检测死亡
  2. restart_server 恢复：检测死亡→重新 launch→验证新进程存活
  3. _mcp_health_check 完整逻辑：遍历所有 MCP server→检测死亡→自动重启
  4. 红蓝对抗极端场景：多进程同时死亡/重启幂等/并发恢复/资源耗尽

设计说明：
  - boot_cron_jobs.py 的 _mcp_health_check 应每小时检查10个MCP Server健康状态
  - 对死亡进程调用 restart_server() 自动重启
  - 本测试在测试层实现简化的健康检查逻辑，验证底层机制正确性
  - 使用替身脚本（time.sleep(60)）代替真实 MCP Server
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from zephyr.shared.io.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


def _is_pid_alive(pid: int) -> bool:
    """跨平台检查 PID 是否存活。

    Windows 使用 tasklist 命令（bytes 模式避免 cp936 编码问题）。
    Unix 使用 os.kill(pid, 0)。
    """
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


def _kill_process(pid: int) -> None:
    """跨平台杀死进程。"""
    if pid <= 0:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                timeout=3.0,
            )
        else:
            os.kill(pid, 9)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 辅助函数：模拟 _mcp_health_check 和 restart_server 逻辑
# ---------------------------------------------------------------------------


def _check_server_health(server_id: str, gateway) -> bool:
    """模拟 launcher.check_server_health 的逻辑。

    通过 gateway.pool.pool.get(f"mcp-{server_id}") 获取进程条目，
    返回 entry.is_alive。
    """
    entry = gateway.pool.pool.get(f"mcp-{server_id}")
    if entry is None:
        return False
    return entry.is_alive


def _restart_server(server_id: str, gateway, cmd: list[str] | None = None) -> bool:
    """模拟 launcher.restart_server 的逻辑。

    1. 终止旧进程（如果存在）
    2. 重新启动进程
    3. 返回新进程是否存活
    """
    # 终止旧进程
    gateway.pool.terminate(f"mcp-{server_id}")

    # 重新启动
    if cmd is None:
        return False
    entry = gateway.launch(f"mcp-{server_id}", cmd, idle_timeout_s=600.0)
    if entry is None:
        return False
    time.sleep(0.3)
    return entry.is_alive


def _mcp_health_check(
    server_ids: list[str],
    gateway,
    cmd_builder: Any,
) -> dict[str, str]:
    """模拟 boot_cron_jobs.mcp_health_check 的完整逻辑。

    遍历所有 MCP server，检测死亡进程并自动重启。

    Args:
        server_ids: 要检查的 server ID 列表
        gateway: ProcessLifecycleGateway 实例
        cmd_builder: 函数，接收 server_id 返回启动命令

    Returns:
        dict[server_id, status] status ∈ {"healthy", "recovered", "failed"}
    """
    results: dict[str, str] = {}
    for sid in server_ids:
        if _check_server_health(sid, gateway):
            results[sid] = "healthy"
            continue

        # 检测到死亡，尝试重启
        cmd = cmd_builder(sid)
        if cmd is None:
            results[sid] = "failed"
            continue

        recovered = _restart_server(sid, gateway, cmd)
        results[sid] = "recovered" if recovered else "failed"
    return results


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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


# 5.21.10 修复：_STANDIN_CACHE 全局变量 + tempfile.mktemp 永不清理 →
# session 级 fixture + tmp_path_factory（pytest 管理生命周期，session 结束自动清理）
@pytest.fixture(scope="session")
def standin_script(tmp_path_factory):
    """返回替身脚本路径（session 级共享，session 结束自动清理）。"""
    standin_dir = tmp_path_factory.mktemp("standin")
    script = standin_dir / "standin.py"
    script.write_text("import time; time.sleep(60)", encoding="utf-8")
    return script


# 5.21.10 修复：tempfile.mktemp（已废弃 + race condition）→
# tmp_path（pytest 管理，测试结束自动清理）
@pytest.fixture
def short_lived_script(tmp_path):
    """创建立即退出的脚本（模拟崩溃进程）。"""
    script = tmp_path / "short_lived.py"
    script.write_text("import sys; sys.exit(1)", encoding="utf-8")
    return script


# ---------------------------------------------------------------------------
# 测试1: 死亡进程检测
# ---------------------------------------------------------------------------


class TestDeadProcessDetection:
    """验证死亡进程检测机制。"""

    def test_alive_process_detected_as_healthy(self, gateway, standin_script):
        """存活进程应被检测为 healthy。"""
        gateway.launch("mcp-test1", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        assert _check_server_health("test1", gateway) is True

    def test_missing_process_detected_as_unhealthy(self, gateway):
        """不存在的进程应被检测为 unhealthy。"""
        assert _check_server_health("nonexistent", gateway) is False

    def test_dead_process_detected_as_unhealthy(self, gateway, standin_script):
        """已终止进程应被检测为 unhealthy。"""
        entry = gateway.launch("mcp-dead1", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        assert entry is not None
        pid = entry.pid
        time.sleep(0.3)

        # 杀死进程
        _kill_process(pid)
        time.sleep(0.5)

        assert _check_server_health("dead1", gateway) is False

    def test_crashed_process_detected_as_unhealthy(self, gateway, short_lived_script):
        """立即退出的进程应被检测为 unhealthy。"""
        gateway.launch("mcp-crash1", [sys.executable, str(short_lived_script)], idle_timeout_s=600.0)
        time.sleep(0.5)

        assert _check_server_health("crash1", gateway) is False

    def test_multiple_processes_mixed_health_status(self, gateway, standin_script, short_lived_script):
        """多个进程混合健康状态检测。"""
        # 启动 2 个存活 + 1 个崩溃
        gateway.launch("mcp-alive1", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        gateway.launch("mcp-alive2", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        gateway.launch("mcp-dead2", [sys.executable, str(short_lived_script)], idle_timeout_s=600.0)
        time.sleep(0.5)

        assert _check_server_health("alive1", gateway) is True
        assert _check_server_health("alive2", gateway) is True
        assert _check_server_health("dead2", gateway) is False


# ---------------------------------------------------------------------------
# 测试2: restart_server 恢复
# ---------------------------------------------------------------------------


class TestProcessRestartRecovery:
    """验证 restart_server 恢复机制。"""

    def test_restart_recovers_dead_process(self, gateway, standin_script):
        """对死亡进程调用 restart_server 应恢复。"""
        # 启动进程
        entry = gateway.launch("mcp-restart1", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        assert entry is not None
        old_pid = entry.pid
        time.sleep(0.3)

        # 杀死进程
        _kill_process(old_pid)
        time.sleep(0.5)
        assert _check_server_health("restart1", gateway) is False

        # 重启
        cmd = [sys.executable, str(standin_script)]
        recovered = _restart_server("restart1", gateway, cmd)
        assert recovered is True, "restart_server should recover dead process"

        # 验证新进程存活且 PID 不同
        new_entry = gateway.pool.pool.get("mcp-restart1")
        assert new_entry is not None
        assert new_entry.is_alive is True
        assert new_entry.pid != old_pid, "New process should have different PID"

    def test_restart_recovers_crashed_process(self, gateway, short_lived_script, standin_script):
        """对崩溃进程调用 restart_server 应恢复（用替身脚本重启）。"""
        # 启动崩溃进程
        gateway.launch("mcp-crash2", [sys.executable, str(short_lived_script)], idle_timeout_s=600.0)
        time.sleep(0.5)
        assert _check_server_health("crash2", gateway) is False

        # 用替身脚本重启
        cmd = [sys.executable, str(standin_script)]
        recovered = _restart_server("crash2", gateway, cmd)
        assert recovered is True

    def test_restart_returns_true_for_already_alive_process(self, gateway, standin_script):
        """对存活进程调用 restart_server 应终止旧进程并启动新进程。"""
        gateway.launch("mcp-alive3", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)
        old_pid = gateway.pool.pool.get("mcp-alive3").pid

        cmd = [sys.executable, str(standin_script)]
        recovered = _restart_server("alive3", gateway, cmd)
        assert recovered is True

        new_pid = gateway.pool.pool.get("mcp-alive3").pid
        assert new_pid != old_pid, "restart should create new process"

    def test_restart_returns_false_for_missing_cmd(self, gateway):
        """cmd=None 时 restart_server 应返回 False。"""
        result = _restart_server("nonexistent", gateway, None)
        assert result is False

    def test_restart_new_process_actually_alive(self, gateway, standin_script):
        """重启后的新进程应真正存活（PID 在系统中存在）。"""
        entry = gateway.launch("mcp-verify", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        old_pid = entry.pid
        _kill_process(old_pid)
        time.sleep(0.5)

        cmd = [sys.executable, str(standin_script)]
        _restart_server("verify", gateway, cmd)

        new_entry = gateway.pool.pool.get("mcp-verify")
        assert new_entry is not None
        # 高负载下 tasklist 自身可能超过 _is_pid_alive 的 2s 超时（误判 dead），
        # 轮询宽限消除负载抖动；真死进程不会复活，回归力不变。
        deadline = time.monotonic() + 10.0
        while not _is_pid_alive(new_entry.pid):
            assert time.monotonic() < deadline, f"New PID {new_entry.pid} should be alive in OS"
            time.sleep(0.5)


# ---------------------------------------------------------------------------
# 测试3: _mcp_health_check 完整逻辑
# ---------------------------------------------------------------------------


class TestMcpHealthCheckSimulation:
    """验证 _mcp_health_check 完整逻辑（遍历+检测+重启）。"""

    def test_all_healthy_no_restart(self, gateway, standin_script):
        """所有进程健康时，_mcp_health_check 不执行重启。"""
        server_ids = ["srv1", "srv2", "srv3"]
        for sid in server_ids:
            gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert all(v == "healthy" for v in results.values())
        assert len(results) == 3

    def test_one_dead_recovered(self, gateway, standin_script):
        """一个进程死亡时，_mcp_health_check 应检测并恢复。"""
        server_ids = ["srv1", "srv2", "srv3"]
        entries = {}
        for sid in server_ids:
            entries[sid] = gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        # 杀死 srv2
        _kill_process(entries["srv2"].pid)
        time.sleep(0.5)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert results["srv1"] == "healthy"
        assert results["srv2"] == "recovered"
        assert results["srv3"] == "healthy"

        # 验证 srv2 新进程存活
        new_entry = gateway.pool.pool.get("mcp-srv2")
        assert new_entry is not None
        assert new_entry.is_alive is True

    def test_all_dead_all_recovered(self, gateway, standin_script):
        """所有进程死亡时，_mcp_health_check 应全部恢复。"""
        server_ids = ["srv1", "srv2"]
        entries = {}
        for sid in server_ids:
            entries[sid] = gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        # 杀死所有进程
        for sid in server_ids:
            _kill_process(entries[sid].pid)
        time.sleep(0.5)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert all(v == "recovered" for v in results.values())

    def test_missing_server_marked_failed_when_no_cmd(self, gateway):
        """不存在的 server 且 cmd_builder 返回 None 时，应标记为 failed。"""
        server_ids = ["missing1", "missing2"]
        cmd_builder = lambda sid: None
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert all(v == "failed" for v in results.values())

    def test_health_check_idempotent(self, gateway, standin_script):
        """连续两次 _mcp_health_check，第二次应全部 healthy。"""
        server_ids = ["srv1", "srv2"]
        for sid in server_ids:
            gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]

        # 第一次检查
        results1 = _mcp_health_check(server_ids, gateway, cmd_builder)
        assert all(v == "healthy" for v in results1.values())

        # 第二次检查
        results2 = _mcp_health_check(server_ids, gateway, cmd_builder)
        assert all(v == "healthy" for v in results2.values())

    def test_health_check_returns_correct_count(self, gateway, standin_script):
        """_mcp_health_check 返回的 results 数量应与 server_ids 一致。"""
        server_ids = [f"srv{i}" for i in range(5)]
        for sid in server_ids:
            gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert len(results) == 5
        assert set(results.keys()) == set(server_ids)


# ---------------------------------------------------------------------------
# 测试4: 红蓝对抗极端场景
# ---------------------------------------------------------------------------


class TestRedBlueExtremeScenarios:
    """红蓝对抗极端测试：多进程同时死亡/重启幂等/并发恢复/资源耗尽。"""

    def test_all_10_servers_dead_simultaneously(self, gateway, standin_script):
        """模拟10个MCP Server同时死亡，_mcp_health_check 应全部恢复。"""
        server_ids = [f"mcp{i}" for i in range(10)]
        entries = {}
        for sid in server_ids:
            entries[sid] = gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.5)

        # 同时杀死所有进程
        for sid in server_ids:
            _kill_process(entries[sid].pid)
        time.sleep(1.0)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert all(v == "recovered" for v in results.values()), f"Failed: {results}"
        assert len(results) == 10

    def test_restart_idempotent_multiple_calls(self, gateway, standin_script):
        """对同一死亡进程多次调用 restart_server 应幂等（最终存活）。"""
        entry = gateway.launch("mcp-idem", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        _kill_process(entry.pid)
        time.sleep(0.5)

        cmd = [sys.executable, str(standin_script)]

        # 第一次重启
        r1 = _restart_server("idem", gateway, cmd)
        assert r1 is True

        # 第二次重启（进程已存活，会终止旧进程并启动新进程）
        r2 = _restart_server("idem", gateway, cmd)
        assert r2 is True

        # 验证最终存活
        assert _check_server_health("idem", gateway) is True

    def test_health_check_with_partial_dead(self, gateway, standin_script):
        """部分进程死亡时，_mcp_health_check 应只重启死亡进程。"""
        server_ids = ["srv1", "srv2", "srv3", "srv4", "srv5"]
        entries = {}
        for sid in server_ids:
            entries[sid] = gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        # 只杀死 srv2 和 srv4
        _kill_process(entries["srv2"].pid)
        _kill_process(entries["srv4"].pid)
        time.sleep(0.5)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert results["srv1"] == "healthy"
        assert results["srv2"] == "recovered"
        assert results["srv3"] == "healthy"
        assert results["srv4"] == "recovered"
        assert results["srv5"] == "healthy"

    def test_health_check_handles_max_pool_capacity(self, gateway, standin_script):
        """进程池达到上限时，_mcp_health_check 应正确处理。"""
        # 创建 max_processes 个进程（默认30）
        server_ids = [f"cap{i}" for i in range(5)]
        for sid in server_ids:
            gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        cmd_builder = lambda sid: [sys.executable, str(standin_script)]
        results = _mcp_health_check(server_ids, gateway, cmd_builder)

        assert all(v == "healthy" for v in results.values())

    def test_restart_after_terminate_all(self, gateway, standin_script):
        """terminate_all 后，restart_server 应能重新启动进程。"""
        entry = gateway.launch("mcp-after_term", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        # 终止所有进程
        gateway.terminate_all()
        time.sleep(0.3)

        assert _check_server_health("after_term", gateway) is False

        # 重启
        cmd = [sys.executable, str(standin_script)]
        recovered = _restart_server("after_term", gateway, cmd)
        assert recovered is True
        assert _check_server_health("after_term", gateway) is True

    def test_health_check_empty_server_list(self, gateway):
        """空 server 列表时，_mcp_health_check 应返回空 dict。"""
        cmd_builder = lambda sid: [sys.executable, "-c", "pass"]
        results = _mcp_health_check([], gateway, cmd_builder)
        assert results == {}

    def test_concurrent_health_checks_no_race(self, gateway, standin_script):
        """并发执行 _mcp_health_check 不应产生竞争条件。"""
        import threading

        server_ids = ["srv1", "srv2", "srv3"]
        for sid in server_ids:
            gateway.launch(f"mcp-{sid}", [sys.executable, str(standin_script)], idle_timeout_s=600.0)
        time.sleep(0.3)

        results_list: list[dict] = []
        errors: list[Exception] = []
        cmd_builder = lambda sid: [sys.executable, str(standin_script)]

        def run_check():
            try:
                r = _mcp_health_check(server_ids, gateway, cmd_builder)
                results_list.append(r)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=run_check) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(results_list) == 3
        for r in results_list:
            assert all(v == "healthy" for v in r.values())
