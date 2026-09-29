# [MODULE] tests.scripts.test_session_worktree_archive
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] scripts.session_worktree (lane-archive), zephyr SessionRegistry
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 全部 git 操作在 tmp 仓；活跃会话硬拒无逃生；真 ahead 分支禁 -D（保留+台账）；dry-run 默认零副作用
# [MODIFY-GUARD]
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_session_worktree_archive.py — lane-archive 子命令单测（RB-4 车道生命周期治本）。

真源: docs/_working/root_cure_campaign/RB4_lane_lifecycle.md §2
测试组（tmp 仓三态 + 行为契约）:
- test_archive_shell_lane_zero_loss_execute: 纯壳（ahead=0 干净）→ remove+prune+branch -d 全过
- test_archive_real_ahead_keeps_branch_and_ledger: 真 ahead → worktree 删、分支保留（禁 -D）、白名单台账落盘
- test_archive_active_session_hard_reject: 活跃会话（registry 命中）→ 硬拒，车道与分支原样
- test_archive_dry_run_default_noop: 默认 dry-run → 只打印计划，worktree/脏文件原样、零 patch
- test_archive_dirty_lane_rescue_and_evidence: 脏车道 → patch 存证 + ？？入 rescue+mapping + 清理
- test_archive_resolves_by_branch_name: 分支名反查 porcelain 注册表
- test_archive_detached_lane: detached 车道（无分支）→ 清 worktree，跳过分支处置
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# scripts/ 非包目录，按路径加载被测模块（对标 tests/scripts/test_session_worktree_env.py 惯例）
_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "session_worktree.py"


