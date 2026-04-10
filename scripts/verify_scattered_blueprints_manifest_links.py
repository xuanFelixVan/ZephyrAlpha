# -*- coding: utf-8 -*-
"""校验 ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.md 中列表内链是否均可解析。仓库根执行。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = (
    REPO / "docs" / "09_AUDIT" / "STATE" / "ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.md"
)
ITEM_RE = re.compile(r"^\s*-\s*\[([^\]]+)\]\(([^)]+)\)\s*$")


def main() -> int:
    if not MANIFEST.is_file():
        print(f"ERROR: manifest not found: {MANIFEST}", file=sys.stderr)
        return 2
    missing: list[str] = []
    ok = 0
    for line in MANIFEST.read_text(encoding="utf-8", errors="replace").splitlines():
        m = ITEM_RE.match(line)
        if not m:
            continue
        href = m.group(2).strip()
        target = (MANIFEST.parent / href).resolve()
        try:
            target.relative_to(REPO)
        except ValueError:
            missing.append(f"escape? {href}")
            continue
        if not target.is_file():
            missing.append(href)
        else:
            ok += 1
    print(f"Scattered manifest: valid {ok}, missing {len(missing)}")
    for x in missing[:30]:
        print(f"  MISSING: {x}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
