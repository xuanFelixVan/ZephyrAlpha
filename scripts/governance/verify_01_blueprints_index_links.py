# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
"""
校验 01_BLUEPRINTS/INDEX.md 中「完整文件列表」的每一条 ./xxx.md 内链是否可解析且文件存在。

仓库根执行: python scripts/governance/verify_01_blueprints_index_links.py
退出码: 缺失则 1；否则 0。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INDEX = REPO / "docs" / "05_IMPLEMENTATION" / "06_CONSTRUCTION_DOCS" / "01_BLUEPRINTS" / "INDEX.md"
LIST_ITEM_RE = re.compile(r"^\s*-\s*\[([^\]]+)\]\(\./([^)]+)\)\s*$")


def main() -> int:
    if not INDEX.is_file():
        print(f"ERROR: INDEX not found: {INDEX}", file=sys.stderr)
        return 2
    text = INDEX.read_text(encoding="utf-8", errors="replace")
    in_list = False
    missing: list[tuple[str, str]] = []
    ok = 0
    for line in text.splitlines():
        if "## 完整文件列表" in line:
            in_list = True
            continue
        if in_list and line.startswith("## ") and "完整文件列表" not in line:
            break
        if not in_list:
            continue
        m = LIST_ITEM_RE.match(line)
        if not m:
            continue
        name = m.group(2).strip()
        if not name.lower().endswith(".md"):
            continue
        target = INDEX.parent / name
        if not target.is_file():
            missing.append((m.group(1), name))
        else:
            ok += 1
    print(f"01_BLUEPRINTS INDEX: valid links {ok}, missing {len(missing)}")
    for stem, fn in missing[:50]:
        print(f"  MISSING: [{stem}](./{fn})")
    if len(missing) > 50:
        print(f"  ... and {len(missing) - 50} more")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
