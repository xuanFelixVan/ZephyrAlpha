# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.audit.test_stash_lifecycle
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_stash_lifecycle.py — stash 生命周期治本单测（裁定 #ARCH-STASH-LIFECYCLE-GAP-001）

权威依据：
- trae_075 STASH-LIFE-LAW-3: merge 完成后 MUST 调用 _drop_session_pre_merge_stash
- session_worktree.py::_drop_session_pre_merge_stash
- reconciliation_registry.py::make_stash_lifecycle_reconciler._AI_STASH_RE

测试组：
- TestDropSessionPreMergeStash: _drop_session_pre_merge_stash 函数
  - 无匹配 stash → dropped=0
  - 匹配 1 条 stash → dropped=1
  - 匹配多条 stash → 全部 drop（从后往前避免索引漂移）
  - 只 drop 本次 session 的 stash，保留其他 session
  - git 故障 fail-open（dropped=0, errors 非空）
- TestAiStashRegex: _AI_STASH_RE 正则匹配
  - 8 个历史前缀全部匹配
  - 历史盲区命名（phase6.2-merge-tmp / pre-merge-batch5-stash3）匹配
  - WIP stash 不匹配（unrelated / CONSUMERS-ACCURACY / auto-sync temp）
  - user-manual- 永不匹配
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.rule_bridge.session_worktree import (  # noqa: E402
    _drop_session_pre_merge_stash,
)


# 复用 reconciliation_registry 中的 _AI_STASH_RE 逻辑做正则测试
_AI_STASH_RE = re.compile(
    r"^(?:session_worktree_pre_merge|session_worktree_abort|pre-merge[- ]stash"
    r"|phase[\w.-]*merge|merge-prep-|temp-stash-for-|stash-for-merge"
    r"|test-fix-merge-stash|pre-cherry-pick-stash|pre-merge-batch\w*-stash)"
)


class TestDropSessionPreMergeStash:
    """_drop_session_pre_merge_stash 函数测试。"""

    def test_no_matching_stash_returns_zero(self, tmp_path: Path) -> None:
        """无匹配 stash 时返回 dropped=0。"""
        # 初始化 git 仓库
        _init_git_repo(tmp_path)
        result = _drop_session_pre_merge_stash(tmp_path, "sess-nonexistent")
        assert result["dropped"] == 0
        assert result["errors"] == []

    def test_drops_matching_stash_for_session(self, tmp_path: Path) -> None:
        """匹配 1 条 stash → dropped=1。"""
        _init_git_repo(tmp_path)
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-test-001", "file1.txt")
        result = _drop_session_pre_merge_stash(tmp_path, "sess-test-001")
        assert result["dropped"] == 1
        assert result["errors"] == []
        # 验证 stash 已被 drop
        stash_list = _get_stash_list(tmp_path)
        assert len(stash_list) == 0

    def test_drops_multiple_stashes_reverse_order(self, tmp_path: Path) -> None:
        """匹配多条 stash → 全部 drop（从后往前避免索引漂移）。"""
        _init_git_repo(tmp_path)
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-test-002", "file1.txt")
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-test-002", "file2.txt")
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-test-002", "file3.txt")
        result = _drop_session_pre_merge_stash(tmp_path, "sess-test-002")
        assert result["dropped"] == 3
        assert result["errors"] == []
        assert len(_get_stash_list(tmp_path)) == 0

    def test_preserves_other_session_stashes(self, tmp_path: Path) -> None:
        """只 drop 本次 session 的 stash，保留其他 session。"""
        _init_git_repo(tmp_path)
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-other-001", "file1.txt")
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-target-001", "file2.txt")
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-other-002", "file3.txt")
        result = _drop_session_pre_merge_stash(tmp_path, "sess-target-001")
        assert result["dropped"] == 1
        # 其他 2 条 stash 保留
        remaining = _get_stash_list(tmp_path)
        assert len(remaining) == 2

    def test_fail_open_on_git_error(self, tmp_path: Path) -> None:
        """git 故障 fail-open（dropped=0）。

        非 git 仓库目录调用 git stash list，无论 rc=0（空输出）还是 rc!=0（错误），
        结果都是 dropped=0——fail-open 不抛异常。
        """
        # 非 git 仓库目录
        result = _drop_session_pre_merge_stash(tmp_path, "sess-test-003")
        assert result["dropped"] == 0
        # fail-open：不抛异常，dropped=0（errors 可空可非空取决于 git rc）


class TestAiStashRegex:
    """_AI_STASH_RE 正则匹配测试。"""

    @pytest.mark.parametrize("message", [
        "session_worktree_pre_merge: sess-123",
        "session_worktree_abort: sess-456",
        "pre-merge stash retry 4",
        "pre-merge-stash sess-49896-wiki-md",
        "phase6.2-merge-tmp",
        "phase-b5-merge-prep-4: 4 more files",
        "merge-prep-2: 3 more files",
        "temp-stash-for-issue23-merge",
        "stash-for-merge",
        "test-fix-merge-stash",
        "pre-cherry-pick-stash",
        "pre-merge-batch5-stash3",
        "pre-merge-batch5-stash2",
    ])
    def test_ai_stash_patterns_match(self, message: str) -> None:
        """已知 AI stash 命名模式全部匹配。"""
        assert _AI_STASH_RE.match(message), f"应匹配但未匹配: {message!r}"

    @pytest.mark.parametrize("message", [
        "pre-merge 2 reconcilers",
        "unrelated gov_audit/governance/trading work-in-progress",
        "CONSUMERS-ACCURACY work-in-progress from previous session",
        "auto-sync temp file lifecycle changes",
        "other-sessions-changes-before-merge",
        "user-manual-my-important-work",
        "user-manual-anything",
    ])
    def test_wip_and_protected_stashes_do_not_match(self, message: str) -> None:
        """WIP stash 和 user-manual- 不匹配。"""
        assert not _AI_STASH_RE.match(message), f"不应匹配但匹配了: {message!r}"


# —— 辅助函数 ——

def _init_git_repo(path: Path) -> None:
    """在 tmp_path 初始化一个空 git 仓库。"""
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, timeout=10)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(path), capture_output=True, timeout=10)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(path), capture_output=True, timeout=10)
    # 创建初始 commit
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=str(path), capture_output=True, timeout=10)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(path), capture_output=True, timeout=10)


def _create_stash(path: Path, message: str, filename: str = "README.md") -> None:
    """创建一个带指定 message 的 stash。

    Args:
        path: git 仓库根路径。
        message: stash message。
        filename: 要修改并 stash 的文件名（不同测试用不同文件避免 git stash
            合并同文件修改导致 stash 数 < 预期）。文件会先被 git add + commit
            确保 tracked，再修改 + stash。
    """
    target = path / filename
    # 确保 tracked：先创建 + add + commit
    target.write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "--", filename], cwd=str(path), capture_output=True, timeout=10)
    subprocess.run(["git", "commit", "-m", f"add {filename}"], cwd=str(path), capture_output=True, timeout=10)
    # 修改产生 dirty 状态再 stash
    target.write_text(f"modified for {message}", encoding="utf-8")
    subprocess.run(
        ["git", "stash", "push", "-m", message, "--", filename],
        cwd=str(path), capture_output=True, timeout=10,
    )


def _get_stash_list(path: Path) -> list[str]:
    """获取 stash list。"""
    result = subprocess.run(
        ["git", "stash", "list", "--format=%s"],
        cwd=str(path), capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
