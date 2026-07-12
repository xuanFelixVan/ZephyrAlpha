# [A_test] module_id: SRC-TST-2233 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-test_source_consistency_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_test_source_consistency_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_test_source_consistency_gate.py — TEST-SOURCE-CONSISTENCY 门禁单测

权威依据：test_source_consistency_gate.py（make_test_source_consistency_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestHasModuleLevelSkip: _has_module_level_skip 模块级 skip 检测
  - 无 skip → False
  - pytest.skip(allow_module_level=True) → True
  - pytest.importorskip → True
  - 函数内 skip → False（非模块级）
  - 赋值形式 _ = pytest.skip(...) → True
  - 类内 skip → False（非模块级）
- TestModuleToPath: _module_to_path 模块路径转文件路径
- TestExtractSourceSymbols: _extract_source_symbols 顶层符号提取
  - class / def / async def / 顶层赋值 / 带注解赋值
  - 不提取类内方法
  - __all__ 不限制符号提取（PRIVATE 不在 __all__ 但仍被提取）
  - 语法错误 → None（fail-open）
- TestExtractAllList: _extract_all_list __all__ 提取（工具函数）
- TestGatewayIntegration: mock gateway + tmp_path 文件系统集成测试
  - 无 staged 文件 → 放行
  - staged 但无 tests/ 文件 → 放行
  - import 存在的符号 → 放行
  - import 不存在的符号 → 阻断
  - module-level skip 豁免
  - 相对导入跳过
  - 通配符 import 跳过
  - 非 zephyr.* import 跳过
  - 源码模块不存在 → 阻断（模块已删除/迁移）
  - __all__ 不阻断 import（PRIVATE 不在 __all__ 但 import 放行）

测试隔离：monkeypatch 设置 _SRC_ROOT 指向 tmp_path，MagicMock 模拟 gateway._run_git，
不读/不写真实仓库。
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

