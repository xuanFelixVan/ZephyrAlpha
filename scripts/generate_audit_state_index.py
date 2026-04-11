# -*- coding: utf-8 -*-
"""
重新生成 docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/INDEX.md
（除 INDEX.md 外本目录全部 *.md，按文件名排序；链接统一为 ./文件名.md，满足 P1-2）。

仓库根执行:
  python scripts/generate_audit_state_index.py
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO / "docs" / "05_IMPLEMENTATION" / "04_OPERATIONS" / "audit_state"
OUT = AUDIT_DIR / "INDEX.md"


def main() -> None:
    files = sorted(
        p.name
        for p in AUDIT_DIR.glob("*.md")
        if p.is_file() and p.name.upper() != "INDEX.MD"
    )
    n = len(files)
    today = date.today().isoformat()

    lines = [
        "---",
        "module_id: INDEX_AUDIT_STATE_20260408120000",
        "version: 1.1.1",
        "status: Active",
        "created_date: 2026-04-07",
        f"last_updated: '{today}'",
        "owner: 个人开发者",
        "responsibility:",
        "  - audit_state 目录导航与文档索引",
        "standard_type: 专业量化机构文档",
        "applicable_scope: 05_IMPLEMENTATION/04_OPERATIONS/audit_state",
        "---",
        "",
        "# audit_state 目录索引",
        "",
        "> **核心职责**：提供 `audit_state` 目录下审计/整改类 Markdown 的可点击导航。",
        "> **生成方式**：下列列表由 `scripts/generate_audit_state_index.py` 自动生成，请勿手工逐条维护文件名。",
        "",
        "---",
        "",
        "## 目录概览",
        "",
        r"**目录路径**: `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state`  ",
        f"**Markdown 文件数**（不含本 INDEX）: **{n}**  ",
        f"**索引生成日期**: {today}",
        "",
        "---",
        "",
        "## 上级与接力",
        "",
        "- [04_OPERATIONS 索引](../INDEX.md)",
        "- [04_OPERATIONS 门面（README）](../README.md)",
        "- [全仓库文件治理任务清单 §7](../../06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md#7-一次性深度治理目录队列与退出标准)",
        "- [治理工具总索引](../../06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)",
        "- [09_AUDIT 域索引](../../../09_AUDIT/INDEX.md)",
        "- [STATE 子域索引](../../../09_AUDIT/STATE/INDEX.md)",
        "- [L1 治理快照（20260408）](../../../09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.md)",
        "",
        "---",
        "",
        "## 文档列表（按文件名排序）",
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
            "## 统计信息",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| **总文档数** | {n} |",
            f"| **最后更新** | {today} |",
            "",
            "---",
            "",
            "**维护**：新增/重命名报告后执行 `python scripts/generate_audit_state_index.py` 刷新本页。",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Wrote {OUT} ({n} entries)")


if __name__ == "__main__":
    main()
