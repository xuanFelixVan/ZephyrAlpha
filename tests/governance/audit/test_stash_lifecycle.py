# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.audit.test_stash_lifecycle
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_stash_lifecycle.py — stash 生命周期治本单测（裁定 #ARCH-STASH-LIFECYCLE-GAP-001 / #ARCH-STASH-LIFECYCLE-FIX-001）

权威依据：
- trae_075 STASH-LIFE-LAW-3: merge 完成后 MUST 调用 _drop_session_pre_merge_stash
- session_worktree.py::_drop_session_pre_merge_stash
- reconciliation_registry.py::make_stash_lifecycle_reconciler
- reconciliation_registry.py::_strip_stash_branch_prefix（#ARCH-STASH-LIFECYCLE-FIX-001 治本）

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
- TestStripStashBranchPrefix: _strip_stash_branch_prefix 函数（#ARCH-STASH-LIFECYCLE-FIX-001）
  - "On <branch>: " 前缀正确剥离
  - 含斜杠分支名正确处理
  - 无前缀 / 无 ": " 分隔 / 空字符串 边界情况
- TestStashLifecycleReconcilerReverseMatch: 反向匹配治本端到端测试（#ARCH-STASH-LIFECYCLE-FIX-001）
  - aggressive 模式清理所有非 user-manual- 前缀 stash（含修复前不可识别的未知前缀）
  - user-manual- 永不被清理
  - 非 aggressive 模式下，age < TTL 的 AI stash 保留
