# [BLUEPRINT] MOD-GOV-058 | scripts/governance/check_test_symbol_validity.py | §
# [MODULE] scripts.governance.check_test_symbol_validity
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance._shared.constants (EXIT_*/REPO_ROOT)
# [CONSUMERS] .pre-commit-config.yaml gate-test-symbol-validity；手动全量审计
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读检测（不写任何文件）；无法解析到仓内真源的 import 一律跳过（不误报三方库）；__all__ 与顶层符号并集判定
# [MODIFY-GUARD] 检测语义变更须同步 tests/governance/test_check_test_symbol_validity.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=PASS / 1=发现孤儿符号引用 / 2=脚本自身错误；--warn-only 恒 0
# [TESTS] tests/governance/test_check_test_symbol_validity.py
# [A_module] module_id=MOD-GOV-058 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""check_test_symbol_validity.py — 孤儿测试符号检测门禁（CAND-GATEMECH-007）。

检测"测试文件 import 了真源不存在的符号"（超前孤儿测试）：
AST 扫描测试文件的 ``from X import a, b`` 语句，解析 X 到仓内真源 .py，
比对目标模块的 ``__all__``（静态字面量）与顶层符号并集——引用的符号不存在即报。

病根（2026-08-19 实证）：test_warn_in_main_workspace 引用 _warn_worktree_isolation
符号在源码与 git 全史零命中——超前孤儿测试滞留存量红基线 18 天无门禁拦截。

防误报设计（宁可放过，不可误伤）：
- 模块解析不到仓内 .py（stdlib / 三方库 / 动态装配）→ 跳过，不报。
- ``from x import *`` → 跳过（无法静态枚举）。
- 目标符号集合 = __all__ 字面量 ∪ 顶层 def/class/赋值/import 名（含 __init__
  re-export），动态 __all__ 拼装（append/运算）→ 该模块整模块跳过。
- 语法错误的测试文件 → 跳过（由 GATE-19/语法检查负责）。

Usage:
    python scripts/governance/check_test_symbol_validity.py                # 全量扫 tests/
    python scripts/governance/check_test_symbol_validity.py tests/x.py     # 指定文件
    python scripts/governance/check_test_symbol_validity.py --warn-only    # 不阻断
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 孤儿测试符号检测——测试 import 引用真源不存在的符号即报（CAND-GATEMECH-007）
dimensions:
- D7
priority: P1
timeout_seconds: 60
warn_only: false
"""

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402

__all__: Final = ["OrphanSymbol", "check_test_file", "collect_module_symbols", "main"]


@dataclass(frozen=True)
class OrphanSymbol:
    """一条孤儿符号引用。"""

    test_file: str
    module: str
    symbol: str
    line: int


def _collect_all_literal(node: ast.stmt) -> set[str] | None:
    """提取静态 __all__ 字面量；动态拼装（append/拼接/推导式）返回 None。"""
    if not isinstance(node, (ast.Assign, ast.AnnAssign)):
        return None
    value = node.value
    if value is None or not isinstance(value, (ast.List, ast.Tuple)):
        return None
    names: set[str] = set()
    for elt in value.elts:
        if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
            return None
        names.add(elt.value)
    return names


def _has_dynamic_all_mutation(tree: ast.Module) -> bool:
    """检测 __all__ 动态拼装（append/extend 调用或 += 增强赋值）。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == "__all__":
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "__all__"
        ):
            return True
    return False


def _add_top_level_symbols(tree: ast.Module, symbols: set[str]) -> None:
    """收集模块顶层符号（函数/类/赋值/导入别名）。"""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            symbols.add(node.target.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                symbols.add(alias.asname or alias.name.split(".")[0])


def _collect_all_symbols(tree: ast.Module, symbols: set[str]) -> bool:
    """收集 __all__ 字面量；遇动态拼装返回 False（整模块跳过）。"""
    for node in tree.body:
        all_literal = _collect_all_literal(node)
        if all_literal is None and isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == "__all__" for t in targets):
                return False
        elif all_literal is not None:
            symbols |= all_literal
    return True


