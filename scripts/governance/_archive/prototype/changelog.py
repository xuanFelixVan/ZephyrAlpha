# [BLUEPRINT] MOD-INF-005 | scripts/governance/changelog.py | §
# [MODULE] scripts.governance.changelog
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
#!/usr/bin/env python
"""
changelog.py — 治理域变更日志生成/追加工具.

DOM-GOV-001 §7 运维脚本.
用法: python scripts/governance/changelog.py [--since YYYY-MM-DD] [--format yaml|markdown]
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import sys
from datetime import UTC, datetime
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

PROJECT_ROOT = REPO_ROOT
CHANGELOG_FILE = PROJECT_ROOT / "docs" / "03_modules" / "_domain-governance" / "domain_progress.json"


def load_progress() -> dict:
    """load_progress implementation."""
    if not CHANGELOG_FILE.exists():
        return {}
    import json

    return json.loads(CHANGELOG_FILE.read_text(encoding="utf-8"))


def generate_changelog(data: dict, since: str | None = None) -> list[str]:
    """Generate output from input data."""
    entries: list[str] = []
    entries.append("# DOM-GOV-001 Change Log")
    entries.append(f"Generated: {datetime.now(UTC).isoformat()}")
    entries.append("")

    modules = data.get("modules", {})
    for name, info in sorted(modules.items()):
        progress = info.get("progress", 0)
        phase = info.get("phase", "UNKNOWN")
        entries.append(f"- **{name}** ({info.get('module_id', 'N/A')}): {progress}% [{phase}]")

    gcts = data.get("gct_contracts", {})
    entries.append("\n## GCT Contracts")
    for gct_id, gct_info in sorted(gcts.items()):
        status = gct_info.get("status", "UNKNOWN")
        entries.append(f"- **{gct_id}** [{gct_info.get('from', '?')} → {gct_info.get('to', '?')}]: {status}")

    return entries


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    data = load_progress()
    if not data:
        print("ERROR: domain_progress.json not found")
        return EXIT_FINDINGS

    since = None
    fmt = "markdown"
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--since" and i + 1 < len(sys.argv) - 1:
            since = sys.argv[i + 2]
        elif arg == "--format" and i + 1 < len(sys.argv) - 1:
            fmt = sys.argv[i + 2]

    entries = generate_changelog(data, since)
    for entry in entries:
        print(entry)
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
