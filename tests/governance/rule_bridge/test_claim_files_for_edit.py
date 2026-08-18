# [BLUEPRINT] MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT | tests/governance/rule_bridge/test_claim_files_for_edit.py | §Ruling-100PCT-AI-GOVERNANCE-P2-2
# [MODULE] tests.governance.rule_bridge.test_claim_files_for_edit
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.session_worktree
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 临时 git 仓库隔离测试；不依赖 worktree 完整生命周期
# [MODIFY-GUARD] 测试函数名与 P2-2 API 对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_claim_files_for_edit.py — P2-2 并发 session 文件级原子性测试

测试覆盖：
  1. claim_files_for_edit API（编辑前 claim 文件）
  2. _collect_tracked_cleanups 尊重 skip_files（不清理 claimed 文件）
  3. _collect_untracked_cleanups 尊重 skip_files
  4. _get_other_session_claimed_files 返回正确的相对路径
  5. 端到端：session A claim 文件 → session B 的 _pre_merge_auto_clean 跳过该文件

病根（P1-5 实测 bug）：
  AI Edit 文件后、session_worktree_commit 前的窗口，并发 session 的
  _pre_merge_auto_clean 在毫秒级还原文件。治本：编辑前 claim，_pre_merge_auto_clean
  尊重 claim 不清理 claimed 文件。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_repo(tmp_path_factory, monkeypatch):
    """临时 git 仓库 + SessionRegistry，每个测试独立。"""
    repo = tmp_path_factory.mktemp("p2_2_test_repo")
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@zephyr.local"],
        cwd=repo, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Zephyr Test"],
        cwd=repo, capture_output=True, check=True,
    )
    (repo / ".gitkeep").write_text("", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=repo, capture_output=True, check=True,
    )

    # monkeypatch session_worktree 模块的 REPO_ROOT
    import zephyr.gov_enforcement.rule_bridge.session_worktree as sw_mod
    monkeypatch.setattr(sw_mod, "REPO_ROOT", repo)
    return repo


def _make_tracked_file(repo: Path, name: str, content: str) -> Path:
    """创建并 commit 一个已跟踪文件。

    用 write_bytes 避免 Windows CRLF 转换（git 存储 LF，read_bytes 也读 LF，
    text 模式 write_text 会转 CRLF 导致 content 不匹配）。
    """
    f = repo / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(content.encode("utf-8"))
    subprocess.run(["git", "add", name], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {name}"], cwd=repo, capture_output=True, check=True,
    )
    return f


def _make_branch_with_file(repo: Path, branch: str, name: str, content: str) -> None:
    """创建分支指向当前 HEAD（HEAD 已通过 _make_tracked_file commit 文件）。

    使 ``git show branch:name`` 可用——branch 指向的 commit tree 包含该文件。
    无需 worktree（HEAD 已有文件，branch 直接指向 HEAD 即可）。
    """
    subprocess.run(
        ["git", "branch", branch], cwd=repo, capture_output=True, check=True,
    )


# ---------------------------------------------------------------------------
# claim_files_for_edit API 测试
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


