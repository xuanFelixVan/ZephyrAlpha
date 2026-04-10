# -*- coding: utf-8 -*-
"""
任务 1：生成「正式图纸柜外」活跃 *BLUEPRINT.md 路径清单（可点击相对链接），供总清单引用。

规则（与项目办公室任务 1 口径一致）：
- 仅包含文件名以 BLUEPRINT.md 结尾的 .md（排除 *BLUEPRINTS.md 集合类命名）。
- 排除 docs/06_ARCHIVE、docs/09_ARCHIVE、docs/09_AUDIT、.git 等路径段。
- 排除 audit_state、overnight_runs、double_yaml_dryrun 等过程目录。
- 排除 01_BLUEPRINTS 根目录下 *.md（已由 INDEX.md 枚举）。

输出：
- docs/09_AUDIT/STATE/ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.md
- docs/09_AUDIT/STATE/ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.json

仓库根: python scripts/governance/generate_scattered_blueprints_manifest_task1.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"
OUT_DIR = DOCS / "09_AUDIT" / "STATE"
OUT_MD = OUT_DIR / "ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.md"
OUT_JSON = OUT_DIR / "ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.json"

SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
    }
)
SKIP_PATH_MARKERS = (
    "/06_ARCHIVE/",
    "/09_ARCHIVE/",
    "/09_AUDIT/",
    "audit_state",
    "overnight_runs",
    "double_yaml_dryrun",
)

CABINET_ROOT = (
    DOCS / "05_IMPLEMENTATION" / "06_CONSTRUCTION_DOCS" / "01_BLUEPRINTS"
).resolve()


def skip_path(rel_posix: str) -> bool:
    if any(m in rel_posix for m in SKIP_PATH_MARKERS):
        return True
    return False


def is_scattered_blueprint(p: Path) -> bool:
    if not p.is_file():
        return False
    name = p.name
    if not name.lower().endswith(".md"):
        return False
    if not name.endswith("BLUEPRINT.md"):
        return False
    try:
        rel = p.resolve().relative_to(REPO)
    except ValueError:
        return False
    rel_posix = rel.as_posix()
    if not rel_posix.startswith("docs/"):
        return False
    if skip_path(rel_posix):
        return False
    for part in rel.parts:
        if part in SKIP_DIR_NAMES:
            return False
    try:
        p.resolve().relative_to(CABINET_ROOT)
        # under cabinet tree
        if p.parent.resolve() == CABINET_ROOT:
            return False  # root *.md 由 INDEX 覆盖
    except ValueError:
        pass
    return True


def relpath_for_md(from_dir: Path, target: Path) -> str:
    return os.path.relpath(target, from_dir).replace("\\", "/")


def main() -> int:
    scattered: list[Path] = []
    for p in DOCS.rglob("*.md"):
        if is_scattered_blueprint(p):
            scattered.append(p)
    scattered.sort(key=lambda x: x.as_posix().lower())

    rels = [p.relative_to(REPO).as_posix().replace("\\", "/") for p in scattered]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(rels),
        "paths_posix": rels,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "---",
        "title: 任务1 · 分散正式蓝图路径清单（机器生成）",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"entry_count: {len(rels)}",
        "---",
        "",
        "> **用途**：补充 `01_BLUEPRINTS/INDEX.md` 未覆盖的、仍位于业务目录下的 `*BLUEPRINT.md` 正式稿路径。",
        "> **生成**：`python scripts/governance/generate_scattered_blueprints_manifest_task1.py`",
        "",
        f"## 条目列表（共 **{len(rels)}** 条，相对链接自本文件）",
        "",
    ]
    for p in scattered:
        stem = p.stem
        href = relpath_for_md(OUT_MD.parent, p)
        lines.append(f"- [{stem}]({href})")

    lines.extend(["", "---", "", "**维护**：新增/移动分散蓝图后重跑生成脚本并提交。", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Wrote {OUT_MD} and JSON, entries={len(rels)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
