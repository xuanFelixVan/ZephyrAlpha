# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
"""Write docs/09_AUDIT/STATE/MD_FILES_BY_SUBDIRECTORY_20260408.md grouped by parent dir."""
from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "09_AUDIT" / "STATE" / "MD_FILES_BY_SUBDIRECTORY_20260408.md"

SKIP_PARTS = (".git", ".venv", ".pytest_cache")


def skip_path(p: Path) -> bool:
    parts = set(p.parts)
    return any(s in parts for s in SKIP_PARTS)


def main() -> None:
    md_files: list[str] = []
    for p in REPO.rglob("*.md"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(REPO).as_posix()
        except ValueError:
            continue
        if skip_path(p):
            continue
        md_files.append(rel)
    md_files.sort()

    by_dir: dict[str, list[str]] = defaultdict(list)
    for rel in md_files:
        parent = str(Path(rel).parent)
        if parent == ".":
            parent = "."
        by_dir[parent].append(rel)

    lines: list[str] = [
        "# Markdown 文件按子目录清单（文档审计适用）",
        "",
        "> **生成时间**: 2026-04-08",
        "> **排除路径**: `.venv/`、`.pytest_cache/`（依赖与缓存内 md 不纳入治理审计）",
        "> **说明**: 仓库根若存在与 `docs/` 并行的 `05_IMPLEMENTATION/` 等目录，将一并列出以便对照目录漂移。",
        "> **配套全案**: `docs/09_AUDIT/PROCEDURES/FULL_SYSTEM_AUDIT_COMPLETE_CASE_20260408.md`",
        "",
        "## 统计",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 子目录数（含根 `.`） | {len(by_dir)} |",
        f"| Markdown 文件总数 | {len(md_files)} |",
        "",
    ]

    for d in sorted(by_dir.keys(), key=lambda x: (x != ".", x.lower())):
        files = sorted(by_dir[d])
        lines.append(f"## `{d}`（{len(files)} 个文件）")
        lines.append("")
        for f in files:
            lines.append(f"- `{f}`")
        lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} files={len(md_files)} dirs={len(by_dir)}")


if __name__ == "__main__":
    main()
