# [A_test] module_id: SRC-TST-2122 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] tests.test_detect_forward_reference
# [INVARIANTS] has_future_annotations; find_self_references excludes method body; scan_file exit codes
# [MODIFY-GUARD] scanner logic changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_detect_forward_reference.py
# [TTL] task_bound
from __future__ import annotations

import ast
import os
import sys
import tempfile
from pathlib import Path

import pytest

import importlib.util
from zephyr.shared.io.paths import REPO_ROOT

# 用 importlib 直接加载，绕过 governance 命名冲突
#（src/zephyr/governance/ 与 scripts/governance/ 同名导致包解析歧义）
_DFR_PATH = REPO_ROOT / "scripts" / "governance" / "d7_code" / "detect_forward_reference.py"
_spec = importlib.util.spec_from_file_location("detect_forward_reference", _DFR_PATH)
_dfr = importlib.util.module_from_spec(_spec)
sys.modules["detect_forward_reference"] = _dfr  # 注册到 sys.modules，供内部 dataclass 解析 __module__
_spec.loader.exec_module(_dfr)
EXIT_FINDINGS = _dfr.EXIT_FINDINGS
EXIT_PASS = _dfr.EXIT_PASS
ForwardRefViolation = _dfr.ForwardRefViolation
find_self_references = _dfr.find_self_references
has_future_annotations = _dfr.has_future_annotations
scan_file = _dfr.scan_file


class TestHasFutureAnnotations:
    """测试 has_future_annotations 函数。"""

    def test_with_future_import(self):
        code = "from __future__ import annotations\nclass X: pass\n"
        tree = ast.parse(code)
        assert has_future_annotations(tree) is True

    def test_without_future_import(self):
        code = "class X: pass\n"
        tree = ast.parse(code)
        assert has_future_annotations(tree) is False

    def test_with_other_future_import(self):
        code = "from __future__ import generator_stop\nclass X: pass\n"
        tree = ast.parse(code)
        assert has_future_annotations(tree) is False


class TestFindSelfReferences:
    """测试 find_self_references 函数。"""

    def test_class_variable_reference_detected(self):
        """类变量引用自身类名——应检测到（前向引用 bug）。"""
        code = "class Node:\n    instances = []\n    _registry = Node()\n"
        tree = ast.parse(code)
        class_node = tree.body[0]
        refs = find_self_references(class_node)
        assert len(refs) == 1
        assert refs[0][2] == "Node"

    def test_method_body_reference_not_detected(self):
        """方法体内引用自身类名——不应检测到（方法运行时类已定义）。"""
        code = (
            "class Member:\n"
            "    def __eq__(self, other):\n"
            "        return isinstance(other, Member)\n"
        )
        tree = ast.parse(code)
        class_node = tree.body[0]
        refs = find_self_references(class_node)
        assert len(refs) == 0

    def test_base_class_reference_detected(self):
        """基类引用自身——应检测到。"""
        code = "class Recursive(Recursive):\n    pass\n"
        tree = ast.parse(code)
        class_node = tree.body[0]
        refs = find_self_references(class_node)
        assert len(refs) == 1

    def test_decorator_reference_detected(self):
        """方法装饰器引用自身——应检测到（装饰器在类定义时执行）。"""
        code = (
            "class Meta:\n"
            "    @Meta.register\n"
            "    def foo(self): pass\n"
        )
        tree = ast.parse(code)
        class_node = tree.body[0]
        refs = find_self_references(class_node)
        assert len(refs) == 1
        assert refs[0][2] == "Meta"

    def test_no_reference_clean(self):
        """无自身引用——返回空列表。"""
        code = "class Clean:\n    x = 42\n    def foo(self): return self.x\n"
        tree = ast.parse(code)
        class_node = tree.body[0]
        refs = find_self_references(class_node)
        assert len(refs) == 0

    def test_attribute_reference_detected(self):
        """属性引用 ClassName.xxx——Name 节点应检测到。"""
        code = "class Config:\n    default = Config.settings\n"
        tree = ast.parse(code)
        class_node = tree.body[0]
        refs = find_self_references(class_node)
        assert len(refs) == 1
        assert refs[0][2] == "Config"

    def test_subscript_reference_detected(self):
        """下标引用 ClassName[...]——Name 节点应检测到。"""
        code = "class Container:\n    items = Container[0]()\n"
        tree = ast.parse(code)
        class_node = tree.body[0]
        refs = find_self_references(class_node)
        assert len(refs) == 1
        assert refs[0][2] == "Container"

    def test_nested_class_method_not_detected(self):
        """嵌套类的方法体内引用——不应检测到。"""
        code = (
            "class Outer:\n"
            "    class Inner:\n"
            "        def __eq__(self, other):\n"
            "            return isinstance(other, Inner)\n"
        )
        tree = ast.parse(code)
        outer_node = tree.body[0]
        refs = find_self_references(outer_node)
        assert len(refs) == 0


