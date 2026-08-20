# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_check_commit_message | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_check_commit_message.py — P4-3 check_commit_message.py 单测。

覆盖 5 个测试类 / 18 测试：
1. ``TestExtractSessionId`` (3) — [GW: 标记提取
2. ``TestLoadRegisteredSessions`` (3) — registry 文件加载
3. ``TestExtractCommitType`` (3) — conventional commit type 解析
4. ``TestIsMergeCommit`` (4) — merge commit 判定
5. ``TestCheckCommit`` (5) — 综合判定逻辑（forged / non-GW / whitelist / merge / legit GW）

P4-3（#ARCH-PREVENTABILITY-LAYER-001 Phase 4，2026-07-20）
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# 将 scripts/governance/ 加入 sys.path 以 import check_commit_message
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts" / "governance"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import check_commit_message as ccm  # type: ignore[import-not-found]

# =====================================================================
# 1. TestExtractSessionId
# =====================================================================


class TestExtractSessionId:
    """_extract_session_id 行为测试。"""

    def test_extract_basic(self) -> None:
        msg = "feat(audit): P4-1 ai_error_pattern_library [GW:sess-12345-20260720]"
        assert ccm.extract_session_id(msg) == "sess-12345-20260720"

    def test_extract_with_modifier(self) -> None:
        """[GW:sid:overlap] / [GW:sid:merge] 等修饰符。"""
        msg = "fix(gov): emergency commit [GW:sess-99999-20260720:overlap]"
        assert ccm.extract_session_id(msg) == "sess-99999-20260720"

    def test_extract_none(self) -> None:
        """无 [GW: 标记返回 None。"""
        assert ccm.extract_session_id("docs: update readme") is None
        assert ccm.extract_session_id("") is None


# =====================================================================
# 2. TestLoadRegisteredSessions
# =====================================================================


class TestLoadRegisteredSessions:
    """_load_registered_sessions 行为测试。"""

    def test_load_valid(self, tmp_path: Path) -> None:
        registry = tmp_path / "session_registry.json"
        registry.write_text(
            json.dumps(
                {
                    "sess-aaa-20260720": {"session_id": "sess-aaa-20260720"},
                    "sess-bbb-20260720": {"session_id": "sess-bbb-20260720"},
                    "not-a-session": {"foo": "bar"},  # 非 sess- 前缀，应过滤
                }
            ),
            encoding="utf-8",
        )
        result = ccm.load_registered_sessions(registry)
        assert result == {"sess-aaa-20260720", "sess-bbb-20260720"}

    def test_load_missing_file(self, tmp_path: Path) -> None:
        """文件不存在返回空 set。"""
        result = ccm.load_registered_sessions(tmp_path / "missing.json")
        assert result == set()

    def test_load_corrupt_json(self, tmp_path: Path) -> None:
        """损坏 JSON 返回空 set。"""
        registry = tmp_path / "session_registry.json"
        registry.write_text("{not valid json", encoding="utf-8")
        assert ccm.load_registered_sessions(registry) == set()


# =====================================================================
# 3. TestExtractCommitType
# =====================================================================


class TestExtractCommitType:
    """_extract_commit_type 行为测试。"""

    def test_basic(self) -> None:
        assert ccm.extract_commit_type("feat(audit): add library") == "feat"

    def test_no_scope(self) -> None:
        assert ccm.extract_commit_type("docs: update readme") == "docs"

    def test_non_conventional(self) -> None:
        """非 conventional 格式返回 None。"""
        assert ccm.extract_commit_type("update readme") is None
        assert ccm.extract_commit_type("Merge branch 'dev'") is None


# =====================================================================
# 4. TestIsMergeCommit
# =====================================================================


class TestIsMergeCommit:
    """_is_merge_commit 行为测试。"""

    def test_github_merge(self) -> None:
        assert ccm.is_merge_commit("Merge pull request #123 from xuanFelixVan/feature")

    def test_branch_merge(self) -> None:
        assert ccm.is_merge_commit("Merge branch 'dev' into main")

    def test_squash_merge(self) -> None:
        assert ccm.is_merge_commit("Squashed commit of the following:")

    def test_non_merge(self) -> None:
        assert not ccm.is_merge_commit("feat(audit): add library")
        assert not ccm.is_merge_commit("docs: update readme")


# =====================================================================
# 5. TestCheckCommit
# =====================================================================


class TestCheckCommit:
    """_check_commit 综合判定逻辑测试。"""

    def test_legit_gw_commit(self) -> None:
        """含 [GW:session_id] 且 session 已注册 → 放行。"""
        msg = "feat(audit): P4-1 library [GW:sess-aaa-20260720]"
        violations = ccm.check_commit(
            "abc1234",
            msg,
            {"sess-aaa-20260720"},
            strict=False,
        )
        assert violations == []

    def test_forged_gw_marker(self) -> None:
        """含 [GW:session_id] 但 session 未注册 → forged_gw_marker。"""
        msg = "feat(audit): forged [GW:sess-fake-20260720]"
        violations = ccm.check_commit(
            "abc1234",
            msg,
            {"sess-aaa-20260720"},
            strict=False,
        )
        assert len(violations) == 1
        assert "forged_gw_marker" in violations[0]

    def test_non_gw_whitelisted(self) -> None:
        """无 [GW:] + type ∈ 白名单 → 放行。"""
        msg = "docs(ruling): update P4-1 status"
        violations = ccm.check_commit(
            "abc1234",
            msg,
            set(),
            strict=False,
        )
        assert violations == []

    def test_non_gw_not_whitelisted(self) -> None:
        """无 [GW:] + type ∉ 白名单 → non_gw_commit。"""
        msg = "feat(audit): add new gate"
        violations = ccm.check_commit(
            "abc1234",
            msg,
            set(),
            strict=False,
        )
        assert len(violations) == 1
        assert "non_gw_commit" in violations[0]

    def test_non_gw_strict_mode(self) -> None:
        """strict=1 时白名单不生效。"""
        msg = "docs(ruling): update P4-1 status"
        violations = ccm.check_commit(
            "abc1234",
            msg,
            set(),
            strict=True,
        )
        assert len(violations) == 1
        assert "non_gw_commit" in violations[0]

    def test_merge_commit_exempt(self) -> None:
        """merge commit 即使无 [GW:] 也放行。"""
        msg = "Merge pull request #123 from xuanFelixVan/feature"
        violations = ccm.check_commit(
            "abc1234",
            msg,
            set(),
            strict=True,
        )
        assert violations == []

    def test_ci_mode_format_valid(self) -> None:
        """CI 模式（registry 为空）：合法格式 session_id 放行。"""
        msg = "feat(audit): P4-1 library [GW:sess-12345-20260721003148]"
        # registered_sessions 为空 = CI 模式（.runtime/ gitignored）
        violations = ccm.check_commit("abc1234", msg, set(), strict=False)
        assert violations == []

    def test_ci_mode_format_invalid(self) -> None:
        """CI 模式（registry 为空）：非法格式 session_id 阻断。"""
        msg = "feat(audit): forged [GW:sess-fake-session]"
        violations = ccm.check_commit("abc1234", msg, set(), strict=False)
        assert len(violations) == 1
        assert "forged_gw_marker" in violations[0]
        assert "格式不合规" in violations[0]
