# -*- coding: utf-8 -*-
"""
将 docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state 下文件迁入
docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state（ADR-OC-002）。
同名冲突：迁入文件改名为 MIGRATED_FROM_07_<basename>。

用法（仓库根）: python scripts/consolidate_audit_state_07_to_04.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state"
DST = REPO / "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state"


def main() -> None:
    if not SRC.is_dir():
        print("Source missing:", SRC)
        return
    DST.mkdir(parents=True, exist_ok=True)
    moved = 0
    renamed = 0
    for p in sorted(SRC.iterdir()):
        if not p.is_file():
            continue
        name = p.name
        if name.upper() in ("README.MD", "INDEX.MD"):
            continue
        dest = DST / name
        if dest.exists():
            dest = DST / f"MIGRATED_FROM_07_{name}"
            renamed += 1
        shutil.move(str(p), str(dest))
        moved += 1
    print(f"Moved {moved} files ({renamed} renamed for collision)")

    stub = SRC / "README.md"
    stub.write_text(
        "内容已统一至 `../04_OPERATIONS/audit_state`。\n",
        encoding="utf-8",
        newline="\n",
    )
    idx = SRC / "INDEX.md"
    if idx.exists():
        idx.unlink()
    print("Wrote", stub)


if __name__ == "__main__":
    main()
