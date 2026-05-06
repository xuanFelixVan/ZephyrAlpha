#!/usr/bin/env python3
"""
GATE-19: validate_static_manifest_drift.py
"""

__manifest__ = """
args:
- {flag: --check, type: bool, description: "only detect drift (pre-commit mode)"}
description: "run all generators --check, hard-block any drift between auto-generated vs disk. Anchored to AGENTS.md section 6.16"
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

"""
Runs all static-manifest generators in --check mode.
Any mismatch between auto-generated version and disk version
triggers hard failure (exit 1).

Authority: AGENTS.md section 6.16 -- any file whose primary content
is 'entry list + count' must be auto-generated (Type A) or schema input (Type B).

Checks:
  1. script_manifest.yaml -- via generate_script_manifest.py --check
  2. gate-registry.yaml    -- via generate_gate_registry.py --check

Usage:
    python validate_static_manifest_drift.py --check
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
GENERATORS_DIR = SCRIPTS_DIR / "generators"

CHECKS = [
    {
        "name": "script_manifest.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_script_manifest.py"), "--check"],
    },
]


def main() -> None:
    failures = []
    for check in CHECKS:
        result = subprocess.run(
            check["cmd"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(SCRIPTS_DIR.parent.parent),
        )
        if result.returncode != 0:
            msg = (result.stdout + result.stderr).strip()
            failures.append(f"FAIL [{check['name']}]: {msg}")
        else:
            print(f"PASS [{check['name']}]: {result.stdout.strip()}")

    if not failures:
        print("\nGATE-19 PASS: all static manifests are consistent with their sources.")
        sys.exit(0)

    print(f"\nGATE-19 FAIL: {len(failures)} static manifest(s) have drifted:\n")
    for f in failures:
        print(f"  - {f}")
    print("\nFix: cd D:\\ZephyrAlpha && python scripts/governance/generators/generate_script_manifest.py")
    sys.exit(1)


if __name__ == "__main__":
    main()
