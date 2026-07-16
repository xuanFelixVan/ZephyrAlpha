# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_manifest_admission.py | §
# [MODULE] scripts.governance.d11_compliance.validate_manifest_admission
# [DOMAIN] D_GOV_SCRIPTS
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
# [TTL] permanent
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

__manifest__ = """
args: []
description: Module docstring — see module-level docstring for details.
dimensions:
- D11
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

MANIFEST_PATH = Path("scripts/governance/script_manifest.yaml")


def validate_manifest(path: str | None = None) -> tuple[bool, list[str]]:
    """Validate target against rules and report findings."""
    p = Path(path) if path else MANIFEST_PATH
    errors: list[str] = []
    if not p.exists():
        errors.append(f"Manifest 不存在: {p}")
        return False, errors
    try:
        with open(p, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
    except Exception as exc:
        return False, [f"YAML 解析失败: {exc}"]
    if not isinstance(manifest, dict):
        return False, ["Manifest 不是 dict 结构"]
    required_fields = ["total_scripts", "categories", "scripts"]
    for field in required_fields:
        if field not in manifest:
            errors.append(f"缺少字段: {field}")
    scripts_list = manifest.get("scripts", [])
    if not isinstance(scripts_list, list):
        errors.append("scripts 字段不是 list")
    return len(errors) == 0, errors


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ok, errors = validate_manifest()
    if ok:
        print("✅ Manifest admission validation PASSED")
        return EXIT_PASS
    print("❌ Manifest admission validation FAILED")
    for e in errors:
        print(f"  → {e}")
    return EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
