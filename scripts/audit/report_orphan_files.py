#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
孤儿文件决策报告（F4）：消费 scan_index_health.py 的 JSON，
对零入链（无任何 Markdown 文件指向）的候选文件进行三级分类和决策建议。

三级决策逻辑：
  TIER_1_ADD_LINK    : 有明确的父目录 INDEX.md → 建议在该 INDEX 中补链
  TIER_2_ARCHIVE     : 文件名含历史日期或已存在同名 archive 版本 → 建议归档
  TIER_3_REVIEW      : 无法自动裁决 → 需 Owner 审查

特殊免审类型（自动标记 EXEMPT）：
  - nav_file  : INDEX.md / README.md（多实例设计，不需要被引用）
  - auto_gen  : docs/09_AUDIT/STATE/ / docs/09_AUDIT/REPORTS/ 自动生成报告
  - entry_file: *-entry.md（架构入口，通常由代码系统引用）

仓库根执行:
  python scripts/audit/report_orphan_files.py
  python scripts/audit/report_orphan_files.py --prefix docs/01_FRAMEWORK
  python scripts/audit/report_orphan_files.py --show-exempt
"""

from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C3_JSON_GLOB_PATTERN = "INDEX_HEALTH_ORPHAN_*.json"
OUT_DIR = REPO / "docs" / "09_AUDIT" / "STATE"

AUTO_GEN_PREFIXES = (
    "docs/09_AUDIT/STATE/",
    "docs/09_AUDIT/REPORTS/",
    "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/",
    "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/",
)
NAV_BASENAMES = {"index.md", "readme.md"}
DATE_PATTERN = re.compile(r"\d{8}|\d{6}|\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4}_\d{2}")
ARCHIVE_PREFIXES = ("docs/06_ARCHIVE/", "docs/09_ARCHIVE/")


def find_latest_c3_json(out_dir: Path) -> Path | None:
    """Find the most recent non-empty INDEX_HEALTH_ORPHAN JSON."""
    matches = sorted(out_dir.glob(C3_JSON_GLOB_PATTERN), reverse=True)
    for m in matches:
        try:
            with open(m, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("zero_inbound_count", 0) > 0 or data.get("zero_inbound_paths"):
                return m
        except Exception:
            continue
    return matches[0] if matches else None


def build_basename_index(repo: Path) -> dict[str, list[str]]:
    idx: dict[str, list[str]] = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in {".git", ".venv", "__pycache__", "node_modules"}]
        for fn in filenames:
            if not fn.lower().endswith(".md"):
                continue
            full = Path(dirpath) / fn
            try:
                rel = full.relative_to(repo).as_posix()
            except ValueError:
                continue
            idx[fn.lower()].append(rel)
    return dict(idx)


def parent_index_exists(orphan_rel: str, repo: Path) -> str | None:
    """Check if the parent directory has an INDEX.md. Return its relpath if so."""
    parent = Path(orphan_rel).parent
    while str(parent) not in (".", ""):
        idx_path = repo / parent / "INDEX.md"
        if idx_path.is_file():
            return (parent / "INDEX.md").as_posix()
        parent = parent.parent
    return None


def has_archive_sibling(orphan_rel: str, basename_idx: dict[str, list[str]]) -> bool:
    """Check if there's a copy of same basename in an archive directory."""
    bn = Path(orphan_rel).name.lower()
    candidates = basename_idx.get(bn, [])
    for c in candidates:
        if any(c.startswith(ap) for ap in ARCHIVE_PREFIXES):
            return True
    return False


def classify_orphan(orphan_rel: str, repo: Path, basename_idx: dict[str, list[str]]) -> dict:
    bn = Path(orphan_rel).name.lower()
    stem = Path(orphan_rel).stem

    record: dict = {
        "path": orphan_rel,
        "tier": None,
        "action": None,
        "reason": None,
        "suggested_index": None,
    }

    # EXEMPT: nav files
    if bn in NAV_BASENAMES:
        record.update(tier="EXEMPT", action="KEEP", reason="nav_file: 多目录导航文件，无需被引用")
        return record

    # EXEMPT: auto-generated reports/state
    if any(orphan_rel.startswith(p) for p in AUTO_GEN_PREFIXES):
        record.update(tier="EXEMPT", action="KEEP", reason="auto_gen: 自动生成报告，无需内链")
        return record

    # EXEMPT: entry files
    if orphan_rel.endswith("-entry.md"):
        record.update(tier="EXEMPT", action="KEEP", reason="entry_file: 架构入口文件，由系统引用")
        return record

    # TIER_2 first: date in filename (historical/versioned doc)
    if DATE_PATTERN.search(stem):
        record.update(
            tier="TIER_2_ARCHIVE",
            action="ARCHIVE",
            reason="文件名含日期模式（历史版本/快照），建议归档至 docs/06_ARCHIVE/",
        )
        return record

    # TIER_2: already has archive sibling
    if has_archive_sibling(orphan_rel, basename_idx):
        record.update(
            tier="TIER_2_ARCHIVE",
            action="ARCHIVE",
            reason="存在同名归档副本，本文件应归档或删除",
        )
        return record

    # TIER_1: parent directory has INDEX.md → suggest adding link
    idx_path = parent_index_exists(orphan_rel, repo)
    if idx_path:
        record.update(
            tier="TIER_1_ADD_LINK",
            action="ADD_LINK",
            reason="父目录 INDEX.md 存在 → 在 INDEX 中补充入链",
            suggested_index=idx_path,
        )
        return record

    # TIER_3: cannot auto-decide
    record.update(
        tier="TIER_3_REVIEW",
        action="OWNER_REVIEW",
        reason="无父目录 INDEX、无归档副本、无日期标记 → 需 Owner 判断保留/归档/删除",
    )
    return record


