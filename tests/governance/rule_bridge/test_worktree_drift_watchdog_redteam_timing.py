# [BLUEPRINT] MOD-GOV_COMMIT_GATE_REGISTRY | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.governance.rule_bridge.test_worktree_drift_watchdog_redteam_timing
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
# [TTL] permanent
"""红队时序竞态攻击测试（#ARCH-308 工作区孤儿 WIP 治本三件套：A1 死会话清扫 / A2 派生自动收敛）。

攻击面：_sweep_dead_sessions 与 _auto_commit_derived 的"判定 → 执行"窗口内，
被并发会话注册 / 并发写入击败的可能性。

场景矩阵：
  R3.1 会话注册后立即死亡 → 清扫必须完整（卸 staged / 删 claim 快照 / 释放锁）
       且工作树内容零损毁、注册表条目不被越权 reap
  R3.2 心跳滞后但 PID 存活 → PID 存活双检必须拦截清扫
       （含 list_active 快照与 raw 注册表读取之间的竞态窗变体）
  R3.3 A2 稳定窗口内被另一写入方改写 → stable 计数器重置，不在 stable=1 提交半成品
  R3.4 清扫进行中另一会话注册 → 已开始的清扫继续完成，新会话零误伤，
       下轮清扫正确识别其为活跃
  R3.5 派生提交进行中会话注册 → 在飞提交完成（不中断），下轮检测在场缩手

时序控制方法：线程级竞态难以确定性复现，统一用 monkeypatch 在判定/执行边界
插入"另一会话动作"（_git 钩子 / fake gateway 副作用），精确构造竞态窗口的
中间状态——等价于线程在临界区被抢占的那一刻。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog as wd
from zephyr.security.access_control.session_concurrency import SessionRegistry


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )


def _git_out(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    ).stdout


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """临时 git 仓库：含一个已提交 tracked 文件（与既有 watchdog 测试同构）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "data" / "databases").mkdir(parents=True)  # reconcile_execution_log 落库目录
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
    _git(
        repo, "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.autocrlf=false", "commit", "-q", "-m", "add hot"
    )
    return repo


def _write_claim_snapshot(repo: Path, sid: str, files: list[str]) -> Path:
    snap = repo / ".runtime" / "claim_snapshots" / f"{sid}.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(json.dumps({"files": files}), encoding="utf-8")
    return snap


def _read_state(repo: Path) -> dict:
    return json.loads((repo / ".runtime" / "drift_watchdog" / "state.json").read_text(encoding="utf-8"))


def _read_audit(repo: Path) -> list[dict]:
    p = repo / ".runtime" / "audit" / "worktree_drift_watchdog.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _staged_names(repo: Path) -> set[str]:
    out = _git_out(repo, "diff", "--cached", "--name-only")
    return {ln.strip() for ln in out.splitlines() if ln.strip()}


def _spawn_sleeper() -> subprocess.Popen:
    """真实存活的占位进程（模拟在飞会话 PID）。"""
    return subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(300)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@pytest.fixture
def lock_release_recorder(monkeypatch) -> list[str]:
    """锁释放打桩：记录被释放的 sid，不触真实锁库（防测试副作用泄漏到主仓）。"""
    released: list[str] = []
    monkeypatch.setattr(wd, "_release_session_locks", lambda root, sid: released.append(sid) or True)
    return released


# ── R3.1：会话注册后立即死亡 → 清扫 ──────────────────────────────────────────