def _load_module(repo: Path, monkeypatch: pytest.MonkeyPatch):
    """加载 session_worktree 并把 REPO_ROOT/WORKTREE_ROOT 重定向到给定临时仓。"""
    spec = importlib.util.spec_from_file_location("session_worktree_archive_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "REPO_ROOT", repo)
    monkeypatch.setattr(mod, "WORKTREE_ROOT", repo / ".worktrees")
    return mod


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


@pytest.fixture()
def tmp_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """独立临时 git 仓（基线分支名对齐生产约定 dev）+ 模块 REPO_ROOT 重定向。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    assert _git(repo, "init").returncode == 0
    _git(repo, "config", "user.email", "test@zephyr.local")
    _git(repo, "config", "user.name", "Zephyr Test")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "init")
    _git(repo, "branch", "-m", "dev")
    mod = _load_module(repo, monkeypatch)
    return mod, repo


def _make_lane(repo: Path, sid: str, *, commit: bool = False, dirty_file: bool = False) -> Path:
    """在 tmp 仓创建测试车道（.worktrees/<sid> + session/<sid> 分支）。"""
    wt = repo / ".worktrees" / sid
    r = _git(repo, "worktree", "add", str(wt), "-b", f"session/{sid}")
    assert r.returncode == 0, f"worktree add 失败: {r.stderr}"
    if commit:
        (wt / "ahead.txt").write_text("ahead content\n", encoding="utf-8")
        r = subprocess.run(["git", "add", "-A"], cwd=wt, capture_output=True, text=True)
        assert r.returncode == 0
        r = subprocess.run(["git", "commit", "-m", f"lane {sid} unique work"], cwd=wt, capture_output=True, text=True)
        assert r.returncode == 0, f"worktree commit 失败: {r.stderr}"
    if dirty_file:
        (wt / "untracked.txt").write_text("dirty rescue me\n", encoding="utf-8")
    return wt


def _ns(mod, targets: list[str], *, execute: bool = False, **kw) -> argparse.Namespace:
    """构造 cmd_archive 的 argparse.Namespace（未传字段走 getattr 默认）。"""
    return argparse.Namespace(
        targets=targets,
        execute=execute,
        batch_file=kw.get("batch_file"),
        all=kw.get("all", False),
        skip_rescue=kw.get("skip_rescue", False),
        base=kw.get("base", "dev"),
        command="archive",
        func=mod.cmd_archive,
    )


def _branch_exists(repo: Path, branch: str) -> bool:
    return bool(_git(repo, "branch", "--list", branch).stdout.strip())


def test_archive_shell_lane_zero_loss_execute(tmp_repo):
    """纯壳（ahead=0 且干净）：execute → worktree remove+prune+branch -d 全过。"""
    mod, repo = tmp_repo
    sid = "st-shell"
    wt = _make_lane(repo, sid)
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "纯壳归档应成功"
    assert sid not in _git(repo, "worktree", "list").stdout, "worktree 仍注册"
    assert not _branch_exists(repo, f"session/{sid}"), "壳分支应被 -d 删除"
    assert not wt.exists(), "worktree 目录应消失"


def test_archive_real_ahead_keeps_branch_and_ledger(tmp_repo):
    """真 ahead：worktree 删、分支保留（禁 -D）、白名单台账落盘。"""
    mod, repo = tmp_repo
    sid = "st-ahead"
    _make_lane(repo, sid, commit=True)
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "真 ahead 车道归档主流程应成功"
    assert sid not in _git(repo, "worktree", "list").stdout, "worktree 仍注册"
    assert _branch_exists(repo, f"session/{sid}"), "真 ahead 分支必须保留（archive 路径禁 -D）"
    ledger = repo / ".runtime" / "quarantine" / "ahead_branches.log"
    assert ledger.exists(), "白名单台账未落盘"
    text = ledger.read_text(encoding="utf-8")
    assert sid in text and f"session/{sid}" in text, f"台账未含 sid/分支: {text!r}"
    assert "ahead=" in text, f"台账未含 ahead 数: {text!r}"


def test_archive_active_session_hard_reject(tmp_repo):
    """活跃会话（registry list_active 命中）：execute 硬拒，车道与分支原样，无逃生。"""
    mod, repo = tmp_repo
    sid = "st-active"
    wt = _make_lane(repo, sid, commit=True, dirty_file=True)
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    SessionRegistry(repo).register(sid, pid=os.getpid())  # 当前进程 pid 存活 → 判活
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc != 0, "活跃会话必须硬拒（非零退出）"
    assert sid in _git(repo, "worktree", "list").stdout, "活跃 worktree 被动了！"
    assert wt.exists(), "活跃 worktree 目录被动了！"
    assert _branch_exists(repo, f"session/{sid}"), "活跃分支被动了！"
    assert (wt / "untracked.txt").exists(), "活跃车道脏文件被动了！"


def test_archive_dry_run_default_noop(tmp_repo):
    """默认 dry-run：只打印处置计划，worktree/脏文件原样、零 patch 零台账。"""
    mod, repo = tmp_repo
    sid = "st-dry"
    wt = _make_lane(repo, sid, dirty_file=True)
    rc = mod.cmd_archive(_ns(mod, [sid]))  # 不传 --execute
    assert rc == 0
    assert sid in _git(repo, "worktree", "list").stdout, "dry-run 动了 worktree 注册"
    assert (wt / "untracked.txt").exists(), "dry-run 动了脏文件"
    assert _branch_exists(repo, f"session/{sid}"), "dry-run 动了分支"
    q_dir = repo / ".runtime" / "quarantine"
    assert not q_dir.exists() or not list(q_dir.glob("*.patch")), "dry-run 生成了 patch"


def test_archive_dirty_lane_rescue_and_evidence(tmp_repo):
    """脏车道：patch 存证（含 tracked 修改）+ ？？入 rescue+mapping + 车道/壳分支清理。"""
    mod, repo = tmp_repo
    sid = "st-dirty"
    wt = _make_lane(repo, sid, dirty_file=True)
    (wt / "base.txt").write_text("modified tracked content\n", encoding="utf-8")
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "脏车道归档应成功"
    patches = list((repo / ".runtime" / "quarantine").glob(f"{sid}-retire-*.patch"))
    assert patches, "patch 存证未生成"
    assert "modified tracked content" in patches[0].read_text(encoding="utf-8"), "patch 未含 tracked 修改"
    rescue_dir = repo / ".runtime" / "tmp" / "rescue" / sid
    assert (rescue_dir / "untracked.txt").exists(), "？？文件未入 rescue"
    assert (rescue_dir / "untracked.txt").read_text(encoding="utf-8") == "dirty rescue me\n", "rescue 内容漂移"
    mapping = json.loads((rescue_dir / "mapping.json").read_text(encoding="utf-8"))
    assert "untracked.txt" in mapping["rescued"], f"mapping.json 缺条目: {mapping}"
    assert sid not in _git(repo, "worktree", "list").stdout
    assert not _branch_exists(repo, f"session/{sid}"), "ahead=0 壳分支应被 -d 删除"


def test_archive_resolves_by_branch_name(tmp_repo):
    """分支名反查 porcelain 注册表（输入=分支名而非 sid/path）。"""
    mod, repo = tmp_repo
    sid = "st-bybranch"
    _make_lane(repo, sid, commit=True)
    rc = mod.cmd_archive(_ns(mod, [f"session/{sid}"], execute=True))
    assert rc == 0
    assert sid not in _git(repo, "worktree", "list").stdout
    assert _branch_exists(repo, f"session/{sid}"), "真 ahead 分支应保留（禁 -D）"


def test_archive_detached_lane(tmp_repo):
    """detached 车道（无分支）：ahead 记 0，清 worktree、跳过分支处置。"""
    mod, repo = tmp_repo
    name = "dt-lane"
    wt = repo / ".aidrafts" / name
    r = _git(repo, "worktree", "add", "--detach", str(wt))
    assert r.returncode == 0, f"detached worktree add 失败: {r.stderr}"
    rc = mod.cmd_archive(_ns(mod, [name], execute=True))
    assert rc == 0, "detached 车道归档应成功"
    assert name not in _git(repo, "worktree", "list").stdout
    assert not wt.exists()
