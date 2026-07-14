# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_git_dangerous.py | §
# [MODULE] scripts.governance.d6_security.detect_git_dangerous
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
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
detect_git_dangerous.py — 危险 Git 命令检测



对标：PS-STD-003 ABS-26（禁止 git push --force 到保护分支）
              ABS-27（禁止 git reset --hard 在共享分支）
              ABS-28（禁止 git clean -fd 无确认）

检测内容：
- 文档/脚本中出现的危险 git 命令建议或指令
- git push --force / -f
- git reset --hard
- git clean -fdx / git clean -fd
- git branch -D（强制删除）
- git rebase 高危变体

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 危险 Git 命令检测（ABS-26~28 — push --force / reset --hard / clean -fdx）
dimensions:
- D6
priority: P0
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
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

DANGEROUS_GIT_PATTERNS = [
    ("git\\s+push\\s+.*(--force|-f)", "git push --force 危险操作 (ABS-26)"),
    ("git\\s+reset\\s+--hard", "git reset --hard 危险操作 (ABS-27)"),
    ("git\\s+clean\\s+(-fdx|-fd\\b.*-)", "git clean -fdx/fd 危险操作 (ABS-28)"),
    ("git\\s+branch\\s+-D\\b", "git branch -D 强制删除分支"),
    ("git\\s+rebase\\s+.*(--onto|--root|-i.*origin)", "git rebase 高危变体"),
    ("git\\s+push\\s+--delete\\s+origin", "git push --delete 远程分支删除"),
]
EXCLUDE_FILES = {"detect_git_dangerous.py"}


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    "扫描单个文件并返回发现列表."
    try:
        "扫描单个文件并返回发现列表."
        "扫描并返回发现列表."
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for pattern, label in DANGEROUS_GIT_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": content[: match.start()].count("\n") + 1,
                    "pattern": label,
                    "matched": match.group(0)[:120],
                }
            )
    return findings
    "扫描单个文件并返回发现列表."


def scan_repo(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描仓库并返回发现列表."""
    if scan_dir is None:
        "扫描仓库并返回发现列表."
        "扫描并返回发现列表."
        scan_dir = REPO_ROOT
    all_findings = []
    files_scanned = 0
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_files=frozenset(EXCLUDE_FILES)):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except (ValueError, OSError):
            continue
        if str(rel).startswith("_DO_NOT_USE") or str(rel).startswith(".trae"):
            continue
        files_scanned += 1
        findings = scan_file(filepath)
        all_findings.extend(findings)
    return (all_findings, files_scanned, 0)
    "扫描仓库并返回发现列表."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="危险 Git 命令检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(f"\n[GIT-DANGEROUS] {len(findings)} 危险 Git 命令发现（扫描 {files_scanned} 文件）:\n", file=sys.stderr)
        for f in findings:
            print(f"  [{f['pattern']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['matched']}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
