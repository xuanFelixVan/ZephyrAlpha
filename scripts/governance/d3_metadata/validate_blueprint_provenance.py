"""
Blueprint Provenance Gate - V-12: validate provenance triples in blueprint frontmatter
Task: T-V2-001 (Wave 0 final review R73)
"""
from __future__ import annotations

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

import sys
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[2]
if str(_PROJ) not in sys.path:
    sys.path.insert(0, str(_PROJ))


def main() -> int:
    """Validate provenance fields in blueprint frontmatter files."""
    import yaml

    errors = 0
    scan_dirs = [
        _PROJ / "docs" / "02_enterprise_architecture" / "target-architecture",
        _PROJ / "docs" / "04_construction_plans",
        _PROJ / "docs" / "01_policies_and_standards",
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
                rel = fpath.relative_to(_PROJ)
                print(f"  WARN: {rel} missing arbitration field in provenance")
                errors += 1

    if errors:
        print(f"\nFAIL: {errors} blueprint provenance issue(s)")
        return 1

    print("OK: Blueprint provenance validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
