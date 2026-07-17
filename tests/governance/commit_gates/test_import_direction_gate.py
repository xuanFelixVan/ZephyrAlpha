# [A_test] module_id: SRC-TST-2213 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-import_direction_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_import_direction_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_import_direction_gate.py — NO-UPWARD-IMPORT 门禁单测

权威依据：import_direction_gate.py（make_import_direction_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestTypeCheckingExempt: _collect_type_checking_imports 纯函数（TYPE_CHECKING / typing.TYPE_CHECKING）
- TestGatewayIntegration: mock gateway 流程
  - shared 层向上 import trading → 阻断 (passed=False)
  - shared 层向上 import governance → 阻断
  - shared 层安全 import → 放行
  - TYPE_CHECKING 块内向上 import 豁免 → 放行
  - 非 shared 层文件不检测 → 放行
  - tests/ 豁免
  - fail-open on git diff 失败/异常
  - fail-open on AST 解析失败（SyntaxError）

测试隔离：MagicMock 模拟 gateway._run_git，tmp_path 创建真实 .py 文件。
"""
from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.import_direction_gate import (  # noqa: E402
    _collect_type_checking_imports,
    _is_upward_import,
    make_import_direction_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_path, staged_files=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only（--diff-filter=AM）返回文件列表；
    --show-toplevel 返回 tmp_path。"""
    gw = MagicMock()
    gw.project_root = str(tmp_path)

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
        if "rev-parse" in cmd and "--show-toplevel" in cmd:
            return _MockResult(0, str(tmp_path))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


def _write_file(tmp_path, rel_path, content):
    """在 tmp_path 下创建 rel_path 文件，返回相对路径（正斜杠）。"""
    rel = rel_path.replace("\\", "/")
    full = tmp_path / rel.replace("/", os.sep)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return rel


@pytest.fixture(autouse=True)
def _shadow_open(monkeypatch):
    """源文件用 open(path).read() 未关闭文件句柄（ResourceWarning）。
    注入 shadow open：read() 后立即关闭真实 fd。"""
    import builtins
    _real_open = builtins.open

    class _AutoClose:
        def __init__(self, fp):
            self._fp = fp

        def read(self, *a, **k):
            try:
                return self._fp.read(*a, **k)
            finally:
                self._fp.close()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._fp.close()

        def __getattr__(self, name):
            return getattr(self._fp, name)

    def _shadow(file, mode="r", *args, **kwargs):
        return _AutoClose(_real_open(file, mode, *args, **kwargs))

    import zephyr.gov_enforcement.commit_gates.import_direction_gate as mod
    monkeypatch.setattr(mod, "open", _shadow, raising=False)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_import_direction_gate(), GateSpec)

    def test_gate_id(self):
        assert make_import_direction_gate().gate_id == "NO-UPWARD-IMPORT"

    def test_priority(self):
        assert make_import_direction_gate().priority == 97


# ---------------------------------------------------------------------------
# TestTypeCheckingExempt — _collect_type_checking_imports
# ---------------------------------------------------------------------------
class TestTypeCheckingExempt:
    def test_type_checking_block_collected(self):
        tree = ast.parse(
            "from typing import TYPE_CHECKING\n"
            "if TYPE_CHECKING:\n"
            "    from zephyr.trading.enums import Side\n"
        )
        exempt = _collect_type_checking_imports(tree)
        # 应收集到 1 个 ImportFrom（TYPE_CHECKING 块内）
        assert len(exempt) == 1

    def test_typing_type_checking_attr_collected(self):
        tree = ast.parse(
            "import typing\n"
            "if typing.TYPE_CHECKING:\n"
            "    from zephyr.governance.types import T\n"
        )
        exempt = _collect_type_checking_imports(tree)
        assert len(exempt) == 1

    def test_no_type_checking_block_empty(self):
        tree = ast.parse(
            "from zephyr.trading.enums import Side\n"
        )
        exempt = _collect_type_checking_imports(tree)
        assert exempt == set()

    def test_non_type_checking_if_not_collected(self):
        tree = ast.parse(
            "if True:\n"
            "    from zephyr.trading.enums import Side\n"
        )
        exempt = _collect_type_checking_imports(tree)
        assert exempt == set()


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_upward_trading_import_blocked(self, tmp_path):
        red = "src/zephyr/shared/types.py"
        content = "from zephyr.trading.enums import Side\n"
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert not passed
        assert "NO-UPWARD-IMPORT" in msg or "向上依赖" in msg
        assert "zephyr.trading" in msg

    def test_upward_governance_import_blocked(self, tmp_path):
        red = "src/zephyr/shared/types.py"
        content = "from zephyr.gov_enforcement.rule_bridge import X\n"
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert not passed
        assert "zephyr.gov_enforcement" in msg

    def test_safe_shared_import_passes(self, tmp_path):
        blue = "src/zephyr/shared/types.py"
        content = "from zephyr.shared.ids import ID\n"
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_safe_stdlib_import_passes(self, tmp_path):
        blue = "src/zephyr/shared/types.py"
        content = "from typing import Any\n"
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_type_checking_exempt(self, tmp_path):
        blue = "src/zephyr/shared/types.py"
        content = (
            "from typing import TYPE_CHECKING\n"
            "if TYPE_CHECKING:\n"
            "    from zephyr.trading.enums import Side\n"
        )
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed  # TYPE_CHECKING 块内 import 豁免
        assert msg == ""

    def test_non_shared_file_passes(self, tmp_path):
        # 非 shared 层文件不检测
        red = "src/zephyr/trading/mod.py"
        content = "from zephyr.gov_enforcement.rule_bridge import X\n"
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self, tmp_path):
        red = "tests/governance/test_shared.py"
        content = "from zephyr.trading.enums import Side\n"
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_fails=True)
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_raises=True)
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self, tmp_path):
        red = "src/zephyr/shared/types.py"
        content = "from zephyr.trading.enums import (\n"  # 语法错误
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""

    def test_multiple_upward_imports_blocked(self, tmp_path):
        red = "src/zephyr/shared/types.py"
        content = (
            "from zephyr.trading.enums import Side\n"
            "from zephyr.governance.types import T\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_import_direction_gate().check(gw, [])
        assert not passed
        assert "zephyr.trading" in msg
        assert "zephyr.governance" in msg
