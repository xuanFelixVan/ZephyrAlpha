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
