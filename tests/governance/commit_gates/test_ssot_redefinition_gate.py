# [A_test] module_id: SRC-TST-2106 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-ssot_redefinition_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_ssot_redefinition_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁单测（SSOT-REDEFINITION）

权威依据：ssot_redefinition_gate.py（make_ssot_redefinition_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsSsotSymbol: _is_ssot_symbol 筛选规则（Python 标识符 + 含大写字母）
- TestRedefinitionBlocked: class 定义 / 变量赋值重定义 → 阻断
- TestCanonicalExemption: canonical 文件本身定义 → 通过
- TestImportExemption: import 语句 → 通过
- TestCommentExemption: 注释行 → 通过
- TestDocstringExemption: docstring 行 → 通过
- TestTestExempt: tests/ 下文件 → 通过
- TestNonPyFile: 非 .py 文件 → 通过
- TestNoStagedFile: 空 staged → 通过
- TestFailClosedRegistryMissing: registry 缺失 → 阻断（fail-closed）
- TestFailClosedRegistryUnparseable: registry 解析失败 → 阻断（fail-closed）
- TestRegistryStagedExemption: registry 在 staged 中（正在修复）→ 通过
- TestFailOpenGitDiffFails: git diff 失败 → 通过（fail-open）
- TestUnrelatedSymbolPasses: 无关符号 → 通过

