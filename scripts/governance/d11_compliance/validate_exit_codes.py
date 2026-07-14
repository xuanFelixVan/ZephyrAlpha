# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_exit_codes.py | §
# [MODULE] scripts.governance.d11_compliance.validate_exit_codes
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
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
validate_exit_codes.py — 审计脚本退出码规范门禁

对标 SCRIPT-QUALITY-001 D-F-02（POSIX exit codes）+ D-D-04（同一概念只在一处定义）

检测内容：
- sys.exit(0/1/2) 裸数字 → 应使用 EXIT_PASS / EXIT_FINDINGS / EXIT_ERROR
- return 0/1/2 裸数字（在 main() 或返回 int 的函数中）→ 应使用命名常量
- 缺少 EXIT 常量 import 的文件

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 审计脚本退出码规范门禁——检测裸 sys.exit(0/1/2) 和 return 0/1/2
dimensions:
- D11
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, SCRIPTS_DIR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

RE_SYS_EXIT_BARE = re.compile(r"sys\.exit\(\s*([012])\s*\)")
RE_RETURN_BARE = re.compile(r"^(\s*)return\s+([012])\s*$", re.MULTILINE)
RE_EXIT_CONST = re.compile(r"EXIT_PASS|EXIT_FINDINGS|EXIT_ERROR")
EXCLUDE_DIRS = frozenset({"_shared", "__pycache__", "test_fixtures"})

_BARE_TO_CONST = {"0": "EXIT_PASS", "1": "EXIT_FINDINGS", "2": "EXIT_ERROR"}


def scan_scripts() -> list[dict]:
    """scan_scripts implementation."""
    findings = []
    for py in sorted(SCRIPTS_DIR.rglob("*.py")):
        parts = py.relative_to(SCRIPTS_DIR).parts
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        if py.name == "__init__.py":
            continue
        try:
            src = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(py.relative_to(SCRIPTS_DIR)).replace("\\", "/")

        for m in RE_SYS_EXIT_BARE.finditer(src):
            line_no = src[: m.start()].count("\n") + 1
            findings.append(
                {
                    "file": rel,
                    "line": line_no,
                    "code": m.group(0),
                    "suggestion": f"sys.exit({_BARE_TO_CONST[m.group(1)]})",
                    "type": "sys.exit",
                }
            )

        for m in RE_RETURN_BARE.finditer(src):
            line_no = src[: m.start()].count("\n") + 1
            findings.append(
                {
                    "file": rel,
                    "line": line_no,
                    "code": m.group(0).strip(),
                    "suggestion": f"return {_BARE_TO_CONST[m.group(2)]}",
                    "type": "return",
                }
            )

    return findings


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    findings = scan_scripts()
    if not findings:
        print("OK — all exit codes use named constants", file=sys.stderr)
        return EXIT_PASS

    by_file: dict[str, list[dict]] = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    print(f"FINDINGS — {len(findings)} bare exit code(s) in {len(by_file)} file(s):", file=sys.stderr)
    for file, items in sorted(by_file.items()):
        print(f"\n  {file}:", file=sys.stderr)
        for item in items:
            print(f"    L{item['line']}: {item['code']}  →  {item['suggestion']}", file=sys.stderr)

    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