class TestScanFile:
    """测试 scan_file 函数。"""

    def test_file_with_violation(self, tmp_path):
        """有违规的文件——返回违规列表。"""
        fpath = tmp_path / "bad.py"
        fpath.write_text("class Node:\n    instances = Node()\n", encoding="utf-8")
        violations, has_future, error = scan_file(str(fpath))
        assert error is None
        assert has_future is False
        assert len(violations) == 1
        assert violations[0].class_name == "Node"

    def test_file_with_future_annotations(self, tmp_path):
        """有 from __future__ import annotations 的文件——不报告违规。"""
        fpath = tmp_path / "good_future.py"
        fpath.write_text(
            "from __future__ import annotations\n"
            "class Node:\n"
            "    instances = Node()\n",
            encoding="utf-8",
        )
        violations, has_future, error = scan_file(str(fpath))
        assert error is None
        assert has_future is True
        assert len(violations) == 0

    def test_file_clean(self, tmp_path):
        """无违规的文件——返回空列表。"""
        fpath = tmp_path / "clean.py"
        fpath.write_text("class Clean:\n    x = 42\n", encoding="utf-8")
        violations, has_future, error = scan_file(str(fpath))
        assert error is None
        assert has_future is False
        assert len(violations) == 0

    def test_file_syntax_error(self, tmp_path):
        """语法错误的文件——返回错误。"""
        fpath = tmp_path / "syntax_err.py"
        fpath.write_text("class Broken:\n    def(\n", encoding="utf-8")
        violations, has_future, error = scan_file(str(fpath))
        assert error is not None
        assert "SyntaxError" in error
        assert len(violations) == 0

    def test_file_method_body_not_flagged(self, tmp_path):
        """方法体内的 isinstance 引用——不报告违规。"""
        fpath = tmp_path / "method_ref.py"
        fpath.write_text(
            "class Member:\n"
            "    def __eq__(self, other):\n"
            "        return isinstance(other, Member)\n",
            encoding="utf-8",
        )
        violations, has_future, error = scan_file(str(fpath))
        assert error is None
        assert has_future is False
        assert len(violations) == 0


class TestMainIntegration:
    """测试 main 函数集成。"""

    def test_main_warn_only_exit_zero(self, tmp_path, monkeypatch):
        """--warn-only 模式即使有违规也 exit 0。"""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("class Node:\n    x = Node()\n", encoding="utf-8")

        import governance.d7_code.detect_forward_reference as mod

        monkeypatch.setattr(mod, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(sys, "argv", ["detect_forward_reference.py", "--warn-only"])
        exit_code = mod.main()
        assert exit_code == EXIT_PASS

    def test_main_clean_exit_zero(self, tmp_path, monkeypatch):
        """无违规时 exit 0。"""
        clean_file = tmp_path / "clean.py"
        clean_file.write_text("class Clean:\n    x = 42\n", encoding="utf-8")

        import governance.d7_code.detect_forward_reference as mod

        monkeypatch.setattr(mod, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(sys, "argv", ["detect_forward_reference.py"])
        exit_code = mod.main()
        assert exit_code == EXIT_PASS

    def test_main_violation_exit_one(self, tmp_path, monkeypatch):
        """有违规且非 --warn-only 时 exit 1。"""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("class Node:\n    x = Node()\n", encoding="utf-8")

        import governance.d7_code.detect_forward_reference as mod

        monkeypatch.setattr(mod, "SCAN_DIRS", [tmp_path])
        monkeypatch.setattr(sys, "argv", ["detect_forward_reference.py"])
        exit_code = mod.main()
        assert exit_code == EXIT_FINDINGS
