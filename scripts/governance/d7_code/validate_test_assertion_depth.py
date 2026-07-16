# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_test_assertion_depth.py | §
# [MODULE] scripts.governance.d7_code.validate_test_assertion_depth
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
validate_test_assertion_depth.py — 测试断言深度校验



对标：ISTQB Foundation Level §4.3 — 测试断言应验证具体行为而非仅"抛出异常了"
     Martin Fowler — Assertion Roulette（没有消息的断言 = 猜谜游戏）

检测 tests/ 下测试文件中的浅断言模式：
1. pytest.raises(Type) 未用 match 参数验证错误消息
2. assert True / assert False（占位断言）
3. try/except 捕获异常后无 assert（静默吞掉异常）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 测试断言深度校验——raises 有没有 match、有没有 assert True/False、try/except是否静默吞异常
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""


import argparse
import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import sys
from pathlib import Path
from typing import Any

from _shared.constants import EXIT_PASS, REPO_ROOT

TESTS_DIR = REPO_ROOT / "tests"


def _has_raises_without_match(tree: ast.AST) -> list[int]:
    """_has_raises_without_match implementation."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if (
                    node.func.attr == "raises"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "pytest"
                ):
                    has_match = any(kw.arg == "match" for kw in node.keywords)
                    if not has_match:
                        lines.append(node.lineno)
    return lines


def _has_bare_assert_boolean(tree: ast.AST) -> list[int]:
    """_has_bare_assert_boolean implementation."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            if isinstance(node.test, ast.Constant):
                if isinstance(node.test.value, bool):
                    lines.append(node.lineno)
    return lines


def _has_swallowed_exceptions(tree: ast.AST) -> list[int]:
    """_has_swallowed_exceptions implementation."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                has_assert = False
                for sub in ast.walk(handler):
                    if isinstance(sub, ast.Assert):
                        has_assert = True
                        break
                if not has_assert and handler.body:
                    stmts = [s for s in handler.body if not isinstance(s, ast.Pass)]
                    if stmts and not any(isinstance(s, ast.Assert) for s in stmts):
                        lines.append(handler.lineno)
    return lines


def scan_assertion_depth(test_path: Path) -> dict[str, Any]:
    """扫描断言深度."""
    with open(test_path, encoding="utf-8") as f:
        """扫描断言深度."""
        """扫描并返回发现列表."""
        source = f.read()
    tree = ast.parse(source, filename=str(test_path))

    return {
        "raises_no_match": _has_raises_without_match(tree),
        "bare_bool": _has_bare_assert_boolean(tree),
        "swallowed": _has_swallowed_exceptions(tree),
    }
    """扫描断言深度."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="测试断言深度校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    findings = []
    total_tests = 0

    for test_file in TESTS_DIR.rglob("test_*.py"):
        total_tests += 1
        result = scan_assertion_depth(test_file)

        try:
            rel = test_file.relative_to(REPO_ROOT)
        except ValueError:
            rel = test_file

        if result["raises_no_match"]:
            lines_str = ",".join(str(L) for L in result["raises_no_match"])
            findings.append(f"[P1] {rel}:{lines_str}  pytest.raises 未验证异常消息（建议加 match= 参数）")

        if result["bare_bool"]:
            lines_str = ",".join(str(L) for L in result["bare_bool"])
            findings.append(f"[P1] {rel}:{lines_str}  assert True/False 占位断言")

        if result["swallowed"]:
            lines_str = ",".join(str(L) for L in result["swallowed"])
            findings.append(f"[P1] {rel}:{lines_str}  try/except 块未做断言（异常被静默吞掉）")

    if findings:
        print(f"\n[ASSERT-DEPTH] {len(findings)} 个浅断言问题（扫描 {total_tests} 测试文件）:\n", file=sys.stderr)
        for f_item in findings:
            print(f_item, file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[ASSERT-DEPTH] 全部 {total_tests} 测试文件断言深度合格 ✅\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
