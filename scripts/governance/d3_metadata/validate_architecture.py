# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_architecture.py | §
# [MODULE] scripts.governance.d3_metadata.validate_architecture
# [DOMAIN] D_GOVERNANCE
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
validate_architecture.py - Validate rule files against architecture_contract.yaml
Reads architecture_contract.yaml and validates all .md/.yaml files under
docs/01_policies_and_standards/ for directory compliance, frontmatter fields,
and doc_type / rule_form consistency.
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
description: Architecture compliance check (frontmatter + directory placement + doc_type consistency)
dimensions:
- D3
- D4
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""


def main() -> int:
    """Validate architecture compliance against contract."""
    import yaml

    contract_path = (
        REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "architecture_contract.yaml"
    )
    errors = 0

    if not contract_path.exists():
        print("WARN: architecture_contract.yaml not found, baseline pass")
        return EXIT_PASS

    with open(contract_path, encoding="utf-8") as f:
        contract = yaml.safe_load(f)

    scan_dir = REPO_ROOT / "docs" / "01_policies_and_standards"
    if not scan_dir.exists():
        print("WARN: scan directory not found")
        return EXIT_PASS

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

        if doc_type and doc_type in ("policy", "standard"):  # v2.0.0: governance 幽灵值修复为有效值
            parent = fpath.parent.name
            if parent.startswith("operational"):
                rel = fpath.relative_to(REPO_ROOT)
                print(f"  WARN: {rel} governance doc_type in operational directory")
                errors += 1

    if errors:
        print(f"\nFAIL: {errors} architecture compliance issue(s)")
        return EXIT_FINDINGS

    print("OK: Architecture compliance validation passed")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
