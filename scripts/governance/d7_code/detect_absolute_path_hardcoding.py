# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_absolute_path_hardcoding.py | §
# [MODULE] scripts.governance.d7_code.detect_absolute_path_hardcoding
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
detect_absolute_path_hardcoding.py — 绝对路径硬编码检测（蓝图 §34.1 操作陷阱）

扫描 scripts/governance/ 下全部 .py 文件，
检测硬编码的 D:\\ZephyrAlpha 绝对路径（排除蓝图引用）。

Usage:
    python scripts/governance/d7_code/detect_absolute_path_hardcoding.py
    python scripts/governance/d7_code/detect_absolute_path_hardcoding.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 绝对路径硬编码检测 — 扫描governance/Python 中 D:\\ZephyrAlpha 硬编码
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, SCRIPTS_DIR

HARDCODED_PATH_PATTERN = re.compile(r'["\']D:\\ZephyrAlpha[^"\']*["\']')
ALLOWED_PATTERNS = [
    re.compile(r"__manifest__"),
    re.compile(r"blueprint\.md"),
    re.compile(r"upstream_files"),
    re.compile(r"# .*D:\\\\ZephyrAlpha"),
]

EXCLUDE_FILES = {"__init__.py"}


def scan_file(file_path: Path) -> list[tuple[int, str]]:
    """扫描单个 Python 文件中的硬编码路径。

    Args:
        file_path: Python 文件路径

    Returns:
        list[tuple[int, str]]: (行号, 匹配的行内容) 列表
    """
    violations: list[tuple[int, str]] = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").split("\n")
    except OSError:
        return violations

    for i, line in enumerate(lines, 1):
        if not HARDCODED_PATH_PATTERN.search(line):
            continue
        if any(ap.search(line) for ap in ALLOWED_PATTERNS):
            continue
        violations.append((i, line.strip()))
    return violations


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="绝对路径硬编码检测")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    all_violations: dict[str, list[tuple[int, str]]] = {}
    py_files = sorted(SCRIPTS_DIR.rglob("*.py"))
    for pf in py_files:
        if pf.name in EXCLUDE_FILES:
            continue
        v = scan_file(pf)
        if v:
            all_violations[str(pf.relative_to(SCRIPTS_DIR))] = v

    if all_violations:
        total = sum(len(v) for v in all_violations.values())
        print(f"\n[ABSOLUTE-PATH] 发现 {total} 处硬编码绝对路径：\n", file=sys.stderr)
        for fpath, vlist in sorted(all_violations.items()):
            print(f"  📁 {fpath}:", file=sys.stderr)
            for lineno, line in vlist:
                print(f"      L{lineno}: {line[:120]}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print("\n[ABSOLUTE-PATH] ✅ 无硬编码绝对路径\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
