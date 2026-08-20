# [A_test] module_id: MOD-GOV_no_import_side_effect_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_no_import_side_effect_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_no_import_side_effect_gate.py — NO-IMPORT-SIDE-EFFECT 门禁单测

权威依据：no_import_side_effect_gate.py（make_no_import_side_effect_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestSideEffectDetection: AST 纯函数检测
  - _is_side_effect_call: open/subprocess.run/requests.get/duckdb.connect/Path().read_text
  - _is_eager_singleton: UPPER_SNAKE=Capitalized 调用，allowlist TypeVar/Path
  - _is_name_main_guard: if __name__ == "__main__" 检测
- TestCheckFile: _check_file 模块级副作用检测
  - I/O 调用阻断（open/subprocess.run/Path.read_text）
  - 急切单例阻断（TELEMETRY = InventorySelfMetrics()）
  - 函数体/类体豁免、__main__ guard 豁免、allowlist 豁免
  - added-lines-only（存量违规不检测）
  - try/with 体 descend 检测
  - 语法错误 fail-open
- TestGatewayIntegration: mock gateway 流程
  - staged 文件检测、tests/ 豁免、__main__.py 豁免
  - 非 .py 文件忽略、fail-open on git error

测试隔离：MagicMock 模拟 gateway.run_git，不读/不写真实仓库。
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.no_import_side_effect_gate import (  # noqa: E402
    _check_file,
    _is_eager_singleton,
    _is_main_entry,
    _is_name_main_guard,
    _is_side_effect_call,
    make_no_import_side_effect_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_diff(added: list[tuple[int, str]]) -> str:
    """构造 git diff --unified=0 输出（从 (line_no, content) 对列表）。

    生成单个 hunk 覆盖所有 added 行，gap 行作为 context 行。
    _parse_diff_with_line_numbers 只读 +c（新文件起始行）和 + 前缀行。
    """
    if not added:
        return ""
    min_line = min(ln for ln, _ in added)
    max_line = max(ln for ln, _ in added)
    added_set = {ln for ln, _ in added}
    added_map = {ln: c for ln, c in added}
    total = max_line - min_line + 1
    lines = [
        "diff --git a/src/mod.py b/src/mod.py",
        "--- a/src/mod.py",
        "+++ b/src/mod.py",
        f"@@ -{min_line},{total} +{min_line},{total} @@",
    ]
    for i in range(min_line, max_line + 1):
        if i in added_set:
            lines.append("+" + added_map[i])
        else:
            lines.append(" context")
    return "\n".join(lines)


def _make_gateway(
    staged_files=None,
    project_root=None,
    file_contents=None,
    added_lines_map=None,
    diff_fails=False,
    diff_raises=False,
):
    """构造 mock gateway。

    Args:
        staged_files: --name-only 返回的文件相对路径列表。
        file_contents: {rel_path: str}，git show :path 返回的文件内容。
        added_lines_map: {rel_path: list[(line_no, content)]}，diff added 行。
        diff_fails: True → --name-only 返回 rc=1。
        diff_raises: True → _run_git 抛 RuntimeError。
    """
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

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
        if "show" in cmd:
            path = next((a[1:] for a in cmd if a.startswith(":")), "")
            path = path.replace("\\", "/")
            content = (file_contents or {}).get(path, "")
            return _MockResult(0, content)
        if "--unified=0" in cmd:
            path = cmd[-1].replace("\\", "/")
            added = (added_lines_map or {}).get(path, [])
            return _MockResult(0, _make_diff(added))
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_no_import_side_effect_gate(), GateSpec)

    def test_gate_id(self):
        assert make_no_import_side_effect_gate().gate_id == "NO-IMPORT-SIDE-EFFECT"

    def test_priority(self):
        assert make_no_import_side_effect_gate().priority == 103