def test_r31_register_then_immediate_crash_swept_fully_worktree_preserved(
    git_repo: Path, lock_release_recorder: list[str]
) -> None:
    """R3.1：注册（PID 存活）→ 零窗口崩溃（kill）→ 清扫。

    期望：死会话被识别；staged 卸载 + claim 快照删除 + 锁释放全部执行；
    工作树内容一字节不丢；注册表条目不被 A1 越权物理删除（reap 归既有生命周期）。
    """
    from zephyr.shared.infra.process_pool import is_pid_alive

    proc = _spawn_sleeper()
    try:
        SessionRegistry(git_repo).register("sess-crash", pid=proc.pid)
        assert is_pid_alive(proc.pid), "攻击前置：注册时 PID 必须真实存活"
        snap = _write_claim_snapshot(git_repo, "sess-crash", ["hot.txt"])
        (git_repo / "hot.txt").write_text("crash-wip-uncommitted\n", encoding="utf-8")
        _git(git_repo, "add", "hot.txt")

        # 攻击动作：注册后零窗口崩溃（无心跳、无 unregister、无 release）
        proc.kill()
        proc.wait(timeout=10)
        assert not is_pid_alive(proc.pid), "攻击前置：kill 后 PID 必须确已死亡"

        summary = wd._sweep_dead_sessions(git_repo)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)

    # ① 死会话被正确识别
    assert summary["dead_sessions"] == 1, summary
    # ② 三动作全部执行
    assert summary["unstaged"] == 1, summary
    assert summary["snapshots_removed"] == 1, summary
    assert summary["locks_released"] == 1, summary
    assert lock_release_recorder == ["sess-crash"]
    assert not snap.exists(), "claim 快照必须被删除"
    # ③ staged 卸载（index 回到 HEAD）
    assert _staged_names(git_repo) == set(), f"staged 残留未清: {_staged_names(git_repo)}"
    # ④ 工作树内容零损毁（git reset HEAD 只动 index）
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "crash-wip-uncommitted\n"
    # ⑤ 注册表条目不被 A1 越权 reap（900s 宽限归 list_active 既有生命周期管）
    raw = json.loads((git_repo / ".runtime" / "session_registry.json").read_text(encoding="utf-8"))
    assert "sess-crash" in raw, "A1 不得越权物理删除注册表条目"
    # ⑥ 审计留痕
    assert any(a.get("verdict") == "dead_session_swept" and a.get("session") == "sess-crash" for a in _read_audit(git_repo))
    # ⑦ 幂等：重复攻击零动作
    s2 = wd._sweep_dead_sessions(git_repo)
    assert s2["dead_sessions"] == 0 and s2["unstaged"] == 0, s2


# ── R3.2：心跳滞后但 PID 存活 → 清扫必须缩手 ─────────────────────────────────


def test_r32_stale_heartbeat_live_pid_never_swept(git_repo: Path, lock_release_recorder: list[str]) -> None:
    """R3.2（端到端）：心跳拨回 2h（list_active 判死）但 PID 存活 → 零清扫动作。

    深度施工会话长时间不 claim 新文件即为此态。无论防御由哪一层拦截
    （reap 物理删除使 raw 不可见 / PID 存活双检），安全不变量一致：
    快照保留、staged 不动、锁不放、工作树不动。
    """
    SessionRegistry(git_repo).register("sess-deep-work", pid=os.getpid())
    reg_path = git_repo / ".runtime" / "session_registry.json"
    data = json.loads(reg_path.read_text(encoding="utf-8"))
    data["sess-deep-work"]["last_heartbeat"] -= 7200  # 心跳拨回 2h 前
    reg_path.write_text(json.dumps(data), encoding="utf-8")
    snap = _write_claim_snapshot(git_repo, "sess-deep-work", ["hot.txt"])
    (git_repo / "hot.txt").write_text("deep-wip\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")

    summary = wd._sweep_dead_sessions(git_repo)

    assert summary["dead_sessions"] == 0, f"PID 存活会话被误判清扫: {summary}"
    assert summary["unstaged"] == 0 and summary["snapshots_removed"] == 0, summary
    assert lock_release_recorder == [], "PID 存活会话的锁不得被释放"
    assert snap.exists() and json.loads(snap.read_text(encoding="utf-8")) == {"files": ["hot.txt"]}
    assert _staged_names(git_repo) == {"hot.txt"}, "staged 不得被卸载"
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "deep-wip\n"


