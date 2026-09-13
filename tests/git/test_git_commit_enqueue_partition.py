# [BLUEPRINT] MOD-INF-005 | scripts/git_commit.py | §enqueue-delete-partition
# [MODULE] tests.git.test_git_commit_enqueue_partition
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.git_commit
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/git/test_git_commit_enqueue_partition.py
# [MATURITY] testing
# [INVARIANTS] 全部 tmp_path 临时 git 仓库隔离（cwd 显式指向 tmp 仓，不碰真实仓库）；验证 --enqueue 删除分区：盘上缺失但 index 在册 → deletes 通道；缺失且未跟踪 → fail-closed 拒绝集合
# [MODIFY-GUARD] _git_tracked_subset 契约：保序、git 异常返回空由调用方拒绝
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] self
# [TTL] permanent
"""test_git_commit_enqueue_partition.py — --enqueue 删除分区修复验收。

2026-09-14 实弹：_read_files_from_worktree 对盘上缺失文件直接 QueueReject，
原 try 内 deletes 兜底永不可达（死代码）→ 含删除文件的清单无法入队。
修复=先按存在性分区，缺失文件经 EnqueueOptions.deletes 通道（66 号 §6.1）。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.git_commit import _git_tracked_subset


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """临时 git 仓库：live.txt（盘上在册）+ gone.txt（index 在册、盘上缺失）。"""
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)  # noqa: S603

    git("init", "-q")
    git("config", "user.email", "t@example.test")
    git("config", "user.name", "t")
    (tmp_path / "live.txt").write_text("live\n", encoding="utf-8")
    (tmp_path / "gone.txt").write_text("gone\n", encoding="utf-8")
    git("add", "live.txt", "gone.txt")
    (tmp_path / "gone.txt").unlink()
    return tmp_path


def test_tracked_missing_goes_to_deletes(tmp_repo: Path) -> None:
    """盘上缺失但 index 在册 → 进 deletes；缺失且未跟踪 → 不进。"""
    assert _git_tracked_subset(tmp_repo, ["gone.txt", "ghost.txt"]) == ["gone.txt"]


def test_partition_ordering_matches_enqueue_mode(tmp_repo: Path) -> None:
    """分区语义与 _enqueue_mode 一致：readable 可读、deletes 通道、untracked_missing 拒绝集。"""
    rel_files = ["live.txt", "gone.txt", "ghost.txt"]
    missing = [f for f in rel_files if not (tmp_repo / f).exists()]
    deletes = _git_tracked_subset(tmp_repo, missing)
    assert deletes == ["gone.txt"]
    assert set(missing) - set(deletes) == {"ghost.txt"}
    readable = [f for f in rel_files if (tmp_repo / f).exists()]
    assert readable == ["live.txt"]


def test_git_failure_returns_empty(tmp_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """git 异常 → 返回空列表（fail-closed，由调用方拒绝），不抛异常。"""
    def boom(*args, **kwargs):
        raise OSError("git 不可用")

    monkeypatch.setattr("scripts.git_commit.subprocess.run", boom)
    assert _git_tracked_subset(tmp_repo, ["gone.txt"]) == []
