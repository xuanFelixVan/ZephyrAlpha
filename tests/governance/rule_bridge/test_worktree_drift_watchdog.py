# [BLUEPRINT] MOD-GOV_COMMIT_GATE_REGISTRY | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-GOV_COMMIT_GATE_REGISTRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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


# ── #ARCH-264 裁定落地（2026-08-26）：O6 observe-only / O3-P0 热文件快扫 / O4 quarantine 自管 ──


def test_observe_only_audits_without_alert(git_repo: Path) -> None:
    """O6 唯一告警写者：observe-only 只审计不告警、不推进告警状态。

    网关 post-commit 即时扫降级为观察员（防 daemon/网关双扫描竞态重复告警）；
    observe-only 不得推进 files_state——否则 daemon 侧 dedup 会把真漂移静默吞掉。
    """
    (git_repo / "hot.txt").write_text("v2-stale\n", encoding="utf-8")
    summary = wd.scan_once(git_repo, grace_seconds=0, alert_enabled=False)
    assert summary["alerted"] == 0
    assert summary["observed"] == 1
    # 归因审计照记（verdict=observed，含 hash）
    audit = _read_audit(git_repo)
    observed = [r for r in audit if r.get("verdict") == "observed"]
    assert len(observed) == 1 and observed[0]["work_hash"]
    # 无 critical_warn 落库
    rows = _read_log_actions(git_repo)
    assert not any(r[1] == "critical_warn" for r in rows)
    # 告警状态未推进：daemon（默认 alert_enabled=True）扫同一漂移仍应告警且仅一次
    s2 = wd.scan_once(git_repo, grace_seconds=0)
    assert s2["alerted"] == 1
    rows2 = _read_log_actions(git_repo)
    assert sum(1 for r in rows2 if r[1] == "critical_warn") == 1


def test_hot_only_scans_only_hot_files(git_repo: Path) -> None:
    """O3-P0 热文件快扫：hot_only 只覆盖 DEFAULT_HOT_FILES ∪ design_memos/ 前缀。"""
    # 非热文件漂移
    (git_repo / "plain.txt").write_text("a\n", encoding="utf-8")
    _git(git_repo, "add", "plain.txt")
    _git(git_repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "add plain")
    (git_repo / "plain.txt").write_text("b\n", encoding="utf-8")
    # design_memos 前缀热文件漂移
    memo = (
        git_repo / "docs" / "02_enterprise_architecture" / "07_trading_decision_architecture" / "design_memos" / "m.md"
    )
    memo.parent.mkdir(parents=True, exist_ok=True)
    memo.write_text("v1\n", encoding="utf-8")
    _git(git_repo, "add", ".")
    _git(git_repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "add memo")
    memo.write_text("v2\n", encoding="utf-8")

    s = wd.scan_once(git_repo, grace_seconds=0, hot_only=True)
    assert s["alerted"] == 1, s
    audit = _read_audit(git_repo)
    alerted_files = [r.get("file", "") for r in audit if r.get("verdict") == "alerted"]
    assert alerted_files and all("design_memos" in f for f in alerted_files)


def test_quarantine_retention_sweep(git_repo: Path) -> None:
    """O4 quarantine 自管：超 retention 的 drift_* 目录被清理并逐条留审计。"""
    q = git_repo / ".runtime" / "quarantine"
    old = q / "drift_20200101T000000"
    old.mkdir(parents=True)
    (old / "x.txt").write_text("old\n", encoding="utf-8")
    new = q / "drift_29990101T000000"
    new.mkdir()
    (new / "y.txt").write_text("new\n", encoding="utf-8")

    swept = wd._sweep_quarantine(git_repo, retention_days=30)
    assert swept["removed"] == 1 and swept["kept"] == 1, swept
    assert not old.exists() and new.exists()
    audit = _read_audit(git_repo)
    assert any(r.get("verdict") == "quarantine_retention_sweep" for r in audit)


def test_quarantine_tamper_detected(git_repo: Path) -> None:
    """O4 带外删除可观测：非 watchdog 删除已登记快照目录 → quarantine_tamper 审计。"""
    import shutil

    (git_repo / "hot.txt").write_text("v2\n", encoding="utf-8")
    wd.scan_once(git_repo, grace_seconds=0)  # 产生快照并登记 known_quarantine
    snaps = [p for p in (git_repo / ".runtime" / "quarantine").glob("drift_*") if p.is_dir()]
    assert snaps
    shutil.rmtree(snaps[0])  # 模拟带外裸删除
    wd.scan_once(git_repo, grace_seconds=0)
    audit = _read_audit(git_repo)
    assert any(r.get("verdict") == "quarantine_tamper" for r in audit)


# ── #ARCH-304 裁定落地（2026-08-31）：单活跃会话 auto-claim 替代告警处置 ──────