from zephyr.governance.commit_gates.test_source_consistency_gate import (  # noqa: E402
    _check_test_file,
    _extract_all_list,
    _extract_source_symbols,
    _has_module_level_skip,
    _module_to_path,
    make_test_source_consistency_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

import zephyr.governance.commit_gates.test_source_consistency_gate as _gate_mod  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, file_contents=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回文件列表；git show :path 返回文件内容。"""
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
        if "--unified=0" in cmd:
            # per-file diff: 生成全文件 added diff（模拟新文件）
            py_file = cmd[-1].replace("\\", "/")
            content = (file_contents or {}).get(py_file, "")
            lines = content.splitlines()
            if not lines:
                return _MockResult(0, "")
            diff = f"@@ -0,0 +1,{len(lines)} @@\n"
            for line in lines:
                diff += "+" + line + "\n"
            return _MockResult(0, diff)
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    """验证 make_test_source_consistency_gate() 返回的 GateSpec 字段。"""

    def test_returns_gate_spec(self):
        spec = make_test_source_consistency_gate()
        assert isinstance(spec, GateSpec)

    def test_gate_id(self):
        assert make_test_source_consistency_gate().gate_id == "TEST-SOURCE-CONSISTENCY"

    def test_priority_is_96(self):
        assert make_test_source_consistency_gate().priority == 96

    def test_check_is_callable(self):
        assert callable(make_test_source_consistency_gate().check)


# ---------------------------------------------------------------------------
# TestHasModuleLevelSkip
# ---------------------------------------------------------------------------
class TestHasModuleLevelSkip:
    """验证 _has_module_level_skip 模块级 skip 检测。"""

    def test_no_skip_returns_false(self):
        tree = ast.parse("import pytest\n\ndef test_foo():\n    pass\n")
        assert _has_module_level_skip(tree) is False

    def test_pytest_skip_module_level(self):
        tree = ast.parse(
            'import pytest\npytest.skip("drift known", allow_module_level=True)\n'
        )
        assert _has_module_level_skip(tree) is True

    def test_pytest_importorskip(self):
        tree = ast.parse('import pytest\npytest.importorskip("nonexistent")\n')
        assert _has_module_level_skip(tree) is True

    def test_skip_inside_function_not_exempt(self):
        """函数内的 pytest.skip 不是模块级，不豁免。"""
        tree = ast.parse(
            'import pytest\n\ndef test_foo():\n    pytest.skip("skip this test")\n'
        )
        assert _has_module_level_skip(tree) is False

    def test_assign_skip_detected(self):
        """赋值形式 _ = pytest.skip(...) 也应被检测为模块级 skip。"""
        tree = ast.parse(
            'import pytest\n_ = pytest.skip("drift", allow_module_level=True)\n'
        )
        assert _has_module_level_skip(tree) is True

    def test_skip_inside_class_not_exempt(self):
        """类内的 pytest.skip 不是模块级，不豁免。"""
        tree = ast.parse(
            'import pytest\n\nclass TestFoo:\n    pytest.skip("skip")\n'
        )
        assert _has_module_level_skip(tree) is False


# ---------------------------------------------------------------------------
# TestModuleToPath
# ---------------------------------------------------------------------------
class TestModuleToPath:
    """验证 _module_to_path 模块路径转文件路径。"""

    def test_module_to_py_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        (tmp_path / "zephyr" / "foo").mkdir(parents=True)
        (tmp_path / "zephyr" / "foo" / "bar.py").write_text("", encoding="utf-8")
        result = _module_to_path("zephyr.foo.bar")
        assert result == tmp_path / "zephyr" / "foo" / "bar.py"

    def test_module_to_init_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        (tmp_path / "zephyr" / "foo").mkdir(parents=True)
        (tmp_path / "zephyr" / "foo" / "__init__.py").write_text("", encoding="utf-8")
        result = _module_to_path("zephyr.foo")
        assert result == tmp_path / "zephyr" / "foo" / "__init__.py"

    def test_module_not_exist_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        assert _module_to_path("zephyr.nonexistent.module") is None


# ---------------------------------------------------------------------------
# TestExtractSourceSymbols
# ---------------------------------------------------------------------------
class TestExtractSourceSymbols:
    """验证 _extract_source_symbols 顶层符号提取。"""

    def test_extracts_class_def(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text("class Foo:\n    pass\n", encoding="utf-8")
        assert "Foo" in _extract_source_symbols(f)

    def test_extracts_function_def(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text("def foo():\n    pass\n", encoding="utf-8")
        assert "foo" in _extract_source_symbols(f)

    def test_extracts_async_function_def(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text("async def foo():\n    pass\n", encoding="utf-8")
        assert "foo" in _extract_source_symbols(f)

    def test_extracts_top_level_assign(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text("FOO = 1\n", encoding="utf-8")
        assert "FOO" in _extract_source_symbols(f)

    def test_extracts_annotated_assign(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text("FOO: int = 1\n", encoding="utf-8")
        assert "FOO" in _extract_source_symbols(f)

    def test_does_not_extract_method_inside_class(self, tmp_path):
        """类内方法不提取（只提取顶层符号）。"""
        f = tmp_path / "mod.py"
        f.write_text(
            "class Foo:\n    def method(self):\n        pass\n", encoding="utf-8"
        )
        syms = _extract_source_symbols(f)
        assert "Foo" in syms
        assert "method" not in syms

    def test_all_list_does_not_filter_symbols(self, tmp_path):
        """__all__ 不限制符号提取——PRIVATE 不在 __all__ 但仍被提取。

        设计意图：Python 允许显式 import 任何顶层符号（不受 __all__ 限制），
        故 _extract_source_symbols 检查所有顶层符号而非仅 __all__。
        """
        f = tmp_path / "mod.py"
        f.write_text(
            '__all__ = ["PUBLIC"]\n'
            'PUBLIC = 1\n'
            'PRIVATE = 2\n',
            encoding="utf-8",
        )
        syms = _extract_source_symbols(f)
        assert "PUBLIC" in syms
        assert "PRIVATE" in syms  # 不在 __all__ 但仍被提取

    def test_syntax_error_returns_none(self, tmp_path):
        """源码语法错误 → None（fail-open）。"""
        f = tmp_path / "mod.py"
        f.write_text("def broken(:\n", encoding="utf-8")
        assert _extract_source_symbols(f) is None


# ---------------------------------------------------------------------------
# TestExtractAllList
# ---------------------------------------------------------------------------
class TestExtractAllList:
    """验证 _extract_all_list __all__ 提取（工具函数）。

    注意：gate 本身不依赖 __all__ 过滤——_extract_source_symbols 提取所有顶层符号。
    此工具函数保留供测试验证 __all__ 提取行为正确性。
    """

    def test_list_extraction(self):
        tree = ast.parse('__all__ = ["foo", "bar"]')
        assign = tree.body[0]
        assert isinstance(assign, ast.Assign)
        result = _extract_all_list(assign.value)
        assert result == {"foo", "bar"}

    def test_tuple_extraction(self):
        tree = ast.parse('__all__ = ("foo", "bar")')
        assign = tree.body[0]
        assert isinstance(assign, ast.Assign)
        result = _extract_all_list(assign.value)
        assert result == {"foo", "bar"}

    def test_non_list_tuple_returns_none(self):
        tree = ast.parse('__all__ = "foo"')
        assign = tree.body[0]
        assert isinstance(assign, ast.Assign)
        assert _extract_all_list(assign.value) is None

    def test_empty_list_returns_none(self):
        tree = ast.parse('__all__ = []')
        assign = tree.body[0]
        assert isinstance(assign, ast.Assign)
        assert _extract_all_list(assign.value) is None

    def test_non_string_elements_ignored(self):
        tree = ast.parse('__all__ = [1, "foo", None]')
        assign = tree.body[0]
        assert isinstance(assign, ast.Assign)
        result = _extract_all_list(assign.value)
        assert result == {"foo"}


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    """mock gateway + tmp_path 文件系统集成测试。"""

    def test_no_staged_files_passes(self):
        """无 staged 文件 → 放行。"""
        gw = _make_gateway(staged_files=[])
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_no_test_files_passes(self, tmp_path, monkeypatch):
        """staged 但无 tests/ 文件 → 放行。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        gw = _make_gateway(staged_files=["src/zephyr/foo.py"])
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_valid_import_passes(self, tmp_path, monkeypatch):
        """测试文件 import 存在的符号 → 放行。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        src_dir = tmp_path / "zephyr" / "mod"
        src_dir.mkdir(parents=True)
        (src_dir / "foo.py").write_text("class Foo:\n    pass\n", encoding="utf-8")
        test_file = "tests/test_foo.py"
        test_content = "from zephyr.mod.foo import Foo\n"
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_drifted_import_blocks(self, tmp_path, monkeypatch):
        """测试文件 import 不存在的符号 → 阻断。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        src_dir = tmp_path / "zephyr" / "mod"
        src_dir.mkdir(parents=True)
        (src_dir / "foo.py").write_text("class Foo:\n    pass\n", encoding="utf-8")
        test_file = "tests/test_foo.py"
        test_content = "from zephyr.mod.foo import Bar\n"
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is False
        assert "TEST-SOURCE-CONSISTENCY" in msg
        assert "Bar" in msg

    def test_module_level_skip_exempt(self, tmp_path, monkeypatch):
        """测试文件含 module-level skip → 豁免（不检测漂移）。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_file = "tests/test_foo.py"
        test_content = (
            'import pytest\n'
            'pytest.skip("drift known", allow_module_level=True)\n'
            'from zephyr.nonexistent import Bar\n'
        )
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_relative_import_skipped(self, tmp_path, monkeypatch):
        """相对导入跳过（不检测）。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_file = "tests/test_foo.py"
        test_content = "from . import foo\n"
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_wildcard_import_skipped(self, tmp_path, monkeypatch):
        """通配符 import * 跳过（不检测单个符号）。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        src_dir = tmp_path / "zephyr" / "mod"
        src_dir.mkdir(parents=True)
        (src_dir / "foo.py").write_text("x = 1\n", encoding="utf-8")
        test_file = "tests/test_foo.py"
        test_content = "from zephyr.mod.foo import *\n"
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_non_zephyr_import_skipped(self, tmp_path, monkeypatch):
        """非 zephyr.* import 跳过（第三方包由 pytest.importorskip 处理）。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_file = "tests/test_foo.py"
        test_content = "from os import path\nfrom unittest.mock import MagicMock\n"
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_source_module_not_exist_blocks(self, tmp_path, monkeypatch):
        """源码模块不存在（已删除/迁移）→ 阻断。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_file = "tests/test_foo.py"
        test_content = "from zephyr.deleted.module import Foo\n"
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is False
        assert "TEST-SOURCE-CONSISTENCY" in msg
        assert "zephyr.deleted.module" in msg

    def test_all_list_does_not_block_import(self, tmp_path, monkeypatch):
        """__all__ 不阻断 import——PRIVATE 不在 __all__ 但 import 放行。

        设计意图：Python 允许显式 import 任何顶层符号，gate 检查所有顶层符号
        而非仅 __all__，故 import PRIVATE（不在 __all__）应放行。
        """
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        src_dir = tmp_path / "zephyr" / "mod"
        src_dir.mkdir(parents=True)
        (src_dir / "foo.py").write_text(
            '__all__ = ["PUBLIC"]\n'
            'PUBLIC = 1\n'
            'PRIVATE = 2\n',
            encoding="utf-8",
        )
        test_file = "tests/test_foo.py"
        test_content = "from zephyr.mod.foo import PRIVATE\n"
        gw = _make_gateway(
            staged_files=[test_file], file_contents={test_file: test_content}
        )
        passed, msg = make_test_source_consistency_gate().check(gw, [])
        assert passed is True
        assert msg == ""


# ---------------------------------------------------------------------------
# TestAddedLinesFilter — added 行过滤（防误阻断现有漂移）
# ---------------------------------------------------------------------------
class TestAddedLinesFilter:
    """验证 _check_test_file 的 added_lines 参数——只检查 added 行的 import。"""

    def test_existing_drift_not_blocked(self, tmp_path, monkeypatch):
        """现有漂移（不在 added 行）不阻断——只防新增漂移。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_content = "from zephyr.deleted.module import OldSymbol\n"
        violations = _check_test_file(test_content, "tests/test_foo.py", added_lines={999})
        assert violations == []

    def test_new_drift_blocked(self, tmp_path, monkeypatch):
        """新增漂移（在 added 行）阻断。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_content = "from zephyr.deleted.module import NewSymbol\n"
        violations = _check_test_file(test_content, "tests/test_foo.py", added_lines={1})
        assert len(violations) == 1
        assert "NewSymbol" in violations[0]

    def test_no_added_lines_no_violations(self, tmp_path, monkeypatch):
        """added_lines 为空集合 → 无违规（无新增行）。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_content = "from zephyr.deleted.module import Symbol\n"
        violations = _check_test_file(test_content, "tests/test_foo.py", added_lines=set())
        assert violations == []

    def test_none_added_lines_checks_all(self, tmp_path, monkeypatch):
        """added_lines=None → 检查所有 import（向后兼容）。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        test_content = "from zephyr.deleted.module import Symbol\n"
        violations = _check_test_file(test_content, "tests/test_foo.py", added_lines=None)
        assert len(violations) == 1

    def test_mixed_added_and_existing(self, tmp_path, monkeypatch):
        """混合场景：第1行现有漂移，第2行新增有效 import。"""
        monkeypatch.setattr(_gate_mod, "_SRC_ROOT", tmp_path)
        src_dir = tmp_path / "zephyr" / "valid"
        src_dir.mkdir(parents=True)
        (src_dir / "mod.py").write_text("class Foo:\n    pass\n", encoding="utf-8")
        test_content = (
            "from zephyr.deleted.module import OldSymbol\n"
            "from zephyr.valid.mod import Foo\n"
        )
        violations = _check_test_file(test_content, "tests/test_foo.py", added_lines={2})
        assert violations == []