def test_r32b_race_list_active_snapshot_then_raw_read(
    git_repo: Path, lock_release_recorder: list[str], monkeypatch
) -> None:
    """R3.2（竞态窗变体）：会话在 list_active 快照之后、raw 注册表读取之前注册。

    此时 sid ∈ raw 且 ∉ active → 进入 dead 候选，唯一防线是 _live_pid_sessions
    的 PID 存活双检。攻击目标：验证该双检确实拦截（而非仅靠 reap 时序侥幸）。
    """
    SessionRegistry(git_repo).register("sess-late", pid=os.getpid())  # PID 存活、心跳新鲜
    snap = _write_claim_snapshot(git_repo, "sess-late", ["hot.txt"])
    (git_repo / "hot.txt").write_text("late-wip\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")

    # 竞态构造：list_active 返回"注册前"的空快照（raw 读取时条目已存在）
    monkeypatch.setattr(SessionRegistry, "list_active", lambda self: [])

    summary = wd._sweep_dead_sessions(git_repo)

    assert summary["dead_sessions"] == 0, f"PID 存活双检被竞态击败: {summary}"
    assert lock_release_recorder == []
    assert snap.exists(), "竞态窗内新会话的 claim 快照不得被删"
    assert _staged_names(git_repo) == {"hot.txt"}, "竞态窗内新会话的 staged 不得被卸"
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "late-wip\n"


# ── R3.3：A2 稳定窗口内被另一写入方改写 → 计数器重置 ─────────────────────────


class _FakeCommitResult:
    def __init__(self, status: str = "OK", commit_hash: str = "abc123") -> None:
        self.status = status
        self.commit_hash = commit_hash


def test_r33_hash_change_in_stable_window_resets_counter(git_repo: Path, monkeypatch) -> None:
    """R3.3：第一周期登记候选（work_hash=H1），第二周期前另一会话改写同一文件
    （work_hash=H2）→ stable 计数器必须重置为 1，绝不在 stable=1 时提交半成品。
    """
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    calls: list[list[str]] = []

    class _RecordingGW:
        def __init__(self, project_root=None, registry=None):  # noqa: ANN001
            pass

        def _commit_auto(self, sid, files, msg):  # noqa: ANN001
            calls.append(list(files))
            return _FakeCommitResult()

    monkeypatch.setattr(
        "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway", _RecordingGW
    )

    (git_repo / "hot.txt").write_text("regen-v2\n", encoding="utf-8")
    s1 = wd._auto_commit_derived(git_repo)
    assert s1["committed"] == 0 and s1["candidates"] == 1 and s1["stable"] == 0, s1
    h1 = wd._work_hash(git_repo, "hot.txt")

    # 攻击：稳定窗口内另一写入方改写同一文件（hash 变化）
    (git_repo / "hot.txt").write_text("regen-v3-superseded\n", encoding="utf-8")
    s2 = wd._auto_commit_derived(git_repo)

    # 断言①：不在 stable=1 时提交——零提交调用
    assert s2["committed"] == 0 and calls == [], f"hash 变化后仍在 stable=1 提交半成品: {s2}, {calls}"
    # 断言②：计数器重置（stable 回到 1，hash 更新为 H2）
    cand = _read_state(git_repo)["derived_candidates"]["hot.txt"]
    h2 = wd._work_hash(git_repo, "hot.txt")
    assert h2 != h1, "攻击前置：改写必须改变 work_hash"
    assert cand["stable"] == 1 and cand["hash"] == h2, f"stable 计数器未重置: {cand}"

    # 断言③：重新计满稳定窗后提交的必须是新内容（H2），不是旧半成品
    s3 = wd._auto_commit_derived(git_repo)
    assert s3["committed"] == 1 and len(calls) == 1, (s3, calls)
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "regen-v3-superseded\n"


