# -*- coding: utf-8 -*-
"""
重新生成 docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md
（除 INDEX.md 外本目录全部 *.md，按文件名排序）。仓库根执行:
  python scripts/governance/generate_01_blueprints_index.py
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BLUEPRINT_DIR = REPO / "docs" / "05_IMPLEMENTATION" / "06_CONSTRUCTION_DOCS" / "01_BLUEPRINTS"
OUT = BLUEPRINT_DIR / "INDEX.md"


def main() -> None:
    files = sorted(
        p.name
        for p in BLUEPRINT_DIR.glob("*.md")
        if p.is_file() and p.name.upper() != "INDEX.MD"
    )
    n = len(files)
    today = date.today().isoformat()

    lines = [
        "---",
        "module_id: 01_BLUEPRINTS_INDEX_001",
        "version: 1.1.2",
        "status: Active",
        "created_date: 2026-04-07",
        f"last_updated: '{today}'",
        "owner: 文档管理团队",
        "responsibility:",
        "  - 提供 01_BLUEPRINTS 目录完整索引（机器生成列表）",
        "standard_type: 专业量化机构索引",
        "applicable_scope: 01_BLUEPRINTS",
        "---",
        "",
        "# 01_BLUEPRINTS 索引",
        "",
        "> **说明**：下列「完整文件列表」由 `scripts/governance/generate_01_blueprints_index.py` 生成，避免手工维护漏项。",
        "",
        "## 权威导航",
        "",
        "- 总架构：[ARCHITECTURE.md](../../../01_FRAMEWORK/ARCHITECTURE.md)",
        "- 模块职责边界：[MODULE_RESPONSIBILITY_BOUNDARIES.md](../../../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)",
        "- 架构映射：[BLUEPRINT_ARCHITECTURE_MAPPING.md](../../../01_FRAMEWORK/BLUEPRINT_ARCHITECTURE_MAPPING.md)",
        "",
        "## 治理与接力（项目办公室）",
        "",
        "- [项目办公室总入口](../00_MANAGEMENT/README.md) ｜ [全仓库文件治理任务清单 §7](../00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md#7-一次性深度治理目录队列与退出标准) ｜ [图纸柜规则](../00_MANAGEMENT/01_BLUEPRINTS_REPOSITORY_RULES.md) ｜ [图纸柜执行协议](../00_MANAGEMENT/BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md)  ",
        "- [过程稿与报告子目录说明](./REPORTS/README.md)（非 `*BLUEPRINT.md` 终稿）  ",
        "- [治理工具总索引](../00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md) ｜ [09_AUDIT 域索引](../../../09_AUDIT/INDEX.md) ｜ [STATE 子域索引](../../../09_AUDIT/STATE/INDEX.md) ｜ [L1 治理快照（20260408）](../../../09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.md) ｜ [建设文档区门面](../README.md) ｜ [实施域索引](../../INDEX.md) ｜ [文档总入口](../../../INDEX.md)  ",
        "- **深度 3 前缀体量（rollup）**：[REPO_DIRECTORY_ROLLUP_20260413.md](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260413.md)（检索 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS`；与本目录蓝图文件数口径不同属正常）",
        "",
        "## 目录概要",
        "",
        f"- **本目录 Markdown 文件数**（含报告类；不含本 INDEX）: **{n}**",
        "",
        "## 完整文件列表（按文件名排序）",
        "",
    ]
    for name in files:
        stem = name[:-3] if name.lower().endswith(".md") else name
        lines.append(f"- [{stem}](./{name})")

    lines.extend(
        [
            "",
            "---",
            "",
            "**维护**: 新增/重命名蓝图后运行 `python scripts/governance/generate_01_blueprints_index.py` 更新本页。",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Wrote {OUT} ({n} entries)")


if __name__ == "__main__":
    main()