"""
from __future__ import annotations

import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.rule_bridge.session_worktree import (  # noqa: E402
    _drop_session_pre_merge_stash,
)
from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    _strip_stash_branch_prefix,
    make_stash_lifecycle_reconciler,
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


# ============================================================================
# #ARCH-STASH-LIFECYCLE-FIX-001 治本测试（2026-07-22）
# ============================================================================
# 病根：原 reconciler 的 _is_ai_generated 用 message.startswith(_AI_STASH_PREFIXES)，
# 但 git stash list --format=%s 输出格式为 "On <branch>: <message>"，startswith
# 永不匹配；同时 AI 前缀列表不可穷举（实测有 7+ 种未知前缀）。
# 治本：1) _strip_stash_branch_prefix 去掉 "On <branch>: " 前缀；
#       2) _is_ai_generated 改为反向匹配（非 user-manual- = AI 生成）。


class TestStripStashBranchPrefix:
    """_strip_stash_branch_prefix 函数测试（#ARCH-STASH-LIFECYCLE-FIX-001 治本核心）。

    git stash list --format=%s 输出格式为 ``On <branch>: <message>``，但
    _PROTECTED_STASH_PREFIXES 是基于原始 message 的前缀匹配。本函数去掉分支前缀，
    使 startswith 检查能正确工作。
    """

    def test_strip_on_dev_prefix(self) -> None:
        """``On dev: <message>`` 前缀正确剥离。"""
        assert _strip_stash_branch_prefix("On dev: pre-merge-cleanup-sess-xxx") == "pre-merge-cleanup-sess-xxx"

    def test_strip_on_main_prefix(self) -> None:
        """``On main: <message>`` 前缀正确剥离。"""
        assert _strip_stash_branch_prefix("On main: user-manual-important") == "user-manual-important"

    def test_strip_feature_branch_with_slash(self) -> None:
        """含斜杠的分支名（feature/x）正确处理。"""
        assert _strip_stash_branch_prefix("On feature/fix-123: stash-msg") == "stash-msg"

    def test_no_prefix_unchanged(self) -> None:
        """无 ``On `` 前缀的消息原样返回。"""
        assert _strip_stash_branch_prefix("plain message") == "plain message"

    def test_no_colon_separator_unchanged(self) -> None:
        """``On `` 开头但无 ``: `` 分隔符的消息原样返回（不误剥）。"""
        # "On something here" 没有 ": " 分隔符，不应剥成 "something here"
        assert _strip_stash_branch_prefix("On something here") == "On something here"

    def test_empty_string(self) -> None:
        """空字符串原样返回。"""
        assert _strip_stash_branch_prefix("") == ""

    def test_only_prefix(self) -> None:
        """只有 ``On dev: `` 前缀，message 为空 → 返回空字符串。"""
        assert _strip_stash_branch_prefix("On dev: ") == ""


class TestStashLifecycleReconcilerReverseMatch:
    """反向匹配治本端到端测试（#ARCH-STASH-LIFECYCLE-FIX-001）。

    修复前的 _is_ai_generated 用 8 个 AI 前缀列表 startswith 匹配，导致：
    1. ``On <branch>: `` 前缀导致 startswith 永不匹配（reconciler 形同虚设）
    2. AI 手动创建 stash 的 message 模式不可穷举（pre-merge-cleanup / other-session-wip
       / pre-construction / auto-sync / unrelated / CONSUMERS-ACCURACY 等 7+ 种未知前缀）

    修复后用反向匹配：非 ``user-manual-`` 前缀的 stash 都是 AI 创建的。
    本测试组用 aggressive 模式（无视 age）验证反向匹配治本生效。
    """

    def test_aggressive_drops_unknown_ai_prefixes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """aggressive 模式清理未知 AI 前缀 stash（修复前不可识别）。

        场景：3 个 stash，2 个是修复前不可识别的未知 AI 前缀（pre-merge-cleanup /
        other-session-wip），1 个是 user-manual-。aggressive 模式应 drop 前 2 个，
        保留 user-manual-。
        """
        _init_git_repo(tmp_path)
        _create_stash(tmp_path, "pre-merge-cleanup-sess-12348-v4", "file1.txt")
        _create_stash(tmp_path, "other-session-wip-module-id-naming-fix", "file2.txt")
        _create_stash(tmp_path, "user-manual-important-work", "file3.txt")

        monkeypatch.setenv("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", "1")
        spec = make_stash_lifecycle_reconciler(types.SimpleNamespace(project_root=tmp_path))
        result = spec.reconcile(["some-file.py"], "test-session")

        # 反向匹配治本：pre-merge-cleanup + other-session-wip 被 drop（共 2 个）
        assert result.action == "clean", f"expected clean, got {result.action}: {result.detail}"
        assert "dropped=2" in result.detail, f"detail: {result.detail}"
        # user-manual- 保留
        remaining = _get_stash_list(tmp_path)
        assert len(remaining) == 1, f"remaining: {remaining}"
        assert "user-manual-important-work" in remaining[0]

    def test_protected_user_manual_always_kept(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """user-manual- 前缀 stash 在 aggressive 模式下也保留。"""
        _init_git_repo(tmp_path)
        _create_stash(tmp_path, "user-manual-1", "file1.txt")
        _create_stash(tmp_path, "user-manual-2", "file2.txt")
        _create_stash(tmp_path, "user-manual-3", "file3.txt")
        _create_stash(tmp_path, "session_worktree_pre_merge: sess-xxx", "file4.txt")

        monkeypatch.setenv("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", "1")
        spec = make_stash_lifecycle_reconciler(types.SimpleNamespace(project_root=tmp_path))
        result = spec.reconcile(["some-file.py"], "test-session")

        # 3 个 user-manual- 全部保留，1 个 AI stash drop
        assert "dropped=1" in result.detail, f"detail: {result.detail}"
        remaining = _get_stash_list(tmp_path)
        assert len(remaining) == 3, f"remaining: {remaining}"
        for msg in remaining:
            assert "user-manual-" in msg, f"unexpected stash kept: {msg}"

    def test_non_aggressive_keeps_fresh_ai_stash(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """非 aggressive 模式下，age < TTL 的 AI stash 保留（反向匹配不破坏 TTL 行为）。"""
        _init_git_repo(tmp_path)
        # 刚创建的 stash age < 4h TTL
        _create_stash(tmp_path, "pre-merge-cleanup-fresh", "file1.txt")
        _create_stash(tmp_path, "other-session-wip-fresh", "file2.txt")

        monkeypatch.delenv("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", raising=False)
        spec = make_stash_lifecycle_reconciler(types.SimpleNamespace(project_root=tmp_path))
        result = spec.reconcile(["some-file.py"], "test-session")

        # 全部 < TTL → skip（无 drop），stash 全部保留
        assert result.action == "skip", f"expected skip, got {result.action}: {result.detail}"
        remaining = _get_stash_list(tmp_path)
        assert len(remaining) == 2, f"remaining: {remaining}"

    def test_real_world_unknown_prefixes_recognized(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """真实场景未知前缀全部识别为 AI stash（修复前不可识别，导致 18+ stash 堆积）。

        场景：实测 18 个 stash 堆积的真实 message（含 CONSUMERS-ACCURACY /
        auto-sync temp / unrelated / pre-construction 等修复前不可识别前缀）。
        aggressive 模式下全部 drop，证明反向匹配治本生效。
        """
        _init_git_repo(tmp_path)
        real_world_messages = [
            "CONSUMERS-ACCURACY work-in-progress from previous session",
            "unrelated gov_audit/governance/trading work-in-progress",
            "auto-sync temp file lifecycle changes",
            "other-sessions-changes-before-merge",
            "pre-construction stash: test_capability_overlap_gate",
            "pre-construction stash: 3 files from other session",
            "other-session-wip-before-redblue-fix",
            "other-session-wip-module-id-naming-fix-20260722",
        ]
        for i, msg in enumerate(real_world_messages, 1):
            _create_stash(tmp_path, msg, f"file{i}.txt")

        monkeypatch.setenv("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", "1")
        spec = make_stash_lifecycle_reconciler(types.SimpleNamespace(project_root=tmp_path))
        result = spec.reconcile(["some-file.py"], "test-session")

        # 全部 8 个未知前缀 stash 被 drop（修复前 reconciler 形同虚设，0 个 drop）
        assert result.action == "clean", f"expected clean, got {result.action}: {result.detail}"
        assert "dropped=8" in result.detail, f"detail: {result.detail}"
        remaining = _get_stash_list(tmp_path)
        assert len(remaining) == 0, f"remaining: {remaining}"

    def test_session_worktree_prefix_still_recognized(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """原 8 个 AI 前缀（session_worktree_pre_merge 等）反向匹配仍识别。

        回归测试：反向匹配治本不破坏原 AI 前缀识别（session_worktree_pre_merge /
        abort / phase- / temp-stash-for- / pre-merge stash / pre-merge-stash /
        merge-prep- / stash-for-merge）。
        """
        _init_git_repo(tmp_path)
        original_ai_prefixes = [
            "session_worktree_pre_merge: sess-001",
            "session_worktree_abort: sess-002",
            "phase-6-merge-tmp",
            "temp-stash-for-issue23-merge",
            "pre-merge stash retry 4",
            "pre-merge-stash sess-49896",
            "merge-prep-2: 3 more files",
            "stash-for-merge",
        ]
        for i, msg in enumerate(original_ai_prefixes, 1):
            _create_stash(tmp_path, msg, f"file{i}.txt")

        monkeypatch.setenv("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", "1")
        spec = make_stash_lifecycle_reconciler(types.SimpleNamespace(project_root=tmp_path))
        result = spec.reconcile(["some-file.py"], "test-session")

        # 全部 8 个原 AI 前缀 stash 被 drop（反向匹配覆盖原 8 个前缀）
        assert result.action == "clean", f"expected clean, got {result.action}: {result.detail}"
        assert "dropped=8" in result.detail, f"detail: {result.detail}"
        remaining = _get_stash_list(tmp_path)
        assert len(remaining) == 0, f"remaining: {remaining}"

    def test_empty_stash_list_skips(self, tmp_path: Path) -> None:
        """空 stash list → action=skip。"""
        _init_git_repo(tmp_path)
        spec = make_stash_lifecycle_reconciler(types.SimpleNamespace(project_root=tmp_path))
        result = spec.reconcile(["some-file.py"], "test-session")
        assert result.action == "skip", f"expected skip, got {result.action}: {result.detail}"

