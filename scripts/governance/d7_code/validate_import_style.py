"""
validate_import_style.py — 导入风格一致性校验

对标：PEP 8 — absolute imports recommended over relative imports
     AGENTS.md §6.4 — AI-Construction-Friendliest: 显式优于隐式

检测 src/zephyr/ 下所有 .py 文件中使用相对导入 (from . import) 的文件。
项目主风格是绝对导入 (from zephyr.xxx import yyy)，
相对导入降低 AI 可读性——AI 需要额外推理"这个 . 指向哪个父包"。

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

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

from _shared.constants import REPO_ROOT, SRC_DIR

SKIP_MODULES = {
    "l03_signal_generation",
    "l04_risk_management",
    "l05_portfolio_construction",
    "l06_trade_execution",
    "l07_post_trade_analytics",
    "l08_human_ai_interface",
    "l09_research_innovation",
    "l10_compliance",
    "l11_ml_platform",
    "l13_experimentation",
}

ALLOWED_RELATIVE = {"test_schemas.py"}

def _has_relative_import(tree: ast.AST) -> list[int]:
    lines = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level is not None and node.level > 0:
                lines.append(node.lineno)
    return lines

def scan_import_style(source_path: Path) -> list[int]:
    """扫描 import 风格合规性."""
    with open(source_path, encoding="utf-8") as f:
        """扫描 import 风格合规性."""
        """扫描并返回发现列表."""
        source = f.read()
    tree = ast.parse(source, filename=str(source_path))
    return _has_relative_import(tree)
    """扫描 import 风格合规性."""

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="导入风格一致性校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    findings = []
    total_files = 0

    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        total_files += 1

        parts = set(py_file.parts)
        if parts & SKIP_MODULES:
            continue
        if py_file.name in ALLOWED_RELATIVE:
            continue

        rel_lines = scan_import_style(py_file)
        if rel_lines:
            try:
                rel = py_file.relative_to(REPO_ROOT)
            except ValueError:
                rel = py_file
            lines_str = ",".join(str(L) for L in rel_lines)
            findings.append(f"[P2] {rel}:{lines_str}  使用了相对导入（项目主风格为绝对导入）")

    if findings:
        print(
            f"\n[IMPORT-STYLE] {len(findings)} 个文件使用相对导入（扫描 {total_files} 非__init__文件）:\n",
            file=sys.stderr,
        )
        for f_item in findings:
            print(f_item, file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[IMPORT-STYLE] 全部 {total_files} 文件使用绝对导入 ✅\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if findings else 0)

if __name__ == "__main__":
    main()
