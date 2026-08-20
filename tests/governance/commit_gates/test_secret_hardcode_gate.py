# [A_test] module_id: MOD-GOV_secret_hardcode_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SECRET_HARDCODE_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_secret_hardcode_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_SECRET_HARDCODE_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_secret_hardcode_gate.py — NO-SECRET-HARDCODE 门禁单测

权威依据：secret_hardcode_gate.py（make_secret_hardcode_gate）
#ARCH-SECRETS-GOV-001 Phase 3（密钥治理纵深防御）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestPatterns: SECRET_PATTERNS_DEEP 纯正则检测（P0 高置信度格式 + KEY=value）
- TestGatewayIntegration: mock gateway 流程
  - 新增 .py 含 sk- OpenAI key → 阻断
  - 新增 .py 含 AKIA AWS key → 阻断
  - 新增 .py 含 ghp_ GitHub token → 阻断
  - 新增 .py 含 API_KEY="value" → 阻断
  - 新增 .py 含 password="value" → 阻断
  - 新增 .py 含 database_url 带密码 → 阻断（P1）
  - 新增 .py 安全 → 放行
  - YAML 配置含 api_key: "value" → 阻断
  - JSON 配置含 sk- 值 → 阻断
  - tests/ 豁免
  - .env.example 豁免
  - 扫描脚本 scan_secret_leak.py 自身豁免
  - gate 自身 secret_hardcode_gate.py 豁免
  - docstring 行豁免（.py）
  - 注释行豁免
  - import 行豁免
  - fail-open on git diff 失败
  - fail-open on git diff 异常
  - 多文件混合（一违规一安全）→ 阻断并报告违规文件

测试隔离：MagicMock 模拟 gateway.run_git，不读/不写真实仓库。
mock 真源：test_hardcoded_url_gate.py._make_gateway（同 _diff_helpers 模式）。
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

