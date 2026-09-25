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
- TestRulingApprovalGate: QCure M4.2——裁定册 active+approved_paths 覆盖 → 放行（审计 ruling_approval）；过期裁定阻断
- TestMarkerAntiForgeryGate: QCure M4.2——marker id 实存放行 / 伪造 id 阻断（附防伪拒绝原因）
- TestRegistryFailOpenGate: QCure M4.2——registry 读异常 + marker 在场保持既有放行+审计降级（fail-open 不收紧）
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
    """.gitignore staged 无逃生通道 → 阻断。"""

    def test_gitignore_blocked(self, tmp_path):
        """.gitignore staged 无逃生 → passed=False。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitignore", "src/foo.py"])
        assert passed is False
        assert "PROTECTED-PATHS" in detail
        assert ".gitignore" in detail


class TestGitattributesBlocked:
    """.gitattributes staged 无逃生通道 → 阻断。"""

    def test_gitattributes_blocked(self, tmp_path):
        """.gitattributes staged 无逃生 → passed=False。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [".gitattributes"])
        assert passed is False
        assert "PROTECTED-PATHS" in detail
        assert ".gitattributes" in detail


class TestAgentsMdBlocked:
    """AGENTS.md staged 无逃生通道 → 阻断。"""

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
            gw,
            [".gitignore"],
            commit_message="fix: update gitignore [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]",
        )
        assert passed is True
        assert "[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]" in detail

    def test_approval_marker_with_hash_prefix_passes(self, tmp_path):
        """commit message 含 [ARCH-APPROVAL:#ARCH-007] → passed=True。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(
            gw,
            [".gitattributes"],
            commit_message="chore: tweak lfs [ARCH-APPROVAL:#ARCH-007]",
        )
        assert passed is True

    def test_approval_marker_audits_to_file(self, tmp_path):
        """审批标记逃生 → 落审计到 .runtime/gate_audit/protected_paths_bypass.jsonl。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        gate.check(
            gw,
            [".gitignore"],
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
            ["git", *args],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=True,
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
        msg = "chore: gitignore [ARCH-APPROVAL:ARCH-TEST-010]" if approved else "chore: gitignore (no approval)"
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


# ── QCure M4.2（st-qcure-20260925 施工线C）：审批收敛器 approval_resolver gate 级集成 ──

_CATALOGS = "docs/01_policies_and_standards/_registry/catalogs"
_RULES_HIT = "docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml"


def _make_catalogs(root: Path, issue_ids: list[str] | None = None, rulings: list[dict] | None = None) -> None:
    """tmp_path 造最小注册表 fixture（议题册/裁定册，YAML 结构对齐真源 schema）。"""
    import yaml

    cat = root / _CATALOGS
    cat.mkdir(parents=True, exist_ok=True)
    if issue_ids is not None:
        (cat / "architecture_issue_registry.yaml").write_text(
            yaml.safe_dump({"entries": [{"issue_id": i} for i in issue_ids]}, allow_unicode=True),
            encoding="utf-8",
        )
    if rulings is not None:
        (cat / "ruling_registry.yaml").write_text(
            yaml.safe_dump({"entries": rulings}, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )


def _ruling(**overrides) -> dict:
    """裁定条目基模（#410 形态：active + approved_paths 目录前缀 + 有界 expires_at）。"""
    entry = {
        "ruling_id": "裁定#410",
        "title": "终局班两件收口批准",
        "date": "2026-09-24",
        "category": "架构",
        "status": "active",
        "summary": "rules 清道三袋落地",
        "affected_files": [],
        "related_arch": [],
        "related_rulings": [],
        "superseded_by": None,
        "approved_paths": ["docs/01_policies_and_standards/rules/"],
        "expires_at": "2099-01-01",
    }
    entry.update(overrides)
    return entry


class TestRulingApprovalGate:
    """QCure M4.2：裁定册授权通道接入 gate（裁定#410 授权落地）。"""

    def test_ruling_coverage_passes_with_audit(self, tmp_path):
        """active 裁定 approved_paths 覆盖命中路径 → 放行 + 审计 ruling_approval。"""
        _make_catalogs(tmp_path, rulings=[_ruling()])
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [_RULES_HIT], commit_message="chore: rules cleanup")
        assert passed is True, f"裁定覆盖应放行: {detail}"
        assert "裁定#410" in detail
        audit_file = tmp_path / ".runtime" / "gate_audit" / "protected_paths_bypass.jsonl"
        assert audit_file.is_file()
        content = audit_file.read_text(encoding="utf-8")
        assert "ruling_approval" in content
        assert "裁定#410" in content
        assert '"source": "ruling"' in content  # M4.2 审计 detail 增 source 字段

    def test_expired_ruling_blocks(self, tmp_path):
        """过期裁定不构成授权 → 维持阻断。"""
        _make_catalogs(tmp_path, rulings=[_ruling(expires_at="2020-01-01")])
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [_RULES_HIT], commit_message="chore: rules cleanup")
        assert passed is False, f"过期裁定应阻断: {detail}"
        assert "PROTECTED-PATHS" in detail

    def test_ruling_without_gateway_still_blocks(self, tmp_path):
        """无裁定册 fixture（缺册）+ 无 marker → 维持阻断（unknown 不打开逃生口）。"""
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [_RULES_HIT], commit_message="chore: rules cleanup")
        assert passed is False, f"缺册无 marker 应阻断: {detail}"


