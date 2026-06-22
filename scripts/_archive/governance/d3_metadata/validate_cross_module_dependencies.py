# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_cross_module_dependencies.py | §
"""validate_cross_module_dependencies.py

校验 cross-module-dependency-registry.yaml 中每条依赖的 source/target
均为 docs/03_modules/module-registry.yaml 中已登记的 module_id。
"""

from __future__ import annotations

__manifest__ = {
    "args": [],
    "description": "跨模块依赖登记表与 module-registry 的 module_id 对账",
    "dimensions": ["D3", "D5"],
    "priority": "P1",
    "timeout_seconds": 30,
    "warn_only": False,
}

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()

CROSS_PATH = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "cross-module-dependency-registry.yaml"
)
MODULE_REG_PATH = REPO_ROOT / "docs" / "03_modules" / "module-registry.yaml"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    cross = load_yaml(CROSS_PATH)
    mod_reg = load_yaml(MODULE_REG_PATH)
    known = {m["module_id"] for m in mod_reg.get("modules", []) if isinstance(m, dict) and "module_id" in m}

    missing: list[tuple[str, str, str]] = []
    for dep in cross.get("dependencies", []):
        if not isinstance(dep, dict):
            continue
        dep_id = dep.get("dep_id", "?")
        for field in ("source", "target"):
            mid = dep.get(field)
            if not mid:
                continue
            if mid not in known:
                missing.append((str(dep_id), field, str(mid)))

    if missing:
        print("FAIL: 以下 module_id 未在 module-registry.yaml 登记：", file=sys.stderr)
        for dep_id, field, mid in missing:
            print(f"  {dep_id} {field}={mid}", file=sys.stderr)
        return EXIT_FINDINGS

    print(f"OK: {len(cross.get('dependencies', []))} 条跨模块依赖的 source/target 均已登记")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
