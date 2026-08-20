# [A_test] module_id: MOD-GOV_domain_name_zh_direct_access_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_domain_name_zh_direct_access_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_domain_name_zh_direct_access_gate.py — NO-DOMAIN-NAME-ZH-DIRECT-ACCESS 门禁单测

权威依据：domain_name_zh_direct_access_gate.py（make_domain_name_zh_direct_access_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestPattern: _DIRECT_ACCESS_RE 纯正则检测（命中/安全/边界/方法变体）
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含 DOMAIN_NAME_ZH.get(...) → 阻断 (passed=False)
  - 新增文件含 DOMAIN_NAME_ZH[key] → 阻断
  - 新增文件安全（用 helper）→ 放行
  - tests/ 豁免
  - SSoT 文件 domain_name_mapping.py 豁免（合法直接访问）
  - docstring 行豁免
  - 注释行豁免
  - import 行豁免
  - fail-open on git diff 失败
  - fail-open on git diff 异常

测试隔离：MagicMock 模拟 gateway.run_git，不读/不写真实仓库。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.domain_name_zh_direct_access_gate import (  # noqa: E402
    _DIRECT_ACCESS_RE,
    make_domain_name_zh_direct_access_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, file_contents=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回文件列表；git show :path 返回文件内容；
    per-file diff 视为全文件新增（行号 1..N 与文件内容对齐）。"""
    gw = MagicMock()
    gw.project_root = str(_PROJECT_ROOT)

    if diff_raises:

        def _raise(*a, **k):
            raise RuntimeError("git not found")

        gw.run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if len(cmd) >= 3 and cmd[1] == "show" and cmd[2].startswith(":"):
            py_file = cmd[2][1:].replace("\\", "/")
            return _MockResult(0, (file_contents or {}).get(py_file, ""))
        py_file = cmd[-1].replace("\\", "/")
        content = (file_contents or {}).get(py_file, "")
        lines = content.splitlines()
        if not lines:
            return _MockResult(0, f"+++ b/{py_file}")
        diff_lines = [f"+++ b/{py_file}", f"@@ -0,0 +1,{len(lines)} @@"]
        diff_lines.extend(f"+{ln}" for ln in lines)
        return _MockResult(0, "\n".join(diff_lines))

    gw.run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_domain_name_zh_direct_access_gate(), GateSpec)

    def test_gate_id(self):
        assert make_domain_name_zh_direct_access_gate().gate_id == "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS"

    def test_priority(self):
        assert make_domain_name_zh_direct_access_gate().priority == 72


# ---------------------------------------------------------------------------
# TestPattern — _DIRECT_ACCESS_RE 纯正则检测
# ---------------------------------------------------------------------------
class TestPattern:
    def test_get_method_match(self):
        assert _DIRECT_ACCESS_RE.search("ext_name_zh = DOMAIN_NAME_ZH.get(ext, '')")

    def test_subscript_match(self):
        assert _DIRECT_ACCESS_RE.search("name = DOMAIN_NAME_ZH['D_FACTOR']")

    def test_pop_method_match(self):
        assert _DIRECT_ACCESS_RE.search("DOMAIN_NAME_ZH.pop('D-T3-W0')")

    def test_items_method_match(self):
        assert _DIRECT_ACCESS_RE.search("for k, v in DOMAIN_NAME_ZH.items():")

    def test_keys_method_match(self):
        assert _DIRECT_ACCESS_RE.search("keys = DOMAIN_NAME_ZH.keys()")

    def test_values_method_match(self):
        assert _DIRECT_ACCESS_RE.search("vals = DOMAIN_NAME_ZH.values()")

    def test_with_whitespace(self):
        assert _DIRECT_ACCESS_RE.search("DOMAIN_NAME_ZH .get('D_FACTOR')")

    def test_safe_helper_call(self):
        # 调用 helper 函数（get_domain_name_zh）不应匹配
        assert not _DIRECT_ACCESS_RE.search("name = get_domain_name_zh('D_FACTOR')")

    def test_safe_strict_helper_call(self):
        assert not _DIRECT_ACCESS_RE.search("name = get_domain_name_zh_strict('D_FACTOR')")

    def test_safe_variable_similar_name(self):
        # DOMAIN_NAME_ZH_X 等扩展名不应匹配（词边界保护）
        assert not _DIRECT_ACCESS_RE.search("DOMAIN_NAME_ZH_CACHE['D_FACTOR']")

    def test_safe_comment_about_dict(self):
        # 注释中的 DOMAIN_NAME_ZH 文字不应被正则排除（注释豁免由 _is_exempt_line 处理）
        # 这里测正则本身——正则会匹配，但上层会豁免注释行
        assert _DIRECT_ACCESS_RE.search("# uses DOMAIN_NAME_ZH.get() internally")

    def test_safe_no_dict_reference(self):
        assert not _DIRECT_ACCESS_RE.search("name = 'D_FACTOR'")

    def test_assignment_not_matched_by_regex(self):
        # DOMAIN_NAME_ZH = {...} 赋值不被本正则匹配（由 SSOT-REDEFINITION gate 管辖）
        assert not _DIRECT_ACCESS_RE.search("DOMAIN_NAME_ZH = {")


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_file_with_get_blocked(self):
        red = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "ext_name_zh = DOMAIN_NAME_ZH.get(ext, '')\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert not passed
        assert "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS" in msg
        assert "DOMAIN_NAME_ZH" in msg

    def test_new_file_with_subscript_blocked(self):
        red = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "name = DOMAIN_NAME_ZH['D_FACTOR']\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert not passed

    def test_new_file_with_items_blocked(self):
        red = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "for k, v in DOMAIN_NAME_ZH.items():\n    print(k)\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert not passed

    def test_new_file_safe_helper_passes(self):
        blue = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = (
            "from domain_name_mapping import get_domain_name_zh_strict\next_name_zh = get_domain_name_zh_strict(ext)\n"
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self):
        red = "tests/governance/test_something.py"
        content = "name = DOMAIN_NAME_ZH.get('D_FACTOR', '')\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed  # tests/ 豁免
        assert msg == ""

    def test_ssot_definition_file_exempt(self):
        """domain_name_mapping.py 是 DOMAIN_NAME_ZH 的 SSoT 定义位置，
        其内部访问 DOMAIN_NAME_ZH.get(domain_id, ...) 是合法的 fallback 逻辑。"""
        ssot = "scripts/governance/d5_architecture/generators/domain_name_mapping.py"
        content = (
            "def get_domain_name_zh(domain_id, fallback=''):\n"
            "    return DOMAIN_NAME_ZH.get(domain_id, fallback or domain_id)\n"
        )
        gw = _make_gateway(staged_files=[ssot], file_contents={ssot: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed  # SSoT 定义位置文件级豁免
        assert msg == ""

    def test_docstring_line_exempt(self):
        blue = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = '"""module docstring\nDOMAIN_NAME_ZH.get(ext, \'\') is legacy pattern\n"""\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed  # docstring 内行豁免
        assert msg == ""

    def test_comment_line_exempt(self):
        blue = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "# legacy: DOMAIN_NAME_ZH.get(ext, '')\n"
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed  # 注释行豁免
        assert msg == ""

    def test_import_line_exempt(self):
        blue = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        # 即使 import 行含 DOMAIN_NAME_ZH（不合理但应被豁免）
        content = "from domain_name_mapping import DOMAIN_NAME_ZH\n"
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed  # import 行豁免（但会被其他 gate 阻断，如 SSOT-REDEFINITION）
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        red = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "name = DOMAIN_NAME_ZH.get(ext, '')\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content}, diff_fails=True)
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed  # fail-open（git diff 不可达，检测器失效，不阻断）
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        red = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "name = DOMAIN_NAME_ZH.get(ext, '')\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content}, diff_raises=True)
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed  # fail-open（git diff 异常，检测器失效，不阻断）
        assert msg == ""

    def test_no_staged_files_passes(self):
        gw = _make_gateway(staged_files=[], file_contents={})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_multiple_violations_all_reported(self):
        red = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "a = DOMAIN_NAME_ZH.get(ext, '')\nb = DOMAIN_NAME_ZH['D_FACTOR']\nc = DOMAIN_NAME_ZH.items()\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert not passed
        # 3 处违规都应在 detail 中
        assert msg.count(red) == 3

    def test_error_message_includes_fix_guidance(self):
        red = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        content = "name = DOMAIN_NAME_ZH.get(ext, '')\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_domain_name_zh_direct_access_gate().check(gw, [])
        assert not passed
        # 修复指引：改用 helper
        assert "get_domain_name_zh" in msg
        assert "get_domain_name_zh_strict" in msg
