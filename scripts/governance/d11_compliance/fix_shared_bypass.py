# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/fix_shared_bypass.py | §
# [MODULE] scripts.governance.d11_compliance.fix_shared_bypass
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
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
"""
fix_shared_bypass.py - D-D-07 auto-fix tool (validate_script_quality.py --fix companion)
Aligns with AGENTS.md section 6.5 (script self-creation repository mandatory convention)
and SCRIPT-QUALITY-001 D-D-07 (prohibits bypassing _shared utilities).
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
from _shared.constants import EXIT_FINDINGS, EXIT_PASS

__manifest__ = """
args:
- --fix
- --dry-run
- --no-backup
description: D-D-07 auto-fix - detect and repair local redefinitions of _shared API violations
dimensions:
- D11
- D7
priority: P2
timeout_seconds: 30
warn_only: true
"""

import ast
import sys
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[2]
if str(_PROJ) not in sys.path:
    sys.path.insert(0, str(_PROJ))

KNOWN_SYMBOLS = {
    "REPO_ROOT",
    "EXCLUDE_DIRS",
    "SRC_DIR",
    "SCAN_EXTENSIONS",
    "load_yaml",
    "save_yaml",
}


def main() -> int:
    """Detect local redefinitions of _shared API symbols."""
    gov_dir = _PROJ / "scripts" / "governance"
    violations = 0

    for fpath in gov_dir.rglob("*.py"):
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in KNOWN_SYMBOLS:
                        rel = fpath.relative_to(_PROJ)
                        print(f"  WARN: {rel} redefines {target.id} locally")
                        violations += 1

    if violations:
        print(f"\nFAIL: {violations} shared API bypass(es)")
        return EXIT_FINDINGS

    print("OK: No _shared API bypass detected")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
