"""
validate_index_reality.py - Index-to-reality reconciliation (AGENTS.md section 6.11)
Aligns with ITIL SACM / CMDB reconciliation: claimed file counts in index.md
must match actual files on disk.
"""
from __future__ import annotations

__manifest__ = """
args:
- --warn-only
description: Index-reality sync check (AGENTS.md section 6.11 - index.md claimed script count vs disk actual .py file count)
dimensions:
- D1
priority: P0
timeout_seconds: 15
warn_only: false
"""

import re
import sys
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[2]
if str(_PROJ) not in sys.path:
    sys.path.insert(0, str(_PROJ))


def main() -> int:
    """Validate index.md claims match disk reality."""
    index_path = _PROJ / "scripts" / "governance" / "index.md"
    errors = 0

    if not index_path.exists():
        print("OK: No index.md to validate (baseline pass)")
        return 0

    index_text = index_path.read_text(encoding="utf-8")

    matches = re.findall(r"(\d+)\s*(?:scripts?|\.py files?)", index_text, re.IGNORECASE)
    if not matches:
        print("OK: No numeric script claims found in index.md (baseline pass)")
        return 0

    gov_dir = _PROJ / "scripts" / "governance"
    actual_py = len(list(gov_dir.rglob("*.py")))

    for match in matches:
        claimed = int(match)
        if claimed != actual_py:
            print(f"WARN: index.md claims {claimed} scripts, but disk has {actual_py}")
            errors += 1

    if errors:
        print(f"\nFAIL: {errors} index-reality mismatch(es)")
        return 1

    print(f"OK: Index-reality sync passed ({actual_py} scripts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