class TestMarkerAntiForgeryGate:
    """QCure M4.2：marker 防伪（假号洞顺堵）。"""

    def test_registered_marker_passes(self, tmp_path):
        """marker id 实存于议题册 → 放行（审计 source=marker）。"""
        _make_catalogs(tmp_path, issue_ids=["ARCH-MODEL-LIFECYCLE-001"])
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(
            gw, [".gitignore"],
            commit_message="fix: update gitignore [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]",
        )
        assert passed is True, f"实存 id 应放行: {detail}"
        audit_file = tmp_path / ".runtime" / "gate_audit" / "protected_paths_bypass.jsonl"
        content = audit_file.read_text(encoding="utf-8")
        assert '"source": "marker"' in content

    def test_forged_marker_blocks_with_hint(self, tmp_path):
        """marker id 查无（册可读）→ 阻断，detail 附防伪拒绝原因。"""
        _make_catalogs(tmp_path, issue_ids=["ARCH-OTHER-999"])
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(
            gw, [".gitignore"],
            commit_message="sneak: [ARCH-APPROVAL:ARCH-FAKE-123]",
        )
        assert passed is False, f"伪造 id 应阻断: {detail}"
        assert "未过防伪校验" in detail
        assert "ARCH-FAKE-123" in detail


class TestRegistryFailOpenGate:
    """QCure M4.2：registry 读异常保持既有 fail-open 降级（不收紧）。"""

    def test_unreadable_issue_registry_keeps_failopen(self, tmp_path):
        """议题册读异常（目录占位）+ marker 在场 → 保持既有放行+审计降级。"""
        bad = tmp_path / _CATALOGS / "architecture_issue_registry.yaml"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.mkdir()  # 目录替代文件 → 读取抛 IsADirectoryError
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(
            gw, [".gitignore"],
            commit_message="fix: [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]",
        )
        assert passed is True, f"registry 异常应保持 fail-open 放行: {detail}"
        audit_file = tmp_path / ".runtime" / "gate_audit" / "protected_paths_bypass.jsonl"
        content = audit_file.read_text(encoding="utf-8")
        assert "approval_marker" in content
        assert "marker_registry_failopen" in content

    def test_unreadable_ruling_registry_no_marker_blocks(self, tmp_path):
        """裁定册读异常 + 无 marker → 无逃生口维持阻断（unknown 只对 marker fail-open）。"""
        bad = tmp_path / _CATALOGS / "ruling_registry.yaml"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.mkdir()
        gw = _make_gateway(tmp_path)
        gate = make_protected_paths_gate()
        passed, detail = gate.check(gw, [_RULES_HIT], commit_message="chore: rules cleanup")
        assert passed is False, f"读异常无 marker 应阻断: {detail}"
