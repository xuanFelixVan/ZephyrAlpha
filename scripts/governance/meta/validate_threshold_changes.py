# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_threshold_changes.py | §
# [MODULE] scripts.governance.meta.validate_threshold_changes
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
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
"""validate_threshold_changes.py — 阈值变更审计日志

对标 B16（关键阈值变更审计）+ ITIL 4 Configuration Change Audit。
每次阈值文件被修改时，记录 old→new 的 diff 到 append-only 审计日志。
由 pre_commit 钩子自动触发。

Usage:
    python scripts/governance/meta/validate_threshold_changes.py
    python scripts/governance/meta/validate_threshold_changes.py --warn-only
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT as _REPO_ROOT  # noqa: E402  治本(2026-06-30): SSoT

__manifest__ = """
args: []
description: >
  阈值变更审计——每次阈值文件被修改时，记录 old→new 的 diff 到 append-only 审计日志，
  由 pre_commit 钩子自动触发。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 15
warn_only: false
"""


import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_THRESHOLDS_PATH = _REPO_ROOT / "scripts" / "governance" / "_shared" / "thresholds.yaml"
_AUDIT_LOG_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "threshold_changes_audit.jsonl"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _get_git_diff() -> str:
    """_get_git_diff implementation."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--", str(_THRESHOLDS_PATH)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 or not result.stdout.strip():
        result = subprocess.run(
            ["git", "diff", "--", str(_THRESHOLDS_PATH)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(_REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
    return result.stdout.strip()


def _hash_content(content: str) -> str:
    """_hash_content implementation."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    warn_only = "--warn-only" in sys.argv

    diff = _get_git_diff()
    if not diff:
        if warn_only:
            sys.exit(EXIT_PASS)
        print("[THRESHOLD-AUDIT] 阈值文件无变更", file=sys.stderr)
        sys.exit(EXIT_PASS)

    timestamp = datetime.now(UTC).isoformat()
    diff_hash = _hash_content(diff)
    try:
        current_content = _THRESHOLDS_PATH.read_text(encoding="utf-8")
        current_hash = _hash_content(current_content)
    except OSError:
        current_hash = "UNAVAILABLE"

    audit_entry = {
        "event": "threshold_change",
        "timestamp": timestamp,
        "file": str(_THRESHOLDS_PATH.relative_to(_REPO_ROOT)),
        "diff_hash": diff_hash,
        "content_hash_after": current_hash,
        "diff_preview": diff[:2000],
    }

    _AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")

    print("\n[THRESHOLD-AUDIT] ⚠ 关键阈值已变更", file=sys.stderr)
    print(f"  时间: {timestamp}", file=sys.stderr)
    print(f"  审计日志: {_AUDIT_LOG_PATH.relative_to(_REPO_ROOT)}", file=sys.stderr)
    print(f"  变更摘要:\n{diff[:500]}", file=sys.stderr)

    if warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
