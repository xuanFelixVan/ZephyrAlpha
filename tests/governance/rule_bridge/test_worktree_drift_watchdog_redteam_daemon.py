# [MODULE] tests.governance.rule_bridge.test_worktree_drift_watchdog_redteam_daemon
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
# [TTL] permanent
"""红队测试（R6）：worktree_drift_watchdog daemon 生命周期——僵尸 PID / 锁竞争攻击。

被测面：ensure_daemon / run_daemon / _acquire_single_instance_lock / _pid_path
（#ARCH-308 工作区孤儿 WIP 治本三件套的 daemon 生命周期）。

攻击场景：
  R6.1  PID 文件残留但进程死      → 期望：检出死亡并重生新 daemon
  R6.1b PID 文件损坏（非数字/空） → 期望：按死亡处理并重生（ValueError 容忍）
  R6.2  PID 被其他存活进程复用    → 期望：幂等返回不重复 spawn（红队另报 PID 复用静默盲区）
  R6.3  双实例同时启动            → 期望：msvcrt 字节锁仅一个赢家，输家 run_daemon 即退
  R6.3b 双线程同时 ensure_daemon  → 实证 ensure 级无互斥（双 spawn），由 daemon 锁兜底
  R6.4  锁文件残留但无人持锁      → 期望：可获得（字节锁非存在性锁）
  R6.5  spawn 成功但进程立即崩溃  → 期望：本次返回 True，下次 ensure 检出死亡重 spawn
  R6.6  锁字节偏移漂移（红队发现）→ CONFIRMED VULN：带外向锁文件偏移≥1 追加字节后，
        第二实例锁到不同字节 → 互斥破裂双持锁（xfail-strict 留证，修复后 XPASS 报警）

注意：ensure_daemon 有 PYTEST_CURRENT_TEST 早退闸（B1/R1 防测试泄漏真实 daemon），
本套红队测试经 no_pytest_guard fixture 显式绕过该闸，全部 spawn 走 mock 不落真实进程。
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import types
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog as wd
import zephyr.shared.infra.process_pool as pp

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="msvcrt 字节锁为 Windows 专用（被测模块同款前提）")

_DEAD_PID = 999999  # 功能性死亡 PID（测试中 is_pid_alive 走 mock，不依赖真实 OS 状态）
_FAKE_DAEMON_PID = 888888  # R6.5：spawn 成功但立即崩溃的假 daemon PID


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """临时 git 仓库（与既有蓝队测试同构：init + 一个 tracked 提交）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "dev")
    _git(
        repo,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "-c",
        "core.autocrlf=false",
        "commit",
        "--allow-empty",
        "-q",
        "-m",
        "init",
    )
    (repo / "hot.txt").write_text("v1\n", encoding="utf-8")
    _git(repo, "add", "hot.txt")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.autocrlf=false", "commit", "-q", "-m", "add hot")
    return repo


def _disarm_pytest_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    """绕过 ensure_daemon 的 pytest 早退闸（红队显式攻击 daemon 生命周期本体）。

    必须在测试函数体内调用：pytest 于 call 阶段开始时才设置 PYTEST_CURRENT_TEST
    （setup 阶段的 fixture 操作会被覆盖），空串经 os.environ.get 判 falsy 即放行。
    """
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "")


def _state_dir(repo: Path) -> Path:
    return repo / ".runtime" / "drift_watchdog"


def _pid_file(repo: Path) -> Path:
    return _state_dir(repo) / "watchdog.pid"


def _lock_file(repo: Path) -> Path:
    return _state_dir(repo) / "watchdog.lock"


def _lifecycle_records(repo: Path) -> list[dict]:
    import json

    p = _state_dir(repo) / "watchdog.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


class _SpawnRecorder:
    """spawn_python_hidden mock：记录调用，返回带 pid 的假进程句柄。"""

    def __init__(self, first_pid: int = _FAKE_DAEMON_PID) -> None:
        self.calls: list[list[str]] = []
        self._next_pid = first_pid

    def __call__(self, cmd, **kwargs):  # noqa: ANN001, ANN002, ANN202
        self.calls.append(list(cmd))
        pid = self._next_pid
        self._next_pid += 1
        return types.SimpleNamespace(pid=pid)


# ── R6.1：PID 文件残留但进程死 ────────────────────────────────────────────────


