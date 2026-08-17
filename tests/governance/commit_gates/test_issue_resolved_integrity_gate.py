# [BLUEPRINT] MOD-GOV_COMMIT_GATES | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""test_issue_resolved_integrity_gate.py — ISSUE-RESOLVED-INTEGRITY gate 测试

#ARCH-CONSUMERS-ACCURACY-003 Phase 2 / #ARCH-ISSUE-RESOLVED-INTEGRITY-001 治本
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.issue_resolved_integrity_gate import (
    check_impact_files_exist,
    extract_file_paths_from_impact,
    make_issue_resolved_integrity_gate,
)


# ============================================================================
# extract_file_paths_from_impact 测试
# ============================================================================


class TestExtractFilePathsFromImpact:
    """测试从 impact 字段提取文件路径。"""

    def test_extract_from_list(self):
        """从 YAML 列表提取文件路径。"""
        impact = [
            "src/zephyr/foo/bar.py（some comment）",
            "docs/01_policies_and_standards/_registry/catalogs/test.yaml",
            "纯文字描述无文件路径",
        ]
        paths = extract_file_paths_from_impact(impact)
        path_strs = [p[0] for p in paths]
        assert "src/zephyr/foo/bar.py" in path_strs
        assert "docs/01_policies_and_standards/_registry/catalogs/test.yaml" in path_strs
        assert len(paths) == 2

    def test_extract_from_string(self):
        """从字符串提取文件路径。"""
        impact = "src/zephyr/foo.py\ndocs/test.yaml\n无路径"
        paths = extract_file_paths_from_impact(impact)
        path_strs = [p[0] for p in paths]
        assert "src/zephyr/foo.py" in path_strs
        assert "docs/test.yaml" in path_strs

    def test_extract_from_none(self):
        """None 输入返回空列表。"""
        assert extract_file_paths_from_impact(None) == []

    def test_extract_from_int(self):
        """非字符串/列表输入返回空列表。"""
        assert extract_file_paths_from_impact(42) == []

    def test_extract_json_path(self):
        """提取 .json 后缀路径。"""
        impact = ["data/reports/test.json"]
        paths = extract_file_paths_from_impact(impact)
        assert paths[0][0] == "data/reports/test.json"

    def test_extract_preserves_original_item(self):
        """保留原始字符串用于关键词检测。"""
        impact = ["src/foo.py（删除，untracked 残留）"]
        paths = extract_file_paths_from_impact(impact)
        assert paths[0][0] == "src/foo.py"
        assert "删除" in paths[0][1]


# ============================================================================
# check_impact_files_exist 测试
# ============================================================================


class TestCheckImpactFilesExist:
    """测试 impact 文件存在性检查。"""

    def test_all_files_exist(self, tmp_path):
        """所有文件存在时返回空列表。"""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "foo.py").write_text("# test")
        impact = ["src/foo.py"]
        result = check_impact_files_exist("#ARCH-TEST-001", impact, tmp_path)
        assert result == []

    def test_missing_file(self, tmp_path):
        """文件不存在时返回 warning。"""
        impact = ["src/nonexistent.py"]
        result = check_impact_files_exist("#ARCH-TEST-001", impact, tmp_path)
        assert len(result) == 1
        assert "nonexistent.py" in result[0]
        assert "#ARCH-TEST-001" in result[0]

    def test_skip_keyword_delete(self, tmp_path):
        """含'删除'关键词的条目跳过。"""
        impact = ["src/deleted.py（删除，untracked 残留）"]
        result = check_impact_files_exist("#ARCH-TEST-001", impact, tmp_path)
        assert result == []

    def test_skip_keyword_pending(self, tmp_path):
        """含'待建'关键词的条目跳过。"""
        impact = ["src/pending.py（待建，Phase 2）"]
        result = check_impact_files_exist("#ARCH-TEST-001", impact, tmp_path)
        assert result == []

    def test_skip_keyword_phase2(self, tmp_path):
        """含'Phase 2'关键词的条目跳过。"""
        impact = ["src/phase2.py（Phase 2 长期可选）"]
        result = check_impact_files_exist("#ARCH-TEST-001", impact, tmp_path)
        assert result == []

    def test_mixed_exist_and_missing(self, tmp_path):
        """混合存在和不存在文件。"""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "exists.py").write_text("# test")
        impact = ["src/exists.py", "src/missing.py"]
        result = check_impact_files_exist("#ARCH-TEST-001", impact, tmp_path)
        assert len(result) == 1
        assert "missing.py" in result[0]


# ============================================================================
# GateSpec 字段测试
# ============================================================================


