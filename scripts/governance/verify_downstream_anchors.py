"""下游锚点验证脚本 — 扫描 8 个 L01 模块 blueprint.md 确认 DOM-GOV-001 anchor."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC_DIR))

EXPECTED_MODULES: dict[str, str] = {
    "MOD-INF-018": "agent_rbac",
    "MOD-INF-019": "agent_spec",
    "MOD-INF-020": "audit_trail",
    "MOD-INF-021": "rollback_system",
    "MOD-INF-022": "escalation_protocol",
    "MOD-INF-023": "drift_detector",
    "MOD-INF-024": "budget_enforcer",
    "MOD-INF-025": "a2a_protocol",
}

REQUIRED_ANCHOR = "DOM-GOV-001"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    results: dict[str, bool] = {}
    base = Path("docs/03_modules/l01_infrastructure")

    for mod_id, mod_dir in EXPECTED_MODULES.items():
        bp = base / mod_dir / "blueprint.md"
        if bp.exists():
            content = bp.read_text(encoding="utf-8")
            results[mod_id] = REQUIRED_ANCHOR in content
        else:
            results[mod_id] = False

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Anchor Check: {passed}/{total} modules have {REQUIRED_ANCHOR} anchor")
    for mod_id, has_anchor in results.items():
        icon = "OK" if has_anchor else "MISSING"
        print(f"  [{icon}] {mod_id}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
