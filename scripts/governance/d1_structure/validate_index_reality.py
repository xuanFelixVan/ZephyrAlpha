# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/validate_index_reality.py | §
# [MODULE] scripts.governance.d1_structure.validate_index_reality
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

__manifest__ = """
args: []
description: Module docstring — see module-level docstring for details.
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import sys
from pathlib import Path

import yaml
from _shared.constants import EXIT_FINDINGS, EXIT_PASS


def validate_index(path: str | None = None) -> tuple[bool, list[str]]:
    """Validate target against rules and report findings."""
    p = Path(path or "scripts/governance/script_manifest.yaml")
    errors: list[str] = []
    if not p.exists():
        return False, [f"Manifest 不存在: {p}"]
    with open(p, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    scripts = manifest.get("scripts", [])
    for entry in scripts:
        script_path = entry.get("path", "")
        if not Path(script_path).exists():
            errors.append(f"Manifest entry 路径不存在: {script_path}")
    return len(errors) == 0, errors


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ok, errors = validate_index()
    if ok:
        print("✅ Index reality check PASSED")
        return EXIT_PASS
    print("❌ Index reality check FAILED")
    for e in errors:
        print(f"  → {e}")
    return EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
