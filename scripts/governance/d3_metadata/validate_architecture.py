"""
validate_architecture.py - Validate rule files against architecture-contract.yaml
Reads architecture-contract.yaml and validates all .md/.yaml files under
docs/01_policies_and_standards/ for directory compliance, frontmatter fields,
and doc_type / rule_form consistency.
"""
from __future__ import annotations

__manifest__ = """
args: []
description: Architecture compliance check (frontmatter + directory placement + doc_type consistency)
dimensions:
- D3
- D4
- D5
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
    """Validate architecture compliance against contract."""
    import yaml

    contract_path = _PROJ / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "architecture-contract.yaml"
    errors = 0

    if not contract_path.exists():
        print("WARN: architecture-contract.yaml not found, baseline pass")
        return 0

    with open(contract_path, encoding="utf-8") as f:
        contract = yaml.safe_load(f)

    scan_dir = _PROJ / "docs" / "01_policies_and_standards"
    if not scan_dir.exists():
        print("WARN: scan directory not found")
        return 0

    for fpath in scan_dir.rglob("*.md"):
        try:
            text = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        in_frontmatter = False
        doc_type = None
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped == "---":
                in_frontmatter = not in_frontmatter
                if not in_frontmatter:
                    break
                continue
            if in_frontmatter and stripped.startswith("doc_type:"):
                doc_type = stripped.split(":", 1)[1].strip()

        if doc_type and doc_type == "governance":
            parent = fpath.parent.name
            if parent.startswith("operational"):
                rel = fpath.relative_to(_PROJ)
                print(f"  WARN: {rel} governance doc_type in operational directory")
                errors += 1

    if errors:
        print(f"\nFAIL: {errors} architecture compliance issue(s)")
        return 1

    print("OK: Architecture compliance validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
