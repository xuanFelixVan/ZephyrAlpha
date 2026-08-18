# [A_test] module_id: MOD-GOV_protected_paths_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_protected_paths_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_protected_paths_gate.py — 受保护路径写入检测门禁单测（#ARCH-MODEL-LIFECYCLE-001 P1）

权威依据：protected_paths_gate.py（make_protected_paths_gate）

测试组：
- TestEmptyStagedPass: staged 为空 → 放行
- TestNoProtectedFilesPass: staged 无受保护路径 → 放行
- TestGitignoreBlocked: .gitignore staged 无逃生通道 → 阻断
- TestGitattributesBlocked: .gitattributes staged 无逃生通道 → 阻断
- TestAgentsMdBlocked: AGENTS.md staged 无逃生通道 → 阻断
- TestApprovalMarkerPass: commit message 含 [ARCH-APPROVAL:...] → 放行
- TestEnvBypassPass: ZEPHYR_PROTECTED_PATHS_BYPASS=1 env → 放行
- TestGateSpecFields: gate_id / priority 字段正确
- TestIsProtected: is_protected 公共接口
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.protected_paths_gate import (
    is_protected,
    make_protected_paths_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec


def _make_gateway(project_root: Path | None = None) -> MagicMock:
    """构造 mock gateway。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_is_protected_paths(self):
        """gate_id == 'PROTECTED-PATHS'。"""
        gate = make_protected_paths_gate()
        assert gate.gate_id == "PROTECTED-PATHS"

    def test_priority_is_28(self):
        """priority == 28（早于 FORGED-GW-MARKER=29 / DIRECTORY-CONTRACT=30）。"""
        gate = make_protected_paths_gate()
        assert gate.priority == 28


class TestEmptyStagedPass:
    """staged 为空 → 放行。"""

    def test_empty_staged_passes(self, tmp_path):
        """staged 为空 → passed=True。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "no staged files" in detail


class TestNoProtectedFilesPass:
    """staged 无受保护路径 → 放行。"""

    def test_no_protected_files_passes(self, tmp_path):
        """staged 只有普通文件 → passed=True。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, ["src/zephyr/foo.py", "scripts/bar.py"])
        assert passed is True
        assert "no protected paths" in detail


class TestGitignoreBlocked:
    """ .gitignore staged 无逃生通道 → 阻断。"""

    def test_gitignore_blocked(self, tmp_path):
        """.gitignore staged 无逃生 → passed=False。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitignore", "src/foo.py"])
        assert passed is False
        assert "PROTECTED-PATHS" in detail
        assert ".gitignore" in detail


class TestGitattributesBlocked:
    """ .gitattributes staged 无逃生通道 → 阻断。"""

    def test_gitattributes_blocked(self, tmp_path):
        """.gitattributes staged 无逃生 → passed=False。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitattributes"])
        assert passed is False
        assert "PROTECTED-PATHS" in detail
        assert ".gitattributes" in detail


class TestAgentsMdBlocked:
    """ AGENTS.md staged 无逃生通道 → 阻断。"""

    def test_agents_md_blocked(self, tmp_path):
        """AGENTS.md staged 无逃生 → passed=False。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, ["AGENTS.md"])
        assert passed is False
        assert "PROTECTED-PATHS" in detail
        assert "AGENTS.md" in detail


