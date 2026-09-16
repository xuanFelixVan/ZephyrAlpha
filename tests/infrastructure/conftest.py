# [A_test] module_id: MOD-INF-013_conftest | layer=test | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14（test-support conftest）
# [MODULE] tests.infrastructure.conftest
# [INVARIANTS] 逐用例teardown后pytest直系子进程回归基线; 在途异步孵化先收敛再收割; terminate→wait→kill保收; 会话收尾全量清零
# [CONSUMERS] pytest（tests/infrastructure 全目录自动生效）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 收割失败不掩盖用例结果（psutil 异常一律吞掉，进程残留由下一用例基线差分兜底）
# [TESTS] pytest tests/infrastructure/mcp -q（CHILD-LEAK 应为零）
# [TTL] task_bound

"""tests/infrastructure 子进程保收 conftest（GW9 测试基建稳定化 st-stab-20260916）。

背景（F-06 通宵班实测）：单进程全量跑 tests/infrastructure 时 pytest 子进程数
单调爬升（15% 处 children=72>50），触发 process_reaper DANGEROUS 判据
（children>50）误杀 pytest，全量无法完整跑完。

根因（psutil 逐用例归因实证）：MCP boot 族测试
（test_mcp_full_lifecycle_e2e / test_mcp_boot_hooks_integration /
 test_f3_auto_integration）经 boot_hooks.register_boot_hooks →
_start_mcp_cluster 后台 daemon 线程真实孵化 9 个 MCP server——
scripts/mcp/launcher.launch_all 按 DAG 逐层 spawn 后进入 while-running
常驻循环，进程仅 atexit 才回收。测试内 patch.object(launcher_module, ...)
拦不住：boot_hooks 内部 spec_from_file_location 加载的是全新模块实例。

治本（本文件，fixture 级 teardown 保收）：
  1) 基线快照——用例开始前记录 pytest 进程直系子进程 PID 集合；
  2) 在途孵化收敛等待——daemon 线程按层渐进 spawn（层间 sleep），
     teardown 先等子进程集合连续多轮无新增再动手；
  3) terminate→wait→kill 全量收割本用例新孵化且仍存活的直系子进程。
launcher.launch_all 的层内健康检查会在其孵化进程被收割后判定
"failed to start / died after start" 自行 abort 并 terminate_all 自清，
故集群线程收割后自灭，无跨用例累积；残留竞态窗口由下一用例基线差分
+会话收尾全量清零兜底。
不改 reaper 阈值、不改 process_reaper_keep.txt、不改 launcher/boot_hooks 本体。
"""

from __future__ import annotations

import os
import threading
import time

import pytest

try:
    import psutil
except ImportError:  # pragma: no cover — psutil 是 reaper 硬依赖，缺席即降级为 no-op
    psutil = None

# 在途孵化收敛等待上限：9 server × 4 层 DAG 渐进 spawn ≈ 10s，留余量
_SPAWN_SETTLE_DEADLINE_S = 15.0
# 连续 N 轮子进程集合无新增即判定孵化已收敛
_STABLE_ROUNDS = 3
_POLL_INTERVAL_S = 0.4
_REAP_WAIT_S = 5.0
# 收割后再复核轮数（堵"收割瞬间新孵化"竞态窗口）
_REAP_RECHECK_ROUNDS = 6
# 收割过有残留时，外层再做一轮"收敛等待+收割"（堵多集群线程错峰孵化的二阶竞态）
_OUTER_SETTLE_ROUNDS = 2


def _alive_children(proc):
    try:
        return [c for c in proc.children() if c.pid]
    except psutil.Error:
        return []


def _new_leaks(proc, baseline):
    return [c for c in _alive_children(proc) if c.pid not in baseline]


def _cluster_threads_alive():
    """是否存在存活的 MCP 集群孵化线程（boot_hooks 命名 mcp-cluster-launcher）。

    其孵化进程被收割后：若尚在启动期，launch_all 层内健康检查 abort → 线程自灭；
    若已进入 while-running 常驻循环则线程永驻（只睡眠不再孵化）。
    """
    return any(t.name == "mcp-cluster-launcher" and t.is_alive() for t in threading.enumerate())


def _wait_spawn_settle(proc, baseline):
    """等待在途异步孵化收敛：子进程集合连续多轮无新增（或归零/超时）。"""
    deadline = time.monotonic() + _SPAWN_SETTLE_DEADLINE_S
    prev = None
    stable = 0
    while time.monotonic() < deadline:
        current = {c.pid for c in _new_leaks(proc, baseline)}
        if not current:
            return
        if current == prev:
            stable += 1
            if stable >= _STABLE_ROUNDS:
                return
        else:
            stable = 0
        prev = current
        time.sleep(_POLL_INTERVAL_S)


def _wait_cluster_thread_exit(proc, baseline):
    """收割后等待孵化线程退场（≤3s）：线程死亡=abort 自灭=绝无后续孵化。

    线程仍活（已入 while-running 常驻循环）或出现新孵化时返回，由外层循环处置。
    """
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        if _new_leaks(proc, baseline):
            return
        if not _cluster_threads_alive():
            time.sleep(_POLL_INTERVAL_S)
            if not _cluster_threads_alive() and not _new_leaks(proc, baseline):
                return
        time.sleep(_POLL_INTERVAL_S)


def _reap(procs):
    """terminate → wait → kill 保收（Windows terminate=TerminateProcess 即时生效）。"""
    if not procs:
        return
    for c in procs:
        try:
            c.terminate()
        except psutil.Error:
            pass
    _, alive = psutil.wait_procs(procs, timeout=_REAP_WAIT_S)
    for c in alive:
        try:
            c.kill()
        except psutil.Error:
            pass
    try:
        psutil.wait_procs(alive, timeout=_REAP_WAIT_S)
    except psutil.Error:
        pass


@pytest.fixture(autouse=True)
def _reap_test_spawned_children():
    """逐用例子进程保收：teardown 后 pytest 直系子进程必须回归用例前基线。"""
    if psutil is None:  # pragma: no cover
        yield
        return
    proc = psutil.Process(os.getpid())
    try:
        baseline = {c.pid for c in proc.children()}
    except psutil.Error:
        baseline = set()
    yield
    try:
        for _ in range(_OUTER_SETTLE_ROUNDS):
            _wait_spawn_settle(proc, baseline)
            reaped_any = False
            # 收割 + 复核（收割瞬间新孵化的竞态窗口由复核轮兜底）
            for _ in range(_REAP_RECHECK_ROUNDS):
                leaked = _new_leaks(proc, baseline)
                if not leaked:
                    break
                _reap(leaked)
                reaped_any = True
                time.sleep(_POLL_INTERVAL_S)
            if not reaped_any:
                break
            # 收割过：等孵化线程退场（abort 自灭），若仍冒新孵化则外层再收敛一轮
            _wait_cluster_thread_exit(proc, baseline)
    except Exception:  # noqa: BLE001 — 保收失败绝不掩盖用例结果
        pass


def pytest_sessionfinish(session, exitstatus):
    """会话收尾全量清零：兜住跨用例竞态残留，保证 pytest 退出时子进程归零。"""
    if psutil is None:  # pragma: no cover
        return
    # xdist worker 场景不扫尾（worker 是主进程子进程，收割会误伤分布式调度）
    if (
        session.config.pluginmanager.hasplugin("xdist")
        and os.environ.get("PYTEST_XDIST_WORKER") is not None
    ):
        return
    try:
        proc = psutil.Process(os.getpid())
        _reap(_alive_children(proc))
    except Exception:  # noqa: BLE001
        pass