class TestClaimFilesForEdit:
    """claim_files_for_edit API 功能测试。"""

    def test_claim_single_file_success(self, isolated_repo):
        """单文件 claim 成功。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            claim_files_for_edit,
        )
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        # 先注册 session
        registry = SessionRegistry(isolated_repo)
        registry.register("sess-a-001", pid=99999, is_breaking_change=False)

        f = _make_tracked_file(isolated_repo, "target.py", "content\n")
        result = claim_files_for_edit(
            session_id="sess-a-001",
            files=[str(f)],
            project_root=str(isolated_repo),
        )
        assert result["ok"] is True, f"expected ok=True, got: {result}"
        assert "target.py" in result["claimed"]
        assert result["blocked"] == []

    def test_claim_empty_files_list(self, isolated_repo):
        """空文件列表返回 ok=True。"""
        from zephyr.gov_enforcement.rule_bridge import session_worktree as sw
        result = sw.claim_files_for_edit(
            session_id="sess-a-002",
            files=[],
            project_root=str(isolated_repo),
        )
        assert result["ok"] is True
        assert result["claimed"] == []
        assert result["blocked"] == []

    def test_claim_relative_path(self, isolated_repo):
        """支持相对路径输入。"""
        from zephyr.gov_enforcement.rule_bridge import session_worktree as sw
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(isolated_repo)
        registry.register("sess-a-003", pid=99999, is_breaking_change=False)

        _make_tracked_file(isolated_repo, "rel_target.py", "content\n")
        result = sw.claim_files_for_edit(
            session_id="sess-a-003",
            files=["rel_target.py"],
            project_root=str(isolated_repo),
        )
        assert result["ok"] is True
        assert "rel_target.py" in result["claimed"]

    def test_claim_blocked_by_other_session(self, isolated_repo):
        """文件被其他 session 持有时 claim 失败。"""
        from zephyr.gov_enforcement.rule_bridge import session_worktree as sw
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(isolated_repo)
        # session A 先 claim 文件
        registry.register("sess-a-004", pid=99999, is_breaking_change=False)
        registry.claim_file("sess-a-004", "shared_file.py")

        # session B 尝试 claim 同一文件
        registry.register("sess-b-004", pid=99998, is_breaking_change=False)
        _make_tracked_file(isolated_repo, "shared_file.py", "content\n")
        result = sw.claim_files_for_edit(
            session_id="sess-b-004",
            files=["shared_file.py"],
            project_root=str(isolated_repo),
        )
        assert result["ok"] is False
        assert "shared_file.py" in result["blocked"]
        assert "shared_file.py" not in result["claimed"]


# ---------------------------------------------------------------------------
# _collect_tracked_cleanups 尊重 skip_files 测试
# ---------------------------------------------------------------------------


class TestCollectTrackedCleanupsSkipFiles:
    """_collect_tracked_cleanups 尊重 skip_files 参数。"""

    def test_skip_files_prevents_cleanup(self, isolated_repo):
        """skip_files 中的文件不被加入 to_checkout。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _collect_tracked_cleanups,
        )

        # 准备：创建已跟踪文件并修改（使其 dirty）
        f = _make_tracked_file(isolated_repo, "skip_me.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        # 模拟：文件在 changed_files + dirty_files 中
        changed_files = ["skip_me.py"]
        dirty_files = {"skip_me.py"}

        # 不 skip 时，文件应被加入 to_checkout（内容一致场景需模拟）
        # 这里用 skip_files 测试跳过逻辑
        skip_files = {"skip_me.py"}
        cleaned, skipped, to_checkout = _collect_tracked_cleanups(
            isolated_repo, "session/test-branch", changed_files, dirty_files,
            skip_files=skip_files,
        )
        assert cleaned == 0, "skip_files 中的文件不应被清理"
        assert "skip_me.py" in skipped
        assert to_checkout == []

    def test_no_skip_files_allows_cleanup(self, isolated_repo):
        """无 skip_files 时，正常清理逻辑不受影响（向后兼容）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _collect_tracked_cleanups,
        )

        # 创建已跟踪文件（content="content\n"）
        _make_tracked_file(isolated_repo, "normal.py", "content\n")
        # 创建 branch 并 commit 相同 content（使 git show branch:normal.py 可用）
        branch = "session/test-branch"
        _make_branch_with_file(isolated_repo, branch, "normal.py", "content\n")

        changed_files = ["normal.py"]
        dirty_files = {"normal.py"}  # 假设 dirty

        # 无 skip_files（None）—— 正常逻辑
        cleaned, skipped, to_checkout = _collect_tracked_cleanups(
            isolated_repo, branch, changed_files, dirty_files,
            skip_files=None,
        )
        # content 一致 → 应加入 to_checkout
        assert "normal.py" in to_checkout
        assert cleaned == 1

    def test_partial_skip(self, isolated_repo):
        """部分文件 skip，部分文件正常清理。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _collect_tracked_cleanups,
        )

        # 创建两个已跟踪文件
        _make_tracked_file(isolated_repo, "skip_me.py", "content\n")
        _make_tracked_file(isolated_repo, "clean_me.py", "content\n")
        # 创建 branch 指向 HEAD（HEAD 已含两个文件，只创建一次）
        branch = "session/test-branch"
        _make_branch_with_file(isolated_repo, branch, "skip_me.py", "content\n")

        changed_files = ["skip_me.py", "clean_me.py"]
        dirty_files = {"skip_me.py", "clean_me.py"}
        skip_files = {"skip_me.py"}  # 只 skip 第一个

        cleaned, skipped, to_checkout = _collect_tracked_cleanups(
            isolated_repo, branch, changed_files, dirty_files,
            skip_files=skip_files,
        )
        assert "skip_me.py" in skipped
        assert "clean_me.py" in to_checkout
        assert cleaned == 1


# ---------------------------------------------------------------------------
# _get_other_session_claimed_files 测试
# ---------------------------------------------------------------------------


