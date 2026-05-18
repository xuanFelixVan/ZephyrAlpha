# [BLUEPRINT] MOD-INF-005 | scripts/governance/d2_links/validate_depends_on_format.py | §
"""Module docstring — see module-level docstring for details."""
from __future__ import annotations
from _shared.constants import EXIT_FINDINGS, EXIT_PASS


import sys
from pathlib import Path


def validate_depends_on(blueprint_path: str) -> tuple[bool, list[str]]:
    """Validate target against rules and report findings."""
    p = Path(blueprint_path)
    if not p.exists():
        return False, [f"蓝图不存在: {p}"]
    content = p.read_text(encoding="utf-8")
    errors: list[str] = []
    required_refs = [
        "MOD-INF-006", "MOD-KB-001", "PS-STD-001", "SCRIPT-QUALITY-001",
        "module-registry.yaml", "AGENTS.md", "script_manifest.yaml",
    ]
    for ref in required_refs:
        if ref not in content:
            errors.append(f"未找到依赖引用: {ref}")
    return len(errors) == 0, errors


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if len(sys.argv) < 2:
        print("用法: python validate_depends_on_format.py <蓝图路径>")
        return EXIT_FINDINGS
    ok, errors = validate_depends_on(sys.argv[1])
    if ok:
        print("✅ depends_on format validation PASSED")
        return EXIT_PASS
    print("❌ depends_on format validation FAILED")
    for e in errors:
        print(f"  → {e}")
    return EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
