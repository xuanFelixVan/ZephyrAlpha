# [MODULE] tests.governance.rule_bridge.test_worktree_drift_watchdog_redteam_edge
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
# [TTL] permanent
"""红队极限状态攻击测试（#ARCH-308 工作区孤儿 WIP 治本三件套 A1/A2 + 看门狗本体）。

攻击向量（只写测试，不改被测代码）：
  R4.1 MERGE_HEAD 存续 + 死会话清扫 —— merge 中间态下 index 必须零动作
  R4.2 全 git 命令故障 —— fail-open 不崩溃、零计数、状态文件不损坏
  R4.3 state.json 损坏 —— 回退默认状态并正确重建
  R4.4 quarantine 膨胀（1000 目录）—— retention 清扫不崩溃、不误删非 drift_* 目录
  R4.5 电源断电模拟（清扫中途 KeyboardInterrupt/SystemExit）—— 已生效操作不回滚、
        dead_swept 幂等记录持久化、不重复清扫
  R4.6 超大文件（100MB）hash —— 不崩溃、无内存爆炸
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tracemalloc
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog as wd


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
    """临时 git 仓库：含一个已提交 tracked 文件（与主测试文件同构）。"""
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


def _read_audit(repo: Path) -> list[dict]:
    p = repo / ".runtime" / "audit" / "worktree_drift_watchdog.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _read_log_actions(repo: Path) -> list[tuple]:
    import sqlite3

    db = repo / "data" / "databases" / "governance.db"
    if not db.exists():
        return []
    conn = sqlite3.connect(str(db))
    try:
        return conn.execute("SELECT gate_id, action, detail FROM reconcile_execution_log").fetchall()
    finally:
        conn.close()


def _register_dead_session(repo: Path, sid: str, files: list[str]) -> Path:
    """注册 PID 已死的会话 + 写其 claim 快照（files 列表格式）。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    SessionRegistry(repo).register(sid, pid=4_000_001)  # 不存在的 PID → 功能性死亡
    snap = repo / ".runtime" / "claim_snapshots" / f"{sid}.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(json.dumps({"files": files}), encoding="utf-8")
    return snap


def _write_merge_head(repo: Path) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (repo / ".git" / "MERGE_HEAD").write_bytes((head + "\n").encode("ascii"))


def _staged_files(repo: Path) -> set[str]:
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def _state_file(repo: Path) -> Path:
    return repo / ".runtime" / "drift_watchdog" / "state.json"


# ── R4.1 MERGE_HEAD 存续 + 死会话清扫 ─────────────────────────────────────────


def test_r4_1_merge_head_blocks_unstage_during_dead_sweep(git_repo: Path) -> None:
    """R4.1：merge 中间态 + 死会话残留 —— 清扫对 index 必须零动作（B5 同款豁免）。

    攻击构造：死会话 staged 残留 + MERGE_HEAD 存续。若清扫在 merge 期动 index
    （git reset HEAD --），会破坏在飞的 merge 暂存布局。
    期望防御：unstage 整体跳过（staged 保留、工作树内容不动），其余清扫动作
    （快照删除/锁释放/审计）照常；scan_once 同窗口记 merge_suppressed 零告警。
    """
    snap = _register_dead_session(git_repo, "sess-dead-merge", ["hot.txt"])
    (git_repo / "hot.txt").write_text("merge-window-staged\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")  # 死会话崩溃遗留 staged
    _write_merge_head(git_repo)

    summary = wd._sweep_dead_sessions(git_repo)

    # ① merge 存续期 unstage 整体跳过：index 不被触碰
    assert summary["dead_sessions"] == 1, summary
    assert summary["unstaged"] == 0, f"merge 存续期不得卸载 staged: {summary}"
    assert "hot.txt" in _staged_files(git_repo), "merge 存续期 index 必须保持原样"
    # 工作树内容永不销毁
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "merge-window-staged\n"
    # ② 其余清扫动作（claim 快照删除）不受 merge 影响——死会话卫生照常
    assert not snap.exists()
    assert summary["snapshots_removed"] == 1
    # ③ 审计留痕：dead_session_swept 记录中 unstaged 清单可见被抑制的对象
    swept_recs = [a for a in _read_audit(git_repo) if a.get("verdict") == "dead_session_swept"]
    assert swept_recs and swept_recs[0]["session"] == "sess-dead-merge"

    # ④ 同窗口 scan_once：漂移判定走 merge_suppressed（审计照记），零 critical_warn
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["merge_suppressed"] == 1 and s["alerted"] == 0, s
    assert any(a.get("verdict") == "merge_suppressed" for a in _read_audit(git_repo))
    rows = _read_log_actions(git_repo)
    assert not any(r[1] == "critical_warn" for r in rows), f"merge 存续期不得产生 critical_warn: {rows}"

    # ⑤ merge 消解后下轮恢复：staged 残留可被正常清扫
    (git_repo / ".git" / "MERGE_HEAD").unlink()
    # state.dead_swept 已记录该 sid（上轮已处置快照/锁）→ unstage 幂等不再重复
    s2 = wd._sweep_dead_sessions(git_repo)
    assert s2["dead_sessions"] == 0, f"已清扫会话不得重复处置: {s2}"