# ── R3.4：清扫进行中另一会话注册 ─────────────────────────────────────────────


def test_r34_registration_mid_sweep_completes_newcomer_unscathed(
    git_repo: Path, lock_release_recorder: list[str], monkeypatch
) -> None:
    """R3.4：_sweep_dead_sessions 执行到一半（dead 名单已定、尚未卸 staged）时，
    另一会话注册并 claim 了**另一个文件**。

    期望：已开始的清扫继续完成（不中断、不丢动作）；新会话的快照/staged/锁/注册表
    条目零误伤；下轮清扫正确识别新会话为活跃。
    """
    # 死会话（PID 不存在）+ staged 残留 hot.txt
    SessionRegistry(git_repo).register("sess-dead", pid=4_000_001)
    dead_snap = _write_claim_snapshot(git_repo, "sess-dead", ["hot.txt"])
    # 另一个 tracked 文件（供新会话 claim）
    (git_repo / "other.txt").write_text("o1\n", encoding="utf-8")
    _git(git_repo, "add", "other.txt")
    _git(
        git_repo, "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.autocrlf=false", "commit", "-q", "-m", "add other"
    )
    (git_repo / "hot.txt").write_text("dead-staged\n", encoding="utf-8")
    (git_repo / "other.txt").write_text("newcomer-staged\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt", "other.txt")

    # 竞态钩子：清扫读到 staged 清单的那一刻（dead 名单已定），新会话注册入场
    real_git = wd._git
    fired = {"done": False}

    def git_with_race(root, args):  # noqa: ANN001, ANN202
        rc, out = real_git(root, args)
        if not fired["done"] and args[:3] == ["diff", "--cached", "--name-only"]:
            fired["done"] = True
            SessionRegistry(root).register("sess-new", pid=os.getpid())
            _write_claim_snapshot(Path(root), "sess-new", ["other.txt"])
        return rc, out

    monkeypatch.setattr(wd, "_git", git_with_race)
    summary = wd._sweep_dead_sessions(git_repo)

    assert fired["done"], "攻击前置：竞态钩子必须在清扫中段触发"
    # ① 已开始的清扫继续完成（不中断）
    assert summary["dead_sessions"] == 1 and summary["unstaged"] == 1, summary
    assert summary["snapshots_removed"] == 1 and summary["locks_released"] == 1, summary
    assert not dead_snap.exists()
    # ② 新会话零误伤：快照保留、注册表条目在、锁释放不波及
    new_snap = git_repo / ".runtime" / "claim_snapshots" / "sess-new.json"
    assert new_snap.exists(), "清扫中注册的新会话快照不得被删"
    assert lock_release_recorder == ["sess-dead"], f"锁释放波及新会话: {lock_release_recorder}"
    raw = json.loads((git_repo / ".runtime" / "session_registry.json").read_text(encoding="utf-8"))
    assert "sess-new" in raw
    # ③ staged 精确性：死会话的 hot.txt 被卸，新会话的 other.txt 纹丝不动
    assert _staged_names(git_repo) == {"other.txt"}, f"staged 误伤: {_staged_names(git_repo)}"
    # ④ 工作树内容双双保留
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "dead-staged\n"
    assert (git_repo / "other.txt").read_text(encoding="utf-8") == "newcomer-staged\n"
    # ⑤ 下轮清扫：新会话被正确识别为活跃（零动作）
    s2 = wd._sweep_dead_sessions(git_repo)
    assert s2["dead_sessions"] == 0 and s2["unstaged"] == 0, s2
    assert new_snap.exists() and _staged_names(git_repo) == {"other.txt"}