# ---------------------------------------------------------------------------
# TestSideEffectDetection — AST 纯函数检测
# ---------------------------------------------------------------------------
class TestSideEffectDetection:
    """直接测试 _is_side_effect_call / _is_eager_singleton / _is_name_main_guard。"""

    def _first_call(self, code: str) -> ast.Call:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                return node
        raise ValueError("No Call node found")

    def _first_assign(self, code: str) -> ast.Assign:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                return node
        raise ValueError("No Assign node found")

    # --- _is_side_effect_call: I/O/网络/subprocess/DB ---

    def test_detects_open(self):
        call = self._first_call('open("file.txt")')
        hit, desc = _is_side_effect_call(call)
        assert hit
        assert "open" in desc

    def test_detects_urlopen(self):
        call = self._first_call('from urllib.request import urlopen\nurlopen("http://x")')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_subprocess_run(self):
        call = self._first_call('import subprocess\nsubprocess.run(["ls"])')
        hit, desc = _is_side_effect_call(call)
        assert hit
        assert "subprocess.run" in desc

    def test_detects_subprocess_popen(self):
        call = self._first_call('import subprocess\nsubprocess.Popen(["ls"])')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_requests_get(self):
        call = self._first_call('import requests\nrequests.get("http://x")')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_duckdb_connect(self):
        call = self._first_call('import duckdb\nduckdb.connect("db.duckdb")')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_psycopg2_connect(self):
        call = self._first_call('import psycopg2\npsycopg2.connect("host=x")')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_sqlite3_connect(self):
        call = self._first_call('import sqlite3\nsqlite3.connect("db.sqlite")')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_socket_socket(self):
        call = self._first_call("import socket\nsocket.socket()")
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_path_read_text(self):
        call = self._first_call('from pathlib import Path\nPath("x").read_text()')
        hit, desc = _is_side_effect_call(call)
        assert hit
        assert "Path" in desc

    def test_detects_path_write_text(self):
        call = self._first_call('from pathlib import Path\nPath("x").write_text("y")')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_detects_path_unlink(self):
        call = self._first_call('from pathlib import Path\nPath("x").unlink()')
        hit, _ = _is_side_effect_call(call)
        assert hit

    def test_ignores_len(self):
        call = self._first_call("len([1, 2, 3])")
        hit, _ = _is_side_effect_call(call)
        assert not hit

    def test_ignores_logging_getlogger(self):
        call = self._first_call('import logging\nlogging.getLogger("x")')
        hit, _ = _is_side_effect_call(call)
        assert not hit  # logging not in _SIDE_EFFECT_ATTRS

    def test_ignores_re_compile(self):
        call = self._first_call('import re\nre.compile("x")')
        hit, _ = _is_side_effect_call(call)
        assert not hit  # re not in _SIDE_EFFECT_ATTRS

    def test_ignores_path_join(self):
        """Path("x") / "y" 不是 I/O 方法调用（join 不是 _PATH_IO_METHODS）。"""
        call = self._first_call('from pathlib import Path\nPath("x").joinpath("y")')
        hit, _ = _is_side_effect_call(call)
        assert not hit  # joinpath not in _PATH_IO_METHODS

    # --- _is_eager_singleton ---

    def test_eager_singleton_detected(self):
        assign = self._first_assign("TELEMETRY = InventorySelfMetrics()")
        hit, desc = _is_eager_singleton(assign)
        assert hit
        assert "TELEMETRY" in desc

    def test_eager_singleton_attr_call(self):
        assign = self._first_assign("CLIENT = factory.HttpClient()")
        hit, _ = _is_eager_singleton(assign)
        assert hit

    def test_eager_singleton_ignores_lowercase_target(self):
        assign = self._first_assign("logger = logging.getLogger()")
        hit, _ = _is_eager_singleton(assign)
        assert not hit  # target lowercase

    def test_eager_singleton_ignores_lowercase_func(self):
        assign = self._first_assign('RE = re.compile("x")')
        hit, _ = _is_eager_singleton(assign)
        assert not hit  # func lowercase

    def test_eager_singleton_ignores_typevar(self):
        assign = self._first_assign('T = TypeVar("T")')
        hit, _ = _is_eager_singleton(assign)
        assert not hit  # TypeVar in _PURE_CAPITALIZED

    def test_eager_singleton_ignores_path(self):
        assign = self._first_assign('BASE = Path("/x")')
        hit, _ = _is_eager_singleton(assign)
        assert not hit  # Path in _PURE_CAPITALIZED

    def test_eager_singleton_ignores_enum(self):
        assign = self._first_assign('COLOR = Enum("COLOR", "RED GREEN BLUE")')
        hit, _ = _is_eager_singleton(assign)
        assert not hit  # Enum in _PURE_CAPITALIZED

    def test_eager_singleton_ignores_single_uppercase(self):
        """单字母目标不匹配 _UPPER_NAME_RE（至少 2 个大写字符）。"""
        assign = self._first_assign("X = Foo()")
        hit, _ = _is_eager_singleton(assign)
        assert not hit  # 'X' doesn't match ^[A-Z][A-Z0-9_]+$

    def test_eager_singleton_ignores_non_call_value(self):
        assign = self._first_assign("DATA = [1, 2, 3]")
        hit, _ = _is_eager_singleton(assign)
        assert not hit  # value not a Call

    # --- _is_name_main_guard ---

    def test_name_main_guard_detected(self):
        tree = ast.parse('if __name__ == "__main__":\n    pass')
        assert _is_name_main_guard(tree.body[0].test)

    def test_non_guard_not_detected(self):
        tree = ast.parse("if x == 1:\n    pass")
        assert not _is_name_main_guard(tree.body[0].test)

    def test_name_main_guard_wrong_comparator(self):
        tree = ast.parse('if __name__ != "__main__":\n    pass')
        assert not _is_name_main_guard(tree.body[0].test)

    # --- _is_main_entry ---

    def test_main_entry_detected(self):
        assert _is_main_entry("src/pkg/__main__.py")

    def test_main_entry_windows_path(self):
        assert _is_main_entry("src\\pkg\\__main__.py")

    def test_non_main_entry_not_detected(self):
        assert not _is_main_entry("src/pkg/mod.py")

    def test_bare_main_not_detected(self):
        """无路径前缀的 __main__.py 不豁免（需要 / 前缀）。"""
        assert not _is_main_entry("__main__.py")


