# [MODULE] tests.scripts.test_stash_sentinel
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] scripts.ops.stash_sentinel (absorbed 判定/迁移/fail-closed 面), pytest.MonkeyPatch, subprocess(git)
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部落 tmp_path 假 stash 仓（basetemp=.runtime/tmp/wireB_bt，48h TTL 清扫面，禁写生产 data/）；
#              absorbed 两态（独有 blob 侧/被 HEAD 吸收侧）用真 git stash 实测；fail-closed 三闸
#              （ref 已存在/ref 回读不符回滚/索引位移保 ref）逐闸实测；零删除面=drop 只发生在
#              quarantine ref 核验同 sha 之后
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_stash_sentinel.py — absorbed stash 判定+quarantine 迁移单测（st-diskp0 裁定⑤接线）。

测试组:
- test_not_absorbed_overage_alerts_only: 独有 blob 超龄 → 告警件+台账，零 drop 零 ref
- test_absorbed_overage_migrates: 被 HEAD 吸收超龄 → quarantine ref 同 sha + drop + 台账双侧 sha
- test_absorbed_but_young_noop: absorbed 未超龄 → 零动作
- test_disabled_zero_action: enabled=false → disabled 全零动作
- test_dry_run_zero_side_effect: dry-run → would_migrate 零写（无 ref/无 drop/无台账/无告警）
- test_failclosed_ref_verify_rollback: ref 回读不符 → 回滚删 ref 零 drop
- test_two_absorbed_descending: 两枚 absorbed 超龄降序迁移 + 低位 stash 编号不受扰动
- test_exit_code_mapping: exit 0/1/2 映射（monkeypatch run_once）
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ops" / "stash_sentinel.py"
_OLD_DATE = "20260101T000000+0000"  # 远超 30 天界


