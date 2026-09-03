# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | §#ARCH-308
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# [MODULE] tests.governance.rule_bridge.test_worktree_drift_watchdog_redteam_audit
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
"""红队测试：#ARCH-308 工作区孤儿 WIP 治本三件套——日志/审计攻击面（R5.1~R5.5）。

攻击模型（红队视角，只写测试不改被测代码）：
  R5.1 审计日志写入失败——mock _audit 的 open() 抛 PermissionError（磁盘满/ACL 拒绝），
       验证 _sweep_dead_sessions 主流程（unstage/删快照/释锁/存状态）不被拖垮。
  R5.2 审计日志并发追加——10 线程同写同一 jsonl，验证无异常、行数零丢失、每行合法 JSON、
       无行撕裂；附加大尺寸记录（>8KB 缓冲，多 chunk 写）并发探针。
  R5.3 超大审计记录——10MB detail 字符串写入，验证不崩溃、round-trip 完整、文件仍可续写。
  R5.4 reconcile_execution_log 落库失败——mock _log_reconcile_results 抛
       sqlite3.OperationalError("database is locked")，验证 _sweep_dead_sessions /
       _auto_commit_derived 主流程继续完成。
  R5.5 状态文件结构损坏——合法 JSON 但结构错误（{"files": "not_a_dict"} 及变体），
       验证无异常（回退默认）、不死循环；并对各函数实际消费的键做类型混淆探针。
"""

from __future__ import annotations

import builtins
import json
import logging
import sqlite3
import subprocess
import threading
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog as wd

# ── 测试基建（复用既有 test_worktree_drift_watchdog.py 模式）─────────────────────


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
    """临时 git 仓库：含一个已提交 tracked 文件。"""
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


def _audit_path(repo: Path) -> Path:
    return repo / ".runtime" / "audit" / "worktree_drift_watchdog.jsonl"


