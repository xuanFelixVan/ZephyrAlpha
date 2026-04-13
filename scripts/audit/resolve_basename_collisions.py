#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3.1b: 执行 Basename 碰撞解决方案

根据 BASENAME_COLLISIONS_DECISION_*.md 中的决策，批量执行：
- CONSOLIDATE: 删除 ARCHIVE 版本，保留活跃版本
- KEEP_AS_IS: 不操作
- RELOCATE: （暂未实现）

使用方式:
    python scripts/audit/resolve_basename_collisions.py [--dry-run] [--decision-md PATH]
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
STATE_DIR = REPO_ROOT / "docs" / "09_AUDIT" / "STATE"


class Action(NamedTuple):
    basename: str
    action: str
    paths: list[str]
    keep_path: str | None = None
    delete_paths: list[str] | None = None


def parse_decision_md(md_path: Path) -> dict[str, Action]:
    """
    从决策报告 MD 解析 CONSOLIDATE 行动。
    格式: 表格 + 详情章节
    """
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    actions: dict[str, Action] = {}

    # 从表格提取 action 行 (支持 Markdown 表格格式)
    table_lines = re.findall(
        r"^\|\s*([^\|]+?)\s*\|\s*\d+\s*\|\s*([A-Z_]+)\s*\|",
        content,
        re.MULTILINE,
    )
    action_map = {bn.strip(): act.strip() for bn, act in table_lines}

    # 找 CONSOLIDATE 的 basename
    consolidate_basenames = {bn for bn, act in action_map.items() if act == "CONSOLIDATE"}

    # 对每个 CONSOLIDATE basename，从详情章节提取路径
    for basename in consolidate_basenames:
        section_pattern = rf"### {re.escape(basename)}\n(.*?)(?=###|\Z)"
        match = re.search(section_pattern, content, re.DOTALL)
        if not match:
            continue

        section = match.group(1)
        paths = re.findall(r"^-\s+`([^`]+)`", section, re.MULTILINE)

        if not paths:
            continue

        # 找到 ARCHIVE 和活跃版本
        archive_paths = [p for p in paths if "/ARCHIVE/" in p or ".audit_fix_backup/" in p]
        active_paths = [p for p in paths if p not in archive_paths]

        # CONSOLIDATE: 保留活跃版本数最少的，删除其他
        if len(active_paths) >= 1 and len(archive_paths) >= 1:
            keep_path = active_paths[0]  # 保留第一个活跃版本
            actions[basename] = Action(
                basename=basename,
                action="CONSOLIDATE",
                paths=paths,
                keep_path=keep_path,
                delete_paths=archive_paths,
            )

    return actions


def execute_consolidate(action: Action, dry_run: bool = True) -> dict:
    """
    执行 CONSOLIDATE 行动: 删除 ARCHIVE 版本
    """
    result = {
        "basename": action.basename,
        "action": "CONSOLIDATE",
        "keep": action.keep_path,
        "delete": action.delete_paths or [],
        "deleted_count": 0,
        "errors": [],
    }

    for del_path in action.delete_paths or []:
        full_path = REPO_ROOT / del_path
        if not full_path.exists():
            result["errors"].append(f"{del_path} not found (already deleted?)")
            continue

        try:
            if not dry_run:
                full_path.unlink()
                result["deleted_count"] += 1
            else:
                result["deleted_count"] += 1
        except Exception as e:
            result["errors"].append(f"{del_path}: {e}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Execute basename collision resolutions")
    parser.add_argument(
        "--dry-run", action="store_true", help="Do not delete, only report"
    )
    parser.add_argument(
        "--decision-md",
        type=Path,
        default=STATE_DIR / "BASENAME_COLLISIONS_DECISION_20260413.md",
        help="Path to decision markdown",
    )
    args = parser.parse_args()

    if not args.decision_md.exists():
        print(f"ERROR: {args.decision_md} not found")
        return

    print(f"Loading decisions from {args.decision_md.name} ...")
    actions = parse_decision_md(args.decision_md)
    consolidate_actions = {bn: a for bn, a in actions.items() if a.action == "CONSOLIDATE"}

    print(f"  Found {len(consolidate_actions)} CONSOLIDATE actions")

    results = []
    total_deleted = 0
    total_errors = 0

    for bn, action in sorted(consolidate_actions.items()):
        result = execute_consolidate(action, dry_run=args.dry_run)
        results.append(result)
        total_deleted += result["deleted_count"]
        total_errors += len(result["errors"])

        status = "OK" if not result["errors"] else "FAIL"
        print(f"  {status} {bn}: deleted {result['deleted_count']} versions")
        if result["errors"]:
            for err in result["errors"]:
                print(f"      → {err}")

    # Write report
    timestamp = datetime.now().strftime("%Y%m%d")
    report_json = STATE_DIR / f"BASENAME_COLLISIONS_RESOLVE_{timestamp}.json"
    report_md = STATE_DIR / f"BASENAME_COLLISIONS_RESOLVE_{timestamp}.md"

    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "dry_run": args.dry_run,
                "actions_executed": len(results),
                "total_deleted": total_deleted,
                "total_errors": total_errors,
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    with open(report_md, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("module_id: AUDIT_BASENAME_COLLISIONS_RESOLVE\n")
        f.write("standard_type: audit_action\n")
        f.write(f"generated_at: {timestamp}\n")
        f.write("---\n\n")
        f.write("# Basename 碰撞解决执行报告\n\n")
        f.write(f"> **模式**: {'DRY-RUN' if args.dry_run else 'APPLY'}\n")
        f.write(f"> **执行时间**: {timestamp}\n")
        f.write(f"> **行动总数**: {len(results)}\n")
        f.write(f"> **删除版本数**: {total_deleted}\n")
        f.write(f"> **错误数**: {total_errors}\n\n")
        f.write("## 执行详情\n\n")
        for result in results:
            f.write(f"### {result['basename']}\n\n")
            f.write(f"- **行动**: {result['action']}\n")
            f.write(f"- **保留**: `{result['keep']}`\n")
            f.write(f"- **删除**: {len(result['delete'])} 个版本\n")
            if result["deleted_count"] > 0:
                f.write(f"  - ✓ 已删除 {result['deleted_count']} 个\n")
            for err in result["errors"]:
                f.write(f"  - ✗ {err}\n")
            f.write("\n")

    print(f"\nWrote {report_json}")
    print(f"Wrote {report_md}")

    if args.dry_run:
        print("\n(DRY-RUN mode: no files deleted)")
    else:
        print(f"\n[APPLY] {total_deleted} files deleted, {total_errors} errors")


if __name__ == "__main__":
    main()
