# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_tag_uniqueness.py | §
# [MODULE] scripts.governance.d5_architecture.validators.blueprint.validate_blueprint_tag_uniqueness
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.blueprint.__init__
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
"""GATE-TAG-UNIQUE - Blueprint tag uniqueness validation gate."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()

BLUEPRINT_REGISTRY = REPO_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"

TAG_ALLOWLIST: frozenset[str] = frozenset(
    {
        "infrastructure",
        "infra",
        "observability",
        "vibe-coding",
        "",
    }
)

__manifest__ = {
    "args": [],
    "description": "GATE-TAG-UNIQUE: same tag must not appear in >=2 approved blueprints (single source of truth enforcement)",
    "dimensions": ["D5"],
    "priority": "P1",
    "timeout_seconds": 15,
    "warn_only": True,
}


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    registry = load_yaml(BLUEPRINT_REGISTRY)
    blueprints = registry.get("blueprints", registry) if isinstance(registry, dict) else []

    if not isinstance(blueprints, list):
        print(f"[ERROR] Blueprint registry parse failed, expected list, got: {type(blueprints).__name__}")
        sys.exit(EXIT_FINDINGS)

    approved = [b for b in blueprints if isinstance(b, dict) and b.get("blueprint_status") == "approved"]
    if not approved:
        print("[PASS] No approved blueprints, skipping tag uniqueness check.")
        sys.exit(EXIT_PASS)

    tags_to_modules: dict[str, list[str]] = defaultdict(list)
    for bp in approved:
        tags = bp.get("tags", [])
        if not isinstance(tags, list):
            continue
        module_id = bp.get("module_id", "UNKNOWN")
        for tag in tags:
            if not isinstance(tag, str):
                continue
            tag = tag.strip()
            if not tag:
                continue
            tags_to_modules[tag].append(module_id)

    violations: list[tuple[str, list[str]]] = []
    for tag, mods in sorted(tags_to_modules.items()):
        if tag in TAG_ALLOWLIST:
            continue
        unique_mods = list(dict.fromkeys(mods))
        if len(unique_mods) >= 2:
            violations.append((tag, unique_mods))

    if not violations:
        print("[PASS] All approved blueprint tags are unique.")
        sys.exit(EXIT_PASS)

    print(f"[WARN] Found {len(violations)} tag(s) in >=2 approved blueprints:\n")
    for tag, mods in violations:
        print(f"  {tag} -> {', '.join(mods)}")
    print(f"\n  Total: {len(violations)} violation(s).")
    print("  Each responsibility tag should only appear in ONE approved blueprint.")
    print("  Exceptions: functional-domain / layer / category tags (see TAG_ALLOWLIST).")
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
