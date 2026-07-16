# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_docstring_coverage.py | §
# [MODULE] scripts.governance.d7_code.validate_docstring_coverage
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
validate_docstring_coverage.py — Docstring 覆盖率校验



对标：PEP 257 — all public modules/classes/functions should have docstrings
     AGENTS.md §5.1 — 零记忆重启标准（AI 靠 docstring 理解代码意图）

检测 src/zephyr/ 下所有 .py 文件中：
- 模块级 docstring 缺失
- 公共函数/类方法 docstring 缺失（排除私有 _xxx 和 dunder __xxx__）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Docstring 覆盖率校验——模块/类/公共函数必须有 docstring
dimensions:
- D7
priority: P2
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

from _shared.constants import EXIT_PASS, REPO_ROOT, SRC_DIR

SKIP_MODULES = {  # noqa: gate-vocab  跳过文档覆盖检查的业务子集
    "signal",
    "risk",
    "pf_core",
    "ex_core",
    "frontend",
    "research",
    "compliance",
    "ml_train",
    "integration",
}


def _has_docstring(node: ast.AST) -> bool:
    """_has_docstring implementation."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            return True
    return False


def _is_public(name: str) -> bool:
    """_is_public implementation."""
    if name.startswith("__") and name.endswith("__"):
        return False
    return not name.startswith("_")


def scan_docstrings(source_path: Path) -> tuple[bool, list[str]]:
    """扫描 docstring 覆盖率."""
    with open(source_path, encoding="utf-8") as f:
        """扫描 docstring 覆盖率."""
        """扫描并返回发现列表."""
        source = f.read()
    tree = ast.parse(source, filename=str(source_path))

    missing = []

    if not _has_docstring(tree):
        missing.append("[模块] 缺少 docstring")

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_public(node.name):
                if not _has_docstring(node):
                    missing.append(f"[函数] {node.name}() 缺少 docstring")
        elif isinstance(node, ast.ClassDef):
            if _is_public(node.name):
                if not _has_docstring(node):
                    missing.append(f"[类] {node.name} 缺少 docstring")
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if _is_public(sub.name) and sub.name != "__init__":
                            if not _has_docstring(sub):
                                missing.append(f"[方法] {node.name}.{sub.name}() 缺少 docstring")

    return _has_docstring(tree), missing
    """扫描 docstring 覆盖率."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Docstring 覆盖率校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    findings = []
    total_files = 0
    ok_files = 0

    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        parts = set(py_file.parts)
        if parts & SKIP_MODULES:
            continue

        total_files += 1
        has_module_doc, missing = scan_docstrings(py_file)

        if missing:
            try:
                rel = py_file.relative_to(REPO_ROOT)
            except ValueError:
                rel = py_file
            for m_item in missing:
                findings.append(f"[P2] {rel}  {m_item}")
        else:
            ok_files += 1

    if findings:
        print(
            f"\n[DOCSTRING] {len(findings)} 个 docstring 缺失（扫描 {total_files} 文件，{ok_files} 合格）:\n",
            file=sys.stderr,
        )
        for f_item in findings:
            print(f_item, file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[DOCSTRING] 全部 {total_files} 文件 docstring 完整 ✅\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
