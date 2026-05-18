# [BLUEPRINT] MOD-INF-005 | scripts/governance/d2_links/audit_broken_links.py | §
"""Module docstring — see module-level docstring for details."""
from __future__ import annotations
from _shared.constants import EXIT_FINDINGS, EXIT_PASS


import re
import sys
from pathlib import Path

MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def audit_links(md_path: str) -> tuple[bool, list[str]]:
    """Audit target and report findings."""
    p = Path(md_path)
    if not p.exists():
        return False, [f"文件不存在: {md_path}"]
    content = p.read_text(encoding="utf-8")
    broken: list[str] = []
    for match in MD_LINK.finditer(content):
        target = match.group(2)
        if target.startswith("http"):
            continue
        target_path = (p.parent / target).resolve()
        if not target_path.exists():
            broken.append(f"断链: {target} ← {p.name}")
    return len(broken) == 0, broken


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if len(sys.argv) < 2:
        print("用法: python audit_broken_links.py <MD文件路径>")
        return EXIT_FINDINGS
    ok, broken = audit_links(sys.argv[1])
    if ok:
        print("✅ 无断链")
        return EXIT_PASS
    print("❌ 发现断链:")
    for b in broken:
        print(f"  → {b}")
    return EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
