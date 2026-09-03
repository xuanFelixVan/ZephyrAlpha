# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | §#ARCH-308 工作区孤儿 WIP 治本三件套
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.rule_bridge.test_worktree_drift_watchdog_redteam_concurrent
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
# [TTL] task_bound
"""#ARCH-308 三件套红队并发风暴测试（R1.1-R1.4）。

攻击面：#ARCH-308 A1 死会话清扫（_sweep_dead_sessions）/ A2 派生自动收敛
（_auto_commit_derived）/ scan_once / B1 判读器（classify_workspace_wip.classify）
在同一 repo 上被多线程并发调用时的安全性。

生产相关性：daemon 主循环线程、网关 post-commit reconciler 线程、CLI --once、
多 AI 会话各自的网关进程可对同一仓并发触发上述函数——线程内并发与跨进程并发
在 Windows 文件语义下同源（SessionRegistry._save docstring 已实证跨进程
os.replace WinError 2 竞态，AI-NORTH-001 2026-08-15）。

方法学：测试编码任务书规定的**理想防御契约**（幂等/无异常/无撕裂/无重复提交），
失败即红队突破。每个场景的校验聚合成 violations 清单一次断言，单轮跑齐全部证据。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "governance"))

import classify_workspace_wip as cw  # noqa: E402

import zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog as wd  # noqa: E402


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
    """临时 git 仓库（同既有基线 fixture 模式）：含已提交 tracked 文件 hot.txt。"""
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


def _storm(n_threads: int, fn) -> tuple[list, list[str]]:
    """barrier 同步起爆的线程风暴（最大化撞车概率）。返回 (results, errors)。"""
    barrier = threading.Barrier(n_threads)
    results: list = [None] * n_threads
    errors: list[str] = []

    def _worker(i: int) -> None:
        try:
            barrier.wait(timeout=60)
            results[i] = fn()
        except Exception as e:  # noqa: BLE001 — 红队记录一切逃逸异常
            errors.append(f"thread-{i}: {type(e).__name__}: {e}")

    threads = [threading.Thread(target=_worker, args=(i,), daemon=True) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=180)
    for i, t in enumerate(threads):
        if t.is_alive():
            errors.append(f"thread-{i}: HUNG（join 超时未结束，疑似死锁）")
    return results, errors


def _state_file(repo: Path) -> Path:
    return repo / ".runtime" / "drift_watchdog" / "state.json"


def _check_state_intact(repo: Path, violations: list[str], extra_keys: tuple[str, ...] = ()) -> None:
    """state.json 不撕裂：可解析 + files/alerted 结构完整 + 场景附加键结构完整。"""
    try:
        state = json.loads(_state_file(repo).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        violations.append(f"state.json 撕裂/丢失: {type(e).__name__}: {e}")
        return
    for key in ("files", "alerted", *extra_keys):
        if key in state and not isinstance(state[key], dict):
            violations.append(f"state.json[{key!r}] 非 dict（结构撕裂）: {type(state[key]).__name__}")


def _check_audit_lines(repo: Path, violations: list[str]) -> None:
    """审计 jsonl 每行必须是完整 JSON（并发 append 撕裂=归因证据损坏）。"""
    p = repo / ".runtime" / "audit" / "worktree_drift_watchdog.jsonl"
    if not p.exists():
        return
    for i, ln in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines()):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception:  # noqa: BLE001
            violations.append(f"审计 jsonl 第 {i + 1} 行撕裂: {ln[:100]!r}")
            break


def _staged_files(repo: Path) -> set[str]:
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


# ── R1.1 并发清扫撞车 ─────────────────────────────────────────────────────────


def test_r1_1_concurrent_sweep_dead_sessions(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """10 线程同时 _sweep_dead_sessions（1 死会话 + 1 活跃会话，各 claim 一个 staged 文件）。

    防御契约：无异常逃逸；死会话 staged 卸载全局恰好一次；活跃会话快照/staged 不动；
    工作树内容零销毁；state.json/审计不撕裂。
    """
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    # _release_session_locks 的 import 通道指向真实仓 scripts.lock_files（锚定真实
    # PROJECT_ROOT 的锁注册表）——打桩保持测试密闭（本场景测清扫竞态，不测锁释放）。
    monkeypatch.setattr(wd, "_release_session_locks", lambda root, sid: True)

    # git reset 调用探针：卸载动作执行次数的直接证据
    real_git = wd._git
    reset_calls: list[tuple[tuple[str, ...], int]] = []
    spy_lock = threading.Lock()

    def spy_git(root, args):  # noqa: ANN001, ANN202
        rc, out = real_git(root, args)
        if args[:2] == ["reset", "HEAD"]:
            with spy_lock:
                reset_calls.append((tuple(args[3:]), rc))
        return rc, out

    monkeypatch.setattr(wd, "_git", spy_git)

    # 活跃会话（PID 存活）claim active.txt；死会话（PID 不存在）claim hot.txt
    SessionRegistry(git_repo).register("sess-alive", pid=os.getpid())
    SessionRegistry(git_repo).register("sess-dead", pid=4_000_001)
    snap_dir = git_repo / ".runtime" / "claim_snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    alive_snap = snap_dir / "sess-alive.json"
    alive_snap.write_text(json.dumps({"files": ["active.txt"]}), encoding="utf-8")
    dead_snap = snap_dir / "sess-dead.json"
    dead_snap.write_text(json.dumps({"files": ["hot.txt"]}), encoding="utf-8")

    (git_repo / "active.txt").write_text("active-v1\n", encoding="utf-8")
    _git(git_repo, "add", "active.txt")
    _git(
        git_repo, "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.autocrlf=false", "commit", "-q", "-m", "add active"
    )
    # 两个文件均制造 staged 残留
    (git_repo / "hot.txt").write_text("stale-dead\n", encoding="utf-8")
    (git_repo / "active.txt").write_text("active-wip\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt", "active.txt")

    results, errors = _storm(10, lambda: wd._sweep_dead_sessions(git_repo))

    violations: list[str] = []
    if errors:
        violations.append(f"并发清扫 {len(errors)}/10 线程抛异常: {errors[:3]}")
    ok = [r for r in results if isinstance(r, dict)]
    total_unstaged = sum(int(r.get("unstaged", 0)) for r in ok)
    if total_unstaged != 1:
        violations.append(
            f"死会话 staged 卸载应全局恰好 1 次，实际计数={total_unstaged}"
            f"（git reset 实际调用 {len(reset_calls)} 次: rc 分布 "
            f"{[rc for _, rc in reset_calls]}）"
        )
    total_snaps = sum(int(r.get("snapshots_removed", 0)) for r in ok)
    if total_snaps != 1:
        violations.append(f"死会话快照删除计数应=1，实际={total_snaps}")

    try:
        staged = _staged_files(git_repo)
        if staged != {"active.txt"}:
            violations.append(f"终态 staged 应只剩 active.txt（活跃会话豁免），实际: {sorted(staged)}")
    except Exception as e:  # noqa: BLE001
        violations.append(f"终态 staged 读取失败: {e}")
    content = (git_repo / "hot.txt").read_text(encoding="utf-8")
    if content != "stale-dead\n":
        violations.append(f"工作树内容被销毁（reset 越权动工作树）: {content!r}")
    if not alive_snap.exists():
        violations.append("活跃会话 claim 快照被误删")
    if dead_snap.exists():
        violations.append("死会话 claim 快照未被删除")

    _check_state_intact(git_repo, violations, extra_keys=("dead_swept",))
    try:
        state = json.loads(_state_file(git_repo).read_text(encoding="utf-8"))
        if "sess-dead" not in state.get("dead_swept", {}):
            violations.append("state.dead_swept 未登记 sess-dead（幂等记录丢失）")
    except Exception:  # noqa: BLE001 — 撕裂已在上一步记录
        pass
    _check_audit_lines(git_repo, violations)

    assert not violations, "R1.1 红队突破：\n- " + "\n- ".join(violations)


# ── R1.2 并发派生提交撞车 ─────────────────────────────────────────────────────


class _FakeCommitResult:
    def __init__(self, status: str = "OK", commit_hash: str = "abc123") -> None:
        self.status = status
        self.commit_hash = commit_hash


def test_r1_2_concurrent_auto_commit_derived(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """10 线程同时 _auto_commit_derived（预置 stable=1 候选，全体过稳定窗）。

    防御契约：_commit_auto 全局至多被调 1 次（无重复提交）；无异常逃逸；
    state.derived_candidates 不撕裂。
    """
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    commit_calls: list[tuple[str, list[str], str]] = []
    calls_lock = threading.Lock()

    class _CountingGW:
        def __init__(self, project_root=None, registry=None):  # noqa: ANN001
            pass

        def _commit_auto(self, sid, files, msg):  # noqa: ANN001
            with calls_lock:
                commit_calls.append((sid, list(files), msg))
            # 模拟真实 commit 链路延迟（三 gate + git add/commit 百毫秒级），撑大竞态窗
            time.sleep(0.05)
            return _FakeCommitResult()

    monkeypatch.setattr(
        "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway", _CountingGW
    )

    (git_repo / "hot.txt").write_text("regen-v2\n", encoding="utf-8")
    seed = wd._auto_commit_derived(git_repo)  # 第 1 周期：登记候选 stable=1
    assert seed["candidates"] == 1 and seed["committed"] == 0, f"预置候选失败: {seed}"

    results, errors = _storm(10, lambda: wd._auto_commit_derived(git_repo))

    violations: list[str] = []
    if errors:
        violations.append(f"并发自动收敛 {len(errors)}/10 线程抛异常: {errors[:3]}")
    if len(commit_calls) > 1:
        violations.append(
            f"_commit_auto 被并发调用 {len(commit_calls)} 次（契约≤1）——"
            f"同一文件被重复提交: {[c[1] for c in commit_calls]}"
        )
    # 同一文件被提交多次 = 重复提交（按文件维度逐一点名）
    file_commit_count: dict[str, int] = {}
    for _sid, files, _msg in commit_calls:
        for f in files:
            file_commit_count[f] = file_commit_count.get(f, 0) + 1
    dup = {f: n for f, n in file_commit_count.items() if n > 1}
    if dup:
        violations.append(f"重复提交文件: {dup}")

    _check_state_intact(git_repo, violations, extra_keys=("derived_candidates",))
    try:
        state = json.loads(_state_file(git_repo).read_text(encoding="utf-8"))
        cands = state.get("derived_candidates", {})
        for rel, c in cands.items():
            if not isinstance(c, dict) or "hash" not in c or "stable" not in c:
                violations.append(f"derived_candidates[{rel!r}] 结构撕裂: {c!r}")
                break
    except Exception:  # noqa: BLE001 — 撕裂已记录
        pass
    _check_audit_lines(git_repo, violations)

    assert not violations, "R1.2 红队突破：\n- " + "\n- ".join(violations)


# ── R1.3 并发 scan_once 风暴 ──────────────────────────────────────────────────


def test_r1_3_concurrent_scan_once_storm(git_repo: Path) -> None:
    """20 线程同时 scan_once（含 dirty 文件，0 会话 → alert 路径全链路）。

    防御契约：无异常逃逸；返回结构完整；state.json files/alerted 不撕裂；审计不撕裂。
    """
    (git_repo / "hot.txt").write_text("storm-drift\n", encoding="utf-8")

    results, errors = _storm(20, lambda: wd.scan_once(git_repo, grace_seconds=0))

    violations: list[str] = []
    if errors:
        violations.append(f"并发 scan_once {len(errors)}/20 线程抛异常: {errors[:3]}")
    expected_keys = {
        "scanned", "drifted", "alerted", "observed", "claimed", "auto_claimed",
        "grace_suppressed", "dedup_skipped", "healed", "merge_suppressed",
    }
    for i, r in enumerate(results):
        if not isinstance(r, dict):
            continue  # 异常已计入 errors
        missing = expected_keys - set(r)
        if missing:
            violations.append(f"thread-{i} summary 缺键: {sorted(missing)}")
            break

    _check_state_intact(git_repo, violations)
    _check_audit_lines(git_repo, violations)

    assert not violations, "R1.3 红队突破：\n- " + "\n- ".join(violations)


# ── R1.4 判读器并发调用 ───────────────────────────────────────────────────────


def test_r1_4_concurrent_classify(git_repo: Path) -> None:
    """10 线程同时 classify（1 活跃会话 claim hot.txt + 1 未跟踪文件）。

    防御契约：只读工具无异常；返回结构一致（全键在位）；10 次结果完全一致（确定性）。
    """
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    SessionRegistry(git_repo).register("sess-a", pid=os.getpid())
    snap_dir = git_repo / ".runtime" / "claim_snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    (snap_dir / "sess-a.json").write_text(json.dumps({"files": ["hot.txt"]}), encoding="utf-8")
    (git_repo / "hot.txt").write_text("wip\n", encoding="utf-8")
    (git_repo / "untracked.txt").write_text("new\n", encoding="utf-8")

    results, errors = _storm(10, lambda: cw.classify(git_repo))

    violations: list[str] = []
    if errors:
        violations.append(f"并发 classify {len(errors)}/10 线程抛异常: {errors[:3]}")
    ok = [r for r in results if isinstance(r, dict)]
    expected_top = {"head", "active_sessions", "total_dirty", "categories", "needs_attention", "orphan_wip_estimate", "conclusion"}
    expected_cats = {
        cw.CAT_ACTIVE_WIP, cw.CAT_RUNTIME_TELEMETRY, cw.CAT_DERIVED_SYNC,
        cw.CAT_AUTO_SYNC, cw.CAT_STALE_ROLLBACK, cw.CAT_FRESH_CHANGE, cw.CAT_UNTRACKED,
    }
    for i, r in enumerate(ok):
        if expected_top - set(r):
            violations.append(f"thread-{i} 结果缺顶层键: {sorted(expected_top - set(r))}")
            break
        if set(r["categories"]) != expected_cats:
            violations.append(f"thread-{i} categories 键不一致: {sorted(r['categories'])}")
            break
        if r["total_dirty"] != sum(len(v) for v in r["categories"].values()):
            violations.append(f"thread-{i} total_dirty 与分类计数不一致")
            break
    if ok:
        first = ok[0]
        for i, r in enumerate(ok[1:], 1):
            if r != first:
                violations.append(f"thread-{i} 结果与 thread-0 不一致（只读判读非确定）")
                break
        wip_paths = [e["path"] for e in first["categories"][cw.CAT_ACTIVE_WIP]]
        if "hot.txt" not in wip_paths:
            violations.append(f"hot.txt 未归入 active_wip: {wip_paths}")
        untracked_paths = [e["path"] for e in first["categories"][cw.CAT_UNTRACKED]]
        if "untracked.txt" not in untracked_paths:
            violations.append(f"untracked.txt 未归入 untracked_new: {untracked_paths}")

    assert not violations, "R1.4 红队突破：\n- " + "\n- ".join(violations)