from zephyr.gov_enforcement.commit_gates.secret_hardcode_gate import (  # noqa: E402
    _SECRET_PATTERNS_DEEP,
    make_secret_hardcode_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, file_contents=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回文件列表；git show :path 返回文件内容；
    per-file diff 视为全文件新增（行号 1..N 与文件内容对齐）。

    真源：test_hardcoded_url_gate.py._make_gateway（同 _diff_helpers 调用模式）。
    """
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
        assert isinstance(make_secret_hardcode_gate(), GateSpec)

    def test_gate_id(self):
        assert make_secret_hardcode_gate().gate_id == "NO-SECRET-HARDCODE"

    def test_priority(self):
        # 128 = SECRET-REGISTRY-CONSISTENCY(127) 之后、CAPABILITY-OVERLAP(200) 之前
        assert make_secret_hardcode_gate().priority == 128


# ---------------------------------------------------------------------------
# TestPatterns — SECRET_PATTERNS_DEEP 纯正则检测
# ---------------------------------------------------------------------------
class TestPatterns:
    """验证每个 P0 高置信度格式能被对应正则命中。"""

    def test_openai_sk_key_match(self):
        # sk- + 32 alphanumerics
        red = "sk-" + "a" * 32
        assert any(p[0].search(red) for p in _SECRET_PATTERNS_DEEP)

    def test_aws_akia_match(self):
        # AKIA + 16 uppercase alphanumerics
        red = "AKIA" + "ABCDEFGHJKLMNPQRSTUVWXYZ"[:16]
        assert any(p[0].search(red) for p in _SECRET_PATTERNS_DEEP)

    def test_github_token_match(self):
        # ghp_ + 36 chars
        red = "ghp_" + "a" * 36
        assert any(p[0].search(red) for p in _SECRET_PATTERNS_DEEP)

    def test_api_key_assignment_match(self):
        red = 'api_key = "12345678abcdef"'
        assert any(p[0].search(red) for p in _SECRET_PATTERNS_DEEP)

    def test_password_assignment_match(self):
        red = 'password = "abc"'
        assert any(p[0].search(red) for p in _SECRET_PATTERNS_DEEP)

    def test_safe_no_secret(self):
        blue = "x = 1 + 2\nprint('hello world')"
        assert not any(p[0].search(blue) for p in _SECRET_PATTERNS_DEEP)

    def test_safe_short_value_not_match(self):
        # api_key 值 < 8 字符不匹配（{8,} 下限）
        blue = 'api_key = "short"'
        assert not any(p[0].search(blue) for p in _SECRET_PATTERNS_DEEP)


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_py_with_openai_key_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'OPENAI_KEY = "sk-' + "a" * 32 + '"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "NO-SECRET-HARDCODE" in msg
        assert "sk-" in msg or "OpenAI" in msg

    def test_new_py_with_aws_key_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'AWS_KEY = "AKIA' + "ABCDEFGHJKLMNPQRSTUVWXYZ"[:16] + '"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "AKIA" in msg or "AWS" in msg

    def test_new_py_with_github_token_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'GH_TOKEN = "ghp_' + "a" * 36 + '"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "ghp_" in msg or "GitHub" in msg

    def test_new_py_with_api_key_assignment_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'api_key = "12345678abcdef"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "API Key" in msg

    def test_new_py_with_password_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'password = "s3cret_pass"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "Password" in msg

    def test_new_py_with_database_url_p1_blocked(self):
        """P1 模式（数据库连接串含密码）也阻断——全阻断策略（warn 升级 block）。"""
        red = "src/zephyr/trading/mod.py"
        content = 'DATABASE_URL = "postgres://user:pass@host:5432/db"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "P1" in msg or "数据库" in msg

    def test_new_py_safe_passes(self):
        blue = "src/zephyr/trading/mod.py"
        content = 'x = 1\nprint("hello")\nTOKEN = get_required_secret("TOKEN")\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_yaml_config_with_api_key_blocked(self):
        red = "src/zephyr/data/config/secrets.yaml"
        content = 'api_key: "12345678abcdef"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "API Key" in msg

    def test_json_config_with_openai_value_blocked(self):
        red = "src/zephyr/data/config/keys.json"
        content = '{"openai": "sk-' + "a" * 32 + '"}\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "OpenAI" in msg or "sk-" in msg

    def test_tests_dir_exempt(self):
        red = "tests/governance/test_something.py"
        content = 'api_key = "12345678abcdef"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed  # tests/ 豁免
        assert msg == ""

    def test_env_example_exempt(self):
        red = ".env.example"
        content = "TUSHARE_TOKEN=sk-1234567890abcdef1234567890abcdef\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed  # .env.example 豁免
        assert msg == ""

    def test_scan_secret_leak_script_exempt(self):
        """扫描脚本自身含模式字面量，必须豁免（否则自检误报）。"""
        red = "scripts/governance/d6_security/scan_secret_leak.py"
        content = 'SECRET_PATTERNS = [(re.compile(r"sk-[a-zA-Z0-9]{32,}"), "OpenAI")]\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed  # 扫描脚本自身豁免
        assert msg == ""

    def test_gate_self_exempt(self):
        """gate 自身含模式字面量，必须豁免。"""
        red = "src/zephyr/gov_enforcement/commit_gates/secret_hardcode_gate.py"
        content = '_PATTERN = re.compile(r"sk-[a-zA-Z0-9]{32,}")\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed  # gate 自身豁免
        assert msg == ""

    def test_docstring_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = '"""module docstring\napi_key = "12345678abcdef"\n"""\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed  # docstring 内行豁免
        assert msg == ""

    def test_comment_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = '# api_key = "12345678abcdef"\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed  # 注释行豁免
        assert msg == ""

    def test_import_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = "from x import api_key  # noqa\n"
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed  # import 行豁免
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_mixed_files_reports_only_violation(self):
        """一违规一安全混合 → 阻断并仅报告违规文件。"""
        red = "src/zephyr/trading/bad.py"
        blue = "src/zephyr/trading/good.py"
        gw = _make_gateway(
            staged_files=[red, blue],
            file_contents={
                red: 'api_key = "12345678abcdef"\n',
                blue: "x = 1\n",
            },
        )
        passed, msg = make_secret_hardcode_gate().check(gw, [])
        assert not passed
        assert "bad.py" in msg
        assert "good.py" not in msg