# ── R4.2 全 git 命令故障（fail-open）──────────────────────────────────────────


@pytest.fixture
def git_total_failure(monkeypatch) -> None:
    """模拟 git 完全不可用：所有 _git 调用返回 (2, '')。"""
    monkeypatch.setattr(wd, "_git", lambda root, args: (2, ""))


def test_r4_2_scan_once_git_total_failure_failopen(git_repo: Path, git_total_failure) -> None:
    """R4.2a：git 全故障 → scan_once 零计数返回，不抛异常，状态文件零改动。"""
    _state_file(git_repo).parent.mkdir(parents=True, exist_ok=True)
    pristine = json.dumps({"files": {"x": {"work_hash": "a"}}, "alerted": {}})
    _state_file(git_repo).write_text(pristine, encoding="utf-8")

    summary = wd.scan_once(git_repo, grace_seconds=0)  # 不得抛异常
    assert summary["scanned"] == 0 and summary["drifted"] == 0 and summary["alerted"] == 0, summary
    assert all(v == 0 for v in summary.values()), f"git 全故障必须全零摘要: {summary}"
    # 状态文件不被损坏（fail-open 提前返回，不写状态）
    assert _state_file(git_repo).read_text(encoding="utf-8") == pristine
    json.loads(_state_file(git_repo).read_text(encoding="utf-8"))  # 合法 JSON
    # 不产生告警落库
    assert not any(r[1] == "critical_warn" for r in _read_log_actions(git_repo))


def test_r4_2_auto_commit_derived_git_total_failure_failopen(git_repo: Path, git_total_failure, monkeypatch) -> None:
    """R4.2b：git 全故障 → _auto_commit_derived 零计数，绝不盲目提交，状态合法。"""
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    _register_dead_session(git_repo, "sess-dead-gitdown", ["hot.txt"])
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")

    summary = wd._auto_commit_derived(git_repo)  # 不得抛异常
    assert summary["committed"] == 0 and summary["failed"] == 0, summary
    assert summary["candidates"] == 0 and summary["stable"] == 0, (
        f"git 故障下不得产生候选/稳定集（看不到 dirty=零提交面）: {summary}"
    )
    if _state_file(git_repo).exists():
        json.loads(_state_file(git_repo).read_text(encoding="utf-8"))  # 合法 JSON 不损坏


def test_r4_2_sweep_dead_sessions_git_total_failure_failopen(git_repo: Path, git_total_failure) -> None:
    """R4.2c：git 全故障 → 死会话清扫不崩溃；git 派生动作（unstage）零计数。

    注意：快照删除是纯文件系统动作（死会话判定靠 PID 不依赖 git），按设计仍执行；
    关键安全断言是 git 派生计数为零 + 状态文件合法。
    """
    _register_dead_session(git_repo, "sess-dead-gitdown", ["hot.txt"])
    (git_repo / "hot.txt").write_text("stale\n", encoding="utf-8")

    summary = wd._sweep_dead_sessions(git_repo)  # 不得抛异常
    assert summary["unstaged"] == 0, f"git 故障下不得有 unstage 计数: {summary}"
    assert summary["dead_sessions"] == 1, summary  # 文件系统级清扫仍可达
    # 状态文件合法重建（含 dead_swept 幂等记录）
    state = json.loads(_state_file(git_repo).read_text(encoding="utf-8"))
    assert "sess-dead-gitdown" in state.get("dead_swept", {})


# ── R4.3 state.json 损坏 ──────────────────────────────────────────────────────


