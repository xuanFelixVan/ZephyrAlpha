# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/validate_read_before_write.py | §
# [MODULE] scripts.governance.d1_structure.validate_read_before_write
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
"""validate_read_before_write.py — 先读后写校验（IRN-008）

对标：GOV-MOD-002 IRN-008（先读后写）

检测内容：
- --session-log: 检查 Session Log 中每个 Write 操作前是否有对应的 Read 记录
- --file: 检查指定文件在 session log 中是否先被 Read 再被 Write

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --session-log, type: str, description: "检查指定 Session Log 的先读后写合规性"}
- {flag: --file, type: str, description: "检查指定文件在 session log 中是否先 Read 后 Write"}
description: >
  先读后写校验（IRN-008）——检查 Session Log 中每个 Write 前是否有对应 Read。
  对标 GOV-MOD-002 ai-behavior-iron-policy.md IRN-008。
dimensions:
- D1
priority: P1
timeout_seconds: 15
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

READ_PATTERNS = [
    re.compile(r"(?:Read|read|读取|查看).*?['\"]?([^'\"\s]+\.(?:py|md|yaml|yml|json|toml))['\"]?", re.IGNORECASE),
    re.compile(r"(?:SearchReplace|Edit).*?file_path.*?['\"]([^'\"]+)['\"]", re.IGNORECASE),
]

WRITE_PATTERNS = [
    re.compile(
        r"(?:Write|write|创建|写入|保存).*?['\"]?([^'\"\s]+\.(?:py|md|yaml|yml|json|toml))['\"]?", re.IGNORECASE
    ),
    re.compile(r"(?:SearchReplace|Edit).*?file_path.*?['\"]([^'\"]+)['\"]", re.IGNORECASE),
]


def extract_file_operations(content: str) -> list[tuple[str, str, int]]:
    """extract_file_operations implementation."""
    ops = []
    for i, line in enumerate(content.split("\n"), 1):
        for pat in READ_PATTERNS:
            m = pat.search(line)
            if m:
                ops.append(("READ", m.group(1), i))
                break
        else:
            for pat in WRITE_PATTERNS:
                m = pat.search(line)
                if m:
                    ops.append(("WRITE", m.group(1), i))
                    break
    return ops


def check_session_log(session_log_path: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    log_path = Path(session_log_path)
    if not log_path.exists():
        print(f"IRN-008 WARNING: session log '{session_log_path}' not found, skipping")
        return findings
    content = log_path.read_text(encoding="utf-8", errors="replace")
    ops = extract_file_operations(content)
    read_files: dict[str, int] = {}
    for op_type, filepath, line_num in ops:
        normalized = filepath.replace("\\", "/")
        if op_type == "READ":
            read_files.setdefault(normalized, line_num)
        elif op_type == "WRITE":
            if normalized not in read_files:
                findings.append(f"IRN-008 FAIL: file '{filepath}' written at line {line_num} without prior Read record")
            elif read_files[normalized] > line_num:
                findings.append(
                    f"IRN-008 FAIL: file '{filepath}' written at line {line_num} before Read at line {read_files[normalized]}"
                )
    return findings


def check_file_read_before_write(session_log_path: str, target_file: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    log_path = Path(session_log_path)
    if not log_path.exists():
        return findings
    content = log_path.read_text(encoding="utf-8", errors="replace")
    ops = extract_file_operations(content)
    normalized_target = target_file.replace("\\", "/")
    first_read = None
    first_write = None
    for op_type, filepath, line_num in ops:
        if filepath.replace("\\", "/") == normalized_target:
            if op_type == "READ" and first_read is None:
                first_read = line_num
            elif op_type == "WRITE" and first_write is None:
                first_write = line_num
    if first_write is not None and first_read is None:
        findings.append(f"IRN-008 FAIL: file '{target_file}' written at line {first_write} without any Read record")
    elif first_write is not None and first_read is not None and first_read > first_write:
        findings.append(
            f"IRN-008 FAIL: file '{target_file}' written at line {first_write} before Read at line {first_read}"
        )
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Read-before-write validation (IRN-008)")
    parser.add_argument("--session-log", type=str, help="Check session log for read-before-write compliance")
    parser.add_argument("--file", type=str, help="Check specific file in session log")
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.session_log:
        if args.file:
            all_findings.extend(check_file_read_before_write(args.session_log, args.file))
        else:
            all_findings.extend(check_session_log(args.session_log))

    if not args.session_log:
        print("Usage: validate_read_before_write.py --session-log <path> [--file <target>]")
        sys.exit(EXIT_ERROR)

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