def test_r34b_same_file_reclaim_mid_sweep_must_not_unstage(
    git_repo: Path, lock_release_recorder: list[str], monkeypatch
) -> None:
    """R3.4b（高危变体）：新会话在 active_claims 快照之后、git reset 之前
    re-claim **同一文件**。

    安全不变量（模块文档明示）："被活跃会话 re-claim 的文件跳过"。
    竞态击败该不变量 = 在飞会话的 staged 被误卸（内容零丢失但制造提交摩擦）。
    本测试断言不变量成立——失败即竞态窗口实锤。
    """
    SessionRegistry(git_repo).register("sess-dead", pid=4_000_001)
    _write_claim_snapshot(git_repo, "sess-dead", ["hot.txt"])
    (git_repo / "hot.txt").write_text("contested-wip\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")

    real_git = wd._git
    fired = {"done": False}

    def git_with_race(root, args):  # noqa: ANN001, ANN202
        rc, out = real_git(root, args)
        if not fired["done"] and args[:3] == ["diff", "--cached", "--name-only"]:
            fired["done"] = True
            # 攻击：active_claims 已快照完毕，此时新会话注册并 re-claim 同一文件
            SessionRegistry(root).register("sess-new", pid=os.getpid())
            _write_claim_snapshot(Path(root), "sess-new", ["hot.txt"])
        return rc, out

    monkeypatch.setattr(wd, "_git", git_with_race)
    summary = wd._sweep_dead_sessions(git_repo)

    assert fired["done"], "攻击前置：竞态钩子必须在清扫中段触发"
    # 硬底线：无论竞态结果如何，工作树内容必须零损毁
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "contested-wip\n"
    # 安全不变量：被（新）活跃会话 re-claim 的文件不得被卸载
    assert summary["unstaged"] == 0, (
        f"竞态窗口实锤：active_claims 快照→git reset 之间 re-claim 的文件被误卸 "
        f"(unstaged={summary['unstaged']})。窗口=[_active_sessions_and_claims 返回, "
        f"git reset HEAD 执行]，影响=在飞会话提交摩擦（内容零丢失）"
    )
    assert _staged_names(git_repo) == {"hot.txt"}, "re-claim 文件的 staged 不得被卸"


# ── R3.5：派生提交进行中会话注册 ─────────────────────────────────────────────


def test_r35_registration_mid_commit_completes_then_backs_off(git_repo: Path, monkeypatch) -> None:
    """R3.5：_auto_commit_derived 已判定零会话在场，_commit_auto 在飞期间另一会话注册。

    期望：已开始的提交继续完成（不中断）；下轮 _auto_commit_derived 检测到
    新会话在场立即缩手（零追加提交）；新会话注册表条目完好。
    """
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    calls: list[list[str]] = []

    class _RaceGW:
        def __init__(self, project_root=None, registry=None):  # noqa: ANN001
            pass

        def _commit_auto(self, sid, files, msg):  # noqa: ANN001
            calls.append(list(files))
            # 攻击：提交在飞期间（零会话判定已过时），另一会话注册入场
            SessionRegistry(git_repo).register("sess-late", pid=os.getpid())
            return _FakeCommitResult()

    monkeypatch.setattr(
        "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway", _RaceGW
    )

    (git_repo / "hot.txt").write_text("regen-v2\n", encoding="utf-8")
    s1 = wd._auto_commit_derived(git_repo)
    assert s1["committed"] == 0 and s1["candidates"] == 1, s1  # 周期①：登记候选

    s2 = wd._auto_commit_derived(git_repo)  # 周期②：稳定 → 提交（注册在飞发生）
    # ① 已开始的提交不中断
    assert s2["committed"] == 1 and len(calls) == 1, (s2, calls)
    # ② 注册确实发生在提交在飞期间
    info = SessionRegistry(git_repo).get_session("sess-late")
    assert info is not None, "竞态钩子注册的会话必须真实在场"

    # ③ 下轮：新会话在场 → 缩手，零追加提交
    s3 = wd._auto_commit_derived(git_repo)
    assert s3["committed"] == 0 and s3["candidates"] == 0 and s3["stable"] == 0, s3
    assert len(calls) == 1, f"新会话在场后仍追加提交: {calls}"
