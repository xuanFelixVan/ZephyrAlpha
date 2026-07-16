# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/check_protected_paths.py | §
# [MODULE] scripts.governance.d6_security.check_protected_paths
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
"""check_protected_paths.py — 受保护路径写入检查（IRN-010）

对标：GOV-MOD-002 IRN-010（受保护路径不可写）

检测内容：
- 检查目标路径是否在受保护清单中
- 受保护路径：.git/、AGENTS.md、meta/*.md、architecture_model/

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --path, type: str, description: "检查指定路径是否受保护"}
- {flag: --session-log, type: str, description: "检查 Session Log 中的写入记录是否违反受保护路径"}
description: >
  受保护路径写入检查（IRN-010）——检查目标路径是否在受保护清单中。
  对标 GOV-MOD-002 ai-behavior-iron-policy.md IRN-010。
dimensions:
- D6
priority: P1
timeout_seconds: 15
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

PROTECTED_PATTERNS = [
    (".git/", "只读——禁止任何操作"),
    ("AGENTS.md", "重大修改须 Owner 审批"),
    ("docs/01_policies_and_standards/rules/", "重大修改须 Owner 审批（rules/ 下所有 .yaml）"),
    ("architecture_model/", "重大修改须 Owner 审批"),
]


def check_path(target_path: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    normalized = target_path.replace("\\", "/")
    if not normalized.startswith("/"):
        try:
            normalized = str(Path(target_path).resolve().relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            pass
    for pattern, reason in PROTECTED_PATTERNS:
        if pattern in normalized or normalized.startswith(pattern):
            findings.append(f"IRN-010 FAIL: path '{target_path}' matches protected pattern '{pattern}' — {reason}")
    return findings


def check_session_log(session_log_path: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    log_path = Path(session_log_path)
    if not log_path.exists():
        print(f"IRN-010 WARNING: session log '{session_log_path}' not found, skipping")
        return findings
    content = log_path.read_text(encoding="utf-8", errors="replace")
    import re

    write_entries = re.findall(
        r"(?:Write|write|创建|修改|编辑).*?['\"]?([^'\"\s]+\.(?:py|md|yaml|yml|json))['\"]?", content
    )
    for entry_path in write_entries:
        findings.extend(check_path(entry_path))
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Protected paths write check (IRN-010)")
    parser.add_argument("--path", type=str, help="Check if a specific path is protected")
    parser.add_argument("--session-log", type=str, help="Check session log for protected path violations")
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.path:
        all_findings.extend(check_path(args.path))

    if args.session_log:
        all_findings.extend(check_session_log(args.session_log))

    if not any([args.path, args.session_log]):
        print("Usage: check_protected_paths.py --path <target_path> or --session-log <log_path>")
        sys.exit(EXIT_ERROR)

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