def test_auto_claim_single_active_session(git_repo: Path) -> None:
    """#ARCH-304：恰好 1 个活跃注册会话 → auto-claim 替代告警，零 critical_warn。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    reg = SessionRegistry(git_repo)
    reg.register("sess-ai")
    (git_repo / "hot.txt").write_text("v2-unclaimed\n", encoding="utf-8")
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["auto_claimed"] == 1 and s["alerted"] == 0, s

    # 零告警落库
    rows = _read_log_actions(git_repo)
    assert not any(r[1] == "critical_warn" for r in rows)

    # 审计留痕：auto-claim 事件（文件/会话/时间/漂移 hash）
    audit = _read_audit(git_repo)
    ac = [r for r in audit if r.get("verdict") == "auto_claimed"]
    assert len(ac) == 1
    assert ac[0]["file"] == "hot.txt"
    assert ac[0]["auto_claim_session"] == "sess-ai"
    assert ac[0]["work_hash"] and ac[0]["ts"]

    # 既有 claim 机制生效：registry 持有 + 快照持久化 + adopt 审计
    info = reg.get_session("sess-ai")
    assert info is not None and any("hot.txt" in f for f in info.held_files)
    assert (git_repo / ".runtime" / "claim_snapshots" / "sess-ai.json").exists()
    assert (git_repo / ".runtime" / "claim_snapshots" / "sess-ai_adopted.jsonl").exists()

    # 二轮扫描：同签名 dedup，仍零告警零重复 claim
    s2 = wd.scan_once(git_repo, grace_seconds=0)
    assert s2["alerted"] == 0 and s2["auto_claimed"] == 0

    # 进一步漂移（新签名）：已被认领 → claimed 豁免，不告警不再 auto-claim
    (git_repo / "hot.txt").write_text("v3-more-work\n", encoding="utf-8")
    s3 = wd.scan_once(git_repo, grace_seconds=0)
    assert s3["alerted"] == 0 and s3["auto_claimed"] == 0 and s3["claimed"] == 1, s3


def test_multi_active_sessions_keep_alert(git_repo: Path) -> None:
    """#ARCH-304 安全闸：>1 活跃会话（归属歧义）→ 维持原快照+告警，零 auto-claim。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    reg = SessionRegistry(git_repo)
    reg.register("sess-a")
    reg.register("sess-b")
    (git_repo / "hot.txt").write_text("v2-ambiguous\n", encoding="utf-8")
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["alerted"] == 1 and s["auto_claimed"] == 0, s
    rows = _read_log_actions(git_repo)
    assert any(r[0] == wd.GATE_ID and r[1] == "critical_warn" for r in rows)
    # 快照存证照常
    snaps = list((git_repo / ".runtime" / "quarantine").glob("drift_*/hot.txt"))
    assert len(snaps) == 1
    # 歧义场景不得擅自归属：两 session 均未被动持有该文件
    for sid in ("sess-a", "sess-b"):
        info = reg.get_session(sid)
        assert info is not None and not any("hot.txt" in f for f in info.held_files)


def test_zero_sessions_keep_alert(git_repo: Path) -> None:
    """#ARCH-304 安全闸：0 活跃会话 → 维持原告警路径（与裁定前行为一致）。"""
    (git_repo / "hot.txt").write_text("v2-orphan\n", encoding="utf-8")
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["alerted"] == 1 and s["auto_claimed"] == 0, s
    rows = _read_log_actions(git_repo)
    assert any(r[1] == "critical_warn" for r in rows)


def test_auto_claim_failure_falls_back_to_alert(git_repo: Path, monkeypatch) -> None:
    """#ARCH-304 fail-closed：单会话但 claim 失败（冲突/异常）→ 回落原告警路径不放松。"""
    monkeypatch.setattr(wd, "_active_sessions_and_claims", lambda root: (["sess-x"], {}))
    monkeypatch.setattr(wd, "_auto_claim_single_session", lambda root, rel, sid: False)
    (git_repo / "hot.txt").write_text("v2-claimfail\n", encoding="utf-8")
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["alerted"] == 1 and s["auto_claimed"] == 0, s
    rows = _read_log_actions(git_repo)
    assert any(r[1] == "critical_warn" for r in rows)


def test_claimed_gateway_snapshot_format_exempt(git_repo: Path) -> None:
    """claim 快照读取兼容网关 save_session_snapshot 格式（{"snapshots": {abs: baseline}}）。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    SessionRegistry(git_repo).register("sess-x")
    snap_dir = git_repo / ".runtime" / "claim_snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    (snap_dir / "sess-x.json").write_text(
        json.dumps(
            {
                "session_id": "sess-x",
                "snapshots": {str((git_repo / "hot.txt").resolve()): ""},
                "claim_head": "",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (git_repo / "hot.txt").write_text("v2-claimed-wip\n", encoding="utf-8")
    s = wd.scan_once(git_repo, grace_seconds=0)
    assert s["claimed"] == 1 and s["alerted"] == 0 and s["auto_claimed"] == 0, s
