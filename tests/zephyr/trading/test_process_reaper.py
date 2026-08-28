# [MODULE] tests.zephyr.trading.test_process_reaper
# [DOMAIN] D_INFRA_RUNTIME
# [TTL] permanent
"""process_reaper 判定矩阵单测（classify_process 纯函数，无 psutil 依赖）。

覆盖裁定矩阵全部分支（2026-08-28 裁定）：
白名单/Trae 后代永不杀、DANGEROUS 即杀、.runtime 孤儿即杀、孤儿分级、
非孤儿长命空转分级、自保。fail-safe 方向断言：边界条件一律偏向不杀。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.trading.process_reaper import (  # noqa: E402
    _GHOST_STRIKES_TO_KILL,
    _advance_ghost_state,
    _is_trae_child_cmdline,
    classify_process,
    classify_trae_process,
)

_BASE = dict(
    pid=1234,
    cmdline=r"python D:\ZephyrAlpha\some_script.py",
    age_s=100.0,
    mem_mb=100.0,
    cpu_pct=5.0,
    children=0,
    orphan=False,
    is_self_ancestor=False,
    is_trae_descendant=False,
    whitelist_hit=None,
)


def _classify(**overrides):
    kw = {**_BASE, **overrides}
    return classify_process(**kw)


class TestNeverKillGuards:
    """fail-safe 核心：三类保护命中时永不杀。"""

    def test_self_ancestor_never_killed(self):
        v = _classify(is_self_ancestor=True, mem_mb=99999.0, orphan=True, age_s=999999.0)
        assert v.action == "skip" and v.reason == "self_or_ancestor"

    def test_whitelist_never_killed(self):
        v = _classify(
            whitelist_hit="whitelist:zephyr\\.data\\.scheduler",
            cmdline=r"python -m zephyr.data.scheduler",
            age_s=999999.0,
            orphan=True,
            mem_mb=0.0,
            cpu_pct=0.0,
        )
        assert v.action == "skip" and v.reason.startswith("whitelist:")

    def test_trae_descendant_never_killed(self):
        v = _classify(is_trae_descendant=True, age_s=999999.0, cpu_pct=0.0)
        assert v.action == "skip" and v.reason == "trae_descendant"


class TestDangerous:
    def test_huge_memory_killed(self):
        v = _classify(mem_mb=11.0 * 1024, age_s=60.0)  # 即使年轻也杀
        assert v.action == "kill" and "dangerous" in v.reason

    def test_too_many_children_killed(self):
        v = _classify(children=51)
        assert v.action == "kill" and "dangerous" in v.reason

    def test_dangerous_beats_trae_protection(self):
        # Trae 后代保护优先于 DANGEROUS（IDE 子进程资源失控由 IDE 负责，fail-safe 不杀）
        v = _classify(is_trae_descendant=True, mem_mb=11.0 * 1024)
        assert v.action == "skip"


class TestRuntimeDirOrphan:
    """sweep_runner 族命中：.runtime/ 路径 + 孤儿 + 超龄 30min 才杀（2026-08-28
    reconcile_worker 误杀实证后从「立即杀」改为分级——detached 合法短任务天生孤儿且分钟级）。"""

    def test_runtime_dir_orphan_aged_killed(self):
        v = _classify(
            cmdline=r"python .runtime\test_sweep\sweep_runner.py .runtime\test_sweep\manifest.txt",
            orphan=True,
            age_s=31 * 60.0,  # 超龄 30min 杀
        )
        assert v.action == "kill" and "runtime_dir_orphan" in v.reason

    def test_runtime_dir_orphan_young_only_reported(self):
        # 未超龄不杀（report 观察）——给 detached 合法短任务留活路
        v = _classify(
            cmdline=r"python .runtime\test_sweep\sweep_runner.py .runtime\test_sweep\manifest.txt",
            orphan=True,
            age_s=60.0,
        )
        assert v.action == "report" and "runtime_dir_orphan_watch" in v.reason

    def test_runtime_dir_non_orphan_not_killed(self):
        # 父活着的 .runtime 脚本（正在执行的合法短任务）不走此条，按正常规则判
        v = _classify(cmdline=r"python .runtime\test_sweep\sweep_runner.py", orphan=False, age_s=60.0)
        assert v.action == "skip"

    def test_reconcile_worker_never_killed_young(self):
        """2026-08-28 误杀回归：git commit 后 GitCommitGateway 拉起的审计 worker
        （detached spawn 天生孤儿 + payload 在 .runtime/reconcile_reports/），
        分钟级生命周期内绝不杀（实证 age=1min 即被杀、23 具 payload 遗体）。"""
        v = _classify(
            cmdline=r'"C:\...\python.exe" -m zephyr.governance.audit.reconcile_worker --payload D:\ZephyrAlpha\.runtime\reconcile_reports\reconcile_payload_abc123.json',
            orphan=True,  # detached spawn 架构特征，非异常
            age_s=60.0,
        )
        assert v.action == "report", "reconcile_worker 运行窗口内必须只观察不杀"
        # 真卡死超龄的 worker 仍会被清（fail-safe 双向不失效）
        v2 = _classify(
            cmdline=r'"C:\...\python.exe" -m zephyr.governance.audit.reconcile_worker --payload D:\ZephyrAlpha\.runtime\reconcile_reports\reconcile_payload_abc123.json',
            orphan=True,
            age_s=45 * 60.0,
        )
        assert v2.action == "kill"


class TestOrphanGrading:
    def test_orphan_aged_killed(self):
        v = _classify(orphan=True, age_s=3 * 3600.0)
        assert v.action == "kill" and "orphan_aged" in v.reason

    def test_orphan_watch_window_reported(self):
        v = _classify(orphan=True, age_s=3600.0)  # 1h：30min~2h 观察窗
        assert v.action == "report" and "orphan_watch" in v.reason

    def test_orphan_young_skipped(self):
        v = _classify(orphan=True, age_s=600.0)  # 10min：太年轻，给创建者留窗口
        assert v.action == "skip" and "orphan_young" in v.reason

    def test_orphan_boundary_2h_killed(self):
        v = _classify(orphan=True, age_s=2 * 3600.0 + 1)
        assert v.action == "kill"


class TestIdleGrading:
    """非孤儿长命空转（zombie_scanner 阈值修正版：必须年龄+CPU 双信号交叉）。"""

    def test_idle_aged_killed(self):
        v = _classify(age_s=7 * 3600.0, cpu_pct=0.1)
        assert v.action == "kill" and "idle_aged" in v.reason

    def test_aged_but_busy_not_killed(self):
        # 超龄但在真实干活（CPU 高）——scheduler 类业务繁忙场景，fail-safe 不杀
        v = _classify(age_s=7 * 3600.0, cpu_pct=50.0)
        assert v.action == "skip"

    def test_idle_watch_reported(self):
        v = _classify(age_s=2 * 3600.0, cpu_pct=0.05)
        assert v.action == "report" and "idle_watch" in v.reason

    def test_normal_skipped(self):
        v = _classify()
        assert v.action == "skip" and v.reason == "normal"


class TestRealWorldFixtures:
    """2026-08-28 事故实录回归：确保历史肇事者必被杀、被保留者必不杀。"""

    def test_sweep_runner_killed(self):
        # 事故急性特征=循环派生 60+ 进程 7.7GB：DANGEROUS 判据即时杀（无年龄窗）
        v = _classify(
            cmdline=r'"C:\...\python.exe" .runtime\test_sweep\sweep_runner.py .runtime\test_sweep\manifest_b2_A.txt',
            orphan=True,
            age_s=18 * 60.0,  # 事故时仅 18 分钟龄
            children=51,
        )
        assert v.action == "kill" and "dangerous" in v.reason
        # 单残留超龄路径：31min 走 runtime_dir_orphan 杀
        v2 = _classify(
            cmdline=r'"C:\...\python.exe" .runtime\test_sweep\sweep_runner.py .runtime\test_sweep\manifest_b2_A.txt',
            orphan=True,
            age_s=31 * 60.0,
        )
        assert v2.action == "kill" and "runtime_dir_orphan" in v2.reason

    def test_orphan_pytest_aged_killed(self):
        v = _classify(
            cmdline=r'"C:\...\python.exe" -m pytest -n 0 -q --tb=short tests\infrastructure',
            orphan=True,
            age_s=3 * 3600.0,
        )
        assert v.action == "kill"

    def test_scheduler_whitelisted(self):
        v = _classify(
            cmdline=r'"C:\...\python.exe" -m zephyr.data.scheduler',
            whitelist_hit="whitelist:zephyr\\.data\\.scheduler",
            orphan=True,  # 事故实证：scheduler 父进程已死仍是合法服务
            age_s=8 * 3600.0,
            cpu_pct=100.0,
        )
        assert v.action == "skip"


# ============== 幽灵判据三件套（2026-08-28 终审重构）==============

_NOW = "2026-08-28 14:00:00"
_MAIN_CMD = r'"D:\AI\Trae CN\Trae CN.exe"'
_RENDERER_CMD = r'"D:\AI\Trae CN\Trae CN.exe" --type=renderer --user-data-dir="C:\...\Trae CN" --vscode-window-config=vscode:abc'
_EXTWORKER_CMD = r'"D:\AI\Trae CN\Trae CN.exe" "d:\AI\...\serverWorkerMain" --node-ipc --clientProcessId=27916'

# 典型活 IDE 拓扑：main(100) <- renderer(200)、utility(300)、ext worker(400 <- 300)
_LIVE_PROCS = {
    100: {"name": "Trae CN.exe", "ppid": 999, "create_time": 1000.0, "cmdline": _MAIN_CMD},
    200: {"name": "Trae CN.exe", "ppid": 100, "create_time": 1010.0, "cmdline": _RENDERER_CMD},
    300: {"name": "Trae CN.exe", "ppid": 100, "create_time": 1020.0, "cmdline": '"Trae CN.exe" --type=utility'},
    400: {"name": "Trae CN.exe", "ppid": 300, "create_time": 1030.0, "cmdline": _EXTWORKER_CMD},
    999: {"name": "explorer.exe", "ppid": 1, "create_time": 100.0, "cmdline": "explorer.exe"},
}


def _classify_trae(pid, procs):
    info = procs[pid]
    return classify_trae_process(
        pid=pid,
        name=info["name"],
        cmdline=info["cmdline"],
        ppid=info["ppid"],
        create_time=info["create_time"],
        procs=procs,
    )


class TestClassifyTraeProcess:
    """内核态拓扑判据：main 永不判、父活不判、父死/PID复用判嫌疑。"""

    def test_non_trae_never_suspect(self):
        assert _classify_trae(999, _LIVE_PROCS) is None

    def test_main_never_suspect_even_ppid_dangling(self):
        # main 的父 explorer 死了（ppid 悬空）也永不判——事故核心防护
        procs = {100: _LIVE_PROCS[100]}
        assert _classify_trae(100, procs) is None

    def test_child_parent_alive_not_suspect(self):
        assert _classify_trae(200, _LIVE_PROCS) is None
        assert _classify_trae(400, _LIVE_PROCS) is None

    def test_child_parent_gone_suspect(self):
        # renderer 的父 main 死了（崩溃残留）——真幽灵，必须判
        procs = {k: v for k, v in _LIVE_PROCS.items() if k != 100}
        reason = _classify_trae(200, procs)
        assert reason is not None and "gone" in reason

    def test_ext_worker_parent_gone_suspect(self):
        # extension host worker（无 --type=）父 utility 死了也判——靠 --node-ipc 标记
        procs = {k: v for k, v in _LIVE_PROCS.items() if k != 300}
        reason = _classify_trae(400, procs)
        assert reason is not None and "gone" in reason

    def test_pid_reuse_suspect(self):
        # 父 PID 被复用：复用者 create_time 必晚于子出生 -> 父实死
        procs = dict(_LIVE_PROCS)
        procs[100] = {"name": "svchost.exe", "ppid": 1, "create_time": 9999.0, "cmdline": "svchost.exe"}
        reason = _classify_trae(200, procs)
        assert reason is not None and "pid_reused" in reason


class TestTraeChildCmdline:
    def test_type_marker_is_child(self):
        assert _is_trae_child_cmdline(_RENDERER_CMD)

    def test_node_ipc_marker_is_child(self):
        assert _is_trae_child_cmdline(_EXTWORKER_CMD)

    def test_bare_main_not_child(self):
        assert not _is_trae_child_cmdline(_MAIN_CMD)


class TestGhostStateMachine:
    """3 轮确认状态机：连续在列才达斩杀线，恢复即出列，进程消失即出列。"""

    @staticmethod
    def _current(*pids):
        return {p: {"reason": "trae_orphan:ppid=100_gone", "cmdline": _RENDERER_CMD} for p in pids}

    def test_first_round_no_kill(self):
        state, kill_ready = _advance_ghost_state({"version": 1, "suspects": {}}, self._current(200), _NOW)
        assert kill_ready == []
        assert state["suspects"]["200"]["strikes"] == 1

    def test_three_consecutive_rounds_reach_kill_line(self):
        state = {"version": 1, "suspects": {}}
        for _ in range(_GHOST_STRIKES_TO_KILL - 1):
            state, kill_ready = _advance_ghost_state(state, self._current(200), _NOW)
            assert kill_ready == []
        state, kill_ready = _advance_ghost_state(state, self._current(200), _NOW)
        assert kill_ready == [200]
        assert state["suspects"]["200"]["strikes"] == _GHOST_STRIKES_TO_KILL

    def test_recovery_between_rounds_evicts(self):
        # 第 2 轮恢复（父活=不在嫌疑集）-> 出列；第 3 轮再嫌疑 -> 从 strikes=1 重新计
        state, _ = _advance_ghost_state({"version": 1, "suspects": {}}, self._current(200), _NOW)
        state, kill_ready = _advance_ghost_state(state, self._current(), _NOW)  # 恢复轮
        assert state["suspects"] == {} and kill_ready == []
        state, kill_ready = _advance_ghost_state(state, self._current(200), _NOW)
        assert state["suspects"]["200"]["strikes"] == 1 and kill_ready == []

    def test_process_exit_evicts(self):
        state, _ = _advance_ghost_state({"version": 1, "suspects": {}}, self._current(200), _NOW)
        state, kill_ready = _advance_ghost_state(state, {}, _NOW)  # 进程消失
        assert state["suspects"] == {} and kill_ready == []

    def test_independent_pids_counted_separately(self):
        state, _ = _advance_ghost_state({"version": 1, "suspects": {}}, self._current(200, 300), _NOW)
        state, kill_ready = _advance_ghost_state(state, self._current(300), _NOW)  # 200 恢复出列
        assert "200" not in state["suspects"]
        assert state["suspects"]["300"]["strikes"] == 2 and kill_ready == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