class TestGateSpecFields:
    """测试 GateSpec 字段。"""

    def test_gate_id(self):
        assert make_issue_resolved_integrity_gate().gate_id == "ISSUE-RESOLVED-INTEGRITY"

    def test_priority_is_130(self):
        # 117=RECONCILER-FILE-OPS 已占用，后到者让位至 130
        assert make_issue_resolved_integrity_gate().priority == 130

    def test_check_callable(self):
        assert callable(make_issue_resolved_integrity_gate().check)


# ============================================================================
# _check 闭包测试
# ============================================================================


class TestCheckClosure:
    """测试 _check 闭包行为。"""

    def _make_gateway(self, project_root, content=""):
        """构造 mock gateway。

        _read_staged_file 是 _diff_helpers 的模块级函数，内部调用
        gateway.run_git(["git", "show", ":" + py_file])，返回 SubprocessResult。
        因此需 mock gw.run_git 返回带 returncode + stdout 的结果。
        """
        gw = MagicMock()
        gw.project_root = str(project_root) if project_root is not None else None
        result = MagicMock()
        result.returncode = 0 if content else 1
        result.stdout = content
        gw.run_git = MagicMock(return_value=result)
        return gw

    def test_no_staged_registry(self, tmp_path):
        """没有 staged registry 文件时放行。"""
        gw = self._make_gateway(tmp_path)
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(gw, ["src/some_file.py"])
        assert passed is True
        assert detail == ""

    def test_staged_registry_no_resolved(self, tmp_path):
        """staged registry 无 resolved 条目时放行。"""
        content = """\
module_id: TEST
entries:
  - issue_id: '#ARCH-001'
    status: open
    impact:
      - src/nonexistent.py
"""
        gw = self._make_gateway(tmp_path, content)
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(
            gw,
            ["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"],
        )
        assert passed is True
        assert detail == ""

    def test_staged_registry_resolved_file_exists(self, tmp_path):
        """resolved 条目的 impact 文件存在时放行。"""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "exists.py").write_text("# test")
        content = f"""\
module_id: TEST
entries:
  - issue_id: '#ARCH-TEST-001'
    status: resolved
    impact:
      - src/exists.py
"""
        gw = self._make_gateway(tmp_path, content)
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(
            gw,
            ["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"],
        )
        assert passed is True  # warn-only
        assert detail == ""

    def test_staged_registry_resolved_file_missing(self, tmp_path):
        """resolved 条目的 impact 文件不存在时 warn。"""
        content = """\
module_id: TEST
entries:
  - issue_id: '#ARCH-TEST-001'
    status: resolved
    impact:
      - src/nonexistent.py
"""
        gw = self._make_gateway(tmp_path, content)
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(
            gw,
            ["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"],
        )
        assert passed is True  # warn-only：passed=True 不阻断
        assert "nonexistent.py" in detail
        assert "#ARCH-TEST-001" in detail

    def test_staged_registry_resolved_file_deleted(self, tmp_path):
        """resolved 条目的 impact 文件已删除（含关键词）时放行。"""
        content = """\
module_id: TEST
entries:
  - issue_id: '#ARCH-TEST-001'
    status: resolved
    impact:
      - src/deleted.py（删除，untracked 残留）
"""
        gw = self._make_gateway(tmp_path, content)
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(
            gw,
            ["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"],
        )
        assert passed is True
        assert detail == ""

    def test_fail_open_yaml_parse_error(self, tmp_path):
        """YAML 解析失败时 fail-open。"""
        content = "invalid: yaml: content: ["
        gw = self._make_gateway(tmp_path, content)
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(
            gw,
            ["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"],
        )
        assert passed is True
        assert detail == ""

    def test_fail_open_empty_content(self, tmp_path):
        """空内容时 fail-open。"""
        gw = self._make_gateway(tmp_path, "")
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(
            gw,
            ["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"],
        )
        assert passed is True
        assert detail == ""

    def test_fail_open_no_project_root(self, tmp_path):
        """project_root 不可达时 fail-open。"""
        content = "entries: []"
        gw = self._make_gateway(None, content)
        gate = make_issue_resolved_integrity_gate()
        passed, detail = gate.check(
            gw,
            ["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"],
        )
        assert passed is True
        assert detail == ""

    def test_windows_path_normalization(self, tmp_path):
        """Windows 反斜杠路径归一化。"""
        content = """\
module_id: TEST
entries:
  - issue_id: '#ARCH-TEST-001'
    status: resolved
    impact:
      - src/nonexistent.py
"""
        gw = self._make_gateway(tmp_path, content)
        gate = make_issue_resolved_integrity_gate()
        # Windows 反斜杠路径
        passed, detail = gate.check(
            gw,
            ["docs\\01_policies_and_standards\\_registry\\catalogs\\architecture_issue_registry.yaml"],
        )
        assert passed is True  # warn-only
        assert "nonexistent.py" in detail
