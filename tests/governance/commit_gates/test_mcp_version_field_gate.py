# [A_test] module_id: MOD-GOV-mcp_version_field_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_mcp_version_field_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_mcp_version_field_gate.py — MCP version 字段缺失硬阻断门禁单测（MCP-VERSION-FIELD）

权威依据：mcp_version_field_gate.py（make_mcp_version_field_gate）
5.35 API 版本管理防复发

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestVersionMissingBlocked: mcp.json 缺 version → hard-block
- TestVersionPresentPasses: mcp.json 有 version → 通过
- TestNoMcpJsonPasses: 无 mcp.json staged → 通过
- TestInvalidJsonFailOpen: JSON 语法错误 → 通过（fail-open）
- TestNonDictTopLevelFailOpen: 顶层非 object → 通过（fail-open）
- TestFailOpenGitDiff: git diff 失败 → 通过
- TestMultipleMcpJson: 多个 mcp.json 全缺 version → 全报告
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from tests.governance.commit_gates.gate_test_helpers import make_mock_gateway  # noqa: E402
from zephyr.gov_enforcement.commit_gates.mcp_version_field_gate import (  # noqa: E402
    make_mcp_version_field_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    def test_gate_id(self):
        gate = make_mcp_version_field_gate()
        assert gate.gate_id == "MCP-VERSION-FIELD"

    def test_priority(self):
        gate = make_mcp_version_field_gate()
        assert gate.priority == 126

    def test_is_gatespec(self):
        gate = make_mcp_version_field_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestVersionMissingBlocked (hard-block 命中)
# ============================================================================


class TestVersionMissingBlocked:
    def test_version_missing_blocked(self):
        """mcp.json 缺 version 字段 → hard-block"""
        mcp_file = "config/mcp.json"
        json_content = '{"tools": [{"name": "foo"}]}'
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "MCP-VERSION-FIELD" in detail
        assert "version" in detail

    def test_empty_object_blocked(self):
        """mcp.json 是空对象 {} → hard-block（缺 version）"""
        mcp_file = "config/mcp.json"
        json_content = "{}"
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, _ = gate.check(gw, [])
        assert not passed

    def test_nested_mcp_json_blocked(self):
        """src/.../mcp.json 缺 version → hard-block（路径不限）"""
        mcp_file = "src/zephyr/integration/mcp/mcp.json"
        json_content = '{"server": {"name": "test"}}'
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, _ = gate.check(gw, [])
        assert not passed


# ============================================================================
# TestVersionPresentPasses (有 version → 通过)
# ============================================================================


class TestVersionPresentPasses:
    def test_version_present_passes(self):
        """mcp.json 有 version 字段 → 通过"""
        mcp_file = "config/mcp.json"
        json_content = '{"version": "1.0.0", "tools": [{"name": "foo"}]}'
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_version_semver_passes(self):
        """mcp.json version 是语义版本号 → 通过"""
        mcp_file = "config/mcp.json"
        json_content = '{"version": "2.3.1-beta"}'
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestNoMcpJsonPasses (无 mcp.json staged → 通过)
# ============================================================================


class TestNoMcpJsonPasses:
    def test_no_mcp_json_passes(self):
        """staged 全是 .py 文件 → 通过"""
        py_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway(
            [py_file],
            {py_file: ["x = 1"]},
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_empty_staged_passes(self):
        """空 staged → 通过"""
        gw = make_mock_gateway([], {})
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestInvalidJsonFailOpen (JSON 语法错误 → fail-open)
# ============================================================================


class TestInvalidJsonFailOpen:
    def test_invalid_json_fail_open(self):
        """mcp.json JSON 语法错误 → 通过（fail-open，由其他 gate 管完整性）"""
        mcp_file = "config/mcp.json"
        json_content = "{invalid json content"
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # fail-open
        assert detail == ""


# ============================================================================
# TestNonDictTopLevelFailOpen (顶层非 object → fail-open)
# ============================================================================


class TestNonDictTopLevelFailOpen:
    def test_list_top_level_fail_open(self):
        """mcp.json 顶层是 list → 通过（fail-open）"""
        mcp_file = "config/mcp.json"
        json_content = "[1, 2, 3]"
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # fail-open
        assert detail == ""

    def test_string_top_level_fail_open(self):
        """mcp.json 顶层是 string → 通过（fail-open）"""
        mcp_file = "config/mcp.json"
        json_content = '"just a string"'
        gw = make_mock_gateway(
            [mcp_file],
            {},
            file_contents={mcp_file: json_content},
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed


# ============================================================================
# TestFailOpenGitDiff
# ============================================================================


class TestFailOpenGitDiff:
    def test_git_diff_fail_open(self):
        """git diff --name-only returncode != 0 → fail-open（通过）"""
        gw = make_mock_gateway([], {}, diff_fail=True)
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestMultipleMcpJson (多个 mcp.json 全缺 version → 全报告)
# ============================================================================


class TestMultipleMcpJson:
    def test_multiple_mcp_json_all_reported(self):
        """多个 mcp.json 全缺 version → 全报告"""
        mcp1 = "config/mcp.json"
        mcp2 = "src/zephyr/integration/mcp/mcp.json"
        gw = make_mock_gateway(
            [mcp1, mcp2],
            {},
            file_contents={
                mcp1: '{"tools": []}',
                mcp2: '{"server": {}}',
            },
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert mcp1 in detail
        assert mcp2 in detail

    def test_mixed_pass_and_fail(self):
        """一个 mcp.json 有 version，一个缺 → 只报缺的"""
        mcp1 = "config/mcp.json"
        mcp2 = "src/zephyr/integration/mcp/mcp.json"
        gw = make_mock_gateway(
            [mcp1, mcp2],
            {},
            file_contents={
                mcp1: '{"version": "1.0.0", "tools": []}',
                mcp2: '{"server": {}}',
            },
        )
        gate = make_mcp_version_field_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert mcp2 in detail
        assert mcp1 not in detail  # 有 version 的不报
