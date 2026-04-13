#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3.1c: 执行孤儿文件解决方案

根据 ORPHAN_DECISION_*.jsonl 中的决策，批量执行：
- TIER_1_ADD_LINK (action=ADD_LINK): 在父目录 INDEX.md 中添加链接引用
- TIER_2_ARCHIVE  (action=ARCHIVE): 移动到 docs/06_ARCHIVE/
- EXEMPT / TIER_3_REVIEW: 跳过

JSONL 字段: {"path": ..., "tier": ..., "action": ..., "reason": ..., "suggested_index": ...}

使用方式:
    python scripts/audit/resolve_orphan_files.py [--dry-run] [--decision-jsonl PATH]
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent.parent
STATE_DIR   = REPO_ROOT / "docs" / "09_AUDIT" / "STATE"


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def load_orphan_decisions(jsonl_path: Path) -> list[dict]:
    decisions = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                decisions.append(json.loads(line))
    return decisions


def add_link_to_index(index_path: Path, file_path: Path, dry_run: bool) -> dict:
    """在 INDEX.md 末尾添加链接（若还不存在）。"""
    if not index_path.exists():
        return {"success": False, "message": f"INDEX not found: {index_path}"}

    try:
        rel_path = file_path.relative_to(index_path.parent)
    except ValueError:
        return {"success": False, "message": "Cannot compute relative path"}

    link_line = f"- [{file_path.stem}]({rel_path})"

    with open(index_path, encoding="utf-8") as f:
        content = f.read()

    # 已存在则跳过
    if str(rel_path) in content or f"/{file_path.name}" in content:
        return {"success": False, "message": "Link already exists"}

    # 追加到尾部（最保险）
    new_content = content.rstrip("\n") + f"\n\n<!-- orphan-link -->\n{link_line}\n"

    if not dry_run:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    return {"success": True, "message": f"Appended: {link_line}"}


