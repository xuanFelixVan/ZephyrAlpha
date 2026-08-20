# [BLUEPRINT] MOD-GOV_COMMIT_GATE_REGISTRY | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.governance.rule_bridge.test_worktree_drift_watchdog
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
# [TTL] permanent
"""worktree_drift_watchdog 单元测试（#ARCH-WORKTREE-WRITE-INTEGRITY-001 P0-1/P0-2）。

覆盖：漂移检出+快照+告警落库+归因审计 / claimed 豁免 / grace 宽限窗 / dedup /
自愈 clean / 同内容重写不告警（CRLF 幻影免疫）/ reconciler ensure-daemon 幂等。
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
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


def _read_log_actions(repo: Path) -> list[tuple]:
    db = repo / "data" / "databases" / "governance.db"
    if not db.exists():
        return []
    conn = sqlite3.connect(str(db))
    try:
        return conn.execute("SELECT gate_id, action, detail FROM reconcile_execution_log").fetchall()
    finally:
        conn.close()


def test_drift_alert_snapshot_audit(git_repo: Path) -> None:
    """未登记写入方漂移 → 告警 + 快照 + 归因审计（前后 hash）。"""
    (git_repo / "hot.txt").write_text("v2-stale-overwrite\n", encoding="utf-8")
    summary = wd.scan_once(git_repo, grace_seconds=0)
    assert summary["alerted"] == 1, summary
    assert summary["drifted"] == 1

    # 快照存证（内容=漂移后的磁盘内容）
    snaps = list((git_repo / ".runtime" / "quarantine").glob("drift_*/hot.txt"))
    assert len(snaps) == 1
    assert snaps[0].read_text(encoding="utf-8") == "v2-stale-overwrite\n"

    # 归因审计含前后 hash + verdict
    audit = _read_audit(git_repo)
    alerted = [r for r in audit if r.get("verdict") == "alerted"]
    assert len(alerted) == 1
    assert alerted[0]["work_hash"] and alerted[0]["head_blob"]
    assert "prev_work_hash" in alerted[0]

    # 告警落库（critical_warn → banner 链路）
    rows = _read_log_actions(git_repo)
    assert any(r[0] == wd.GATE_ID and r[1] == "critical_warn" for r in rows)


def test_dedup_same_signature(git_repo: Path) -> None:
    """同一漂移签名第二轮扫描不重复告警。"""
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    s1 = wd.scan_once(git_repo, grace_seconds=0)
    s2 = wd.scan_once(git_repo, grace_seconds=0)
    assert s1["alerted"] == 1
    assert s2["alerted"] == 0 and s2["dedup_skipped"] == 1
    rows = _read_log_actions(git_repo)
    assert sum(1 for r in rows if r[1] == "critical_warn") == 1


def test_self_heal_on_resolve(git_repo: Path) -> None:
    """漂移消解（内容恢复）→ 自动写 clean 记录消音。"""
    target = git_repo / "hot.txt"
    target.write_text("v2\n", encoding="utf-8")
    wd.scan_once(git_repo, grace_seconds=0)
    target.write_text("v1\n", encoding="utf-8")  # 恢复 HEAD 内容
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["healed"] == 1, s
    rows = _read_log_actions(git_repo)
    assert any(r[1] == "clean" for r in rows)
    # 状态清空：再扫描无动作
    s3 = wd.scan_once(git_repo, grace_seconds=0)
    assert s3["alerted"] == 0 and s3["healed"] == 0


def test_claimed_file_exempt(git_repo: Path, monkeypatch) -> None:
    """文件在活跃 session 的 claim 快照中 → claimed 豁免不告警。"""
    monkeypatch.setattr(
        wd,
        "_active_sessions_and_claims",
        lambda root: (["sess-x"], {"hot.txt": "sess-x"}),
    )
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["claimed"] == 1 and s["alerted"] == 0
    audit = _read_audit(git_repo)
    assert any(r.get("verdict") == "claimed" for r in audit)


def test_grace_window_suppresses(git_repo: Path) -> None:
    """commit 后宽限窗内（reconciler 派生写）→ 记录但不告警。"""
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    s = wd.scan_once(git_repo, grace_seconds=99999)  # 强制在宽限窗内
    assert s["grace_suppressed"] == 1 and s["alerted"] == 0
    audit = _read_audit(git_repo)
    assert any(r.get("verdict") == "grace_suppressed" for r in audit)


def test_identical_rewrite_no_alert(git_repo: Path) -> None:
    """同内容重写（幻影类）→ git 语义比对无差异，零告警。"""
    (git_repo / "hot.txt").write_text("v1\n", encoding="utf-8")  # 内容同 HEAD
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["alerted"] == 0


def test_reconciler_ensure_daemon_idempotent(git_repo: Path, monkeypatch) -> None:
    """reconciler：ensure_daemon 幂等 + 返回合法 ReconcileResult。"""
    spawned: list[str] = []
    monkeypatch.setattr(
        wd,
        "ensure_daemon",
        lambda root, interval=60: spawned.append(str(root)) or True,
    )

    class _GW:
        project_root = git_repo

    spec = wd.make_worktree_drift_watchdog_reconciler(_GW())
    assert spec.gate_id == wd.GATE_ID
    assert spec.file_ops == frozenset({"read", "write"})
    assert spec.trigger(["a.py"]) is True
    assert spec.trigger([]) is False
    result = spec.reconcile(["a.py"], "sess-t")
    assert result.action in {"clean", "warn"}
    assert len(spawned) == 1  # ensure_daemon 被调一次


# ── B5 治本（2026-08-19）：merge 存续期豁免 + reflog 宽限锚点扩展 ─────────────


def test_merge_head_suppresses_alert(git_repo: Path) -> None:
    """MERGE_HEAD 存续期 drift → merge_suppressed（audit 照记），零 critical_warn。"""
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(git_repo),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (git_repo / ".git" / "MERGE_HEAD").write_bytes((head + "\n").encode("ascii"))
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["alerted"] == 0 and s["merge_suppressed"] == 1
    audit = _read_audit(git_repo)
    assert any(r.get("verdict") == "merge_suppressed" for r in audit)
    actions = _read_log_actions(git_repo)
    assert not any(a[1] == "critical_warn" for a in actions), f"merge 存续期不得产生 critical_warn: {actions}"


def test_merge_head_cleared_resumes_watch(git_repo: Path) -> None:
    """MERGE_HEAD 消解后新 drift → 恢复 alert（豁免不卡死）。"""
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(git_repo),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    mh = git_repo / ".git" / "MERGE_HEAD"
    mh.write_bytes((head + "\n").encode("ascii"))
    s1 = wd.scan_once(git_repo, grace_seconds=0)
    assert s1["merge_suppressed"] == 1
    mh.unlink()
    # 内容再变一次（新签名，破 dedup）→ merge 豁免消失 → 超窗 → alert
    (git_repo / "hot.txt").write_text("v3\n", encoding="utf-8")
    s2 = wd.scan_once(git_repo, grace_seconds=0)
    assert s2["alerted"] == 1 and s2["merge_suppressed"] == 0


def test_reflog_anchor_extends_grace(git_repo: Path, monkeypatch) -> None:
    """commit 锚点超窗但 HEAD/stash reflog 新近活跃（stash 周期回写）→ grace_suppressed。"""
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    real_git = wd._git
    now = wd.now_utc().timestamp()

    def fake_git(root, args):
        if args[:2] == ["log", "-1"]:  # last commit 两小时前（超窗）
            return 0, str(now - 7200)
        if args[:1] == ["reflog"] and "stash" in args:  # stash 刚活动过
            return 0, str(now - 10)
        if args[:1] == ["reflog"]:
            return 0, str(now - 7200)
        return real_git(root, args)

    monkeypatch.setattr(wd, "_git", fake_git)
    s = wd.scan_once(git_repo, grace_seconds=600)
    assert s["alerted"] == 0 and s["grace_suppressed"] == 1, f"stash reflog 新近活跃应延 grace: {s}"


def test_grace_expired_still_alerts(git_repo: Path, monkeypatch) -> None:
    """全部锚点超窗 + 真 drift → 仍 alert（安全网回归，豁免不失效）。"""
    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    real_git = wd._git
    now = wd.now_utc().timestamp()

    def fake_git(root, args):
        if args[:2] == ["log", "-1"]:
            return 0, str(now - 7200)
        if args[:1] == ["reflog"] and "stash" in args:
            return 0, ""  # 无 stash
        if args[:1] == ["reflog"]:
            return 0, str(now - 7200)
        return real_git(root, args)

    monkeypatch.setattr(wd, "_git", fake_git)
    s = wd.scan_once(git_repo, grace_seconds=600)
    assert s["alerted"] == 1, f"全锚点超窗真漂移必须 alert: {s}"
