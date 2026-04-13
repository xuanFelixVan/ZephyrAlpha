#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Basename 碰撞决策报告（F3）：消费 scan_basename_collisions.py 的 JSON，
对 6 个非导航碰撞生成决策表和建议。

策略：
- KEEP_AS_IS: 两个版本都有效，可共存（常见于 archive 中的旧版）
- CONSOLIDATE: 内容相同/高度相似 → 删除副本，保留源
- RELOCATE: 一个应该在专属目录 → 建议移动

仓库根执行:
  python scripts/audit/report_basename_collisions.py
"""

from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C2_JSON = REPO / "docs" / "09_AUDIT" / "STATE" / "BASENAME_COLLISIONS_20260413.json"
OUT_DIR = REPO / "docs" / "09_AUDIT" / "STATE"


def main() -> None:
    with open(C2_JSON, encoding="utf-8") as f:
        c2 = json.load(f)

    clusters = c2.get("clusters", [])
    non_nav_count = c2.get("non_nav_collision_basenames", 0)

    decisions = []
    for cluster in clusters:
        bn = cluster["basename"]
        paths = cluster["paths"]
        if len(paths) <= 1:
            continue

        decision = {
            "basename": bn,
            "count": len(paths),
            "paths": paths,
            "action": "KEEP_AS_IS",
            "reason": None,
        }

        if bn in ("SITEMAP.md", "CHANGELOG.md"):
            decision.update(
                action="KEEP_AS_IS",
                reason="多目录各维护一份，不重复" if len(paths) <= 3 else "超多实例，需审查"
            )
        elif any("ARCHIVE" in p or "archive" in p for p in paths):
            decision.update(
                action="CONSOLIDATE",
                reason="一份在 ARCHIVE（已归档），一份在活跃目录 → 保活跃，删归档"
            )
        elif len(paths) == 2:
            if "REPORTS" in paths[0] and "REPORTS" not in paths[1]:
                decision.update(
                    action="CONSOLIDATE",
                    reason="REPORTS 中的报告是中间产物，应删除"
                )

        decisions.append(decision)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d")

    md_lines = [
        "---",
        f"module_id: AUDIT_BASENAME_COLLISIONS_DECISION_{ts}",
        "standard_type: audit_state",
        "generated_by: scripts/audit/report_basename_collisions.py",
        "---",
        "",
        "# Basename 碰撞决策报告",
        "",
        f"> **生成时间**: {ts}",
        f"> **非导航碰撞**: {non_nav_count} 个 basename",
        "",
        "## 决策汇总",
        "",
        "| Basename | 数量 | 行动 | 理由 |",
        "|----------|------|------|------|",
    ]

    for d in decisions:
        bn = d["basename"]
        cnt = d["count"]
        action = d["action"]
        reason = d["reason"] or "-"
        md_lines.append(f"| {bn} | {cnt} | {action} | {reason} |")

    md_lines.extend(["", "## 详情", ""])

    for d in decisions:
        md_lines.append(f"### {d['basename']}")
        md_lines.append("")
        for p in d["paths"]:
            md_lines.append(f"- `{p}`")
        md_lines.append("")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / f"BASENAME_COLLISIONS_DECISION_{ts}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