def test_r61_stale_pid_file_respawns_daemon(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R6.1：watchdog.pid 指向死进程 → ensure_daemon 检出死亡并 spawn 新 daemon。

    防御层：ensure_daemon 的 is_pid_alive 存活双检（先于任何 TTL/信任）。
    """
    _disarm_pytest_guard(monkeypatch)
    _state_dir(git_repo).mkdir(parents=True)
    _pid_file(git_repo).write_text(str(_DEAD_PID), encoding="utf-8")

    monkeypatch.setattr(pp, "is_pid_alive", lambda pid: False)  # 一切 PID 已死
    rec = _SpawnRecorder()
    monkeypatch.setattr(pp, "spawn_python_hidden", rec)

    ok = wd.ensure_daemon(git_repo)
    assert ok is True
    assert len(rec.calls) == 1, f"死 PID 残留必须触发重生: {rec.calls}"
    # PID 文件被更新为新 daemon 的 PID（僵尸 PID 被覆盖）
    assert _pid_file(git_repo).read_text(encoding="utf-8").strip() == str(_FAKE_DAEMON_PID)
    # 生命周期审计留痕
    spawned = [r for r in _lifecycle_records(git_repo) if r.get("status") == "spawned"]
    assert len(spawned) == 1 and spawned[0]["pid"] == _FAKE_DAEMON_PID


@pytest.mark.parametrize("garbage", ["not-a-pid", "", "  \n", "12.5", "0x10"])
def test_r61b_corrupt_pid_file_respawns_daemon(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch, garbage: str
) -> None:
    """R6.1b：PID 文件内容损坏（非整数/空/浮点/十六进制）→ 按死亡处理重生，不抛异常。"""
    _disarm_pytest_guard(monkeypatch)
    _state_dir(git_repo).mkdir(parents=True)
    _pid_file(git_repo).write_text(garbage, encoding="utf-8")

    alive_calls: list[int] = []
    monkeypatch.setattr(pp, "is_pid_alive", lambda pid: alive_calls.append(pid) or False)
    rec = _SpawnRecorder()
    monkeypatch.setattr(pp, "spawn_python_hidden", rec)

    ok = wd.ensure_daemon(git_repo)  # int() ValueError 必须被容忍
    assert ok is True
    assert len(rec.calls) == 1, f"损坏 PID 文件必须重生 daemon（garbage={garbage!r}）"


# ── R6.2：PID 被其他存活进程复用 ─────────────────────────────────────────────


def test_r62_pid_reuse_by_live_process_suppresses_spawn(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R6.2：watchdog.pid 被复用为当前 pytest 进程 PID（存活但非 daemon）。

    期望行为（幂等语义）：is_pid_alive 命中 → 直接返回 True，不重复 spawn。
    红队标注（FINDING R6.2）：ensure_daemon 只验"活着"不验"是谁"——PID 被 OS 回收
    复用后，ensure 永远幂等返回而真实 daemon 并不存在 → 静默监视盲区（fail-silent）。
    本测试锁定当前行为；修复方向见报告（PID+启动时间/命令行指纹双检）。
    """
    _disarm_pytest_guard(monkeypatch)
    _state_dir(git_repo).mkdir(parents=True)
    _pid_file(git_repo).write_text(str(os.getpid()), encoding="utf-8")

    # 不 mock is_pid_alive——真实探测：当前进程必存活
    rec = _SpawnRecorder()
    monkeypatch.setattr(pp, "spawn_python_hidden", rec)

    ok = wd.ensure_daemon(git_repo)
    assert ok is True
    assert len(rec.calls) == 0, "存活 PID 必须幂等返回不重复 spawn"
    # PID 文件原样保留（未被覆写）
    assert _pid_file(git_repo).read_text(encoding="utf-8").strip() == str(os.getpid())
    # 无 spawned 生命周期记录（未误报重生）
    assert not [r for r in _lifecycle_records(git_repo) if r.get("status") == "spawned"]


# ── R6.3：双实例同时启动（锁竞争）─────────────────────────────────────────────


def test_r63_concurrent_lock_acquisition_single_winner(git_repo: Path) -> None:
    """R6.3：8 线程同刻抢 _acquire_single_instance_lock → 恰好 1 个赢家。

    防御层：msvcrt LK_NBLCK 字节锁（跨句柄互斥，同进程多线程亦互斥——
    Windows LockFile 语义实证）。无双 daemon 并发的根保证。
    """
    n_threads = 8
    barrier = threading.Barrier(n_threads)
    results: list = []
    errors: list = []

    def worker() -> None:
        try:
            barrier.wait(timeout=10)
            results.append(wd._acquire_single_instance_lock(git_repo))
        except Exception as e:  # noqa: BLE001 — 记录线程内异常供主线程断言
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert not errors, f"锁竞争线程异常: {errors}"
    assert len(results) == n_threads
    winners = [fh for fh in results if fh is not None]
    losers = [fh for fh in results if fh is None]
    assert len(winners) == 1, f"字节锁必须恰好 1 个赢家（实际 {len(winners)}）→ 双 daemon 风险！"
    assert len(losers) == n_threads - 1
    winners[0].close()


def test_r63_run_daemon_second_instance_exits_immediately(git_repo: Path) -> None:
    """R6.3 补：持锁状态下第二个 run_daemon → 立即 return 0（skipped），不进主循环。

    #99 单实例闸：Task Scheduler RestartOnFailure 连环拉起的第二实例零堆积。
    """
    fh = wd._acquire_single_instance_lock(git_repo)
    assert fh is not None
    try:
        rc = wd.run_daemon(git_repo)  # 锁已被持有 → 必须立即返回，绝不进 while True
        assert rc == 0
    finally:
        fh.close()
    skipped = [r for r in _lifecycle_records(git_repo) if r.get("status") == "skipped"]
    assert len(skipped) == 1, f"第二实例必须留 skipped 审计: {_lifecycle_records(git_repo)}"
    assert "single-instance" in skipped[0].get("reason", "")


def test_r63b_concurrent_ensure_daemon_double_spawn_race(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R6.3b 实证：ensure_daemon 自身无 spawn 级互斥——双线程同时 ensure 会双 spawn。

    竞态窗口：读 PID 文件（不存在）→ spawn → 写 PID 文件，全程无锁。barrier 强制
    两线程都通过 PID 检查后同刻进入 spawn → 确定性双 spawn。

    纵深防御：双 spawn 不等于双 daemon 驻留——输家在 run_daemon 的 msvcrt 字节锁
    即退（test_r63_run_daemon_second_instance_exits_immediately 覆盖），PID 文件
    即使被输家覆写，下次 ensure 检出死 PID 也会自愈。本测试锁定当前竞态存在性，
    供 ensure 级加锁修复后回归翻转。
    """
    _disarm_pytest_guard(monkeypatch)
    monkeypatch.setattr(pp, "is_pid_alive", lambda pid: False)
    barrier = threading.Barrier(2)
    rec = _SpawnRecorder(first_pid=900001)

    def fake_spawn(cmd, **kwargs):  # noqa: ANN001, ANN002, ANN202
        out = rec(cmd, **kwargs)
        try:
            barrier.wait(timeout=10)  # 双线程都在 spawn 内会师 = 都通过了 PID 检查
        except threading.BrokenBarrierError:
            pass  # 若未来 ensure 加锁，单线程到此不炸，由调用数断言区分
        return out

    monkeypatch.setattr(pp, "spawn_python_hidden", fake_spawn)

    results: list = []
    errors: list = []

    def worker() -> None:
        try:
            results.append(wd.ensure_daemon(git_repo))
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert not errors, f"并发 ensure 不得抛异常（fail-open 语义）: {errors}"
    assert results == [True, True]
    assert len(rec.calls) == 2, (
        f"竞态实证口径变化：当前 ensure 级无互斥=2 次 spawn（由 daemon 字节锁兜底）；"
        f"若 ensure 已加锁则应为 1（请同步翻转本断言）: 实际 {len(rec.calls)}"
    )
    # PID 文件必指向其一（具体赢家不定），但必须是合法新 PID
    assert int(_pid_file(git_repo).read_text(encoding="utf-8").strip()) in {900001, 900002}


# ── R6.4：锁文件残留但进程死 ──────────────────────────────────────────────────


def test_r64_stale_lock_file_is_acquirable(git_repo: Path) -> None:
    """R6.4：watchdog.lock 文件残留（无持有者）→ 新实例可获得锁。

    防御层：字节锁而非存在性锁——文件存在不构成互斥，崩溃残留零阻碍；
    持有者死亡后 OS 随句柄表关闭自动释放字节锁（无死锁残留）。
    """
    _state_dir(git_repo).mkdir(parents=True)
    _lock_file(git_repo).write_bytes(b"")  # 残留空锁文件（模拟崩溃现场）

    fh1 = wd._acquire_single_instance_lock(git_repo)
    assert fh1 is not None, "残留锁文件不得阻碍新实例获锁（字节锁非存在性锁）"
    # 持锁期间第二实例被拒
    fh2 = wd._acquire_single_instance_lock(git_repo)
    assert fh2 is None, "持锁期间第二实例必须被拒"
    # 持有者"死亡"（句柄关闭=OS 释放字节锁）→ 下任可获锁（无 TTL 等待窗）
    fh1.close()
    fh3 = wd._acquire_single_instance_lock(git_repo)
    assert fh3 is not None, "持有者死亡后字节锁必须随句柄释放"
    fh3.close()


# ── R6.5：daemon 启动后立即崩溃 ──────────────────────────────────────────────


def test_r65_spawn_success_then_immediate_crash_respawns(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R6.5：spawn 返回成功但进程立即退出 → 本次 ensure=True；下次 ensure 检出死 PID 重生。

    防御层：ensure_daemon 每次调用都重新做 PID 存活双检，不缓存"已启动"状态——
    启动即崩在下一次 post-commit reconciler 触发时自愈。
    """
    _disarm_pytest_guard(monkeypatch)
    alive_pids: set[int] = set()  # 空集 = 一切进程已死（spawn 即崩）
    monkeypatch.setattr(pp, "is_pid_alive", lambda pid: pid in alive_pids)
    rec = _SpawnRecorder(first_pid=_FAKE_DAEMON_PID)
    monkeypatch.setattr(pp, "spawn_python_hidden", rec)

    # 第一次 ensure：无 PID 文件 → spawn "成功"，写入死 PID
    assert wd.ensure_daemon(git_repo) is True
    assert len(rec.calls) == 1
    assert _pid_file(git_repo).read_text(encoding="utf-8").strip() == str(_FAKE_DAEMON_PID)

    # 进程"立即崩溃"（alive_pids 仍为空）→ 第二次 ensure 检出死亡并重生
    assert wd.ensure_daemon(git_repo) is True
    assert len(rec.calls) == 2, "启动即崩后下次 ensure 必须检出死 PID 重生"
    assert _pid_file(git_repo).read_text(encoding="utf-8").strip() == str(_FAKE_DAEMON_PID + 1)

    spawned = [r for r in _lifecycle_records(git_repo) if r.get("status") == "spawned"]
    assert len(spawned) == 2


def test_r65_spawn_alive_stays_idempotent(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R6.5 对照组：spawn 后进程真的活着 → 后续 ensure 幂等不重复 spawn。"""
    _disarm_pytest_guard(monkeypatch)
    alive_pids: set[int] = set()
    monkeypatch.setattr(pp, "is_pid_alive", lambda pid: pid in alive_pids)
    rec = _SpawnRecorder(first_pid=_FAKE_DAEMON_PID)
    monkeypatch.setattr(pp, "spawn_python_hidden", rec)

    assert wd.ensure_daemon(git_repo) is True
    alive_pids.add(_FAKE_DAEMON_PID)  # 这次 daemon 活下来了
    assert wd.ensure_daemon(git_repo) is True
    assert wd.ensure_daemon(git_repo) is True
    assert len(rec.calls) == 1, "存活 daemon 期间 ensure 必须幂等零重复 spawn"


# ── R6.6：红队发现——锁字节偏移漂移破互斥（CONFIRMED VULN）────────────────────


@pytest.mark.xfail(
    strict=True,
    reason=(
        "CONFIRMED VULN R6.6：_acquire_single_instance_lock 未钉死锁字节偏移——"
        "'a+b' 打开位置=文件大小，带外向锁文件偏移≥1 追加 1 字节后，第二实例锁到不同字节，"
        "与第一实例同时持锁 → 互斥破裂可双 daemon。修复：msvcrt.locking 前 fh.seek(0)。"
    ),
)
def test_r66_lock_byte_offset_drift_breaks_mutex(git_repo: Path) -> None:
    """R6.6 攻击：持有者锁字节 0 期间，带外写者向偏移 ≥1 追加字节（锁字节本身受
    Windows 强制锁保护写不动，但后续字节不设防），锁文件变长 → 第二实例 'a+b'
    打开位置=新文件大小 → LK_NBLCK 锁到不同字节 → 双实例同时"持锁"。

    前置条件：有写者能向 .runtime/drift_watchdog/watchdog.lock 追加字节
    （事故/越权写/日志误定向）。当前代码库无写者，属潜在隐患而非现实触发链。
    """
    fh1 = wd._acquire_single_instance_lock(git_repo)
    assert fh1 is not None
    try:
        # 带外攻击：seek 越过锁字节 0（写锁字节会被拒），在偏移 1 落 1 字节
        with open(_lock_file(git_repo), "r+b") as attacker:
            attacker.seek(1)
            attacker.write(b"X")
        assert _lock_file(git_repo).stat().st_size == 2

        fh2 = wd._acquire_single_instance_lock(git_repo)
        try:
            assert fh2 is None, (
                "MUTEX BROKEN：锁文件变长后第二实例锁到不同偏移字节，"
                "与第一实例同时持锁 → 双 daemon 并发窗口"
            )
        finally:
            if fh2 is not None:
                fh2.close()
    finally:
        fh1.close()
