# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_shell_true.py | §
# [MODULE] scripts.governance.d6_security.detect_shell_true
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
detect_shell_true.py — shell=True 调用检测



对标：PS-STD-003 ABS-43（禁止使用 shell=True 执行子进程）
     ADR-0018 Agent Sandbox（AGENTS 操作安全）
     process_sandbox.py（所有命令必须以 list[str] 形式传入）

检测内容：
- Python: subprocess.run/call/Popen 中使用 shell=True
- Python: os.system() 调用（等价于 shell=True）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: shell=True / os.system() 调用检测（ABS-43 — P0安全红线）
dimensions:
- D6
priority: P0
timeout_seconds: 30
warn_only: false
"""


import ast
import re
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

SHELL_TRUE_PATTERNS = [
    "subprocess\\.\\w+\\([^)]*shell\\s*=\\s*True",
    "os\\.system\\(",
    "os\\.popen\\(",
    "commands\\.getoutput\\(",
    "commands\\.getstatusoutput\\(",
]
WHITELIST_FILES = {"detect_shell_true.py"}


def _get_code_lines(filepath: Path) -> set:
    """_get_code_lines implementation."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return set()
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return set()
    code_lines = set()
    for node in ast.walk(tree):
        if hasattr(node, "lineno"):
            code_lines.add(node.lineno)
    return code_lines


def scan_file_ast(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    "扫描单个文件并返回发现列表."
    code_lines = _get_code_lines(filepath)
    "扫描并返回发现列表."
    if not code_lines:
        return findings
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for pattern in SHELL_TRUE_PATTERNS:
        for match in re.finditer(pattern, content):
            line_num = content[: match.start()].count("\n") + 1
            if line_num not in code_lines:
                continue
            matched = match.group(0)[:100]
            findings.append({"file": str(filepath.relative_to(REPO_ROOT)), "line": line_num, "matched": matched})
    return findings
    "扫描单个文件并返回发现列表."


def scan_repo(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描仓库并返回发现列表."""
    if scan_dir is None:
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
        findings = scan_file_ast(filepath)
        all_findings.extend(findings)
    return (all_findings, files_scanned, 0)
    "扫描仓库并返回发现列表."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="shell=True / os.system() 调用检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(
            f"\n[SHELL-SCAN] {len(findings)} shell=True/os.system 调用发现（扫描 {files_scanned} 文件）:\n",
            file=sys.stderr,
        )
        for f in findings:
            print(f"  {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['matched']}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} Python files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
