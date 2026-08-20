# [A_test] module_id: MOD-GOV_capability_lookup_required_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_capability_lookup_required_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_capability_lookup_required_gate.py — CAPABILITY-LOOKUP-REQUIRED 门禁单测

权威依据：capability_lookup_required_gate.py（make_capability_lookup_required_gate）
       #ARCH-GOV-CONVERGENCE-META Phase 3.4a 病根3治本

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestExemptions: 豁免场景（non-Zephyr / 空 files / .md-only / tests-only / 无业务代码）
- TestBypass: 逃生通道（env var / commit msg marker / merge commit）
- TestAuditLog: audit log 真实读写
  - 目录缺失 → fail-closed
  - 文件不存在 → 阻断
  - 文件存在但空 → 阻断
  - 文件存在且有 entry → 放行
  - 文件存在但 JSON 损坏 → fail-closed
- TestSessionIdMissing: session_id 缺失放行（SESSION-REQUIRED gate 处理）
- TestEndToEnd: 调 rule_discovery → 写 audit log → commit 通过

测试隔离：使用 tmp_path fixture 隔离 audit log 目录，不污染真实 .runtime/。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_gateway(project_root: Path):
    """构造 mock gateway with project_root."""
    from unittest.mock import MagicMock

    gw = MagicMock()
    gw.project_root = project_root
    return gw


def _make_zephyr_gateway(tmp_path: Path):
    """构造 mock gateway 含 Zephyr 项目结构 (scripts/governance/d1_structure)."""
    governance_dir = tmp_path / "scripts" / "governance" / "d1_structure"
    governance_dir.mkdir(parents=True, exist_ok=True)
    # 创建 src/zephyr/ 真实路径用于测试业务代码检测
    (tmp_path / "src" / "zephyr").mkdir(parents=True, exist_ok=True)
    return _make_gateway(tmp_path)


