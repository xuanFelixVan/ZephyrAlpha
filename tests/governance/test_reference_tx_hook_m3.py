# [TTL] permanent
"""M3 钩链瘦身回归钉（st-commitspeed-tbl-20260924 T6，B0_3 红测 R3a 的永久化）。

钉住三件不可回退的事：
1. **forward 路径 git 子进程数 ≤1**（PATH shim 计数法）。原 5 调用版（rev-parse 根发现 +
   merge-base×2 + log %P + log %B）在此断言下必红——本钉防"取数扇出悄悄长回来"。
   计数口径：merge-commit 的 forward 移动（2 parents 早退，免造注册表），合并调用计 1，
   早退后零额外 git 调用。
2. **rewind 静默放行**：old..new 空输出 = 真回退语义（单调用取数的核心等价推导）。
3. **不可读 OID fail-closed**：取数失败不得变成放行（rc=1 阻断）。

根发现走查（零子进程）在 scratch 仓与 worktree 两形态下都被本测试隐式覆盖：
测试以 cwd=scratch 仓裸调钩子文件，走查必须命中 scratch/.git 才能通过 case 3 的
报告落点断言（reports 写进 scratch 而非真仓 .runtime = 隔离即证据）。
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / "scripts" / "governance" / "git_hooks" / "reference_transaction_guard.sh"
ZERO = "0" * 40


def _shim_git(tmp_path: Path) -> tuple[Path, dict]:
    """PATH shim：把 git 调用计数后转投真 git（真路径由测试侧解析，勿硬编码）。"""
    real_git = shutil.which("git")
    assert real_git, "git 不在 PATH"
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    counter = shim_dir / "count.txt"
    counter.write_text("", encoding="utf-8")
    (shim_dir / "git").write_text(
        f'#!/bin/sh\necho "$@" >> "{counter.as_posix()}"\nexec "{Path(real_git).as_posix()}" "$@"\n',
        encoding="utf-8",
        newline="\n",
    )
    import os

    env = dict(os.environ)
    env["PATH"] = shim_dir.as_posix() + os.pathsep + env["PATH"]
    return counter, env


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def _scratch_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "hookrepo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main", ".")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "f.txt").write_text("a", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "c1")
    c1 = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "-b", "side")
    (repo / "f.txt").write_text("b", encoding="utf-8")
    _git(repo, "commit", "-qam", "c2")
    _git(repo, "checkout", "-q", "-b", "dev", "main")
    _git(repo, "merge", "-q", "--no-ff", "-m", "merge side", "side")
    merge = _git(repo, "rev-parse", "HEAD")
    return repo, c1, merge  # c1=merge 的第一父


def _run_hook(repo: Path, payload: str, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(HOOK), "prepared"],
        input=payload,
        capture_output=True,
        text=True,
        cwd=str(repo),
        env=env,
    )


def test_forward_path_single_git_call(tmp_path):
    repo, parent, merge = _scratch_repo(tmp_path)
    counter, env = _shim_git(tmp_path)
    p = _run_hook(repo, f"{parent} {merge} refs/heads/dev\n", env)
    calls = [l for l in counter.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert p.returncode == 0, p.stderr
    assert len(calls) <= 1, f"forward 路径 git 子进程数 {len(calls)}（M3 目标 ≤1）：{calls}"


def test_rewind_silently_skipped(tmp_path):
    repo, parent, merge = _scratch_repo(tmp_path)
    counter, env = _shim_git(tmp_path)
    p = _run_hook(repo, f"{merge} {parent} refs/heads/dev\n", env)  # new 是 old 祖先=真回退
    assert p.returncode == 0
    calls = [l for l in counter.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(calls) <= 1
    assert (
        not list((repo / ".runtime" / "reconcile_reports").glob("*.json"))
        if (repo / ".runtime" / "reconcile_reports").exists()
        else True
    )


def test_unreadable_oid_fails_closed(tmp_path):
    repo, parent, merge = _scratch_repo(tmp_path)
    _counter, env = _shim_git(tmp_path)
    bad = "f" * 40
    p = _run_hook(repo, f"{bad} {merge} refs/heads/dev\n", env)
    assert p.returncode == 1, "不可读 OID 必须阻断（fail-closed），不得静默放行"
    reports = list((repo / ".runtime" / "reconcile_reports").glob("reference_transaction_guard_*.json"))
    assert reports, "阻断必须落审计报告（且经根发现走查落在 scratch 仓=隔离证据）"


def test_deletion_and_non_dev_skip_without_git(tmp_path):
    repo, parent, merge = _scratch_repo(tmp_path)
    counter, env = _shim_git(tmp_path)
    p1 = _run_hook(repo, f"{parent} {ZERO} refs/heads/dev\n", env)
    p2 = _run_hook(repo, f"{parent} {merge} refs/heads/session/x\n", env)
    calls = [l for l in counter.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert (p1.returncode, p2.returncode) == (0, 0)
    assert calls == [], "deletion/非 dev ref 在零 git 调用内完成早退"