测试隔离：使用 monkeypatch 改 REGISTRY_YAML 指向 tmp_path 下临时 yaml；
MagicMock 模拟 gateway._run_git 返回预设 staged 文件列表 + diff content；
不读/不写真实仓库，不依赖真实 registry。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.ssot_redefinition_gate import (  # noqa: E402
    _is_ssot_symbol,
    make_ssot_redefinition_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


# ============================================================================
# 测试用 registry YAML（含 rule_patterns_ssot capability）
# ============================================================================

_REGISTRY_YAML = """\
capabilities:
  - capability_id: rule_patterns_ssot
    canonical_override: src/zephyr/governance/rule_patterns.py
    aliases:
      - rule_patterns
      - security_patterns
      - MODULE_ID_RE
      - DIGIT_SUFFIX_RE
      - RULE_NAME_RE
      - PIICategory
      - POISONING_INDICATORS
      - PII_PATTERNS
    description: 测试用 SSoT 真源
"""


@pytest.fixture
def setup_registry(tmp_path, monkeypatch):
    """在 tmp_path 下创建 registry.yaml 并 monkeypatch REGISTRY_YAML 指向它。"""
    registry_path = tmp_path / "capability_registry.yaml"
    registry_path.write_text(_REGISTRY_YAML, encoding="utf-8")
    from zephyr.governance import capability_lookup
    monkeypatch.setattr(capability_lookup, "REGISTRY_YAML", registry_path)
    return registry_path


def _make_mock_gateway(staged_files: list[str], file_diffs: dict[str, list[str]]) -> MagicMock:
    """构造 mock gateway，_run_git 根据 cmd 返回预设结果。

    Args:
        staged_files: git diff --name-only 返回的文件列表（相对路径）
        file_diffs: {py_file: [added_line1, added_line2, ...]}
    """
    gw = MagicMock()

    def _run_git(cmd):
        result = MagicMock()
        if "--name-only" in cmd:
            result.returncode = 0
            result.stdout = "\n".join(staged_files)
            return result
        # per-file diff: cmd[-1] 是 py_file
        py_file = cmd[-1].replace("\\", "/")
        lines = file_diffs.get(py_file, [])
        diff_lines = [f"+++ b/{py_file}", f"@@ -0,0 +1,{len(lines)} @@"]
        diff_lines.extend(f"+{l}" for l in lines)
        result.returncode = 0
        result.stdout = "\n".join(diff_lines)
        return result

    gw._run_git.side_effect = _run_git
    return gw


# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    def test_gate_id(self):
        gate = make_ssot_redefinition_gate()
        assert gate.gate_id == "SSOT-REDEFINITION"

    def test_priority(self):
        gate = make_ssot_redefinition_gate()
        assert gate.priority == 65

    def test_is_gatespec(self):
        gate = make_ssot_redefinition_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestIsSsotSymbol
# ============================================================================


class TestIsSsotSymbol:
    def test_pascal_case(self):
        assert _is_ssot_symbol("PIICategory")

    def test_upper_snake(self):
        assert _is_ssot_symbol("MODULE_ID_RE")
        assert _is_ssot_symbol("POISONING_INDICATORS")
        assert _is_ssot_symbol("PII_PATTERNS")
        assert _is_ssot_symbol("DIGIT_SUFFIX_RE")
        assert _is_ssot_symbol("RULE_NAME_RE")

    def test_lowercase_filename_not_symbol(self):
        assert not _is_ssot_symbol("rule_patterns")
        assert not _is_ssot_symbol("security_patterns")

    def test_non_identifier(self):
        assert not _is_ssot_symbol("foo-bar")
        assert not _is_ssot_symbol("123abc")
        assert not _is_ssot_symbol("")

    def test_single_upper(self):
        assert _is_ssot_symbol("X")


# ============================================================================
# TestRedefinitionBlocked (红队)
# ============================================================================


class TestRedefinitionBlocked:
    def test_class_definition_blocked(self, setup_registry):
        red_file = "src/zephyr/governance/semantic_audit/privacy.py"
        gw = _make_mock_gateway(
            [red_file],
            {red_file: ["class PIICategory(str):", "    EMAIL = 'email'"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "PIICategory" in detail
        assert "canonical" in detail.lower()
        assert "SSoT" in detail

    def test_assignment_blocked(self, setup_registry):
        red_file = "src/zephyr/governance/audit_trail/kb_gate.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["POISONING_INDICATORS = []"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "POISONING_INDICATORS" in detail

    def test_type_annotation_blocked(self, setup_registry):
        red_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["PII_PATTERNS: dict = {}"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "PII_PATTERNS" in detail

    def test_multiple_violations_all_reported(self, setup_registry):
        red_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [red_file],
            {red_file: ["class PIICategory(str):", "POISONING_INDICATORS = []"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "PIICategory" in detail
        assert "POISONING_INDICATORS" in detail


# ============================================================================
# TestCanonicalExemption (蓝队)
# ============================================================================


class TestCanonicalExemption:
    def test_canonical_file_definition_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/rule_patterns.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["class PIICategory(str, Enum):", "    EMAIL = 'email'"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed

    def test_canonical_file_assignment_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/rule_patterns.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["POISONING_INDICATORS: list = []"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed


# ============================================================================
# TestImportExemption (蓝队)
# ============================================================================


class TestImportExemption:
    def test_from_import_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["from zephyr.governance.rule_patterns import PIICategory"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed

    def test_plain_import_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["import PIICategory"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed


# ============================================================================
# TestCommentExemption (蓝队)
# ============================================================================


class TestCommentExemption:
    def test_comment_class_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["# class PIICategory was here"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed

    def test_comment_assignment_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["# PIICategory = ..."]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed


# ============================================================================
# TestDocstringExemption (蓝队)
# ============================================================================


class TestDocstringExemption:
    def test_docstring_with_symbol_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        # docstring 行首是 ''' 或 """
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ['"""PIICategory docs"""', "class PIICategory(str):"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, detail = gate.check(gw, [])
        # docstring 行豁免，但后续 class 定义行应阻断
        assert not passed
        assert "PIICategory" in detail


# ============================================================================
# TestTestExempt (蓝队)
# ============================================================================


class TestTestExempt:
    def test_tests_dir_passes(self, setup_registry):
        blue_file = "tests/governance/test_something.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["class PIICategory(str):"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed


# ============================================================================
# TestNonPyFile
# ============================================================================


class TestNonPyFile:
    def test_yaml_file_passes(self, setup_registry):
        gw = _make_mock_gateway(
            ["docs/registry.yaml"], {"docs/registry.yaml": ["PIICategory: foo"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed

    def test_md_file_passes(self, setup_registry):
        gw = _make_mock_gateway(
            ["docs/readme.md"], {"docs/readme.md": ["# PIICategory"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed


# ============================================================================
# TestNoStagedFile
# ============================================================================


class TestNoStagedFile:
    def test_empty_staged_passes(self, setup_registry):
        gw = _make_mock_gateway([], {})
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed

    def test_no_py_file_passes(self, setup_registry):
        gw = _make_mock_gateway(["docs/notes.md"], {})
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed


# ============================================================================
# TestFailClosedRegistryMissing
# ============================================================================


class TestFailClosedRegistryMissing:
    def test_registry_missing_blocks(self, tmp_path, monkeypatch):
        # registry 文件不存在 → fail-closed（阻断）
        missing_path = tmp_path / "nonexistent.yaml"
        from zephyr.governance import capability_lookup
        monkeypatch.setattr(capability_lookup, "REGISTRY_YAML", missing_path)
        gw = _make_mock_gateway(
            ["src/zephyr/governance/some_module.py"],
            {"src/zephyr/governance/some_module.py": ["class PIICategory(str):"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, detail = gate.check(gw, [])
        assert not passed  # fail-closed
        assert "fail-closed" in detail
        assert "缺失" in detail


# ============================================================================
# TestFailClosedRegistryUnparseable
# ============================================================================


class TestFailClosedRegistryUnparseable:
    def test_unparseable_registry_blocks(self, tmp_path, monkeypatch):
        # registry 解析失败 → fail-closed（阻断）
        bad_path = tmp_path / "bad.yaml"
        bad_path.write_text("{{not valid yaml: [unclosed", encoding="utf-8")
        from zephyr.governance import capability_lookup
        monkeypatch.setattr(capability_lookup, "REGISTRY_YAML", bad_path)
        gw = _make_mock_gateway(
            ["src/zephyr/governance/some_module.py"],
            {"src/zephyr/governance/some_module.py": ["class PIICategory(str):"]},
        )
        gate = make_ssot_redefinition_gate()
        passed, detail = gate.check(gw, [])
        assert not passed  # fail-closed
        assert "fail-closed" in detail
        assert "解析失败" in detail


# ============================================================================
# TestRegistryStagedExemption (registry 在 staged 中正在修复 → 放行)
# ============================================================================


class TestRegistryStagedExemption:
    def test_missing_registry_in_staged_passes(self, tmp_path, monkeypatch):
        # registry 缺失但本身在 staged 中（正在修复）→ 放行
        registry_path = tmp_path / "capability_canonical_file_registry.yaml"
        # 不创建文件（缺失）
        from zephyr.governance import capability_lookup
        monkeypatch.setattr(capability_lookup, "REGISTRY_YAML", registry_path)
        gw = _make_mock_gateway(
            [
                "capability_canonical_file_registry.yaml",
                "src/zephyr/governance/some_module.py",
            ],
            {"src/zephyr/governance/some_module.py": ["class PIICategory(str):"]},
        )
        gw.project_root = tmp_path  # 使 relative_to 可解析
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed  # registry 正在修复

    def test_unparseable_registry_in_staged_passes(self, tmp_path, monkeypatch):
        # registry 解析失败但本身在 staged 中（正在修复）→ 放行
        registry_path = tmp_path / "capability_canonical_file_registry.yaml"
        registry_path.write_text("{{broken", encoding="utf-8")
        from zephyr.governance import capability_lookup
        monkeypatch.setattr(capability_lookup, "REGISTRY_YAML", registry_path)
        gw = _make_mock_gateway(
            [
                "capability_canonical_file_registry.yaml",
                "src/zephyr/governance/some_module.py",
            ],
            {"src/zephyr/governance/some_module.py": ["class PIICategory(str):"]},
        )
        gw.project_root = tmp_path  # 使 relative_to 可解析
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed  # registry 正在修复


# ============================================================================
# TestFailOpenGitDiffFails
# ============================================================================


class TestFailOpenGitDiffFails:
    def test_git_diff_name_only_fails_passes(self, setup_registry):
        gw = MagicMock()
        result = MagicMock()
        result.returncode = 1
        result.stdout = ""
        gw._run_git.return_value = result
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed  # fail-open

    def test_git_diff_exception_passes(self, setup_registry):
        gw = MagicMock()
        gw._run_git.side_effect = RuntimeError("git not found")
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed  # fail-open


# ============================================================================
# TestUnrelatedSymbolPasses (蓝队)
# ============================================================================


class TestUnrelatedSymbolPasses:
    def test_unrelated_class_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["class MyLocalClass:"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed

    def test_unrelated_var_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["MY_LOCAL_VAR = 42"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed

    def test_lowercase_var_passes(self, setup_registry):
        blue_file = "src/zephyr/governance/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["pii_category = None"]}
        )
        gate = make_ssot_redefinition_gate()
        passed, _ = gate.check(gw, [])
        assert passed  # 小写不是 SSoT 符号