def move_to_archive(file_path: Path, dry_run: bool) -> dict:
    """将文件移至 docs/06_ARCHIVE/，保留相对目录结构。"""
    try:
        rel = file_path.relative_to(REPO_ROOT / "docs")
    except ValueError:
        return {"success": False, "message": "Not under docs/"}

    archive_path = REPO_ROOT / "docs" / "06_ARCHIVE" / rel
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        return {"success": False, "message": "Source file not found"}

    if archive_path.exists():
        return {"success": False, "message": f"Archive target exists: {archive_path.relative_to(REPO_ROOT)}"}

    if not dry_run:
        file_path.rename(archive_path)

    return {"success": True, "message": f"→ docs/06_ARCHIVE/{rel}"}


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Execute orphan file resolutions (Phase 3.1c)")
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not modify files")
    parser.add_argument(
        "--decision-jsonl",
        type=Path,
        default=STATE_DIR / "ORPHAN_DECISION_20260413.jsonl",
    )
    parser.add_argument(
        "--tier1-limit",
        type=int,
        default=0,
        help="Max TIER_1 items to process (0 = all)",
    )
    args = parser.parse_args()

    if not args.decision_jsonl.exists():
        print(f"ERROR: {args.decision_jsonl} not found")
        return

    print(f"Loading decisions from {args.decision_jsonl.name} ...")
    decisions = load_orphan_decisions(args.decision_jsonl)
    print(f"  Total records: {len(decisions)}")

    tier1 = [d for d in decisions if d.get("action") == "ADD_LINK"]
    tier2 = [d for d in decisions if d.get("action") == "ARCHIVE"]

    print(f"  TIER_1_ADD_LINK : {len(tier1)}")
    print(f"  TIER_2_ARCHIVE  : {len(tier2)}")

    if args.tier1_limit:
        tier1 = tier1[: args.tier1_limit]
        print(f"  (limited TIER_1 to {args.tier1_limit})")

    results: list[dict] = []
    t1_ok = t1_fail = t2_ok = t2_fail = 0

    # ── TIER_1: ADD_LINK ──────────────────────
    print("\nProcessing TIER_1_ADD_LINK ...")
    for d in tier1:
        fpath       = REPO_ROOT / d["path"]
        idx_rel     = d.get("suggested_index") or ""
        idx_path    = REPO_ROOT / idx_rel if idx_rel else None

        if idx_path is None or not idx_path.exists():
            t1_fail += 1
            results.append({"file": d["path"], "action": "ADD_LINK", "result": "FAILED",  "reason": "INDEX not found"})
            continue

        res = add_link_to_index(idx_path, fpath, dry_run=args.dry_run)
        if res["success"]:
            t1_ok += 1
            results.append({"file": d["path"], "action": "ADD_LINK", "result": "SUCCESS", "message": res["message"]})
        else:
            t1_fail += 1
            results.append({"file": d["path"], "action": "ADD_LINK", "result": "SKIPPED", "reason":  res["message"]})

    print(f"  OK {t1_ok} added  FAIL {t1_fail} failed/skipped")

    # -- TIER_2: ARCHIVE -----------------------------------------
    print("Processing TIER_2_ARCHIVE ...")
    for d in tier2:
        fpath = REPO_ROOT / d["path"]
        res   = move_to_archive(fpath, dry_run=args.dry_run)
        if res["success"]:
            t2_ok += 1
            results.append({"file": d["path"], "action": "ARCHIVE", "result": "SUCCESS", "message": res["message"]})
        else:
            t2_fail += 1
            results.append({"file": d["path"], "action": "ARCHIVE", "result": "FAILED",  "reason":  res["message"]})

    print(f"  OK {t2_ok} archived  FAIL {t2_fail} failed")

    # ── Write reports ─────────────────────────
    timestamp  = datetime.now().strftime("%Y%m%d")
    report_json = STATE_DIR / f"ORPHAN_RESOLVE_{timestamp}.json"
    report_md   = STATE_DIR / f"ORPHAN_RESOLVE_{timestamp}.md"

    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp":    timestamp,
                "dry_run":      args.dry_run,
                "tier1_total":  len(tier1),
                "tier1_ok":     t1_ok,
                "tier1_fail":   t1_fail,
                "tier2_total":  len(tier2),
                "tier2_ok":     t2_ok,
                "tier2_fail":   t2_fail,
                "results_sample": results[:100],
            },
            f, indent=2, ensure_ascii=False,
        )

    with open(report_md, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("module_id: AUDIT_ORPHAN_RESOLVE\n")
        f.write("standard_type: audit_action\n")
        f.write(f"generated_at: {timestamp}\n")
        f.write("---\n\n")
        f.write("# 孤儿文件解决执行报告（Phase 3.1c）\n\n")
        f.write(f"> **模式**: {'DRY-RUN' if args.dry_run else 'APPLY'}\n")
        f.write(f"> **执行时间**: {timestamp}\n\n")
        f.write("## 统计\n\n")
        f.write("| 行动 | 总数 | 成功 | 失败/跳过 |\n")
        f.write("|------|------|------|----------|\n")
        f.write(f"| ADD_LINK | {len(tier1)} | {t1_ok} | {t1_fail} |\n")
        f.write(f"| ARCHIVE  | {len(tier2)} | {t2_ok} | {t2_fail} |\n\n")
        f.write("## 详情（前 100 条）\n\n")
        for r in results[:100]:
            status = "OK" if r["result"] == "SUCCESS" else ("SKIP" if r["result"] == "SKIPPED" else "FAIL")
            note   = r.get("message") or r.get("reason") or ""
            f.write(f"- {status} `{r['file']}` → {r['result']}: {note}\n")
        if len(results) > 100:
            f.write(f"\n_... and {len(results) - 100} more (see JSON)_\n")

    print(f"\nWrote {report_json.name}")
    print(f"Wrote {report_md.name}")
    mode = "DRY-RUN" if args.dry_run else "APPLY"
    print(f"\n[{mode}] TIER_1: {t1_ok}/{len(tier1)} added  TIER_2: {t2_ok}/{len(tier2)} archived")


if __name__ == "__main__":
    main()