def write_jsonl(results: list[dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_report_md(results: list[dict], ts: str, stats: dict, path: Path) -> None:
    from collections import Counter
    tier_counts = Counter(r["tier"] for r in results)
    action_counts = Counter(r["action"] for r in results)

    lines = [
        "---",
        f"module_id: AUDIT_ORPHAN_DECISION_{ts}",
        "standard_type: audit_state",
        "generated_by: scripts/audit/report_orphan_files.py",
        "---",
        "",
        "# 孤儿文件决策报告（F4）",
        "",
        f"> **生成时间**: {ts}",
        f"> **候选文件数**: {stats['total_orphans']}",
        f"> **分析范围**: {stats['prefix']}",
        "",
        "## 统计总览",
        "",
        "| 层级 | 数量 |",
        "|------|------|",
    ]
    for tier, cnt in tier_counts.most_common():
        lines.append(f"| {tier} | {cnt} |")

    lines.extend(["", "## 行动汇总", "", "| 行动 | 数量 |", "|------|------|"])
    for action, cnt in action_counts.most_common():
        lines.append(f"| {action} | {cnt} |")

    for tier in ["TIER_1_ADD_LINK", "TIER_2_ARCHIVE", "TIER_3_REVIEW"]:
        items = [r for r in results if r["tier"] == tier]
        if not items:
            continue
        lines.extend(["", f"## {tier}（{len(items)} 条）", ""])
        for r in items[:50]:
            suggested = f" → `{r['suggested_index']}`" if r.get("suggested_index") else ""
            lines.append(f"- `{r['path']}`{suggested}")
        if len(items) > 50:
            lines.append(f"  _…（共 {len(items)} 条，完整列表见 JSONL）_")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="孤儿文件决策报告（F4）")
    parser.add_argument("--prefix", default=None, help="仅处理该前缀下的孤儿候选")
    parser.add_argument("--show-exempt", action="store_true", help="报告中包含 EXEMPT 类型")
    parser.add_argument("--c3-json", default=None, help="指定 C3 JSON 路径（默认取最新）")
    args = parser.parse_args()

    c3_path = Path(args.c3_json) if args.c3_json else find_latest_c3_json(OUT_DIR)
    if not c3_path or not c3_path.is_file():
        print("ERROR: C3 JSON not found. Run scan_index_health.py first.")
        sys.exit(1)

    print(f"Loading orphan data from {c3_path} ...")
    with open(c3_path, encoding="utf-8") as f:
        c3 = json.load(f)

    orphans: list[str] = c3.get("zero_inbound_paths", [])
    print(f"  Total zero-inbound candidates: {len(orphans)}")

    if args.prefix:
        orphans = [p for p in orphans if p.startswith(args.prefix)]
        print(f"  After prefix filter '{args.prefix}': {len(orphans)}")

    print("Building basename index ...")
    basename_idx = build_basename_index(REPO)

    print("Classifying orphans ...")
    results = [classify_orphan(p, REPO, basename_idx) for p in orphans]

    from collections import Counter
    tier_counts = Counter(r["tier"] for r in results)
    print("  Tier distribution:", dict(tier_counts.most_common()))

    if not args.show_exempt:
        report_results = [r for r in results if r["tier"] != "EXEMPT"]
    else:
        report_results = results

    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    jsonl_path = OUT_DIR / f"ORPHAN_DECISION_{ts}.jsonl"
    write_jsonl(results, jsonl_path)

    stats = {
        "total_orphans": len(orphans),
        "prefix": args.prefix or "docs/",
    }
    md_path = OUT_DIR / f"ORPHAN_DECISION_{ts}.md"
    write_report_md(report_results, ts, stats, md_path)

    print(f"Wrote {jsonl_path}")
    print(f"Wrote {md_path}")

    # Summary
    non_exempt = [r for r in results if r["tier"] != "EXEMPT"]
    t1 = sum(1 for r in non_exempt if r["tier"] == "TIER_1_ADD_LINK")
    t2 = sum(1 for r in non_exempt if r["tier"] == "TIER_2_ARCHIVE")
    t3 = sum(1 for r in non_exempt if r["tier"] == "TIER_3_REVIEW")
    print(f"\nAction summary (non-EXEMPT {len(non_exempt)} files):")
    print(f"  TIER_1_ADD_LINK  : {t1:4d}  (在父目录 INDEX 补链)")
    print(f"  TIER_2_ARCHIVE   : {t2:4d}  (归档)")
    print(f"  TIER_3_REVIEW    : {t3:4d}  (需 Owner 审查)")


if __name__ == "__main__":
    main()