class TestApprovalMarkerPass:
    """commit message 含 [ARCH-APPROVAL:...] → 放行。"""

    def test_approval_marker_passes(self, tmp_path):
        """commit message 含 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] → passed=True。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(
            gw, [".gitignore"],
            commit_message="fix: update gitignore [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]",
        )
        assert passed is True
        assert "[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]" in detail

    def test_approval_marker_with_hash_prefix_passes(self, tmp_path):
        """commit message 含 [ARCH-APPROVAL:#ARCH-007] → passed=True。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(
            gw, [".gitattributes"],
            commit_message="chore: tweak lfs [ARCH-APPROVAL:#ARCH-007]",
        )
        assert passed is True

    def test_approval_marker_audits_to_file(self, tmp_path):
        """审批标记逃生 → 落审计到 .runtime/gate_audit/protected_paths_bypass.jsonl。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        gate.check(
            gw, [".gitignore"],
            commit_message="fix: update [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]",
        )
        audit_file = tmp_path / ".runtime" / "gate_audit" / "protected_paths_bypass.jsonl"
        assert audit_file.is_file()
        content = audit_file.read_text(encoding="utf-8")
        assert "approval_marker" in content
        assert "ARCH-MODEL-LIFECYCLE-001" in content


class TestEnvBypassPass:
    """ZEPHYR_PROTECTED_PATHS_BYPASS=1 env → 放行。"""

    def test_env_bypass_passes(self, tmp_path, monkeypatch):
        """env=1 → passed=True。"""
        monkeypatch.setenv("ZEPHYR_PROTECTED_PATHS_BYPASS", "1")
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitignore"])
        assert passed is True
        assert "ZEPHYR_PROTECTED_PATHS_BYPASS=1" in detail

    def test_env_bypass_audits_to_file(self, tmp_path, monkeypatch):
        """env 逃生 → 落审计到 .runtime/gate_audit/protected_paths_bypass.jsonl。"""
        monkeypatch.setenv("ZEPHYR_PROTECTED_PATHS_BYPASS", "1")
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        gate.check(gw, [".gitignore"])
        audit_file = tmp_path / ".runtime" / "gate_audit" / "protected_paths_bypass.jsonl"
        assert audit_file.is_file()
        content = audit_file.read_text(encoding="utf-8")
        assert "env_bypass" in content


class TestIsProtected:
    """is_protected 公共接口。"""

    def test_gitignore_is_protected(self):
        """.gitignore → True。"""
        assert is_protected(".gitignore") is True

    def test_gitattributes_is_protected(self):
        """.gitattributes → True。"""
        assert is_protected(".gitattributes") is True

    def test_agents_md_is_protected(self):
        """AGENTS.md → True。"""
        assert is_protected("AGENTS.md") is True

    def test_normal_file_not_protected(self):
        """src/foo.py → False。"""
        assert is_protected("src/zephyr/foo.py") is False

    def test_dot_slash_prefix_normalized(self):
        """./.gitignore → True（前缀归一化）。"""
        assert is_protected("./.gitignore") is True

    def test_backslash_normalized(self):
        """Windows 反斜杠路径 → True。"""
        assert is_protected(".gitignore") is True


class TestMergeBranchApprovalGate:
    """B4 治本（2026-08-19）Layer 1：merge finalize 场景分支侧审批转置。

    与 Layer 2（tests/scripts/test_check_protected_paths_merge.py）共享真源三件套
    （check_protected_paths._merge_head_shas 等）；Layer 1 仅在 gateway 检测到在途
    merge（B2① 落地后=显式 --merge-finalize）时启用，核验异常维持阻断（fail-closed）。
    """

    @staticmethod
    def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        return subprocess.run(
            ["git", *args], cwd=str(repo),
            capture_output=True, text=True, encoding="utf-8", env=env, check=True,
        )

    def _make_merge_scene(self, repo: Path, approved: bool) -> None:
        """真分叉 + side 分支改 .gitignore（按 approved 带不带审批标记）+ 在途 MERGE_HEAD。"""
        self._git(repo, "init")
        self._git(repo, "config", "user.name", "Test")
        self._git(repo, "config", "user.email", "test@test.com")
        (repo / ".gitignore").write_text("*.log\n", encoding="utf-8")
        (repo / "main.py").write_text("x = 1\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-m", "init", "--no-verify")
        base_ref = self._git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        self._git(repo, "checkout", "-qb", "side")
        (repo / ".gitignore").write_text("*.log\n*.tmp\n", encoding="utf-8")
        self._git(repo, "add", ".gitignore")
        msg = (
            "chore: gitignore [ARCH-APPROVAL:ARCH-TEST-010]"
            if approved else "chore: gitignore (no approval)"
        )
        self._git(repo, "commit", "-m", msg, "--no-verify")
        self._git(repo, "checkout", "-q", base_ref)
        (repo / "main2.py").write_text("y = 2\n", encoding="utf-8")
        self._git(repo, "add", "main2.py")
        self._git(repo, "commit", "-m", "main advances", "--no-verify")
        self._git(repo, "merge", "--no-commit", "--no-ff", "side")

    def _make_merge_gateway(self, repo: Path) -> MagicMock:
        gw = _make_gateway(repo)
        gw._is_merge_in_progress.return_value = True
        return gw

    def test_merge_finalize_branch_approved_passes(self, tmp_path):
        """merge finalize + 分支侧带审批标记 → 放行（merge_branch_approval 审计）。"""
        self._make_merge_scene(tmp_path, approved=True)
        gw = self._make_merge_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitignore"], commit_message="merge: finalize")
        assert passed is True, f"分支侧已审批应放行: {detail}"
        assert "branch-side commits approved" in detail
        audit_file = tmp_path / ".runtime" / "gate_audit" / "protected_paths_bypass.jsonl"
        assert audit_file.is_file()
        content = audit_file.read_text(encoding="utf-8")
        assert "merge_branch_approval" in content
        assert "ARCH-TEST-010" in content

    def test_merge_finalize_branch_unapproved_blocks(self, tmp_path):
        """merge finalize + 分支侧无审批标记 → 维持阻断。"""
        self._make_merge_scene(tmp_path, approved=False)
        gw = self._make_merge_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitignore"], commit_message="merge: finalize")
        assert passed is False, f"分支侧无审批应维持阻断: {detail}"
        assert "PROTECTED-PATHS" in detail

    def test_no_merge_no_marker_still_blocks(self, tmp_path):
        """回归防破：非 merge + 无标记 → 阻断（gateway 报无在途 merge）。"""
        self._make_merge_scene(tmp_path, approved=True)
        gw = _make_gateway(tmp_path)
        gw._is_merge_in_progress.return_value = False  # 非 merge 场景
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitignore"], commit_message="normal commit")
        assert passed is False, f"非 merge 无标记应阻断: {detail}"
