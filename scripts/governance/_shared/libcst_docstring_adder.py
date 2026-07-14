# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/libcst_docstring_adder.py | §
# [MODULE] scripts.governance._shared.libcst_docstring_adder
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
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
# [TTL] task_bound
"""libcst_docstring_adder.py — Lossless docstring addition using LibCST.

Uses Concrete Syntax Tree (CST) instead of ast.unparse() to preserve
ALL formatting: inline comments, whitespace, blank lines, parentheses.

Usage:
    python _shared/libcst_docstring_adder.py [files...]

If no files given, scans all .py under scripts/governance/ (excluding
__init__.py and _shared/).

Safety guarantees:
    - Roundtrip: parse_module(code).code == code (byte-for-byte)
    - Only adds docstrings where missing; never modifies existing code
    - Inline comments, block comments, and formatting are 100% preserved
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import libcst as cst
from libcst import Expr, Newline, SimpleStatementLine, SimpleString, TrailingWhitespace

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()


def _has_docstring_cst(node: cst.FunctionDef | cst.Module) -> bool:
    """Check if a CST node already has a docstring."""
    if isinstance(node, cst.Module):
        stmts = node.body
    elif isinstance(node, cst.FunctionDef):
        stmts = node.body.body
    else:
        return False
    if not stmts:
        return False
    first = stmts[0]
    return (
        isinstance(first, SimpleStatementLine)
        and len(first.body) == 1
        and isinstance(first.body[0], Expr)
        and isinstance(first.body[0].value, SimpleString)
    )


def _infer_func_docstring(func_name: str) -> str:
    """Infer a docstring description from function name prefix."""
    templates = {
        "main": "Entry point: parse args, run logic, return exit code.",
        "check_": "Check compliance and report findings.",
        "validate_": "Validate target against rules and report findings.",
        "audit_": "Audit target and report findings.",
        "detect_": "Detect issues in target and report findings.",
        "generate_": "Generate output from input data.",
        "sync_": "Synchronize target with source of truth.",
        "merge_": "Merge sources into unified output.",
        "batch_": "Batch process multiple targets.",
        "analyze_": "Analyze target and report insights.",
    }
    for prefix, desc in templates.items():
        if func_name.startswith(prefix):
            return desc
    return f"{func_name} implementation."


class ModuleDocstringAdder(cst.CSTTransformer):
    """CST transformer that adds module-level docstrings where missing."""

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Add docstring to module if missing."""
        if _has_docstring_cst(updated_node):
            return updated_node
        docstring_node = SimpleStatementLine(
            body=[Expr(value=SimpleString('"""Module docstring — see module-level docstring for details."""'))],
            leading_lines=[],
            trailing_whitespace=TrailingWhitespace(newline=Newline()),
        )
        new_body = (docstring_node,) + updated_node.body
        return updated_node.with_changes(body=new_body)


class FunctionDocstringAdder(cst.CSTTransformer):
    """CST transformer that adds function docstrings where missing."""

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        """Add docstring to function if missing."""
        if _has_docstring_cst(updated_node):
            return updated_node
        desc = _infer_func_docstring(updated_node.name.value)
        docstring_node = SimpleStatementLine(
            body=[Expr(value=SimpleString(f'"""{desc}"""'))],
            leading_lines=[],
            trailing_whitespace=TrailingWhitespace(newline=Newline()),
        )
        new_body = updated_node.body.with_changes(body=[docstring_node] + list(updated_node.body.body))
        return updated_node.with_changes(body=new_body)


def add_docstrings_lossless(filepath: Path, *, dry_run: bool = False) -> tuple[int, int]:
    """Add missing docstrings to a Python file using lossless LibCST transformation."""
    code = filepath.read_text(encoding="utf-8")
    try:
        tree = cst.parse_module(code)
    except cst.ParserSyntaxError as e:
        print(f"  SKIP (parse error): {filepath}: {e}")
        return 0, 0

    original_code = tree.code
    modified = tree.visit(ModuleDocstringAdder())
    modified = modified.visit(FunctionDocstringAdder())
    new_code = modified.code

    if new_code == original_code:
        return 0, 0

    module_added = not _has_docstring_cst(cst.parse_module(original_code)) and _has_docstring_cst(
        cst.parse_module(new_code)
    )
    func_with_doc_before = sum(
        1
        for node in ast.walk(ast.parse(original_code))
        if isinstance(node, ast.FunctionDef) and ast.get_docstring(node)
    )
    func_with_doc_after = sum(
        1 for node in ast.walk(ast.parse(new_code)) if isinstance(node, ast.FunctionDef) and ast.get_docstring(node)
    )
    func_added = func_with_doc_after - func_with_doc_before

    if dry_run:
        print(f"  WOULD ADD: {filepath}: +{1 if module_added else 0} module, +{func_added} function docstrings")
        return module_added, func_added

    filepath.write_text(new_code, encoding="utf-8")
    print(f"  ADDED: {filepath}: +{1 if module_added else 0} module, +{func_added} function docstrings")
    return module_added, func_added


def main() -> int:
    """Entry point: scan files and add missing docstrings using LibCST."""
    parser = argparse.ArgumentParser(description="Lossless docstring addition using LibCST")
    parser.add_argument("files", nargs="*", help="Specific .py files to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even if changes needed")
    args = parser.parse_args()

    if args.files:
        targets = [Path(f) for f in args.files]
    else:
        gov_dir = REPO_ROOT / "scripts" / "governance"
        targets = [
            f
            for f in iter_files(gov_dir, extensions=SCAN_EXTENSIONS_PY)
            if f.name != "__init__.py" and "_shared" not in f.parts
        ]

    total_module = 0
    total_func = 0
    for fp in targets:
        m, f = add_docstrings_lossless(fp, dry_run=args.dry_run)
        total_module += m
        total_func += f

    print(f"\nSummary: +{total_module} module docstrings, +{total_func} function docstrings")
    if args.dry_run:
        print("(dry run — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
