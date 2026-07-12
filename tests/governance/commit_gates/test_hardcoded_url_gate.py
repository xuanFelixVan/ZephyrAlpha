# [A_test] module_id: SRC-TST-2226 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-hardcoded_url_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_hardcoded_url_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_hardcoded_url_gate.py — NO-HARDCODED-URL 门禁单测

权威依据：hardcoded_url_gate.py（make_hardcoded_url_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestPattern: _HARDCODED_LOCALHOST_RE 纯正则检测（命中/安全/边界/大小写/协议）
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含硬编码 localhost URL → 阻断 (passed=False)
  - 新增文件安全 → 放行 (passed=True)
  - tests/ 豁免
  - SSoT 文件 constants.py 豁免
  - docstring 行豁免
  - 注释行豁免
  - import 行豁免
  - fail-open on git diff 失败
  - fail-open on git diff 异常

注意：hardcoded_url 不做 AST 解析，按行扫描 added 行 + 正则匹配；
docstring/注释/import 行级豁免由 _extract_docstring_lines / _is_exempt_line 处理；
shared/foundation/constants.py 作为 SSoT 定义位置文件级豁免。

测试隔离：MagicMock 模拟 gateway._run_git，不读/不写真实仓库。
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

from zephyr.governance.commit_gates.hardcoded_url_gate import (  # noqa: E402
    _HARDCODED_LOCALHOST_RE,
    make_hardcoded_url_gate,
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
        gw._run_git = _raise
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

    gw._run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_hardcoded_url_gate(), GateSpec)

    def test_gate_id(self):
        assert make_hardcoded_url_gate().gate_id == "NO-HARDCODED-URL"

    def test_priority(self):
        assert make_hardcoded_url_gate().priority == 94


# ---------------------------------------------------------------------------
# TestPattern — _HARDCODED_LOCALHOST_RE 纯正则检测
# ---------------------------------------------------------------------------
class TestPattern:
    def test_http_localhost_match(self):
        assert _HARDCODED_LOCALHOST_RE.search("http://localhost:")

    def test_https_localhost_match(self):
        assert _HARDCODED_LOCALHOST_RE.search("https://localhost:")

    def test_http_localhost_with_port(self):
        assert _HARDCODED_LOCALHOST_RE.search("http://localhost:11434")

    def test_https_localhost_with_port(self):
        assert _HARDCODED_LOCALHOST_RE.search("https://localhost:11434")

    def test_url_in_string_literal(self):
        assert _HARDCODED_LOCALHOST_RE.search('URL = "http://localhost:8080"')

    def test_safe_example_com(self):
        assert not _HARDCODED_LOCALHOST_RE.search("http://example.com")

    def test_safe_localhost_no_colon(self):
        # 无冒号不匹配（端口分隔符是检测锚点）
        assert not _HARDCODED_LOCALHOST_RE.search("http://localhost")

    def test_safe_ftp_protocol(self):
        # 仅 http/https，ftp 不匹配
        assert not _HARDCODED_LOCALHOST_RE.search("ftp://localhost:")

    def test_case_sensitive_uppercase(self):
        # 正则小写，HTTP:// 不匹配
        assert not _HARDCODED_LOCALHOST_RE.search("HTTP://localhost:")

    def test_safe_no_url(self):
        assert not _HARDCODED_LOCALHOST_RE.search("no url here")


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_file_with_hardcoded_url_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'url = "http://localhost:11434"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert not passed
        assert "NO-HARDCODED-URL" in msg
        assert "localhost" in msg

    def test_new_file_https_url_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'url = "https://localhost:11434"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert not passed

    def test_new_file_safe_passes(self):
        blue = "src/zephyr/trading/mod.py"
        content = 'url = "http://example.com"\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self):
        red = "tests/governance/test_something.py"
        content = 'url = "http://localhost:11434"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_ssot_constants_exempt(self):
        red = "src/zephyr/shared/foundation/constants.py"
        content = 'DEFAULT_OLLAMA_URL = "http://localhost:11434"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed  # SSoT 定义位置文件级豁免
        assert msg == ""

    def test_docstring_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = (
            '"""module docstring\n'
            'url = "http://localhost:11434"\n'
            '"""\n'
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed  # docstring 内行豁免
        assert msg == ""

    def test_manifest_mode_url_not_exempt(self):
        """R95 修复：__manifest__ = \"\"\"...\"\"\" 模式中 URL 应被检测（不再被错误豁免）。

        旧 bug：__manifest__ 结束独立 \"\"\" 行被误判为新 docstring 起始，导致后续
        含硬编码 URL 的代码行被错误豁免。
        新方案：ast 只识别真正 docstring，__manifest__ 是 Assign 节点不豁免。
        """
        red = "src/zephyr/trading/mod.py"
        content = (
            '__manifest__ = """\n'
            'args: []\n'
            '"""\n'
            '\n'
            'url = "http://localhost:11434"\n'
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert not passed  # 应被阻断（R95 修复）
        assert "NO-HARDCODED-URL" in msg
        assert "localhost" in msg

    def test_comment_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = '# url = "http://localhost:11434"\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed  # 注释行豁免
        assert msg == ""

    def test_import_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = 'from x import y  # http://localhost:11434\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed  # import 行豁免
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_hardcoded_url_gate().check(gw, [])
        assert passed
        assert msg == ""