def collect_module_symbols(path: Path) -> set[str] | None:
    """收集模块可用符号（__all__ ∪ 顶层符号）。文件缺失/语法错误/动态 __all__ 返回 None（跳过）。"""
    if not path.is_file():
        return None
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return None
    if _has_dynamic_all_mutation(tree):
        return None

    symbols: set[str] = set()
    _add_top_level_symbols(tree, symbols)
    if not _collect_all_symbols(tree, symbols):
        return None
    return symbols


def _resolve_module(dotted: str, level: int, test_file: Path, repo_root: Path) -> Path | None:
    """把 import 模块路径解析为仓内 .py 文件；不可解析返回 None（跳过，不报）。"""
    if level > 0:
        base = test_file.parent
        for _ in range(level - 1):
            base = base.parent
        parts = dotted.split(".") if dotted else []
        anchor = base.joinpath(*parts) if parts else base
        for candidate in (anchor.with_suffix(".py"), anchor / "__init__.py"):
            if candidate.is_file():
                return candidate
        return None
    parts = dotted.split(".")
    roots = [repo_root / "src", repo_root, repo_root / "scripts" / "governance"]
    for root in roots:
        anchor = root.joinpath(*parts)
        for candidate in (anchor.with_suffix(".py"), anchor / "__init__.py"):
            if candidate.is_file():
                return candidate
    return None


def check_test_file(test_file: Path, repo_root: Path) -> list[OrphanSymbol]:
    """扫描单个测试文件的 from-import 符号有效性。"""
    try:
        tree = ast.parse(test_file.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return []

    findings: list[OrphanSymbol] = []
    try:
        rel = test_file.relative_to(repo_root).as_posix()
    except ValueError:
        rel = test_file.as_posix()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or (node.module is None and node.level == 0):
            continue
        module = node.module or ""
        if any(alias.name == "*" for alias in node.names):
            continue
        source = _resolve_module(module, node.level, test_file, repo_root)
        if source is None:
            continue
        symbols = collect_module_symbols(source)
        if symbols is None:
            continue
        for alias in node.names:
            if alias.name in symbols:
                continue
            # from pkg import submodule —— 名字是子模块文件而非符号，豁免
            if (source.parent / f"{alias.name}.py").is_file() or (source.parent / alias.name / "__init__.py").is_file():
                continue
            findings.append(OrphanSymbol(rel, module, alias.name, node.lineno))
    return findings


def _iter_test_files(repo_root: Path) -> list[Path]:
    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        return []
    return sorted(tests_dir.rglob("test_*.py"))


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="孤儿测试符号检测（CAND-GATEMECH-007）")
    parser.add_argument("files", nargs="*", help="待检测测试文件（pre-commit positional；为空全量扫 tests/）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    parser.add_argument("--ci", action="store_true", help="CI 硬阻断模式（与默认一致，占位兼容）")
    args = parser.parse_args()

    try:
        targets = [Path(f).resolve() for f in args.files] if args.files else _iter_test_files(REPO_ROOT)
        findings: list[OrphanSymbol] = []
        for test_file in targets:
            if test_file.is_file():
                findings.extend(check_test_file(test_file, REPO_ROOT))
    except OSError as exc:
        print(f"[TEST-SYMBOL] ERROR: 扫描失败（{type(exc).__name__}）", file=sys.stderr)
        return EXIT_ERROR

    if findings:
        print(f"\n[TEST-SYMBOL] {len(findings)} 处孤儿符号引用（测试 import 了真源不存在的符号）:\n", file=sys.stderr)
        for f in findings:
            print(f"  {f.test_file}:{f.line}  from {f.module} import {f.symbol}  ← 符号不存在", file=sys.stderr)
        print("\n修复: 修正 import 符号名，或删除超前孤儿测试（真源符号以 __all__ ∪ 顶层符号为准）", file=sys.stderr)
    else:
        print(f"[TEST-SYMBOL] PASS（扫描 {len(targets)} 个测试文件，0 孤儿符号引用）", file=sys.stderr)

    if args.warn_only:
        return EXIT_PASS
    return EXIT_FINDINGS if findings else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
