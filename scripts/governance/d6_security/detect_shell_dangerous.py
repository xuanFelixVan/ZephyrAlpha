# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_shell_dangerous.py | §
# [MODULE] scripts.governance.d6_security.detect_shell_dangerous
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
detect_shell_dangerous.py — 危险 Shell 命令检测



对标：PS-STD-003 ABS-38（禁止 rm -rf / 无确认破坏性删除）
              ABS-39（禁止在脚本中嵌入高危系统命令）

检测内容：
- rm -rf / 及变体（Unix）
- del /f /s /q 递归强制删除（Windows）
- format / mkfs 磁盘格式化命令
- dd 磁盘覆写命令
- :(){ :|:& };: fork bomb 模式
- chmod 777 过度授权

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 危险 Shell 命令检测（ABS-38~39 — rm -rf / / format / fork bomb）
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

ensure_utf8_stdout()
import argparse

DANGEROUS_SHELL_PATTERNS = [
    ("rm\\s+-rf\\s+/", "rm -rf / 根目录破坏命令 (ABS-38)"),
    ("rm\\s+-rf\\s+[~/]", "rm -rf 家目录/根目录 危险变体 (ABS-38)"),
    ("rm\\s+-rf\\s+\\*", "rm -rf * 通配删除 (ABS-38)"),
    ("rm\\s+-rf\\s+--no-preserve-root", "rm -rf --no-preserve-root 危险选项 (ABS-38)"),
    ("del\\s+/[fs](?:\\s+/[qs])?\\s+\\*\\.\\*", "Windows 递归强制删除 (ABS-38)"),
    ("del\\s+/[fs](?:\\s+/[qs])?\\s+[A-Z]:\\\\", "Windows 盘符强制删除 (ABS-38)"),
    ("\\bformat\\s+[A-Z]:", "Windows format 格式化命令 (ABS-39)"),
    ("\\bmkfs\\.", "mkfs 磁盘格式化命令 (ABS-39)"),
    ("\\bdd\\s+if=", "dd 磁盘覆写命令 (ABS-39)"),
    (":\\(\\)\\s*\\{.*:\\|:&\\s*\\};:", "Fork Bomb 模式 (ABS-39)"),
    ("chmod\\s+(777|o\\+w\\s+/|a\\+w\\s+/)", "chmod 777 / 过度授权 (ABS-39)"),
    (">\\s*/dev/sd[a-z]", "覆写块设备 (ABS-39)"),
]
EXCLUDE_FILES = {"detect_shell_dangerous.py"}


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
    for pattern, label in DANGEROUS_SHELL_PATTERNS:
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
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_dirs=EXCLUDE_DIRS):
        if filepath.name in EXCLUDE_FILES:
            continue
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
    parser = argparse.ArgumentParser(description="危险 Shell 命令检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(
            f"\n[SHELL-DANGEROUS] {len(findings)} 危险 Shell 命令发现（扫描 {files_scanned} 文件）:\n", file=sys.stderr
        )
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