def _corrupt_state(repo: Path) -> None:
    p = _state_file(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{invalid", encoding="utf-8")


def test_r4_3_corrupt_state_sweep_recovers(git_repo: Path) -> None:
    """R4.3a：state.json 非法 JSON → 死会话清扫回退默认状态，不崩溃，正确重建。"""
    _register_dead_session(git_repo, "sess-dead-corrupt", ["hot.txt"])
    (git_repo / "hot.txt").write_text("stale\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")
    _corrupt_state(git_repo)

    summary = wd._sweep_dead_sessions(git_repo)  # 不得抛异常
    assert summary["dead_sessions"] == 1 and summary["unstaged"] == 1, summary

    # 新状态被正确重建：合法 JSON + 默认键 + dead_swept 幂等记录
    state = json.loads(_state_file(git_repo).read_text(encoding="utf-8"))
    assert isinstance(state.get("files"), dict) and isinstance(state.get("alerted"), dict)
    assert "sess-dead-corrupt" in state.get("dead_swept", {}), state


def test_r4_3_corrupt_state_auto_commit_recovers(git_repo: Path, monkeypatch) -> None:
    """R4.3b：state.json 非法 JSON → 派生自动收敛回退默认状态，不崩溃，候选重建。"""
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    (git_repo / "hot.txt").write_text("regen-v2\n", encoding="utf-8")
    _corrupt_state(git_repo)

    summary = wd._auto_commit_derived(git_repo)  # 不得抛异常
    assert summary["candidates"] == 1 and summary["committed"] == 0, summary

    state = json.loads(_state_file(git_repo).read_text(encoding="utf-8"))
    cand = state.get("derived_candidates", {})
    assert "hot.txt" in cand and cand["hot.txt"]["stable"] == 1, state
    # 二次调用（状态已合法）：稳定性累计正常推进
    s2 = wd._auto_commit_derived(git_repo)
    assert s2["stable"] == 1, s2


# ── R4.4 quarantine 膨胀（1000 目录）──────────────────────────────────────────


def test_r4_4_quarantine_bloat_1000_dirs_sweep(git_repo: Path) -> None:
    """R4.4a：1000 个 drift_* 快照目录 + 诱饵 → retention=0 全清，诱饵零误伤。

    攻击意图：膨胀目录拖垮/卡死清扫循环，或诱使清扫越界删除非本家产物。
    """
    q = git_repo / ".runtime" / "quarantine"
    q.mkdir(parents=True)
    base = datetime(2020, 1, 1, tzinfo=timezone.utc)
    n = 1000
    for i in range(n):
        ts = (base + timedelta(seconds=i)).strftime("%Y%m%dT%H%M%S")
        d = q / f"drift_{ts}"
        d.mkdir()
        (d / "blob.bin").write_bytes(b"x")
    # 诱饵：非 drift_* 目录 / 非法时间戳目录 / 未来时间目录 / drift_ 前缀的**文件**
    (q / "manual_evidence").mkdir()
    (q / "drift_not-a-timestamp").mkdir()
    (q / "drift_29990101T000000").mkdir()
    (q / "drift_19991231T235959").write_bytes(b"i am a file not a dir")

    result = wd._sweep_quarantine(git_repo, retention_days=0)  # 不得抛异常
    assert result["removed"] == n, result
    assert result["kept"] == 2, result  # 非法时间戳 + 未来时间各 1

    # 全部 drift_<过去ts> 目录消失
    remaining = list(q.glob("drift_2*"))
    assert all(p.name in {"drift_29990101T000000"} or not p.is_dir() for p in remaining), remaining
    # 诱饵零误伤
    assert (q / "manual_evidence").is_dir()
    assert (q / "drift_not-a-timestamp").is_dir()
    assert (q / "drift_29990101T000000").is_dir()
    assert (q / "drift_19991231T235959").is_file()
    assert q.is_dir()  # quarantine 根本身不被删
    # 逐条审计：1000 条 quarantine_retention_sweep
    sweeps = [a for a in _read_audit(git_repo) if a.get("verdict") == "quarantine_retention_sweep"]
    assert len(sweeps) == n


def test_r4_4_maybe_sweep_quarantine_throttled_entry(git_repo: Path, monkeypatch) -> None:
    """R4.4b：日级节流入口 _maybe_sweep_quarantine（注入 retention_days=0）。

    首次调用执行清扫并写节流标记；同日二次调用必须整体跳过（防每周期扫爆目录）。
    """
    orig_sweep = wd._sweep_quarantine
    monkeypatch.setattr(wd, "_sweep_quarantine", lambda root: orig_sweep(root, retention_days=0))

    q = git_repo / ".runtime" / "quarantine"
    q.mkdir(parents=True)
    today_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    d1 = q / f"drift_{today_ts}"
    d1.mkdir()

    wd._maybe_sweep_quarantine(git_repo)  # 不得抛异常
    assert not d1.exists(), "retention=0 时当日快照也应被清理"
    state = json.loads(_state_file(git_repo).read_text(encoding="utf-8"))
    assert state.get("quarantine_last_sweep") == datetime.now(timezone.utc).date().isoformat()

    # 同日二次调用：节流命中 → 新建的过期目录也不扫
    d2 = q / "drift_20200101T000000"
    d2.mkdir()
    wd._maybe_sweep_quarantine(git_repo)
    assert d2.exists(), "日级节流：同日第二轮必须整体跳过"


# ── R4.5 电源断电模拟（清扫中途崩溃）──────────────────────────────────────────


@pytest.mark.parametrize("exc", [KeyboardInterrupt, SystemExit])
def test_r4_5_power_loss_completed_ops_not_rolled_back(git_repo: Path, monkeypatch, exc) -> None:
    """R4.5 安全不变量：清扫中途断电，已执行操作不回滚、重扫零重复动作、内容零丢失。

    崩溃点：首个死会话的锁释放环节（此时 unstage + 快照删除已完成）。
    """
    sid = "sess-dead-power"
    snap = _register_dead_session(git_repo, sid, ["hot.txt"])
    (git_repo / "hot.txt").write_text("power-wip\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")

    calls = {"n": 0}

    def _crash_release(root, sid_):  # noqa: ANN001
        calls["n"] += 1
        if calls["n"] == 1:
            raise exc("simulated power loss")
        return True

    monkeypatch.setattr(wd, "_release_session_locks", _crash_release)

    with pytest.raises(exc):
        wd._sweep_dead_sessions(git_repo)

    # ① 已生效操作不回滚：unstage 已落 index，快照已删，工作树内容保留
    assert _staged_files(git_repo) == set(), "断电前已执行的 unstage 不得回滚"
    assert not snap.exists(), "断电前已删除的快照不得复活"
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "power-wip\n", "工作树内容永不销毁"

    # ② 恢复供电后重扫：无异常；动作级幂等（无 staged 可卸/无快照可删）
    s2 = wd._sweep_dead_sessions(git_repo)
    assert s2["unstaged"] == 0 and s2["snapshots_removed"] == 0, f"重复清扫不得有重复动作: {s2}"
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "power-wip\n"
    # 治本后语义（R4.5 修复，2026-09-03）：幂等记录先于锁释放落盘——断电后重扫
    # 该会话已在 dead_swept 中，会话级零重复计数（原断言 ==1 记录的是修复前缺口）。
    assert s2["dead_sessions"] == 0


def test_r4_5_power_loss_dead_swept_durability(git_repo: Path, monkeypatch) -> None:
    """R4.5 幂等持久化：断电后 dead_swept 记录必须已保存，同一会话不得重复清扫。"""
    sid = "sess-dead-power-2"
    _register_dead_session(git_repo, sid, ["hot.txt"])
    (git_repo / "hot.txt").write_text("power-wip\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")

    monkeypatch.setattr(
        wd,
        "_release_session_locks",
        lambda root, sid_: (_ for _ in ()).throw(KeyboardInterrupt("simulated power loss")),
    )
    with pytest.raises(KeyboardInterrupt):
        wd._sweep_dead_sessions(git_repo)

    state = json.loads(_state_file(git_repo).read_text(encoding="utf-8")) if _state_file(git_repo).exists() else None
    assert state is not None and sid in state.get("dead_swept", {}), (
        "漏洞 R4.5：断电发生在清扫循环中途 → dead_swept 幂等记录未持久化"
        "（_save_state 在循环结束后才调用），下次调用将重复清扫同一会话"
    )


# ── R4.6 超大文件 hash ────────────────────────────────────────────────────────


def test_r4_6_huge_file_hash_no_memory_explosion(git_repo: Path) -> None:
    """R4.6：100MB 稀疏文件 hash-object —— 不崩溃、结果正确、Python 侧无内存爆炸。"""
    size = 100 * 1024 * 1024
    big = git_repo / "big.bin"
    with open(big, "wb") as fh:
        fh.truncate(size)  # NTFS 稀疏置长，瞬时完成

    # 期望 hash：git blob 口径 sha1("blob <size>\0" + content)
    h = hashlib.sha1()
    h.update(f"blob {size}\x00".encode("ascii"))
    chunk = b"\x00" * (1024 * 1024)
    for _ in range(size // len(chunk)):
        h.update(chunk)
    expected = h.hexdigest()

    tracemalloc.start()
    try:
        result = wd._work_hash(git_repo, "big.bin")  # 不得抛异常
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    assert result == expected, f"100MB 文件 hash 错误（或 git 超时优雅降级为空串）: {result!r}"
    assert peak < 16 * 1024 * 1024, f"hash 计算 Python 侧内存爆炸: peak={peak / 1024 / 1024:.1f}MB"
