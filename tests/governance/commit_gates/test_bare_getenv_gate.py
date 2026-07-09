# [A_test] module_id: SRC-TST-2228 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-bare_getenv_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_bare_getenv_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_bare_getenv_gate.py — NO-BARE-GETENV 门禁单测

权威依据：bare_getenv_gate.py（make_bare_getenv_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestBareGetenvVisitor: AST visitor 检测（os.getenv / os.environ.get / os.environ["..."]）
- TestGatewayIntegration: mock gateway 流程
  - 新增 .py 含裸 os.getenv("API_KEY") → 阻断 (passed=False)
  - 新增 .py 安全 → 放行
  - 变量参数豁免（os.getenv(key)）
  - tests/ 豁免
  - AST 语法错误 fail-open
  - git diff 失败/异常 fail-open

注意：gate 用 open(path).read() 未关闭（ResourceWarning），autouse fixture
注入 shadow open 包装为读取后自动关闭。
检测模式真源=SECRET_INDICATOR_PATTERNS（KEY/TOKEN/SECRET/PASSWORD/PASSWD/PWD/CREDENTIAL）。

测试隔离：MagicMock 模拟 gateway._run_git + tmp_path 真实文件，不读/不写真实仓库。
"""
from __future__ import annotations

import ast
import builtins
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.bare_getenv_gate import (  # noqa: E402
    _BareGetenvVisitor,
    make_bare_getenv_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, project_root=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回新增文件列表；rev-parse --show-toplevel
    返回 project_root。文件内容由 tmp_path 真实文件提供。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

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
        if "rev-parse" in cmd:
            return _MockResult(0, str(gw.project_root))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


@pytest.fixture(autouse=True)
def _shadow_open(monkeypatch):
    """源文件 open(abs_path).read() 未关闭（ResourceWarning），包装为读取后自动关闭。"""
    real_open = builtins.open

    class _ShadowFile:
        def __init__(self, fh):
            self._fh = fh

        def read(self, *a, **k):
            try:
                return self._fh.read(*a, **k)
            finally:
                self._fh.close()

        def readlines(self, *a, **k):
            try:
                return self._fh.readlines(*a, **k)
            finally:
                self._fh.close()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._fh.close()

        def __getattr__(self, name):
            return getattr(self._fh, name)

        def close(self):
            self._fh.close()

    def _shadowed_open(file, mode="r", *args, **kwargs):
        return _ShadowFile(real_open(file, mode, *args, **kwargs))

    monkeypatch.setattr(builtins, "open", _shadowed_open)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_bare_getenv_gate(), GateSpec)

    def test_gate_id(self):
        assert make_bare_getenv_gate().gate_id == "NO-BARE-GETENV"

    def test_priority(self):
        assert make_bare_getenv_gate().priority == 81


# ---------------------------------------------------------------------------
# TestBareGetenvVisitor — AST 检测纯函数
# ---------------------------------------------------------------------------
class TestBareGetenvVisitor:
    def _violations(self, code):
        tree = ast.parse(code)
        v = _BareGetenvVisitor()
        v.visit(tree)
        return v.violations

    def test_detects_os_getenv_secret(self):
        v = self._violations('import os\nx = os.getenv("API_KEY")')
        assert len(v) == 1
        assert v[0][1] == "os.getenv"
        assert v[0][2] == "API_KEY"

    def test_detects_os_environ_get_secret(self):
        v = self._violations('import os\nx = os.environ.get("SECRET_TOKEN")')
        assert len(v) == 1
        assert v[0][1] == "os.environ.get"
        assert v[0][2] == "SECRET_TOKEN"

    def test_detects_os_environ_subscript_secret(self):
        v = self._violations('import os\nx = os.environ["DB_PASSWORD"]')
        assert len(v) == 1
        assert v[0][1] == 'os.environ["..."]'
        assert v[0][2] == "DB_PASSWORD"

    def test_ignores_variable_arg(self):
        v = self._violations('import os\nkey = "API_KEY"\nx = os.getenv(key)')
        assert v == []  # 变量参数豁免

    def test_ignores_non_secret_key(self):
        v = self._violations('import os\nx = os.getenv("HOME")')
        assert v == []  # HOME 不含 SECRET 模式

    def test_ignores_other_module_getenv(self):
        v = self._violations('x = myobj.getenv("API_KEY")')
        assert v == []  # 非 os.getenv

    def test_detects_multiple_violations(self):
        code = (
            'import os\n'
            'a = os.getenv("API_KEY")\n'
            'b = os.environ.get("DB_PASSWORD")\n'
        )
        v = self._violations(code)
        assert len(v) == 2


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_py_with_bare_getenv_blocked(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text(
            'import os\nx = os.getenv("API_KEY")\n', encoding="utf-8"
        )
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert not passed
        assert "API_KEY" in msg or "getenv" in msg

    def test_new_py_safe_passes(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text("x = 1\n", encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_variable_arg_passes(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text(
            'import os\nkey = "API_KEY"\nx = os.getenv(key)\n', encoding="utf-8"
        )
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # 变量参数豁免
        assert msg == ""

    def test_os_environ_subscript_blocked(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text(
            'import os\nx = os.environ["DB_PASSWORD"]\n', encoding="utf-8"
        )
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert not passed
        assert "PASSWORD" in msg or "environ" in msg

    def test_tests_dir_exempt(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_x.py").write_text(
            'import os\nx = os.getenv("API_KEY")\n', encoding="utf-8"
        )
        rel = "tests/test_x.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # tests/ 豁免
        assert msg == ""

    def test_non_py_file_ignored(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.txt").write_text(
            'os.getenv("API_KEY")', encoding="utf-8"
        )
        rel = "src/mod.txt"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_syntax_error_fail_open(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text("def (\n", encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # AST 解析失败 fail-open
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(diff_fails=True, project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(diff_raises=True, project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_secret_getenv_passes(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text(
            'import os\nx = os.getenv("HOME")\n', encoding="utf-8"
        )
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # HOME 非密钥模式
        assert msg == ""

    def test_os_environ_get_blocked(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text(
            'import os\nx = os.environ.get("API_TOKEN")\n', encoding="utf-8"
        )
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert not passed
        assert "API_TOKEN" in msg or "environ" in msg
