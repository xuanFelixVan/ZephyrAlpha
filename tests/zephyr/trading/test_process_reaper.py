# [MODULE] tests.zephyr.trading.test_process_reaper
# [DOMAIN] D_INFRA_RUNTIME
# [TTL] permanent
"""process_reaper 判定矩阵单测（classify_process 纯函数，无 psutil 依赖）。

覆盖裁定矩阵全部分支（2026-08-28 裁定）：
白名单/Trae 后代永不杀、DANGEROUS 即杀、.runtime 孤儿即杀、孤儿分级、
非孤儿长命空转分级、自保。fail-safe 方向断言：边界条件一律偏向不杀。

另覆盖 kill 日志可归因字段（处方 P-12，2026-09-26）：
旧渲染只落 PID+reason→ 同 reason 的两个不同进程在日志里无法区分（红证），
新渲染行尾追加 name+cmd 片段→ 可区分；并钉住行格式向后兼容
（`KILLED PID=` / `reason=` 既有读法）、cmdline 硬截断、缺失字段不抛、
疑似密钥实参脱敏、控制字符不拆行。
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import zephyr.trading.process_reaper as pr  # noqa: E402
from zephyr.trading.process_reaper import (  # noqa: E402
    _CMD_SNIPPET_MAX,
    _DERIVED_ORPHAN_MARKERS,
    _GHOST_STRIKES_TO_KILL,
    _advance_ghost_state,
    _is_trae_child_cmdline,
    _log_kill,
    _reap_derived_orphans,
    classify_process,
    classify_trae_process,
)


@pytest.fixture(autouse=True)
def _isolate_kill_log(monkeypatch, tmp_path):
    """测试隔离铁律（宪法 §9.6）：kill 日志一律落 tmp_path，禁写生产 data/runtime/。

    本文件既有的 _reap_derived_orphans / _reap_incubated_expired 用例原先会经
    _log_kill 写生产 data/runtime/reaper_kill.log（P-12 施工时发现的既有泄漏），
    此处整册重定向，不改任何判定语义。
    """
    monkeypatch.setattr(pr, "_KILL_LOG", tmp_path / "reaper_kill.log")


def _read_kill_lines():
    p = pr._KILL_LOG
    if not p.exists():
        return []
    return [l for l in p.read_text(encoding="utf-8").splitlines() if l]


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
_RENDERER_CMD = (
    r'"D:\AI\Trae CN\Trae CN.exe" --type=renderer --user-data-dir="C:\...\Trae CN" --vscode-window-config=vscode:abc'
)
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


class TestDerivedOrphans:
    """判定矩阵第 10 条：项目衍生孤儿（ollama/llama-server 族，2026-09-15 事故补丁）。"""

    @staticmethod
    def _proc(ppid, age_h, cmd, name=""):
        return {
            "name": name,
            "ppid": ppid,
            "cmdline": cmd,
            "create_time": time.time() - age_h * 3600,
        }

    def _run(self, procs, monkeypatch, dry_run=False):
        import zephyr.trading.process_reaper as m

        monkeypatch.setattr(m, "_collect_metrics", lambda d: None)
        killed: list[int] = []
        monkeypatch.setattr(m, "_kill_pid_tree", lambda pid: killed.append(pid) or True)
        report = m.ReapReport()
        m._reap_derived_orphans(procs, dry_run, report)
        return report, killed

    def test_aged_serve_orphan_killed(self, monkeypatch):
        # serve 父进程(PPID=1)已死且超龄 -> 收割
        procs = {10: self._proc(1, 3.0, r"C:\Programs\Ollama\ollama.exe serve")}
        report, killed = self._run(procs, monkeypatch)
        assert killed == [10]
        assert report.killed[0]["reason"].startswith("derived_orphan_aged")

    def test_aged_llama_server_orphan_killed(self, monkeypatch):
        # llama-server 的父(10)已死=不在进程表内 -> 收割
        procs = {11: self._proc(10, 3.0, r"C:\Programs\Ollama\llama-server.exe --model x", name="llama-server.exe")}
        report, killed = self._run(procs, monkeypatch)
        assert killed == [11]
        assert report.killed[0]["reason"].startswith("derived_orphan_aged")

    def test_parent_alive_never_judged(self, monkeypatch):
        procs = {
            9: self._proc(1, 3.0, r"bash.exe"),
            10: self._proc(9, 3.0, r"C:\Programs\Ollama\ollama.exe serve"),
            11: self._proc(10, 3.0, r"C:\Programs\Ollama\llama-server.exe --model x", name="llama-server.exe"),
        }
        report, killed = self._run(procs, monkeypatch)
        assert killed == [] and report.reported == []

    def test_young_derived_orphan_skipped(self, monkeypatch):
        procs = {11: self._proc(10, 0.1, r"C:\Programs\Ollama\llama-server.exe --model x", name="llama-server.exe")}
        report, killed = self._run(procs, monkeypatch)
        assert killed == [] and report.reported == []

    def test_watch_window_reported_not_killed(self, monkeypatch):
        procs = {11: self._proc(10, 1.0, r"C:\Programs\Ollama\llama-server.exe --model x", name="llama-server.exe")}
        report, killed = self._run(procs, monkeypatch)
        assert killed == []
        assert len(report.reported) == 1 and report.reported[0]["reason"] == "derived_orphan_watch"

    def test_huge_memory_killed_regardless_of_age(self, monkeypatch):
        import zephyr.trading.process_reaper as m

        procs = {11: self._proc(10, 0.1, r"C:\Programs\Ollama\llama-server.exe --model x", name="llama-server.exe")}
        monkeypatch.setattr(m, "_collect_metrics", lambda d: d.update({11: {**d[11], "mem_mb": 11.0 * 1024}}))
        monkeypatch.setattr(m, "_kill_pid_tree", lambda pid: True)
        report = m.ReapReport()
        m._reap_derived_orphans(procs, False, report)
        assert len(report.killed) == 1 and "derived_orphan_dangerous" in report.killed[0]["reason"]

    def test_dry_run_no_kill(self, monkeypatch):
        procs = {11: self._proc(10, 3.0, r"C:\Programs\Ollama\llama-server.exe --model x", name="llama-server.exe")}
        report, killed = self._run(procs, monkeypatch, dry_run=True)
        assert killed == [] and len(report.killed) == 1 and report.killed[0]["killed"] is False

    def test_non_ollama_orphan_not_judged(self, monkeypatch):
        procs = {11: self._proc(10, 3.0, r"msedge.exe --type=renderer")}
        report, killed = self._run(procs, monkeypatch)
        assert killed == [] and report.reported == []

    def test_markers_cover_llama_server_and_ollama_serve(self):
        joined = [rx.pattern for rx in _DERIVED_ORPHAN_MARKERS]
        assert any("llama-server" in p for p in joined)
        assert any("serve" in p for p in joined)


# ============== kill 日志可归因字段（处方 P-12，2026-09-26 观测面修复）==============
# 事故背景：09-25 10:37:34 那一刀（PID=18208, reason=runtime_dir_orphan:age=36min）
# 在旧行格式下只能靠 .runtime/process_incubator/ledger.jsonl 反查 PID 才认出
# owner=reconcile_runner（它正托管一轮备份，被 _KILL_CHILD_RECURSIVE 级联带走）。
# 本组用例只钉观测字段，不触碰任何判定阈值/判据语义。


# 修复前行格式的机械复刻：签名兼容（吸收新 kwargs）但**丢弃** name/cmdline——
# 这正是"旧实现风格"，用于红证。
def _install_legacy_renderer(monkeypatch) -> None:
    def _legacy(pid, reason, dry_run, name="", cmdline=""):  # noqa: ANN001
        path = pr._KILL_LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        tag = "DRY-RUN" if dry_run else "KILLED"
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {tag} PID={pid} reason={reason}\n")

    monkeypatch.setattr(pr, "_log_kill", _legacy)


# 行格式向后兼容契约：既有 grep 口径（'KILLED PID=' / 'reason='）必须继续命中
_LEGACY_LINE_RE = re.compile(r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] (KILLED|DRY-RUN) PID=\d+ reason=\S+")


def _derived_orphan_pair():
    """两个同 reason（derived_orphan_aged:age=3.0h）但身份不同的孤儿——P-12 悬案原型。"""
    aged = time.time() - 3 * 3600.0
    return {
        201: {
            "name": "llama-server.exe",
            "ppid": 1,
            "cmdline": r"C:\Programs\Ollama\llama-server.exe --model qwen2.5 --host 0.0.0.0",
            "create_time": aged,
        },
        202: {
            "name": "ollama.exe",
            "ppid": 1,
            "cmdline": r"C:\Programs\Ollama\ollama.exe serve",
            "create_time": aged,
        },
    }


def _strip_pid(line: str) -> str:
    return re.sub(r"PID=\d+", "PID=<n>", line)


class TestKillLogAttribution:
    """红证 + 新行为：kill 行必须能回答"杀的是谁"，同时不破既有行格式。"""

    def test_red_proof_legacy_renderer_cannot_attribute(self, monkeypatch):
        """红证：把渲染换回修复前实现，跑同一条窄路径（_reap_derived_orphans）——
        两次收割的日志行去掉 PID 后逐字符相同，日志里没有任何身份字段。"""
        import zephyr.trading.process_reaper as m

        _install_legacy_renderer(monkeypatch)
        monkeypatch.setattr(m, "_collect_metrics", lambda d: None)
        monkeypatch.setattr(m, "_kill_pid_tree", lambda pid: True)
        report = m.ReapReport()
        m._reap_derived_orphans(_derived_orphan_pair(), False, report)
        lines = _read_kill_lines()
        assert len(lines) == 2, f"窄路径应落 2 行，实得 {lines}"
        # 旧格式：无身份字段可读
        assert all(" name=" not in l and " cmd=" not in l for l in lines), lines
        # 旧格式：两条不同进程的收割在"身份"维度完全不可区分（除 PID 外逐字符同）
        assert _strip_pid(lines[0]) == _strip_pid(lines[1]), lines

    def test_new_renderer_distinguishes_same_reason_two_processes(self, monkeypatch):
        import zephyr.trading.process_reaper as m

        monkeypatch.setattr(m, "_collect_metrics", lambda d: None)
        monkeypatch.setattr(m, "_kill_pid_tree", lambda pid: True)
        report = m.ReapReport()
        m._reap_derived_orphans(_derived_orphan_pair(), False, report)
        lines = _read_kill_lines()
        assert len(lines) == 2, lines
        assert _strip_pid(lines[0]) != _strip_pid(lines[1]), lines
        assert "name=llama-server.exe" in lines[0] and "llama-server.exe --model qwen2.5" in lines[0], lines[0]
        assert "name=ollama.exe" in lines[1] and "ollama.exe serve" in lines[1], lines[1]
        # 既有 grep 口径未破
        assert all(_LEGACY_LINE_RE.match(l) for l in lines), lines

    def test_dry_run_tag_and_reason_field_unchanged(self, monkeypatch):
        import zephyr.trading.process_reaper as m

        monkeypatch.setattr(m, "_collect_metrics", lambda d: None)
        m._reap_derived_orphans(_derived_orphan_pair(), True, m.ReapReport())
        line = _read_kill_lines()[0]
        assert "] DRY-RUN PID=201 reason=derived_orphan_aged:age=3.0h " in line, line
        assert " cmd=" in line and " name=llama-server.exe" in line, line

    def test_failed_kill_marker_stays_in_reason_field(self, monkeypatch):
        import zephyr.trading.process_reaper as m

        monkeypatch.setattr(m, "_collect_metrics", lambda d: None)
        monkeypatch.setattr(m, "_kill_pid_tree", lambda pid: False)
        m._reap_derived_orphans(_derived_orphan_pair(), False, m.ReapReport())
        line = _read_kill_lines()[0]
        assert "[FAILED]" in line.split(" name=")[0], line  # [FAILED] 仍属 reason 段，不跑到行尾
        assert line.count(" name=") == 1 and line.count(" cmd=") == 1, line

    def test_cmdline_hard_truncated(self):
        long_cmd = r"python D:\ZephyrAlpha\scripts\long_run.py --tag " + "A" * 500
        _log_kill(7001, "orphan_aged:age=3.0h", dry_run=False, name="python.exe", cmdline=long_cmd)
        line = _read_kill_lines()[-1]
        cmd = line.split(" cmd=", 1)[1]
        assert cmd.endswith("...") and len(cmd) <= _CMD_SNIPPET_MAX + 3, f"截断失效 len={len(cmd)}"
        assert cmd[:_CMD_SNIPPET_MAX] == long_cmd[:_CMD_SNIPPET_MAX], cmd

    def test_name_and_cmdline_missing_render_dash_and_never_raise(self):
        # 老调用形状（三参数）继续可用，缺字段渲染为 '-'，不抛
        _log_kill(7002, "ghost_only", dry_run=False)
        # 显式空串 / None / 非字符串 / __str__ 抛异常的怪对象：一律不得反噬收割动作
        _log_kill(7003, "ghost_only", dry_run=False, name="", cmdline="")
        _log_kill(7004, "ghost_only", dry_run=True, name=None, cmdline=None)

        class _Boom:
            def __str__(self):
                raise RuntimeError("畸形 name 对象")

        _log_kill(7005, "ghost_only", dry_run=False, name=_Boom(), cmdline=12345)
        lines = _read_kill_lines()
        assert lines[0].endswith(" name=- cmd=-"), lines[0]
        assert lines[1].endswith(" name=- cmd=-"), lines[1]
        assert lines[2].endswith(" name=- cmd=-"), lines[2]
        assert " name=- cmd=12345" in lines[3], lines[3]

    def test_secret_args_redacted(self):
        _log_kill(
            7006,
            "orphan_aged:age=2.1h",
            dry_run=False,
            name="python.exe",
            cmdline=r"python job.py --password=Sup3rS3cret --token: abc.def.ghi",
        )
        line = _read_kill_lines()[-1]
        assert "Sup3rS3cret" not in line and "abc.def.ghi" not in line, line
        assert "password=***" in line and "token: ***" in line, line

    def test_control_chars_cannot_split_log_line(self):
        evil = "python ok.py\n[2026-09-26 00:00:00] KILLED PID=99999 reason=forged"
        _log_kill(7007, "orphan_aged:age=2.0h", dry_run=False, name="python.exe", cmdline=evil)
        lines = _read_kill_lines()
        assert len(lines) == 1, f"一行一条目不变量被破坏: {lines}"
        # 伪造串被压平进 cmd 字段内：行首仍是唯一合法条目，PID/reason/name 段不可被污染
        assert re.match(_LEGACY_LINE_RE, lines[0]), lines[0]
        head = lines[0].split(" cmd=", 1)[0]
        assert "forged" not in head and "99999" not in head, head
        assert lines[0].count("[2026-09-26 00:00:00]") == 1 or "00:00:00]" in lines[0].split(" cmd=", 1)[1]

    def test_ghost_state_machine_carries_name(self):
        """幽灵族窄路径的归因字段来源：状态机条目须带 name（旧状态文件缺键也不崩）。"""
        current = {200: {"reason": "trae_orphan:ppid=100_gone", "cmdline": _RENDERER_CMD, "name": "Trae CN.exe"}}
        state, _ = _advance_ghost_state({"version": 1, "suspects": {}}, current, _NOW)
        assert state["suspects"]["200"]["name"] == "Trae CN.exe"
        legacy_state = {
            "version": 1,
            "suspects": {"200": {"strikes": 1, "first_seen": _NOW, "reason": "r", "cmdline": "c"}},
        }
        state2, kill_ready = _advance_ghost_state(legacy_state, current, _NOW)
        assert state2["suspects"]["200"]["name"] == "Trae CN.exe"
        assert kill_ready == []
        # 嫌疑集本身缺 name（历史/异常路径）→ 空串，kill 日志渲染 '-'
        state3, _ = _advance_ghost_state({"version": 1, "suspects": {}}, {200: {"reason": "r", "cmdline": "c"}}, _NOW)
        assert state3["suspects"]["200"]["name"] == ""


class TestKillLogAttributionOtherLanes:
    """其余 _log_kill 调用点（孵化收割 / 孤儿主循环）同批补齐。"""

    def test_incubation_kill_log_carries_live_and_registered_name(self, monkeypatch, tmp_path):
        ledger = tmp_path / "led" / "ledger.jsonl"
        monkeypatch.setattr(pr, "_INCUBATOR_LEDGER_REL", ledger)  # 绝对路径：pathlib 取绝对侧
        monkeypatch.setattr(pr, "_kill_pid_tree", lambda pid: True)
        ledger.parent.mkdir(parents=True, exist_ok=True)
        rec = {
            "record_id": "r1",
            "child_pid": 18208,
            "name": "powershell.exe",
            "cmd": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -File scripts\backup\backup.ps1",
            "spawned_at": time.time() - 3600,
            "expected_lifetime_s": 60.0,
            "owner": "reconcile_runner",
        }
        ledger.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired({18208: {"name": "powershell.exe", "cmdline": rec["cmd"]}}, False, report)
        line = _read_kill_lines()[-1]
        assert _LEGACY_LINE_RE.match(line), line
        assert "name=powershell.exe" in line and "backup.ps1" in line, line
        assert "owner=reconcile_runner" in line, line  # reason 段格式未动

    def test_incubation_kill_log_survives_nameless_records(self, monkeypatch, tmp_path):
        """登记里没 name、进程表条目也没 name（孤儿矩阵外部输入）→ 渲染 '-' 不抛。"""
        ledger = tmp_path / "led" / "ledger.jsonl"
        monkeypatch.setattr(pr, "_INCUBATOR_LEDGER_REL", ledger)
        monkeypatch.setattr(pr, "_kill_pid_tree", lambda pid: True)
        ledger.parent.mkdir(parents=True, exist_ok=True)
        rec = {
            "record_id": "r2",
            "child_pid": 18209,
            "cmd": "",
            "spawned_at": time.time() - 3600,
            "expected_lifetime_s": 60.0,
            "owner": "x",
        }
        ledger.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        pr._reap_incubated_expired({18209: {}}, False, pr.ReapReport(dry_run=False))
        line = _read_kill_lines()[-1]
        assert line.endswith(" name=- cmd=-"), line


class TestReapCycleNeverBlindsStatus:
    """reap() 必须保证：无论本轮死在哪一步，状态快照都落盘，且失能可归因。

    病根实证（2026-09-26 本班会）：计划任务真跑分支自 09-25 01:49 起每次都在 kill 之后
    爆炸——`tmp/process_reaper.log` 里 01:14:31 有真杀、01:33:53/01:40:22 有本轮 watch 行，
    但 `.runtime/process_reaper/last_run.json` 连续 23.5h 停更且 LastTaskResult=1，
    于是 RULE-GUARDIAN 与 SOP §一.2 唯一的健康凭据变成陈旧读数（冷启动被它误导过一次）。
    """

    def test_ghost_stage_failure_isolated_and_status_written(self, monkeypatch, tmp_path: Path) -> None:
        monkeypatch.setattr(pr, "_STATUS_DIR", tmp_path)
        monkeypatch.setattr(pr, "_STATUS_FILE", tmp_path / "last_run.json")

        def boom(_dry_run: bool) -> dict[str, int]:
            raise RuntimeError("ghost stage exploded")

        monkeypatch.setattr(pr, "_reap_ghost_windows", boom)
        drift_seen: list[bool] = []

        def fake_drift(_dry_run: bool) -> dict[str, object]:
            drift_seen.append(True)
            return {"stash_count": 0, "worktree_changes": 0}

        monkeypatch.setattr(pr, "_collect_drift_metrics", fake_drift)
        report = pr.reap(dry_run=True)  # 不外抛：尾段一步失能不连坐其余两步

        assert any("ghost_stage_failed" in e for e in report.errors), report.errors
        assert "ghost stage exploded" in report.errors[0]
        assert drift_seen, "幽灵步爆炸后 drift 步被一起跳过（三步未隔离）"
        assert pr._STATUS_FILE.exists()
        data = json.loads(pr._STATUS_FILE.read_text(encoding="utf-8"))
        assert any("ghost_stage_failed" in e for e in data["errors"])

    def test_mid_cycle_crash_still_writes_status_then_reraises(self, monkeypatch, tmp_path: Path) -> None:
        """主循环中段爆炸（09-25 起的实际形态）：快照照落、异常照抛＝保留非零退出信号。"""
        monkeypatch.setattr(pr, "_STATUS_DIR", tmp_path)
        monkeypatch.setattr(pr, "_STATUS_FILE", tmp_path / "last_run.json")

        def boom(*_a: object, **_k: object) -> None:
            raise RuntimeError("incubation ledger writeback exploded")

        monkeypatch.setattr(pr, "_reap_incubated_expired", boom)
        with pytest.raises(RuntimeError, match="incubation ledger writeback exploded"):
            pr.reap(dry_run=True)

        assert pr._STATUS_FILE.exists(), "中段爆炸把健康快照一起吃掉＝23.5h 瞎火原形态复现"
        data = json.loads(pr._STATUS_FILE.read_text(encoding="utf-8"))
        assert any("reap_aborted" in e for e in data["errors"]), data["errors"]
        assert "incubation ledger writeback exploded" in data["errors"][0]

    def test_hardening_structure_is_present(self) -> None:
        """治本结构守卫：主体不得再自行落盘，快照只由 reap 外层 finally 负责。"""
        src = (pr.REPO_ROOT / "src" / "zephyr" / "trading" / "process_reaper.py").read_text(encoding="utf-8")
        head = src[src.index("def reap(") : src.index("def _reap_cycle(")]
        body = src[src.index("def _reap_cycle(") :]
        assert "finally:" in head and "_write_status(report)" in head, "reap() 外层 finally 兜底丢失"
        assert "raise" in head, "外层不再上抛＝计划任务退出码被吞（假绿）"
        assert "_write_status(report)" not in body, "落盘点又漏回主体＝中段爆炸仍会瞎"


import psutil as _psutil  # noqa: E402 — 下方 _kill_pid_tree 容错用例需真异常类


class TestKillPidTreeNeverRaises:
    """_kill_pid_tree 遇 AccessDenied 必须"记失败并继续"，绝不能把整轮收割带走。

    事故实形（2026-09-26 本班会，快照自证）：`reap_aborted: psutil.AccessDenied(pid=4908)`
    ——计划任务连续 23.5h 每次真跑都死在这里，连带后面的幽灵扫描/drift 指标/挂在同一
    脉冲上的保命链（应急保命轨 + 内存水位闸）一起停摆；dry-run 不走本函数，手工复现不出来。
    """

    class _FakeProc:
        pid = 4908

        def children(self, recursive: bool = False) -> list:  # noqa: ARG002, FBT001, FBT002
            return []

        def terminate(self) -> None:
            pass

        def kill(self) -> None:
            pass

        def wait(self, timeout: float | None = None) -> int:  # noqa: ARG002
            raise _psutil.AccessDenied(pid=4908)

    @staticmethod
    def _fakes(monkeypatch: pytest.MonkeyPatch, wait_raises: bool = False) -> None:
        monkeypatch.setattr(_psutil, "Process", lambda pid: TestKillPidTreeNeverRaises._FakeProc())
        if wait_raises:

            def boom(targets, timeout=3):  # noqa: ANN001, ARG001
                raise _psutil.AccessDenied(pid=4908)

            monkeypatch.setattr(_psutil, "wait_procs", boom)
        else:
            monkeypatch.setattr(_psutil, "wait_procs", lambda targets, timeout=3: ([], list(targets)))

    def test_proc_wait_denied_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._fakes(monkeypatch)
        assert pr._kill_pid_tree(4908) is False, "读不到退出态却上抛＝整轮连坐的原始形态"

    def test_wait_procs_denied_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._fakes(monkeypatch, wait_raises=True)
        assert pr._kill_pid_tree(4908) is False

    def test_process_open_denied_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def boom(pid: int):  # noqa: ANN001, ARG001
            raise _psutil.AccessDenied(pid=4908)

        monkeypatch.setattr(_psutil, "Process", boom)
        assert pr._kill_pid_tree(4908) is False

    def test_legacy_unguarded_shape_raises_on_same_input(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """红证：同样的输入喂给"修复前无兜底"的调用序列，异常必然冲出（证明尺有牙）。"""
        self._fakes(monkeypatch)
        proc = _psutil.Process(4908)
        _psutil.wait_procs([proc], timeout=3)
        with pytest.raises(_psutil.AccessDenied):
            proc.wait(timeout=2)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
