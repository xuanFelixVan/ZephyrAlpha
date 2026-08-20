# [A_test] module_id: MOD-GOV_bare_getenv_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_BARE_GETENV_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_bare_getenv_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_BARE_GETENV_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_bare_getenv_gate.py — NO-BARE-GETENV 门禁单测

权威依据：bare_getenv_gate.py（make_bare_getenv_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestBareGetenvVisitor: AST visitor 检测（os.getenv / os.environ.get / os.environ["..."]）
- TestGatewayIntegration: mock gateway 流程（新增文件全文件扫描）
  - 新增 .py 含裸 os.getenv("API_KEY") → 阻断 (passed=False)
  - 新增 .py 安全 → 放行
  - 变量参数豁免（os.getenv(key)）
  - tests/ 豁免
  - AST 语法错误 fail-open
  - git diff 失败/异常 fail-open
- TestDiffAwareModifiedFiles: diff-aware 修改文件检测（#ARCH-SECRETS-GOV-001 Phase 2-S3）
  - 修改文件新增行含裸 getenv → 阻断
  - 修改文件存量行含裸 getenv → 放行（不触碰存量基线）
  - 修改文件无新增行违规 → 放行
  - -U0 git diff 失败 → fail-open（跳过该文件）
  - 新增+修改文件混合 → 各自检测

注意：gate 用 open(path).read() 未关闭（ResourceWarning），autouse fixture
注入 shadow open 包装为读取后自动关闭。
检测模式真源=SECRET_INDICATOR_PATTERNS（KEY/TOKEN/SECRET/PASSWORD/PASSWD/PWD/CREDENTIAL）。

测试隔离：MagicMock 模拟 gateway.run_git + tmp_path 真实文件，不读/不写真实仓库。
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