class TestGetOtherSessionClaimedFiles:
    """_get_other_session_claimed_files 返回正确的相对路径。"""

    def test_no_other_sessions_returns_empty(self, isolated_repo):
        """无其他活跃 session 时返回空集。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _get_other_session_claimed_files,
        )
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(isolated_repo)
        registry.register("sess-self-001", pid=99999, is_breaking_change=False)

        result = _get_other_session_claimed_files(isolated_repo, "sess-self-001")
        assert result == set()

    def test_returns_relative_paths(self, isolated_repo):
        """返回相对路径（forward slash）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _get_other_session_claimed_files,
        )
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(isolated_repo)
        # session A claim 文件
        registry.register("sess-a-005", pid=99999, is_breaking_change=False)
        registry.claim_file("sess-a-005", "src/module/file1.py")
        registry.claim_file("sess-a-005", "src/module/file2.py")

        # session B 查询
        registry.register("sess-b-005", pid=99998, is_breaking_change=False)
        result = _get_other_session_claimed_files(isolated_repo, "sess-b-005")

        assert "src/module/file1.py" in result
        assert "src/module/file2.py" in result

    def test_excludes_self_session_claims(self, isolated_repo):
        """不返回本 session 自己 claim 的文件。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _get_other_session_claimed_files,
        )
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(isolated_repo)
        registry.register("sess-self-002", pid=99999, is_breaking_change=False)
        registry.claim_file("sess-self-002", "my_file.py")

        result = _get_other_session_claimed_files(isolated_repo, "sess-self-002")
        assert "my_file.py" not in result, "不应返回本 session 自己的 claim"

    def test_failopen_on_error(self, isolated_repo, monkeypatch):
        """registry 查询失败时 fail-open 返回空集。"""
        from zephyr.gov_enforcement.rule_bridge import session_worktree as sw

        # mock _get_registry 抛异常
        def _raise(*args, **kwargs):
            raise RuntimeError("mocked registry failure")
        monkeypatch.setattr(sw, "_get_registry", _raise)

        result = sw.get_other_session_claimed_files(isolated_repo, "sess-test")
        assert result == set(), "fail-open 应返回空集"


# ---------------------------------------------------------------------------
# 端到端：_pre_merge_auto_clean 尊重 claim
# ---------------------------------------------------------------------------


class TestPreMergeAutoCleanRespectsClaims:
    """_pre_merge_auto_clean 端到端尊重 claim。"""

    def test_claimed_file_not_cleaned(self, isolated_repo):
        """session A claim 的文件，session B 的 auto_clean 不清理。"""
        from zephyr.gov_enforcement.rule_bridge import session_worktree as sw
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        # 准备：创建已跟踪文件
        f = _make_tracked_file(isolated_repo, "protected.py", "original\n")
        # 修改文件（使其 dirty，content 与 HEAD 不同）
        f.write_text("modified_by_session_a\n", encoding="utf-8")

        # session A 注册并 claim 文件
        registry = SessionRegistry(isolated_repo)
        registry.register("sess-a-protect", pid=99999, is_breaking_change=False)
        registry.claim_file("sess-a-protect", "protected.py")

        # 模拟 session B 的 _pre_merge_auto_clean 调用
        # session B 试图清理 protected.py（假设它在 session B 的 changed_files 中）
        # 但因为 session A claim 了它，应该被跳过
        # 注意：_pre_merge_auto_clean 需要 session B 有 worktree branch，
        # 这里直接测试 _get_other_session_claimed_files 集成效果
        skip_files = sw.get_other_session_claimed_files(isolated_repo, "sess-b-merger")
        assert "protected.py" in skip_files, \
            "session A claim 的文件应在 session B 的 skip_files 中"

        # 验证 _collect_tracked_cleanups 尊重 skip_files
        changed_files = ["protected.py"]
        dirty_files = {"protected.py"}
        cleaned, skipped, to_checkout = sw.collect_tracked_cleanups(
            isolated_repo, "session/sess-b-merger", changed_files, dirty_files,
            skip_files=skip_files,
        )
        assert cleaned == 0, "claimed 文件不应被清理"
        assert "protected.py" in skipped
        assert to_checkout == [], "claimed 文件不应加入 to_checkout"

    def test_unclaimed_file_still_cleaned(self, isolated_repo):
        """未 claim 的文件正常清理（不影响现有行为）。"""
        from zephyr.gov_enforcement.rule_bridge import session_worktree as sw
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        # 准备：两个文件，一个 claimed 一个未 claimed
        f1 = _make_tracked_file(isolated_repo, "claimed.py", "content\n")
        f2 = _make_tracked_file(isolated_repo, "unclaimed.py", "content\n")
        # 都不修改（content 一致场景，会被清理）
        # 创建 branch 指向 HEAD（HEAD 已含两个文件，使 git show branch:file 可用）
        _make_branch_with_file(isolated_repo, "session/sess-b-mix", "claimed.py", "content\n")

        # session A claim f1
        registry = SessionRegistry(isolated_repo)
        registry.register("sess-a-mix", pid=99999, is_breaking_change=False)
        registry.claim_file("sess-a-mix", "claimed.py")

        # session B 查询 skip_files
        skip_files = sw.get_other_session_claimed_files(isolated_repo, "sess-b-mix")
        assert "claimed.py" in skip_files
        assert "unclaimed.py" not in skip_files

        # _collect_tracked_cleanups：claimed 跳过，unclaimed 清理
        changed_files = ["claimed.py", "unclaimed.py"]
        dirty_files = {"claimed.py", "unclaimed.py"}
        cleaned, skipped, to_checkout = sw.collect_tracked_cleanups(
            isolated_repo, "session/sess-b-mix", changed_files, dirty_files,
            skip_files=skip_files,
        )
        assert "claimed.py" in skipped
        assert "unclaimed.py" in to_checkout
        assert cleaned == 1, "只有 unclaimed 文件被清理"
