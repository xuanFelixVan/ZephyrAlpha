# [A_test] module_id: SRC-TST-DEAD-WRAPPER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_DEAD_PUBLIC_WRAPPER_RECONCILER | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | §#ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001
# [MODULE] tests.governance.audit.test_dead_public_wrapper_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_DEAD_PUBLIC_WRAPPER_RECONCILER | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_dead_public_wrapper_reconciler.py — 死公共 wrapper 自动检测 reconciler 单测。

#ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001 防复发自动化（2026-08-02）。

测试 make_dead_public_wrapper_reconciler 工厂函数：
- factory 返回正确 ReconcilerSpec（gate_id=GATE-DEAD-PUBLIC-WRAPPER, priority=950）
- trigger 仅在 src/*.py commit 时返回 True
- _find_function_pairs 找模块级/类级 public+private pair
- _is_trivial_wrapper 正确识别 trivial wrapper（body 仅 1 条 return _foo() 语句）
  排除非 trivial（含 if/for/try/多语句）和非目标调用
- _find_dead_public_wrappers 端到端检测（tmp_path 构造 fake 项目结构）
- reconcile: clean（无死 wrapper）/ warn（有死 wrapper）/ 永不抛异常

测试隔离：用 tmp_path 构造最小项目结构，不依赖真实代码库。
"""

from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.dead_public_wrapper_reconciler import (  # noqa: E402
    _GATE_ID,
    _PRIORITY,
    _find_dead_public_wrappers,
    _find_function_pairs,
    _is_trivial_wrapper,
    make_dead_public_wrapper_reconciler,
)
from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec  # noqa: E402

# ============================================================================
# 辅助
# ============================================================================


class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root。"""

    def __init__(self, project_root: Path):
        self.project_root = project_root


def _write_py(path: Path, content: str) -> None:
    """写入 Python 文件（textwrap.dedent 后），自动创建父目录。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")


def _parse(source: str) -> ast.AST:
    """快捷解析 helper。"""
    return ast.parse(textwrap.dedent(source))


# ============================================================================
# 工厂函数测试
# ============================================================================


class TestFactorySpec:
    """make_dead_public_wrapper_reconciler 工厂返回值测试。"""

    def test_factory_returns_spec(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)
        assert spec.gate_id == _GATE_ID == "GATE-DEAD-PUBLIC-WRAPPER"
        assert spec.priority == _PRIORITY == 950
        assert callable(spec.trigger)
        assert callable(spec.reconcile)


class TestTrigger:
    """trigger 仅在 src/*.py commit 时返回 True。"""

    def test_trigger_true_on_src_py(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        assert spec.trigger(["src/zephyr/foo.py"]) is True
        assert spec.trigger(["src/zephyr/sub/bar.py"]) is True

    def test_trigger_false_on_non_src(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        assert spec.trigger(["docs/foo.md"]) is False
        assert spec.trigger(["tests/test_foo.py"]) is False
        assert spec.trigger(["scripts/run.py"]) is False
        assert spec.trigger([]) is False

    def test_trigger_true_when_mixed(self, tmp_path):
        # 只要有一个 src/*.py 就触发
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        assert spec.trigger(["docs/foo.md", "src/zephyr/bar.py"]) is True


# ============================================================================
# _find_function_pairs 测试
# ============================================================================


class TestFindFunctionPairs:
    """_find_function_pairs 找模块级/类级 public+private pair。"""

    def test_module_level_pair(self):
        tree = _parse("""
            def foo():
                pass
            def _foo():
                pass
        """)
        pairs = _find_function_pairs(tree)
        assert len(pairs) == 1
        assert pairs[0]["public_name"] == "foo"
        assert pairs[0]["private_name"] == "_foo"
        assert pairs[0]["scope"] == "module"

    def test_class_level_pair(self):
        tree = _parse("""
            class MyClass:
                def bar(self):
                    pass
                def _bar(self):
                    pass
        """)
        pairs = _find_function_pairs(tree)
        assert len(pairs) == 1
        assert pairs[0]["public_name"] == "bar"
        assert pairs[0]["private_name"] == "_bar"
        assert pairs[0]["scope"] == "class:MyClass"

    def test_no_pair_when_only_public(self):
        tree = _parse("""
            def foo():
                pass
        """)
        pairs = _find_function_pairs(tree)
        assert len(pairs) == 0

    def test_no_pair_when_only_private(self):
        tree = _parse("""
            def _foo():
                pass
        """)
        pairs = _find_function_pairs(tree)
        assert len(pairs) == 0

    def test_excludes_dunder(self):
        # __init__ / __str__ 等应被排除
        tree = _parse("""
            class MyClass:
                def __init__(self):
                    pass
                def _init(self):
                    pass
        """)
        pairs = _find_function_pairs(tree)
        assert len(pairs) == 0

    def test_excludes_make_factory(self):
        # make_* 工厂模式应被排除
        tree = _parse("""
            def make_thing():
                pass
            def _make_thing():
                pass
        """)
        pairs = _find_function_pairs(tree)
        assert len(pairs) == 0


# ============================================================================
# _is_trivial_wrapper 测试
# ============================================================================


class TestIsTrivialWrapper:
    """_is_trivial_wrapper 正确识别 trivial wrapper。"""

    def test_return_direct_call(self):
        # return _foo()
        tree = _parse("""
            def foo():
                return _foo()
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is True

    def test_return_self_call(self):
        # return self._foo()
        tree = _parse("""
            def foo(self):
                return self._foo()
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is True

    def test_return_cls_call(self):
        # return cls._foo()
        tree = _parse("""
            def foo(cls):
                return cls._foo()
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is True

    def test_expr_call_no_return(self):
        # self._foo()  (expression statement, no return)
        tree = _parse("""
            def foo(self):
                self._foo()
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is True

    def test_with_docstring(self):
        # docstring + return _foo()
        tree = _parse('''
            def foo():
                """公共接口。"""
                return _foo()
        ''')
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is True

    def test_not_trivial_if_has_logic(self):
        # 含 if 语句 → 非 trivial
        tree = _parse("""
            def foo():
                if True:
                    return _foo()
                return None
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is False

    def test_not_trivial_if_multi_statement(self):
        # 多语句 → 非 trivial
        tree = _parse("""
            def foo():
                x = 1
                return _foo()
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is False

    def test_not_trivial_if_wrong_target(self):
        # 调用 _bar() 而非 _foo() → 非 trivial wrapper for _foo
        tree = _parse("""
            def foo():
                return _bar()
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is False

    def test_not_trivial_if_no_call(self):
        # return 常量 → 非 trivial
        tree = _parse("""
            def foo():
                return 42
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is False

    def test_not_trivial_if_try_except(self):
        # try/except → 非 trivial
        tree = _parse("""
            def foo():
                try:
                    return _foo()
                except Exception:
                    return None
        """)
        node = tree.body[0]
        assert _is_trivial_wrapper(node, "_foo") is False


# ============================================================================
# _find_dead_public_wrappers 端到端测试
# ============================================================================


class TestFindDeadPublicWrappers:
    """_find_dead_public_wrappers 端到端检测（tmp_path 构造 fake 项目）。"""

    def test_detects_dead_wrapper(self, tmp_path):
        """无外部调用方的 trivial wrapper → 检测为 dead。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            def foo(x):
                return _foo(x)
            def _foo(x):
                return x + 1
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 1
        assert dead[0]["function"] == "foo"
        assert "mod.py" in dead[0]["file"]

    def test_not_dead_when_called_externally(self, tmp_path):
        """有外部调用方 → 非 dead。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            def foo(x):
                return _foo(x)
            def _foo(x):
                return x + 1
        """,
        )
        _write_py(
            src / "caller.py",
            """
            from .mod import foo
            def use():
                return foo(42)
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 0

    def test_not_dead_when_called_in_tests(self, tmp_path):
        """tests/ 中的调用也计入 → 非 dead。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            def foo(x):
                return _foo(x)
            def _foo(x):
                return x + 1
        """,
        )
        tests = tmp_path / "tests"
        _write_py(
            tests / "test_mod.py",
            """
            from zephyr.mod import foo
            def test_foo():
                assert foo(1) == 2
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 0

    def test_not_dead_when_called_in_scripts(self, tmp_path):
        """scripts/ 中的调用也计入 → 非 dead。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            def foo(x):
                return _foo(x)
            def _foo(x):
                return x + 1
        """,
        )
        scripts = tmp_path / "scripts"
        _write_py(
            scripts / "run.py",
            """
            from zephyr.mod import foo
            print(foo(1))
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 0

    def test_class_method_dead_wrapper(self, tmp_path):
        """类方法 dead wrapper 检测。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            class MyClass:
                def bar(self, x):
                    return self._bar(x)
                def _bar(self, x):
                    return x * 2
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 1
        assert dead[0]["function"] == "bar"
        assert "class:MyClass" in dead[0]["scope"]

    def test_skips_non_trivial_wrapper(self, tmp_path):
        """非 trivial wrapper（含额外逻辑）不检测为 dead。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            def foo(x):
                if x > 0:
                    return _foo(x)
                return 0
            def _foo(x):
                return x + 1
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 0

    def test_skips_dunder_methods(self, tmp_path):
        """__dunder__ 方法不检测。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            class MyClass:
                def __len__(self):
                    return self._len()
                def _len(self):
                    return 0
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 0

    def test_multiple_dead_wrappers(self, tmp_path):
        """多文件多 dead wrapper 检测。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "a.py",
            """
            def alpha(x):
                return _alpha(x)
            def _alpha(x):
                return x
        """,
        )
        _write_py(
            src / "b.py",
            """
            def beta(x):
                return _beta(x)
            def _beta(x):
                return x
        """,
        )
        dead = _find_dead_public_wrappers(tmp_path)
        names = {d["function"] for d in dead}
        assert names == {"alpha", "beta"}

    def test_empty_project(self, tmp_path):
        """空项目（无 src/zephyr/）→ 返回空列表。"""
        dead = _find_dead_public_wrappers(tmp_path)
        assert dead == []

    def test_self_call_in_body_counts(self, tmp_path):
        """wrapper body 中的 _foo() 调用不计入 foo 的外部调用方。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            def foo(x):
                return _foo(x)
            def _foo(x):
                return x + 1
        """,
        )
        # _foo() 在 body 中被调用，但 regex 搜的是 foo(，不是 _foo(
        # 所以 foo 的 call_count 应为 1（仅 def 行）→ dead
        dead = _find_dead_public_wrappers(tmp_path)
        assert len(dead) == 1


# ============================================================================
# reconcile 行为测试
# ============================================================================


class TestReconcile:
    """reconcile 行为测试：clean / warn / 永不抛异常。"""

    def test_reconcile_clean_when_no_dead(self, tmp_path):
        """无死 wrapper → action=clean。"""
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        result = spec.reconcile([], "test-session")
        assert result.action == "clean"
        assert result.gate_id == _GATE_ID

    def test_reconcile_warn_when_dead_found(self, tmp_path):
        """有死 wrapper → action=warn。"""
        src = tmp_path / "src" / "zephyr"
        _write_py(
            src / "mod.py",
            """
            def foo(x):
                return _foo(x)
            def _foo(x):
                return x + 1
        """,
        )
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        result = spec.reconcile(["src/zephyr/mod.py"], "test-session")
        assert result.action == "warn"
        assert "foo" in result.detail
        assert result.gate_id == _GATE_ID

    def test_reconcile_detail_truncation(self, tmp_path):
        """超过 _MAX_DETAIL_ITEMS 时截断。"""
        src = tmp_path / "src" / "zephyr"
        # 创建 12 个 dead wrapper（超过 _MAX_DETAIL_ITEMS=10）
        lines: list[str] = []
        for i in range(12):
            lines.append(f"def f{i}(x):")
            lines.append(f"    return _f{i}(x)")
            lines.append(f"def _f{i}(x):")
            lines.append("    return x")
            lines.append("")
        content = "\n".join(lines)
        src.mkdir(parents=True, exist_ok=True)
        (src / "mod.py").write_text(content, encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        result = spec.reconcile(["src/zephyr/mod.py"], "test-session")
        assert result.action == "warn"
        assert "and 2 more" in result.detail

    def test_reconcile_never_raises(self, tmp_path):
        """reconcile 遇到异常时降级为 warn，不抛异常。"""
        gw = _FakeGateway(tmp_path)
        spec = make_dead_public_wrapper_reconciler(gw)
        # 模拟 _find_dead_public_wrappers 抛异常
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "zephyr.governance.audit.dead_public_wrapper_reconciler._find_dead_public_wrappers",
                MagicMock(side_effect=RuntimeError("boom")),
            )
            result = spec.reconcile(["src/zephyr/foo.py"], "test-session")
        assert result.action == "warn"
        assert "error" in result.detail.lower()
        assert result.gate_id == _GATE_ID