from zephyr.gov_enforcement.commit_gates.bare_getenv_gate import (  # noqa: E402
    _BareGetenvVisitor,
    make_bare_getenv_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(
    staged_files=None,
    project_root=None,
    diff_fails=False,
    diff_raises=False,
    modified_files=None,
    added_lines=None,
    u0_fails=False,
):
    """构造 mock gateway。

    --name-status 返回 staged（A）+ modified（M）文件列表；
    -U0 返回修改文件的 diff 输出（新增行）；
    rev-parse 返回 project_root。
    文件内容由 tmp_path 真实文件提供。

    Args:
        staged_files: 新增文件路径列表（A 状态，纯路径）。
        modified_files: 修改文件路径列表（M 状态，纯路径）。
        added_lines: {file_path: diff_output} 修改文件的 -U0 diff 输出。
        diff_fails: --name-status 返回 rc=1（gate fail-open）。
        diff_raises: run_git 抛异常（gate fail-open）。
        u0_fails: -U0 返回 rc=1（修改文件跳过检测）。
    """
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:

        def _raise(*a, **k):
            raise RuntimeError("git not found")

        gw.run_git = _raise
        return gw

    # 构建 --name-status 输出（A\tpath / M\tpath）
    name_status_lines = []
    for f in staged_files or []:
        name_status_lines.append(f"A\t{f}")
    for f in modified_files or []:
        name_status_lines.append(f"M\t{f}")
    name_status_output = "\n".join(name_status_lines)

    def _run_git(cmd):
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        if diff_fails and "--name-status" in cmd_str:
            return _MockResult(1, "")
        if "--name-status" in cmd_str:
            return _MockResult(0, name_status_output)
        if "-U0" in cmd_str:
            if u0_fails:
                return _MockResult(1, "")
            # 提取 file_path: ["git", "diff", "--cached", "-U0", "--", path]
            file_path = ""
            if "--" in cmd:
                idx = cmd.index("--")
                if idx + 1 < len(cmd):
                    file_path = cmd[idx + 1].replace("\\", "/")
            return _MockResult(0, (added_lines or {}).get(file_path, ""))
        if "rev-parse" in cmd_str:
            return _MockResult(0, str(gw.project_root))
        return _MockResult(0, "")

    gw.run_git = _run_git
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
        code = 'import os\na = os.getenv("API_KEY")\nb = os.environ.get("DB_PASSWORD")\n'
        v = self._violations(code)
        assert len(v) == 2


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_py_with_bare_getenv_blocked(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text('import os\nx = os.getenv("API_KEY")\n', encoding="utf-8")
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
        (src / "mod.py").write_text('import os\nkey = "API_KEY"\nx = os.getenv(key)\n', encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # 变量参数豁免
        assert msg == ""

    def test_os_environ_subscript_blocked(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text('import os\nx = os.environ["DB_PASSWORD"]\n', encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert not passed
        assert "PASSWORD" in msg or "environ" in msg

    def test_tests_dir_exempt(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_x.py").write_text('import os\nx = os.getenv("API_KEY")\n', encoding="utf-8")
        rel = "tests/test_x.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # tests/ 豁免
        assert msg == ""

    def test_non_py_file_ignored(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.txt").write_text('os.getenv("API_KEY")', encoding="utf-8")
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
        (src / "mod.py").write_text('import os\nx = os.getenv("HOME")\n', encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # HOME 非密钥模式
        assert msg == ""

    def test_os_environ_get_blocked(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text('import os\nx = os.environ.get("API_TOKEN")\n', encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert not passed
        assert "API_TOKEN" in msg or "environ" in msg


# ---------------------------------------------------------------------------
# TestDiffAwareModifiedFiles — diff-aware 修改文件检测
# （#ARCH-SECRETS-GOV-001 Phase 2-S3）
# ---------------------------------------------------------------------------
class TestDiffAwareModifiedFiles:
    """diff-aware 修改文件检测——只报告 git diff 新增行中的违规。"""

    def test_modified_new_line_with_bare_getenv_blocked(self, tmp_path):
        """修改文件新增行含裸 getenv → 阻断。"""
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text('import os\nx = os.getenv("API_KEY")\ny = 1\n', encoding="utf-8")
        rel = "src/mod.py"
        # diff: 第 2 行是新增行（+ 前缀）
        diff_output = '@@ -1,1 +1,3 @@\n import os\n+x = os.getenv("API_KEY")\n+y = 1\n'
        gw = _make_gateway(
            modified_files=[rel],
            added_lines={rel: diff_output},
            project_root=str(tmp_path),
        )
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert not passed
        assert "API_KEY" in msg or "getenv" in msg

    def test_modified_existing_line_with_bare_getenv_passes(self, tmp_path):
        """修改文件存量行含裸 getenv → 放行（不触碰存量基线）。"""
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text('import os\nx = os.getenv("API_KEY")\ny = 2\n', encoding="utf-8")
        rel = "src/mod.py"
        # diff: 第 2 行是 context（存量），第 3 行是新增行
        diff_output = '@@ -1,2 +1,3 @@\n import os\n x = os.getenv("API_KEY")\n+y = 2\n'
        gw = _make_gateway(
            modified_files=[rel],
            added_lines={rel: diff_output},
            project_root=str(tmp_path),
        )
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # 存量行违规不报告
        assert msg == ""

    def test_modified_no_violation_passes(self, tmp_path):
        """修改文件新增行安全 → 放行。"""
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text("import os\nx = 1\n", encoding="utf-8")
        rel = "src/mod.py"
        diff_output = "@@ -1,1 +1,2 @@\n import os\n+x = 1\n"
        gw = _make_gateway(
            modified_files=[rel],
            added_lines={rel: diff_output},
            project_root=str(tmp_path),
        )
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_u0_diff_fails_fail_open(self, tmp_path):
        """-U0 git diff 失败 → fail-open（跳过该文件检测）。"""
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text('import os\nx = os.getenv("API_KEY")\n', encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(
            modified_files=[rel],
            u0_fails=True,
            project_root=str(tmp_path),
        )
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert passed  # -U0 失败，跳过检测
        assert msg == ""

    def test_added_and_modified_mixed(self, tmp_path):
        """新增+修改文件混合 → 各自检测。"""
        src = tmp_path / "src"
        src.mkdir()
        # 新增文件：含裸 getenv → 应阻断
        (src / "new.py").write_text('import os\nx = os.getenv("NEW_TOKEN")\n', encoding="utf-8")
        # 修改文件：存量行含裸 getenv，新增行安全 → 应放行
        (src / "mod.py").write_text('import os\nx = os.getenv("OLD_KEY")\ny = 2\n', encoding="utf-8")
        diff_output = '@@ -1,2 +1,3 @@\n import os\n x = os.getenv("OLD_KEY")\n+y = 2\n'
        gw = _make_gateway(
            staged_files=["src/new.py"],
            modified_files=["src/mod.py"],
            added_lines={"src/mod.py": diff_output},
            project_root=str(tmp_path),
        )
        passed, msg = make_bare_getenv_gate().check(gw, [])
        assert not passed  # 新增文件有违规
        assert "NEW_TOKEN" in msg