def _register_dead_session(repo: Path, sid: str, files: list[str]) -> Path:
    """注册 PID 已死的会话 + 写其 claim 快照（files 列表格式）。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    SessionRegistry(repo).register(sid, pid=4_000_001)  # 不存在的 PID → 功能性死亡
    snap = repo / ".runtime" / "claim_snapshots" / f"{sid}.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(json.dumps({"files": files}), encoding="utf-8")
    return snap


def _write_state(repo: Path, obj: dict) -> Path:
    """手动写 .runtime/drift_watchdog/state.json（构造损坏现场）。"""
    sd = repo / ".runtime" / "drift_watchdog"
    sd.mkdir(parents=True, exist_ok=True)
    p = sd / "state.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def _git_index_clean(repo: Path) -> bool:
    r = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return r.returncode == 0


class _FakeCommitResult:
    def __init__(self, status: str = "OK", commit_hash: str = "abc123") -> None:
        self.status = status
        self.commit_hash = commit_hash


def _install_fake_gateway(monkeypatch: pytest.MonkeyPatch, calls: list) -> None:
    class _FakeGW:
        def __init__(self, project_root=None, registry=None):  # noqa: ANN001
            pass

        def _commit_auto(self, sid, files, msg):  # noqa: ANN001
            calls.append((sid, list(files), msg))
            return _FakeCommitResult()

    monkeypatch.setattr(
        "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway", _FakeGW
    )


# ── R5.1：审计日志写入失败（PermissionError）不得阻断主流程 ─────────────────────


def test_r51_audit_permission_error_does_not_block_sweep(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """mock _audit 的 open() 抛 PermissionError → 清扫主流程照常完成、零异常。"""
    snap1 = _register_dead_session(git_repo, "sess-dead-1", ["hot.txt"])
    snap2 = _register_dead_session(git_repo, "sess-dead-2", [])
    (git_repo / "hot.txt").write_text("stale-staged\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")

    real_open = builtins.open

    def hostile_open(file, *args, **kwargs):  # noqa: ANN001, ANN202
        if "worktree_drift_watchdog.jsonl" in str(file):
            raise PermissionError(13, "Permission denied (redteam: simulated disk-full/ACL)", str(file))
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", hostile_open)

    with caplog.at_level(logging.WARNING, logger="zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog"):
        summary = wd._sweep_dead_sessions(git_repo)  # 不得抛出

    # 主流程完整完成：双死会话全清扫、staged 卸载、快照全删
    assert summary["dead_sessions"] == 2, summary
    assert summary["unstaged"] == 1, summary
    assert summary["snapshots_removed"] == 2, summary
    assert not snap1.exists() and not snap2.exists()
    # index 回到 HEAD，工作树内容未被销毁
    assert _git_index_clean(git_repo)
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "stale-staged\n"
    # 状态仍持久化（_save_state 在审计失败之后照常执行）
    state = json.loads(
        (git_repo / ".runtime" / "drift_watchdog" / "state.json").read_text(encoding="utf-8")
    )
    assert set(state.get("dead_swept", {})) == {"sess-dead-1", "sess-dead-2"}, state
    # 审计失败被吞并留有 warning（fail-open 但不静默）
    assert any("audit append failed" in r.message for r in caplog.records), caplog.text


# ── R5.2：审计日志并发追加——无撕裂/无丢失/无异常 ──────────────────────────────


def test_r52_concurrent_audit_appends_no_tearing(git_repo: Path) -> None:
    """10 线程 × 100 条小记录并发 _audit：行数零丢失、每行合法 JSON、键集完整。"""
    n_threads, per_thread = 10, 100
    barrier = threading.Barrier(n_threads)
    errors: list[BaseException] = []

    def worker(tid: int) -> None:
        try:
            barrier.wait(timeout=30)
            for i in range(per_thread):
                wd._audit(
                    git_repo,
                    {
                        "ts": "2026-09-03T00:00:00+00:00",
                        "verdict": "redteam_concurrent",
                        "tid": tid,
                        "seq": i,
                        "pad": "x" * 64,
                    },
                )
        except BaseException as e:  # noqa: BLE001 — 汇总线程异常统一断言
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert all(not t.is_alive() for t in threads), "并发写死锁/挂起"
    assert not errors, f"并发 _audit 抛出异常: {errors[:3]}"

    raw_lines = _audit_path(git_repo).read_text(encoding="utf-8").splitlines()
    assert len(raw_lines) == n_threads * per_thread, (
        f"审计行丢失/覆写（append 竞态）: 期望 {n_threads * per_thread} 实得 {len(raw_lines)}"
    )
    seen: set[tuple[int, int]] = set()
    for ln in raw_lines:
        rec = json.loads(ln)  # 任何撕裂行都会在这里炸 JSONDecodeError
        seen.add((rec["tid"], rec["seq"]))
    assert seen == {(t, i) for t in range(n_threads) for i in range(per_thread)}, "记录内容被并发覆写/串行"


def test_r52b_concurrent_large_records_tearing_probe(git_repo: Path) -> None:
    """大尺寸记录（32KB > 8KB 默认缓冲，多 chunk 写）并发追加——行撕裂探针。

    _audit 无任何进程内锁，行完整性完全依赖 OS append 写语义；本探针用超过
    BufferedWriter 缓冲区的记录放大 lseek→write 竞态窗口。
    """
    n_threads, per_thread = 8, 25
    pad = "y" * (32 * 1024)
    barrier = threading.Barrier(n_threads)
    errors: list[BaseException] = []

    def worker(tid: int) -> None:
        try:
            barrier.wait(timeout=30)
            for i in range(per_thread):
                wd._audit(
                    git_repo,
                    {
                        "ts": "2026-09-03T00:00:00+00:00",
                        "verdict": "redteam_concurrent_large",
                        "tid": tid,
                        "seq": i,
                        "pad": pad,
                    },
                )
        except BaseException as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=90)
    assert all(not t.is_alive() for t in threads), "大记录并发写死锁/挂起"
    assert not errors, f"并发大记录 _audit 抛出异常: {errors[:3]}"

    raw_lines = _audit_path(git_repo).read_text(encoding="utf-8").splitlines()
    assert len(raw_lines) == n_threads * per_thread, (
        f"大记录并发写行丢失（OS append 非原子实证）: 期望 {n_threads * per_thread} 实得 {len(raw_lines)}"
    )
    seen: set[tuple[int, int]] = set()
    for ln in raw_lines:
        rec = json.loads(ln)  # 行撕裂 → JSONDecodeError
        assert rec["verdict"] == "redteam_concurrent_large", f"串行污染: {ln[:120]}"
        seen.add((rec["tid"], rec["seq"]))
    assert seen == {(t, i) for t in range(n_threads) for i in range(per_thread)}


# ── R5.3：超大审计记录（10MB）不崩溃、文件可读 ────────────────────────────────


def test_r53_oversized_audit_record_10mb(git_repo: Path) -> None:
    """10MB detail 记录写入：不崩溃、round-trip 完整（或优雅截断需可解析）、文件可续写。"""
    big = "Z" * (10 * 1024 * 1024)  # 10MB
    wd._audit(  # 不得抛出
        git_repo,
        {"ts": "2026-09-03T00:00:00+00:00", "verdict": "redteam_oversized", "detail": big},
    )
    p = _audit_path(git_repo)
    assert p.exists()
    # 大记录之后文件仍可正常追加
    wd._audit(git_repo, {"ts": "2026-09-03T00:00:01+00:00", "verdict": "after_big"})

    lines = p.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2, f"大记录污染文件结构: {len(lines)} 行"
    rec_big = json.loads(lines[0])  # 必须仍是合法 JSON
    assert rec_big["verdict"] == "redteam_oversized"
    # 无截断：detail 完整 round-trip（若未来实现优雅截断，此处改为断言截断标记即可）
    assert rec_big["detail"] == big, "10MB 记录内容被静默截断/损坏"
    rec_after = json.loads(lines[1])
    assert rec_after["verdict"] == "after_big"


# ── R5.4：reconcile_execution_log 落库失败不得阻断主流程 ──────────────────────


def _mock_db_locked(monkeypatch: pytest.MonkeyPatch) -> None:
    import zephyr.governance.audit.reconciliation_registry as rr

    def _boom(*args, **kwargs):  # noqa: ANN001, ANN202
        raise sqlite3.OperationalError("database is locked (redteam)")

    monkeypatch.setattr(rr, "_log_reconcile_results", _boom)


def test_r54a_db_locked_does_not_block_sweep(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """_log_reconcile_results 抛 sqlite3.OperationalError → _sweep_dead_sessions 照常完成。"""
    _mock_db_locked(monkeypatch)
    snap = _register_dead_session(git_repo, "sess-dead", ["hot.txt"])
    (git_repo / "hot.txt").write_text("stale-staged\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")

    with caplog.at_level(logging.WARNING, logger="zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog"):
        summary = wd._sweep_dead_sessions(git_repo)  # 不得抛出

    assert summary["dead_sessions"] == 1, summary
    assert summary["unstaged"] == 1, summary
    assert summary["snapshots_removed"] == 1, summary
    assert not snap.exists()
    assert _git_index_clean(git_repo)
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "stale-staged\n"
    # 文件审计链（_audit）不受影响——落库失败时归因证据仍在
    assert any(a.get("verdict") == "dead_session_swept" for a in _read_audit(git_repo))
    assert any("log_results failed" in r.message for r in caplog.records), caplog.text


def test_r54b_db_locked_does_not_block_auto_commit(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """_log_reconcile_results 抛 sqlite3.OperationalError → _auto_commit_derived 照常收敛提交。"""
    _mock_db_locked(monkeypatch)
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    calls: list = []
    _install_fake_gateway(monkeypatch, calls)
    (git_repo / "hot.txt").write_text("regen-v2\n", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog"):
        s1 = wd._auto_commit_derived(git_repo)  # 登记候选
        s2 = wd._auto_commit_derived(git_repo)  # 稳定窗达成 → 提交（落库失败不得阻断）

    assert s1["committed"] == 0 and s1["candidates"] == 1, s1
    assert s2["committed"] == 1, s2
    assert calls and calls[0][0] == wd._AUTO_DERIVED_SESSION
    # 提交成功路径的文件审计（derived_auto_committed）仍落盘
    assert any(a.get("verdict") == "derived_auto_committed" for a in _read_audit(git_repo))
    # 候选清空、状态持久化
    state = json.loads(
        (git_repo / ".runtime" / "drift_watchdog" / "state.json").read_text(encoding="utf-8")
    )
    assert state.get("derived_candidates") == {}
    assert any("log_results failed" in r.message for r in caplog.records), caplog.text


# ── R5.5：状态文件结构损坏（合法 JSON / 错误结构）──────────────────────────────


def test_r55a_struct_corrupt_state_no_crash_no_hang(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """任务指定现场：state.json = {"files": "not_a_dict"}（合法 JSON、结构错误）。

    验证 _sweep_dead_sessions / _auto_commit_derived 无异常、不进入死循环
    （watchdog 线程 + join 超时硬断言无挂起）。
    """
    state_file = _write_state(git_repo, {"files": "not_a_dict"})
    snap = _register_dead_session(git_repo, "sess-dead", ["hot.txt"])
    (git_repo / "hot.txt").write_text("stale-then-dirty\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    calls: list = []
    _install_fake_gateway(monkeypatch, calls)

    results: dict = {}
    errors: list[BaseException] = []

    def _run() -> None:
        try:
            results["sweep"] = wd._sweep_dead_sessions(git_repo)
            results["auto1"] = wd._auto_commit_derived(git_repo)
            results["auto2"] = wd._auto_commit_derived(git_repo)
        except BaseException as e:  # noqa: BLE001
            errors.append(e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=30)
    assert not t.is_alive(), "结构损坏 state 导致死锁/无限循环"
    assert not errors, f"结构损坏 state 应回退默认而非崩溃: {errors}"

    # 主流程全部完成
    assert results["sweep"]["dead_sessions"] == 1, results
    assert results["sweep"]["unstaged"] == 1, results
    assert not snap.exists()
    assert (git_repo / "hot.txt").read_text(encoding="utf-8") == "stale-then-dirty\n"
    assert results["auto2"]["committed"] == 1, results
    # 治本后语义（R5.5 修复，2026-09-03）：_load_state 结构校验在加载时把类型错乱键
    # 复位为正确空型（files/alerted/dead_swept/derived_candidates→{}）——不再保留
    # 坏值（保留坏值正是 R5.5b-e 类型混淆崩溃的根因）。
    assert json.loads(state_file.read_text(encoding="utf-8")).get("files") == {}


def test_r55b_scan_once_files_type_confusion(git_repo: Path) -> None:
    """探针：{"files": "not_a_dict"} + scan_once —— files 键是 scan_once 主消费对象。

    防御期望：结构错误回退默认基线，零异常、正常告警。
    """
    _write_state(git_repo, {"files": "not_a_dict", "alerted": {}})
    (git_repo / "hot.txt").write_text("v2-drift\n", encoding="utf-8")
    summary = wd.scan_once(git_repo, grace_seconds=0)  # 期望不抛出
    assert summary["alerted"] == 1, summary


def test_r55c_sweep_dead_swept_type_confusion(git_repo: Path) -> None:
    """探针：{"dead_swept": "not_a_dict"} + 死会话在场 —— dead_swept 是 A1 消费对象。

    防御期望：结构错误回退默认（视为无历史清扫记录），零异常完成清扫。
    """
    _write_state(git_repo, {"dead_swept": "not_a_dict"})
    _register_dead_session(git_repo, "sess-dead", ["hot.txt"])
    (git_repo / "hot.txt").write_text("stale\n", encoding="utf-8")
    _git(git_repo, "add", "hot.txt")
    summary = wd._sweep_dead_sessions(git_repo)  # 期望不抛出
    assert summary["dead_sessions"] == 1, summary


def test_r55d_auto_commit_derived_candidates_type_confusion(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """探针：{"derived_candidates": "not_a_dict"} + B 类脏文件在场 —— A2 消费对象。

    防御期望：结构错误回退默认（视为无候选），零异常完成周期。
    """
    _write_state(git_repo, {"derived_candidates": "not_a_dict"})
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"hot.txt"}, []))
    calls: list = []
    _install_fake_gateway(monkeypatch, calls)
    (git_repo / "hot.txt").write_text("regen\n", encoding="utf-8")
    summary = wd._auto_commit_derived(git_repo)  # 期望不抛出
    assert summary["candidates"] >= 0, summary


def test_r55e_scan_once_alerted_type_confusion(git_repo: Path) -> None:
    """探针：{"alerted": "not_a_dict"} + scan_once 自愈路径 —— alerted 是自愈消费对象。"""
    _write_state(git_repo, {"files": {}, "alerted": "not_a_dict"})
    summary = wd.scan_once(git_repo, grace_seconds=0)  # 期望不抛出
    assert isinstance(summary, dict)