def _write_audit_log(audit_dir: Path, session_id: str, entries: list[dict]) -> Path:
    """写入测试用 audit log 文件。"""
    audit_dir.mkdir(parents=True, exist_ok=True)
    log_path = audit_dir / f"{session_id}.jsonl"
    with open(log_path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_path


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------


class TestGateSpecFields:
    def test_is_gate_spec(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )
        from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

        assert isinstance(make_capability_lookup_required_gate(), GateSpec)

    def test_gate_id(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        assert make_capability_lookup_required_gate().gate_id == "CAPABILITY-LOOKUP-REQUIRED"

    def test_priority(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        assert make_capability_lookup_required_gate().priority == 110


# ---------------------------------------------------------------------------
# TestExemptions — 豁免场景
# ---------------------------------------------------------------------------


class TestExemptions:
    def test_non_zephyr_project_passes(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_gateway(tmp_path)  # 无 scripts/governance/d1_structure
        spec = make_capability_lookup_required_gate()
        passed, msg = spec.check(gw, [], session_id="sess-test")
        assert passed is True
        assert "non-Zephyr" in msg

    def test_empty_files_passes(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        passed, msg = spec.check(gw, [], session_id="sess-test")
        assert passed is True
        assert "no files" in msg

    def test_doc_only_commit_passes(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        # 仅 .md 文件
        files = [str(tmp_path / "docs" / "foo.md")]
        # patch REPO_ROOT to tmp_path to avoid cross-drive relpath issues
        with patch(
            "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
            tmp_path,
        ):
            passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is True
        assert "doc-only" in msg

    def test_tests_only_commit_passes(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        # 仅 tests/ 下的 .py 文件
        files = [str(tmp_path / "tests" / "test_foo.py")]
        passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is True

    def test_non_py_business_code_passes(self, tmp_path):
        """src/zephyr/ 下的 .yaml/.json 等非 .py 文件不触发本 gate。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        files = [str(tmp_path / "src" / "zephyr" / "config.yaml")]
        passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is True
        assert "no src/zephyr/**/*.py business code" in msg


# ---------------------------------------------------------------------------
# TestBypass — 逃生通道
# ---------------------------------------------------------------------------


class TestBypass:
    def test_env_var_bypass(self, tmp_path, monkeypatch):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        monkeypatch.setenv("ZEPHYR_BYPASS_LOOKUP", "1")
        spec = make_capability_lookup_required_gate()
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is True
        assert "bypass" in msg.lower()

    def test_commit_msg_bypass_with_reason(self, tmp_path):
        """白名单 reason（gate-fix）→ 放行。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        passed, msg = spec.check(
            gw,
            files,
            session_id="sess-test",
            commit_message="fix: urgent patch [no-lookup:gate-fix-urgent]",
        )
        assert passed is True
        assert "gate-fix-urgent" in msg

    def test_commit_msg_bypass_empty_reason_blocked(self, tmp_path):
        """[no-lookup:] 标记但 reason 为空 → 阻断。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        passed, msg = spec.check(
            gw,
            files,
            session_id="sess-test",
            commit_message="fix: urgent patch [no-lookup:]",
        )
        assert passed is False
        assert "reason 为空" in msg

    def test_merge_commit_exempt(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        passed, msg = spec.check(
            gw,
            files,
            session_id="sess-test",
            commit_message="merge session/sess-12345",
        )
        assert passed is True
        assert "merge" in msg.lower()

    def test_non_whitelist_reason_blocked(self, tmp_path):
        """非白名单 reason（new-feature-xxx）→ 硬阻断（#ARCH-066 治本核心）。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        passed, msg = spec.check(
            gw,
            files,
            session_id="sess-test",
            commit_message="feat: new feature [no-lookup:new-feature-xxx]",
        )
        assert passed is False
        assert "不匹配白名单" in msg or "白名单" in msg

    def test_whitelist_reason_normalization(self, tmp_path):
        """归一化匹配：root_cause_fix（_ → -）匹配 root-cause → 放行。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        spec = make_capability_lookup_required_gate()
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        passed, msg = spec.check(
            gw,
            files,
            session_id="sess-test",
            commit_message="fix: root cause [no-lookup:root_cause_fix]",
        )
        assert passed is True
        assert "root_cause_fix" in msg


# ---------------------------------------------------------------------------
# TestAuditLog — audit log 真实读写
# ---------------------------------------------------------------------------


class TestAuditLog:
    def test_audit_log_dir_missing_blocks(self, tmp_path, monkeypatch):
        """audit log 目录缺失 → fail-closed（防"删目录绕过"攻击）。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        # 模拟 audit log 目录不存在
        gw = _make_zephyr_gateway(tmp_path)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with (
            patch(
                "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
                tmp_path,
            ),
            patch(
                "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.audit_log_dir_exists",
                return_value=False,
            ),
        ):
            spec = make_capability_lookup_required_gate()
            passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is False
        assert "audit log 目录缺失" in msg

    def test_no_audit_log_blocks(self, tmp_path, monkeypatch):
        """session 未调 rule_discovery → audit log 不存在 → 阻断。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            _get_audit_log_path,
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        # 模拟 audit log 目录存在但 session log 文件不存在
        with (
            patch(
                "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
                tmp_path,
            ),
            patch(
                "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.audit_log_dir_exists",
                return_value=True,
            ),
            patch(
                "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.get_audit_log_path",
                return_value=tmp_path / "nonexistent.jsonl",
            ),
        ):
            spec = make_capability_lookup_required_gate()
            passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is False
        assert "未调用" in msg

    def test_audit_log_with_entries_passes(self, tmp_path):
        """audit log 有 entry → 放行。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        # 创建 audit log 文件
        audit_dir = tmp_path / ".runtime" / "lookup_audit"
        _write_audit_log(
            audit_dir,
            "sess-test",
            [
                {
                    "ts": "2026-07-19T08:00:00Z",
                    "tool": "rule_discovery.discover_applicable_rules",
                    "query": {"operation": "file_write"},
                    "result_count": 1,
                    "rule_ids": ["TRAE-001"],
                },
            ],
        )
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        # patch REPO_ROOT 让 gate 找到 tmp_path 下的 audit log
        with patch(
            "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
            tmp_path,
        ):
            spec = make_capability_lookup_required_gate()
            passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is True
        assert "audit log OK" in msg

    def test_audit_log_corrupt_json_blocks(self, tmp_path):
        """audit log JSON 损坏 → fail-closed。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        audit_dir = tmp_path / ".runtime" / "lookup_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        log_path = audit_dir / "sess-test.jsonl"
        log_path.write_text("not a valid json line\n", encoding="utf-8")
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch(
            "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
            tmp_path,
        ):
            spec = make_capability_lookup_required_gate()
            passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is False
        assert "JSON 解析失败" in msg

    def test_audit_log_empty_file_blocks(self, tmp_path):
        """audit log 文件存在但为空 → 阻断（无有效 entry）。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        audit_dir = tmp_path / ".runtime" / "lookup_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        log_path = audit_dir / "sess-test.jsonl"
        log_path.write_text("\n  \n", encoding="utf-8")  # 仅空行
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch(
            "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
            tmp_path,
        ):
            spec = make_capability_lookup_required_gate()
            passed, msg = spec.check(gw, files, session_id="sess-test")
        assert passed is False
        assert "未调用" in msg


# ---------------------------------------------------------------------------
# TestSessionIdMissing — session_id 缺失放行
# ---------------------------------------------------------------------------


class TestSessionIdMissing:
    def test_empty_session_id_passes(self, tmp_path):
        """session_id 为空 → 放行（SESSION-REQUIRED gate 处理）。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        spec = make_capability_lookup_required_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
            tmp_path,
        ):
            passed, msg = spec.check(gw, files, session_id="")
        assert passed is True
        assert "session_id missing" in msg

    def test_unknown_session_id_passes(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )

        gw = _make_zephyr_gateway(tmp_path)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        spec = make_capability_lookup_required_gate()
        passed, msg = spec.check(gw, files, session_id="unknown")
        assert passed is True


# ---------------------------------------------------------------------------
# TestEndToEnd — 调 rule_discovery → 写 audit log → commit 通过
# ---------------------------------------------------------------------------


class TestEndToEnd:
    def test_full_flow_lookup_then_commit(self, tmp_path, monkeypatch):
        """完整流程：AI 调 rule_discovery → 写 audit log → commit 通过。

        模拟真实 AI 工作流：
        1. AI 调 rule_discovery.discover_applicable_rules(operation='file_write',
           session_id='sess-e2e')
        2. rule_discovery_server 写 audit log 到 .runtime/lookup_audit/sess-e2e.jsonl
        3. AI commit src/zephyr/foo.py
        4. CAPABILITY-LOOKUP-REQUIRED gate 读 audit log → 通过
        """
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )
        from zephyr.integration.mcp.rule_discovery_server import (
            LOOKUP_AUDIT_DIR,
            RuleDiscoveryServer,
        )

        # patch LOOKUP_AUDIT_DIR 到 tmp_path 下
        tmp_audit_dir = tmp_path / ".runtime" / "lookup_audit"
        monkeypatch.setattr(
            "zephyr.integration.mcp.rule_discovery_server.LOOKUP_AUDIT_DIR",
            tmp_audit_dir,
        )

        # Step 1: AI 调 rule_discovery
        server = RuleDiscoveryServer()
        result = server.discover_applicable_rules(operation="file_write", session_id="sess-e2e")
        assert result["count"] >= 1, "rule_discovery should return ≥1 rule for file_write"

        # 验证 audit log 已写入
        log_path = tmp_audit_dir / "sess-e2e.jsonl"
        assert log_path.exists(), f"audit log should be written to {log_path}"

        # Step 2: Commit - gate 应通过
        gw = _make_zephyr_gateway(tmp_path)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch(
            "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
            tmp_path,
        ):
            spec = make_capability_lookup_required_gate()
            passed, msg = spec.check(gw, files, session_id="sess-e2e")
        assert passed is True, f"gate should pass after lookup, msg={msg}"
        assert "audit log OK" in msg

    def test_full_flow_no_lookup_blocks(self, tmp_path, monkeypatch):
        """完整流程：AI 未调 rule_discovery → commit 阻断。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            make_capability_lookup_required_gate,
        )
        from zephyr.integration.mcp.rule_discovery_server import LOOKUP_AUDIT_DIR

        # patch LOOKUP_AUDIT_DIR 到 tmp_path 下（空目录）
        tmp_audit_dir = tmp_path / ".runtime" / "lookup_audit"
        tmp_audit_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(
            "zephyr.integration.mcp.rule_discovery_server.LOOKUP_AUDIT_DIR",
            tmp_audit_dir,
        )

        # AI 未调 rule_discovery，直接 commit
        gw = _make_zephyr_gateway(tmp_path)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch(
            "zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate.MAIN_REPO_ROOT",
            tmp_path,
        ):
            spec = make_capability_lookup_required_gate()
            passed, msg = spec.check(gw, files, session_id="sess-no-lookup")
        assert passed is False, "gate should block without lookup"
        assert "未调用" in msg
