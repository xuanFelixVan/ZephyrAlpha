# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_blueprint_provenance.py | §
# [MODULE] scripts.governance.d3_metadata.validate_blueprint_provenance
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
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
Blueprint Provenance Gate - V-12: validate provenance triples in blueprint frontmatter
Task: T-V2-001 (Wave 0 final review R73)
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

__manifest__ = """
args: []
description: Blueprint provenance triple validation (origin_drafts + audit_chain + arbitration)
dimensions:
- D3
- D4
priority: P0
timeout_seconds: 30
warn_only: false
"""


def main() -> int:
    """Validate provenance fields in blueprint frontmatter files."""

    errors = 0
    scan_dirs = [
        REPO_ROOT / "docs" / "04_construction_plans",
        REPO_ROOT / "docs" / "01_policies_and_standards",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for fpath in scan_dir.rglob("*.md"):
            try:
                text = fpath.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            in_frontmatter = False
            provenance = {}
            for line in text.split("\n"):
                stripped = line.strip()
                if stripped == "---":
                    in_frontmatter = not in_frontmatter
                    if not in_frontmatter:
                        break
                    continue
                if in_frontmatter and ":" in stripped:
                    key, _, val = stripped.partition(":")
                    provenance[key.strip()] = val.strip()

            if not provenance:
                continue

            origin = provenance.get("origin_drafts", "")
            arbitration = provenance.get("arbitration", "")
            if not origin:
                continue

            if not arbitration:
                rel = fpath.relative_to(REPO_ROOT)
                print(f"  WARN: {rel} missing arbitration field in provenance")
                errors += 1

    if errors:
        print(f"\nFAIL: {errors} blueprint provenance issue(s)")
        return EXIT_FINDINGS

    print("OK: Blueprint provenance validation passed")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
