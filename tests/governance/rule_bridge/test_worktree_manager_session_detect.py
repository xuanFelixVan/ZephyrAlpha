# [MODULE] tests.governance.rule_bridge.test_worktree_manager_session_detect
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.worktree_manager
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] .aidrafts 与 .worktrees 两代机制均可检出 session_id；非 worktree 返回 None
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] permanent
"""WorktreeManager.get_current_worktree 双机制检测单测（#ARCH-WORKTREE-ENV-001 P2-10）。

覆盖：.aidrafts（旧）/ .worktrees（新，scripts/session_worktree.py）两种布局下
cwd 命中 session_id；repo_root 为 worktree 自身（PYTHONPATH 激活场景）时
经 strip_session_worktree 锚定主仓库基目录仍可命中。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    """构造最小假仓库（.git 目录 + 两代 worktree 布局）。"""
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / ".aidrafts" / "sess-old").mkdir(parents=True)
    (repo / ".worktrees" / "AI-NEW-001").mkdir(parents=True)
    return repo


def test_detect_aidrafts(fake_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """旧机制 .aidrafts/<sid> 检出。"""
    monkeypatch.chdir(fake_repo / ".aidrafts" / "sess-old")
    assert WorktreeManager(fake_repo).get_current_worktree() == "sess-old"


def test_detect_worktrees_new_mechanism(fake_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """新机制 .worktrees/<sid> 检出（原盲区，WORKTREE-REQUIRED 误判源）。"""
    monkeypatch.chdir(fake_repo / ".worktrees" / "AI-NEW-001")
    assert WorktreeManager(fake_repo).get_current_worktree() == "AI-NEW-001"


def test_detect_when_repo_root_is_worktree_itself(fake_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PYTHONPATH 激活场景：repo_root=worktree 根，经主仓锚定基目录仍检出。"""
    wt = fake_repo / ".worktrees" / "AI-NEW-001"
    (wt / ".git").mkdir()  # worktree 内 .git 存在（gitfile 目录化即可过 __init__ 检查）
    monkeypatch.chdir(wt)
    assert WorktreeManager(wt).get_current_worktree() == "AI-NEW-001"


def test_not_in_worktree_returns_none(fake_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """主仓库根 cwd → None。"""
    monkeypatch.chdir(fake_repo)
    assert WorktreeManager(fake_repo).get_current_worktree() is None
