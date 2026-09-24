# [TTL] permanent
"""T7/B2 缓存键隔离判别测试（st-commitspeed-tbl-20260924）。

钉住两件不可回退的事：
- **键隔离**：own 文件不变时，他人向共享 index 暂存/HEAD 前进不得作废我的缓存
  （现码红：key 含 write-tree 全树 sha+head_sha，任何人任何活动=全失效 ⇒ 24h 仅
  87 命中的结构性根因）。
- **内容敏感**：own 文件 staged 内容变化必须立即 miss（缓存投毒的逆命题）。
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.gov_enforcement.rule_bridge import gate_cache_preflight as gcp


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    def git(*a: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, errors="replace")
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()
    git("init", "-q", "--initial-branch=main")
    git("config", "core.autocrlf", "false")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (repo / "own.py").write_text("X = 1\n", encoding="utf-8")
    (repo / "config").mkdir()
    (repo / "config" / "flags.yaml").write_text("flags: {}\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "init")
    return repo


def _gateway(repo: Path) -> SimpleNamespace:
    def run_git(argv: list[str], cwd: str | None = None):
        return subprocess.run(argv, cwd=str(repo), capture_output=True, text=True)

    return SimpleNamespace(run_git=run_git, project_root=str(repo))


def _stage(repo: Path, name: str, text: str) -> None:
    (repo / name).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", name], check=True)


def test_cache_survives_foreign_staging(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """他人暂存活动（index 全树 sha 变化）不得作废 own 文件的缓存。"""
    gw = _gateway(git_repo)
    monkeypatch.setattr(gcp, "compute_fingerprint", lambda g: gcp.Fingerprint(
        staged_tree_sha=subprocess.run(["git", "-C", str(git_repo), "write-tree"], capture_output=True, text=True).stdout.strip(),
        head_sha="h0",
        flags_mtime=1.0,
    ))
    cache = gcp.GateResultCache(gw, ["own.py"])
    cache.store("ENCODING-SAFETY", "scope-x", "detail-v1")
    assert cache.lookup("ENCODING-SAFETY", "scope-x") == "detail-v1"

    # 他人暂存一个与我无关的文件（write-tree 全树 sha 必变）
    _stage(git_repo, "foreign_other.py", "Y = 2\n")

    cache2 = gcp.GateResultCache(gw, ["own.py"])
    assert cache2.lookup("ENCODING-SAFETY", "scope-x") == "detail-v1", (
        "own 内容未变 ⇒ 缓存必须命中（键隔离）"
    )


def test_cache_misses_on_own_content_change(git_repo: Path) -> None:
    """own staged 内容变化必须立即 miss（投毒逆命题）。"""
    gw = _gateway(git_repo)
    cache = gcp.GateResultCache(gw, ["own.py"])
    cache.store("NO-BARE-SQL", "scope-y", "detail-a")
    assert cache.lookup("NO-BARE-SQL", "scope-y") == "detail-a"

    _stage(git_repo, "own.py", "X = 999\n")

    cache2 = gcp.GateResultCache(gw, ["own.py"])
    assert cache2.lookup("NO-BARE-SQL", "scope-y") is None, "own 内容变化 ⇒ 必须 miss"
