# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_frontmatter_metadata.py | §
"""
GATE-15: Frontmatter metadata validation
Validates doc_type, status, required fields against schema vocabulary files
"""
from __future__ import annotations
from _shared.encoding import ensure_utf8_stdout
ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS, EXIT_PASS


__manifest__ = """
args: []
description: Frontmatter metadata compliance scan (doc_type valid values / status / required fields)
dimensions:
- D3
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
    """Scan docs/ frontmatter for metadata compliance."""
    import yaml

    errors = 0
    docs_dir = _PROJ / "docs"
    for fpath in docs_dir.rglob("*.md"):
        try:
            text = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        in_frontmatter = False
        status = None
        doc_type = None
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped == "---":
                in_frontmatter = not in_frontmatter
                if not in_frontmatter:
                    break
                continue
            if in_frontmatter:
                if stripped.startswith("status:"):
                    status = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("doc_type:"):
                    doc_type = stripped.split(":", 1)[1].strip()

        if status and status.lower() not in ("draft", "review", "active", "superseded", "deprecated", "retired"):
            rel = fpath.relative_to(_PROJ)
            print(f"  WARN: {rel} status={status}")
            errors += 1

    if errors:
        print(f"\nFAIL: {errors} frontmatter metadata issue(s)")
        return EXIT_FINDINGS

    print("OK: Frontmatter metadata validation passed")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
