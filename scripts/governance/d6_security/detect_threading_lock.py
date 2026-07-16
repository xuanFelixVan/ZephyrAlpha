# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_threading_lock.py | §
# [MODULE] scripts.governance.d6_security.detect_threading_lock
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
# [TTL] permanent
"""
detect_threading_lock.py — threading.Lock 导入检测



对标：PS-STD-003 ABS-40（禁止 threading.Lock——项目全局异步架构）
     5 份 AI 工程接口规范一致声明（context-engine / agent-orchestrator / ...）

替代方案：进程内锁用 asyncio.Lock，跨进程锁用 filelock.FileLock

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: threading.Lock 导入检测（ABS-40 — 全局异步架构违规）
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
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.walk import iter_files

THREADING_LOCK_PATTERNS = [
    ("from\\s+threading\\s+import\\s+.*\\bLock\\b", "导入 threading.Lock（含 from import）"),
    ("import\\s+threading\\b", "导入 threading 模块（可能使用 threading.Lock）"),
    ("threading\\.Lock\\s*\\(", "直接使用 threading.Lock()"),
]
WHITELIST_FILES = {"detect_threading_lock.py"}


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
    for pattern, label in THREADING_LOCK_PATTERNS:
        for match in re.finditer(pattern, content):
            line_num = content[: match.start()].count("\n") + 1
            line_content = content.split("\n")[line_num - 1].strip()[:100]
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": line_num,
                    "label": label,
                    "line_content": line_content,
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
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_PY, exclude_files=frozenset(WHITELIST_FILES)):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except ValueError:
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
    parser = argparse.ArgumentParser(description="threading.Lock 导入检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(
            f"\n[THREAD-LOCK-SCAN] {len(findings)} threading.Lock 架构违规（扫描 {files_scanned} 文件）:\n",
            file=sys.stderr,
        )
        for f in findings:
            print(f"  VIOLATION [{f['label']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['line_content']}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} Python files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