# ---------------------------------------------------------------------------
# TestCheckFile — _check_file 模块级副作用检测
# ---------------------------------------------------------------------------
class TestCheckFile:
    """直接测试 _check_file（不需 gateway mock）。"""

    def _check(self, code: str, added_lines: set[int] | None = None) -> list[str]:
        if added_lines is None:
            num_lines = len(code.splitlines())
            added_lines = set(range(1, num_lines + 1))
        return _check_file(code, "src/mod.py", added_lines)

    # --- I/O 副作用阻断 ---

    def test_open_blocked(self):
        v = self._check('x = open("file.txt")\n')
        assert len(v) == 1
        assert "open" in v[0]

    def test_subprocess_run_blocked(self):
        v = self._check('import subprocess\nsubprocess.run(["ls"])\n')
        assert len(v) == 1
        assert "subprocess.run" in v[0]

    def test_requests_get_blocked(self):
        v = self._check('import requests\nrequests.get("http://x")\n')
        assert len(v) == 1
        assert "requests.get" in v[0]

    def test_path_read_text_blocked(self):
        v = self._check('from pathlib import Path\ndata = Path("x").read_text()\n')
        assert len(v) == 1
        assert "Path" in v[0]

    def test_with_open_blocked(self):
        """模块级 with open(...) 的 context_expr 含副作用 → 阻断。"""
        v = self._check('with open("file.txt") as f:\n    pass\n')
        assert len(v) == 1
        assert "open" in v[0]

    def test_try_body_open_blocked(self):
        """模块级 try 块体 descend → 阻断。"""
        code = 'try:\n    x = open("file.txt")\nexcept Exception:\n    pass\n'
        v = self._check(code)
        assert len(v) == 1

    # --- 急切单例阻断 ---

    def test_eager_singleton_blocked(self):
        v = self._check("TELEMETRY = InventorySelfMetrics()\n")
        assert len(v) == 1
        assert "TELEMETRY" in v[0]

    def test_eager_singleton_attr_blocked(self):
        v = self._check("CLIENT = factory.HttpClient()\n")
        assert len(v) == 1
        assert "CLIENT" in v[0]

    # --- 豁免场景 ---

    def test_function_body_exempt(self):
        code = 'def f():\n    open("file.txt")\n'
        v = self._check(code)
        assert v == []

    def test_class_body_exempt(self):
        code = 'class C:\n    x = open("file.txt")\n'
        v = self._check(code)
        assert v == []

    def test_name_main_guard_exempt(self):
        code = 'if __name__ == "__main__":\n    open("file.txt")\n'
        v = self._check(code)
        assert v == []

    def test_typevar_passes(self):
        v = self._check('T = TypeVar("T")\n')
        assert v == []

    def test_path_allowlist_passes(self):
        v = self._check('BASE = Path("/x")\n')
        assert v == []

    def test_enum_passes(self):
        v = self._check('COLOR = Enum("COLOR", "RED GREEN BLUE")\n')
        assert v == []

    def test_logger_passes(self):
        """logger = logging.getLogger() — 目标小写 + logging 非副作用 → 放行。"""
        v = self._check("import logging\nlogger = logging.getLogger(__name__)\n")
        assert v == []

    def test_re_compile_passes(self):
        """RE = re.compile(...) — func 小写 → 放行。"""
        v = self._check('import re\nRE = re.compile("x")\n')
        assert v == []

    def test_defaultdict_passes(self):
        """DEFAULT = defaultdict(list) — func 小写 → 放行。"""
        v = self._check("from collections import defaultdict\nDEFAULT = defaultdict(list)\n")
        assert v == []

    # --- added-lines-only ---

    def test_added_lines_only_violation_not_in_added(self):
        """违规在第 2 行但 added_lines 只含第 1 行 → 放行（存量不检测）。"""
        code = "x = 1\nTELEMETRY = InventorySelfMetrics()\n"
        v = _check_file(code, "src/mod.py", {1})
        assert v == []

    def test_added_lines_only_violation_in_added(self):
        """违规在第 2 行且 added_lines 含第 2 行 → 阻断。"""
        code = "x = 1\nTELEMETRY = InventorySelfMetrics()\n"
        v = _check_file(code, "src/mod.py", {1, 2})
        assert len(v) == 1
        assert "TELEMETRY" in v[0]

    # --- fail-open ---

    def test_syntax_error_fail_open(self):
        v = _check_file("def (\n", "src/mod.py", {1})
        assert v == []

    def test_empty_added_lines_no_violation(self):
        """added_lines 为空集 → 无违规（gate 会跳过此文件）。"""
        code = "TELEMETRY = InventorySelfMetrics()\n"
        v = _check_file(code, "src/mod.py", set())
        assert v == []


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    """通过 mock gateway 测试完整 commit gate 流程。"""

    def test_open_blocked(self, tmp_path):
        rel = "src/mod.py"
        code = 'x = open("file.txt")\n'
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, 'x = open("file.txt")')]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert not passed
        assert "open" in msg or "I/O" in msg

    def test_eager_singleton_blocked(self, tmp_path):
        rel = "src/mod.py"
        code = "TELEMETRY = InventorySelfMetrics()\n"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, "TELEMETRY = InventorySelfMetrics()")]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert not passed
        assert "TELEMETRY" in msg or "急切单例" in msg

    def test_subprocess_run_blocked(self, tmp_path):
        rel = "src/mod.py"
        code = 'import subprocess\nsubprocess.run(["ls"])\n'
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, "import subprocess"), (2, 'subprocess.run(["ls"])')]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert not passed
        assert "subprocess" in msg

    def test_safe_code_passes(self, tmp_path):
        rel = "src/mod.py"
        code = "x = 1\n"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, "x = 1")]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_logger_passes(self, tmp_path):
        rel = "src/mod.py"
        code = "import logging\nlogger = logging.getLogger(__name__)\n"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, "import logging"), (2, "logger = logging.getLogger(__name__)")]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_typevar_passes(self, tmp_path):
        rel = "src/mod.py"
        code = 'T = TypeVar("T")\n'
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, 'T = TypeVar("T")')]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_function_body_passes(self, tmp_path):
        rel = "src/mod.py"
        code = 'def f():\n    open("file.txt")\n'
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, "def f():"), (2, '    open("file.txt")')]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed  # function body exempt
        assert msg == ""

    def test_name_main_guard_passes(self, tmp_path):
        rel = "src/mod.py"
        code = 'if __name__ == "__main__":\n    open("file.txt")\n'
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, 'if __name__ == "__main__":'), (2, '    open("file.txt")')]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed  # __main__ guard exempt
        assert msg == ""

    def test_tests_dir_exempt(self, tmp_path):
        rel = "tests/test_x.py"
        code = 'x = open("file.txt")\n'
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, 'x = open("file.txt")')]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed  # tests/ exempt
        assert msg == ""

    def test_main_entry_exempt(self, tmp_path):
        rel = "src/pkg/__main__.py"
        code = 'open("file.txt")\n'
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, 'open("file.txt")')]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed  # __main__.py exempt
        assert msg == ""

    def test_non_py_file_ignored(self, tmp_path):
        rel = "src/mod.txt"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={},
            added_lines_map={},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed  # non-.py filtered by _get_staged_py_files
        assert msg == ""

    def test_no_staged_files_passes(self, tmp_path):
        gw = _make_gateway(staged_files=[], project_root=str(tmp_path))
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_no_added_lines_passes(self, tmp_path):
        """staged 文件存在但无 added 行（纯删除/修改注释）→ 放行。"""
        rel = "src/mod.py"
        code = "x = 1\n"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: []},  # 无 added 行
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_syntax_error_fail_open(self, tmp_path):
        rel = "src/mod.py"
        code = "def (\n"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, "def (")]},
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed  # AST parse fail → fail-open
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(diff_fails=True, project_root=str(tmp_path))
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(diff_raises=True, project_root=str(tmp_path))
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_multiple_violations_blocked(self, tmp_path):
        rel = "src/mod.py"
        code = "import subprocess\nTELEMETRY = InventorySelfMetrics()\n"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={
                rel: [
                    (1, "import subprocess"),
                    (2, "TELEMETRY = InventorySelfMetrics()"),
                ]
            },
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert not passed
        assert "subprocess" in msg or "TELEMETRY" in msg

    def test_added_lines_only_integration(self, tmp_path):
        """违规在第 2 行但 diff 只标记第 1 行为 added → 放行（存量不检测）。"""
        rel = "src/mod.py"
        code = "x = 1\nTELEMETRY = InventorySelfMetrics()\n"
        gw = _make_gateway(
            staged_files=[rel],
            file_contents={rel: code},
            added_lines_map={rel: [(1, "x = 1")]},  # 只有第 1 行 added
        )
        passed, msg = make_no_import_side_effect_gate().check(gw, [])
        assert passed  # violation on line 2 not in added_lines
        assert msg == ""
