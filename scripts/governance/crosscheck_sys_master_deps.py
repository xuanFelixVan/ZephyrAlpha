# [BLUEPRINT] MOD-INF-005 | scripts/governance/crosscheck_sys_master_deps.py | §
# [MODULE] scripts.governance.crosscheck_sys_master_deps
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
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
#!/usr/bin/env python
"""
crosscheck_sys_master_deps.py — 验证 SYS-MASTER-001 + MOD-MASTER_BLUEPRINT 与 DOM-GOV-001 一致.

DOM-GOV-001 §frontmatter depends_on — CT 交叉检查脚本.
用法: python scripts/governance/crosscheck_sys_master_deps.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 蓝图路径真源：blueprint_registry.yaml（SSoT），经 sys_master_compliance.load_blueprint_path 查询
# 不硬编码，消除连字符/下划线漂移
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from zephyr.governance.rule_enforcement.sys_master_compliance import (  # noqa: E402
    MOD_MASTER_PATH,
    SYS_MASTER_PATH,
    load_blueprint_path,
)

DOM_GOV = load_blueprint_path("MOD-GOVERNANCE")

EXPECTED_MODULES = [
    "MOD-INF-018",
    "MOD-INF-019",
    "MOD-INF-020",
    "MOD-INF-021",
    "MOD-INF-022",
    "MOD-INF-023",
    "MOD-INF-024",
    "MOD-INF-025",
]

EXPECTED_CTS = [
    "G-CT-001",
    "G-CT-002",
    "G-CT-003",
    "G-CT-004",
    "G-CT-005",
    "G-CT-006",
    "G-CT-007",
    "G-CT-008",
]


def check_exists(path: Path | None, label: str) -> dict:
    """Check compliance and report findings."""
    if path is None:
        return {"file": "<not in blueprint_registry.yaml>", "label": label, "status": "MISSING"}
    status = "OK" if path.exists() else "MISSING"
    return {"file": str(path.relative_to(PROJECT_ROOT)), "label": label, "status": status}


def check_references(content: str, items: list[str], label: str) -> dict:
    """Check compliance and report findings."""
    found = []
    not_found = []
    for item in items:
        if item in content:
            found.append(item)
        else:
            not_found.append(item)
    return {"label": label, "found": found, "not_found": not_found}


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    results = []

    results.append(check_exists(SYS_MASTER_PATH, "SYS-MASTER-001 blueprint"))
    results.append(check_exists(MOD_MASTER_PATH, "MOD-MASTER_BLUEPRINT blueprint"))
    results.append(check_exists(DOM_GOV, "DOM-GOV-001 blueprint"))

    if DOM_GOV.exists():
        dom_content = DOM_GOV.read_text(encoding="utf-8")
        results.append(check_references(dom_content, EXPECTED_MODULES, "MOD-INF references in DOM-GOV-001"))
        results.append(check_references(dom_content, EXPECTED_CTS, "G-CT references in DOM-GOV-001"))

    all_ok = all(r.get("status", "OK") == "OK" for r in results)
    for r in results:
        print(r)

    if all_ok:
        print("\nALL CHECKS PASSED: SYS-MASTER-001 + MOD-MASTER_BLUEPRINT 与 DOM-GOV-001 一致")
    else:
        print("\nSOME CHECKS FAILED", file=sys.stderr)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
