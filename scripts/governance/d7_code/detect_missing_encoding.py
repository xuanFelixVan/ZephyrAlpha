# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_missing_encoding.py | §
# [MODULE] scripts.governance.d7_code.detect_missing_encoding
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
# [TTL] task_bound
"""
detect_missing_encoding.py — open() 缺 encoding 检测



对标：ABS-24（Python 写文件必须指定 encoding='utf-8'）
     AGENTS.md §4 编码安全（唯一始终生效的硬规则）

检测内容：
- AST 扫描 src/zephyr/ 和 scripts/governance/ 下 .py 文件
- 检测 open() 调用缺少 encoding 参数
- 排除 'rb'/'wb' 二进制模式（不需要 encoding）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: open() 缺 encoding 检测（ABS-24 — Python写文件必须指定encoding='utf-8'）
dimensions:
- D7
priority: P0
timeout_seconds: 30
warn_only: false
"""


import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse


def check_open_encoding(filepath: Path) -> list[dict]:
    """检查 open() 调用缺少 encoding."""
    findings = []
    """检查并返回违规列表."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        is_open = (isinstance(func, ast.Name) and func.id == "open") or (
            isinstance(func, ast.Attribute) and func.attr == "open"
        )
        if not is_open:
            continue

        mode_val = None
        has_encoding = False

        for kw in node.keywords:
            if kw.arg == "encoding":
                has_encoding = True
            elif kw.arg == "mode":
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    mode_val = kw.value.value

        if len(node.args) >= 2:
            mode_arg = node.args[1]
            if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                mode_val = mode_arg.value

        is_binary = mode_val and ("b" in mode_val)

        if not has_encoding and not is_binary:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
            line = node.lineno
            findings.append(
                {
                    "file": rel,
                    "line": line,
                    "severity": "HIGH",
                }
            )

    return findings
    """检查 open() 调用缺少 encoding."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="open() 缺 encoding 检测（ABS-24）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    all_findings = []
    scan_dirs = [
        REPO_ROOT / "src" / "zephyr",
        REPO_ROOT / "scripts" / "governance",
    ]

    files_scanned = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_PY):
            files_scanned += 1
            findings = check_open_encoding(filepath)
            all_findings.extend(findings)

    if all_findings:
        print(
            f"\n[MISSING-ENC] {len(all_findings)} 个 open() 调用缺少 encoding（扫描 {files_scanned} 文件）:",
            file=sys.stderr,
        )
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
    else:
        print(f"[MISSING-ENC] 所有 open() 调用均指定了 encoding（扫描 {files_scanned} 文件）", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
