"""测试结构合规门禁——检查 test_*.py 文件结构，防止"脚本伪装测试"和模块级副作用。

检查项:
  1. 每个 test_*.py 含至少一个 def test_* 函数
  2. 模块级代码零副作用（仅允许 import/常量赋值/类定义/函数定义/docstring）
  3. skip 装饰器必须有 TODO 注释（防止 skip 后遗忘修复）

用法:
  python scripts/governance/check_test_structure.py              # 硬阻断模式
  python scripts/governance/check_test_structure.py --warn-only  # 警告模式
  python scripts/governance/check_test_structure.py --path tests/unit  # 指定目录

退出码: 0 = 全部合规, 1 = 有违规
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 测试结构合规门禁——检查 test_*.py 文件结构，防止"脚本伪装测试"和模块级副作用。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import ast
import re
import sys
from pathlib import Path

_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # 退出码常量（scripts/governance sys.path）  # noqa: E402

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）  # noqa: E402

DEFAULT_TEST_DIR = REPO_ROOT / "tests"

# 已知"脚本伪装测试"——待逐步修复（每个加 def test_* 包装后从此集合删除）。
# 门禁硬阻断新增违规，豁免既有文件，逐步清零至 0。
# 2026-06-26: 8个豁免文件全部已添加 def test_* 包装，集合清零。
_EXEMPTED: set[str] = set()


def _is_docstring_expr(node: ast.Expr) -> bool:
    """Expr 节点是否为 docstring（字符串常量）。"""
    return isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)


def _is_name_main_check(test: ast.expr) -> bool:
    """判断条件是否是 __name__ == "__main__"。"""
    if isinstance(test, ast.Compare):
        if (
            isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and len(test.comparators) == 1
        ):
            cmp = test.comparators[0]
            if isinstance(cmp, ast.Constant) and cmp.value == "__main__":
                return True
    return False


def _is_sys_path_call(node: ast.expr) -> bool:
    """判断表达式是否是 sys.path.insert/append 调用（合法的 path 设置）。"""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if (
        isinstance(func, ast.Attribute)  # .insert / .append
        and isinstance(func.value, ast.Attribute)  # .path
        and isinstance(func.value.value, ast.Name)  # sys
        and func.value.value.id == "sys"
        and func.value.attr == "path"
        and func.attr in ("insert", "append")
    ):
        return True
    return False


def _is_allowed_toplevel(node: ast.stmt) -> bool:
    """判断模块级节点是否允许——精细判定，排除合法模式误报。"""
    if isinstance(
        node,
        (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
    ):
        return True
    # docstring
    if isinstance(node, ast.Expr) and _is_docstring_expr(node):
        return True
    # if __name__ == "__main__": 入口保护
    if isinstance(node, ast.If) and _is_name_main_check(node.test):
        return True
    # try/except（常用于 import 保护，如 importorskip 替代）
    if isinstance(node, ast.Try):
        return True
    # 模块级 assert（前置断言）
    if isinstance(node, ast.Assert):
        return True
    # sys.path.insert/append（路径设置，测试文件标准模式）
    if isinstance(node, ast.Expr) and _is_sys_path_call(node.value):
        return True
    return False


def _has_test_function(tree: ast.Module) -> bool:
    """模块是否含至少一个 def test_* 函数（含类内方法）。"""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                return True
    return False


_TODO_RE = re.compile(r"#\s*TODO", re.IGNORECASE)


def _has_skip_decorator(tree: ast.Module) -> bool:
    """模块是否含带 skip/skipif 装饰器的 test 函数。"""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            for dec in node.decorator_list:
                dec_str = ast.unparse(dec) if hasattr(ast, "unparse") else ""
                if "skip" in dec_str.lower():
                    return True
    return False


def _has_todo_comment(source: str) -> bool:
    """源码中是否含 # TODO 注释。"""
    return bool(_TODO_RE.search(source))


def check_file(filepath: Path) -> tuple[list[str], list[str]]:
    """检查单个 test_*.py，返回 (errors, warns)。
    errors=硬阻断（脚本伪装测试），warns=仅警告（模块级副作用，含合法模式误报）。
    """
    errors: list[str] = []
    warns: list[str] = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        return ([f"语法错误: {e}"], [])

    if not _has_test_function(tree):
        errors.append("缺少 def test_* 函数（疑似'脚本伪装测试'）")

    # skip 装饰器必须有 TODO 注释（防止 skip 后遗忘修复）
    if _has_skip_decorator(tree) and not _has_todo_comment(source):
        warns.append("含 skip 装饰器但无 # TODO 注释（skip 测试须标注修复计划）")

    for node in tree.body:
        if not _is_allowed_toplevel(node):
            if isinstance(node, ast.Expr):
                warns.append(f"模块级副作用语句 (line {node.lineno})")
            else:
                warns.append(f"模块级不允许的语句 (line {node.lineno}): {type(node).__name__}")

    return (errors, warns)


def main() -> int:
    parser = argparse.ArgumentParser(description="测试结构合规门禁")
    parser.add_argument("--warn-only", action="store_true", help="仅警告不阻断（exit 0）")
    parser.add_argument("--path", type=Path, default=DEFAULT_TEST_DIR, help="测试目录")
    args = parser.parse_args()

    test_dir: Path = args.path
    if not test_dir.exists():
        print(f"[ERROR] 测试目录不存在: {test_dir}")
        return EXIT_FINDINGS
    test_files = sorted(test_dir.rglob("test_*.py"))
    print(f"扫描 {len(test_files)} 个 test_*.py 文件...")

    total_errors = 0
    total_warns = 0
    exempt_count = 0
    for f in test_files:
        rel = f.relative_to(REPO_ROOT).as_posix()
        errors, warns = check_file(f)
        is_exempt = rel in _EXEMPTED
        if is_exempt and errors:
            exempt_count += 1
        for e in errors:
            tag = "EXEMPT" if is_exempt else "ERROR"
            print(f"  [{tag}] {rel}: {e}")
        for w in warns:
            print(f"  [WARN]  {rel}: {w}")
        if not is_exempt:
            total_errors += len(errors)
        total_warns += len(warns)

    print("\n== 结果 ==")
    print(f"  扫描: {len(test_files)} | ERROR: {total_errors} | WARN: {total_warns} | EXEMPT: {exempt_count}")

    if total_errors == 0 and total_warns == 0:
        print("  ALL CLEAN")
        return EXIT_PASS
    if total_errors == 0:
        print("  仅有 WARN（不阻断）")
        return EXIT_PASS
    print(f"  {'WARN-ONLY（不阻断）' if args.warn_only else 'BLOCKED by ERROR'}")
    return 0 if args.warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