def _load_module(monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("stash_sentinel_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _git(repo: Path, *args: str, date: str | None = None) -> None:
    env = os.environ.copy()
    if date:
        env["GIT_COMMITTER_DATE"] = date
        env["GIT_AUTHOR_DATE"] = date
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env, text=True)


def _stash_count(repo: Path) -> int:
    r = subprocess.run(["git", "stash", "list"], cwd=repo, capture_output=True, text=True, check=True)
    return len([ln for ln in r.stdout.splitlines() if ln.strip()])


def _stash_sha(repo: Path, index: int = 0) -> str:
    r = subprocess.run(["git", "rev-parse", f"stash@{{{index}}}"], cwd=repo, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _qrefs(repo: Path) -> dict[str, str]:
    r = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/quarantine"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return {ln.split()[0]: ln.split()[1] for ln in r.stdout.splitlines() if ln.strip()}


def _write_flags(root: Path, enabled: bool = True, min_age_days: int = 30) -> None:
    flags = root / "config" / "flags.yaml"
    flags.parent.mkdir(parents=True, exist_ok=True)
    flags.write_text(
        f"flags:\n  stash_sentinel:\n    enabled: {str(enabled).lower()}\n    min_age_days: {min_age_days}\n",
        encoding="utf-8",
    )


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """假 stash 仓：c0=base 提交；flags 出厂 ON。"""
    mod = _load_module(monkeypatch)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    # 关 autocrlf：本机默认 true 时 stash 树存工作树原始字节、commit 存过滤后字节，
    # 同内容双 sha 会使 absorbed 判定恒假（生产语义=更保守方向，测试须关掉才可构造 absorbed 态）
    _git(repo, "config", "core.autocrlf", "false")
    (repo / "f.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "c0")
    _write_flags(repo)
    return {
        "mod": mod,
        "repo": repo,
        "audit": repo / ".runtime" / "audit",
        "alerts": repo / ".runtime" / "workspace_alerts",
    }


def _make_stash(repo: Path, content: str, date: str | None = None) -> str:
    (repo / "f.txt").write_text(content, encoding="utf-8")
    _git(repo, "stash", date=date)
    return _stash_sha(repo)


def test_not_absorbed_overage_alerts_only(env):
    """独有 blob 超龄：告警件+台账行，stash 原样（零 drop 零 quarantine ref）。"""
    e = env
    mod, repo = e["mod"], e["repo"]
    sha = _make_stash(repo, "change1\n", date=_OLD_DATE)
    summary, errors = mod.run_once(repo_root=repo, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert errors == [], errors
    assert summary["scanned"] == 1 and summary["alerted"] == 1 and summary["migrated"] == 0
    assert _stash_count(repo) == 1 and _stash_sha(repo) == sha, "非 absorbed 零动作"
    assert _qrefs(repo) == {}
    alert_file = Path(summary["alert_file"])
    assert alert_file.exists()
    body = json.loads(alert_file.read_text(encoding="utf-8"))
    assert body["event"] == "stash_overage_not_absorbed" and body["severity"] == "escalated"
    assert body["items"][0]["stash_sha"] == sha and body["items"][0]["unique_blobs"] == 1
    lines = (e["audit"] / mod.LEDGER_FILENAME).read_text(encoding="utf-8").strip().splitlines()
    row = json.loads(lines[-1])
    assert row["stash_sha"] == sha and row["unique_blobs"] == 1 and row["action"] == "alert_not_absorbed"


def test_absorbed_overage_migrates(env):
    """被 HEAD 吸收超龄：quarantine ref 指同 sha + stash drop + 台账双侧 sha 相等。"""
    e = env
    mod, repo = e["mod"], e["repo"]
    sha = _make_stash(repo, "change1\n", date=_OLD_DATE)
    # 吸收：同一内容落入 HEAD 历史 → stash 独有 blob 集=空
    (repo / "f.txt").write_text("change1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "absorb")
    summary, errors = mod.run_once(repo_root=repo, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert errors == [], errors
    assert summary["migrated"] == 1 and summary["alerted"] == 0
    refs = {k: v for k, v in _qrefs(repo).items() if k.startswith("refs/quarantine/stash/")}
    assert len(refs) == 1 and next(iter(refs.values())) == sha, "ref 必须指同一 stash sha"
    assert _stash_count(repo) == 0, "absorbed 迁移后 stash 条目 drop"
    row = json.loads((e["audit"] / mod.LEDGER_FILENAME).read_text(encoding="utf-8").strip().splitlines()[-1])
    assert row["stash_sha"] == row["quarantine_sha"] == sha, "台账双侧 sha"
    assert row["dropped"] is True and row["unique_blobs"] == 0


def test_absorbed_but_young_noop(env):
    """absorbed 但未超龄（min_age 调大）：只计数零动作。"""
    e = env
    mod, repo = e["mod"], e["repo"]
    sha = _make_stash(repo, "change1\n")
    (repo / "f.txt").write_text("change1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "absorb")
    summary, _ = mod.run_once(repo_root=repo, min_age_days=10**6, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert summary["young"] == 1 and summary["migrated"] == 0 and summary["alerted"] == 0
    assert _stash_count(repo) == 1 and _stash_sha(repo) == sha and _qrefs(repo) == {}
    assert not (e["audit"] / mod.LEDGER_FILENAME).exists(), "未超龄零台账"


def test_disabled_zero_action(env):
    """enabled=false（flags 覆写）：disabled 全零动作（只报扫描数）。"""
    e = env
    mod, repo = e["mod"], e["repo"]
    _write_flags(repo, enabled=False)
    _make_stash(repo, "change1\n", date=_OLD_DATE)
    summary, errors = mod.run_once(repo_root=repo, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert errors == [] and summary["action"] == "disabled" and summary["scanned"] == 1
    assert summary["migrated"] == 0 and summary["alerted"] == 0
    assert _stash_count(repo) == 1 and _qrefs(repo) == {}
    assert not (e["audit"] / mod.LEDGER_FILENAME).exists()


def test_dry_run_zero_side_effect(env):
    """dry-run：would_migrate 判定面全出，零 ref/零 drop/零台账/零告警。"""
    e = env
    mod, repo = e["mod"], e["repo"]
    sha = _make_stash(repo, "change1\n", date=_OLD_DATE)
    (repo / "f.txt").write_text("change1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "absorb")
    summary, errors = mod.run_once(repo_root=repo, dry_run=True, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert errors == [] and summary["dry_run"] is True and summary["migrated"] == 0
    assert _stash_count(repo) == 1 and _stash_sha(repo) == sha, "dry-run 零 drop"
    assert _qrefs(repo) == {}, "dry-run 零 ref"
    assert not (e["audit"] / mod.LEDGER_FILENAME).exists(), "dry-run 零台账"
    assert not e["alerts"].exists() or not any(e["alerts"].iterdir()), "dry-run 零告警"


def test_failclosed_ref_verify_rollback(env, monkeypatch):
    """fail-closed 闸②：ref 回读 ≠ stash sha → 回滚删自建 ref，零 drop，stash 原样。"""
    e = env
    mod, repo = e["mod"], e["repo"]
    sha = _make_stash(repo, "change1\n", date=_OLD_DATE)
    (repo / "f.txt").write_text("change1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "absorb")
    real = mod._rev_parse
    calls: dict[str, int] = {}

    def fake_rev_parse(root, ref):  # noqa: ANN001 — 测试替身：预检放行、回读核验伪造失配
        if ref.startswith("refs/quarantine/"):
            calls[ref] = calls.get(ref, 0) + 1
            return None if calls[ref] == 1 else "0" * 40
        return real(root, ref)

    monkeypatch.setattr(mod, "_rev_parse", fake_rev_parse)
    summary, errors = mod.run_once(repo_root=repo, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert summary["migrated"] == 0
    assert any("failed_ref_verify" in x or "零 drop" in x for x in errors), errors
    assert _stash_count(repo) == 1 and _stash_sha(repo) == sha, "核验失败零 drop"
    assert not [k for k in _qrefs(repo) if k.startswith("refs/quarantine/stash/")], "自建 ref 已回滚删除"


def test_two_absorbed_descending(env):
    """两枚 absorbed 超龄降序迁移：ref 双枚各自同 sha；年轻非 absorbed 低位编号不受扰动。"""
    e = env
    mod, repo = e["mod"], e["repo"]
    _make_stash(repo, "aaa\n", date=_OLD_DATE)  # → 将成为 stash@{1}
    sha_a = _stash_sha(repo)
    _make_stash(repo, "bbb\n", date=_OLD_DATE)  # → 将成为 stash@{0}，随后被新 stash 顶到 1
    sha_b = _stash_sha(repo)
    # 吸收两枚 blob 进 HEAD 历史
    (repo / "f.txt").write_text("aaa\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "absorb-a")
    (repo / "f.txt").write_text("bbb\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "absorb-b")
    # 年轻非 absorbed 顶到 stash@{0}
    sha_c = _make_stash(repo, "zzz\n")
    assert _stash_sha(repo, 1) == sha_b and _stash_sha(repo, 2) == sha_a
    summary, errors = mod.run_once(repo_root=repo, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert errors == [], errors
    assert summary["migrated"] == 2 and summary["scanned"] == 3 and summary["young"] == 1
    refs = {k: v for k, v in _qrefs(repo).items() if k.startswith("refs/quarantine/stash/")}
    assert set(refs.values()) == {sha_a, sha_b}, "两枚 ref 各指原 sha"
    assert _stash_count(repo) == 1 and _stash_sha(repo, 0) == sha_c, "年轻枚仍在 stash@{0}"


def test_exit_code_mapping(env, monkeypatch):
    """exit 映射：0=完成零告警｜1=有告警｜2=设施故障。"""
    e = env
    mod = e["mod"]

    def _fake(**kw):  # noqa: ANN003 — 测试替身透传
        base = {
            "action": "patrolled",
            "enabled": True,
            "min_age_days": 30.0,
            "scanned": 0,
            "young": 0,
            "migrated": 0,
            "alerted": 0,
            "errors": [],
            "dry_run": False,
            "alert_file": None,
        }
        kind = kw.get("note") or "ok"
        if kind == "alert":
            base["alerted"] = 1
        if kind == "err":
            base["action"] = "error"
        return base, (["boom"] if kind == "err" else [])

    monkeypatch.setattr(mod, "run_once", _fake)
    assert mod.main(["--once", "--note", "ok"]) == 0
    assert mod.main(["--once", "--note", "alert"]) == 1
    assert mod.main(["--once", "--note", "err"]) == 2
