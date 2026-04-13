#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3.1d: 执行 TIER_A D-类蓝图重叠解决

从 BLUEPRINT_D_OVERLAP_TRIAGE_*.json 读取 TIER_A_AUTO 对，
对每对执行：
  - 识别"非 canonical"路径（archive/overlap-/legacy- 端）
  - 删除非 canonical 文件
  - 生成执行报告

使用方式:
    python scripts/audit/resolve_tier_a_overlaps.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent.parent
STATE_DIR   = REPO_ROOT / "docs" / "09_AUDIT" / "STATE"


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def is_archive_path(p: Path) -> bool:
    """判断路径是否属于归档/冗余端。"""
    s = str(p).replace("\\", "/")
    return (
        "/06_ARCHIVE/" in s
        or "overlap-" in p.name
        or "legacy" in p.name
        or p.parent.name in ("duplicates", "audit_reports")
    )


def identify_delete_target(pa: Path, pb: Path, canonical_name: str) -> Path | None:
    """
    返回应该被删除的路径。
    优先级：
      1. 若其中一方是 archive 路径 → 删 archive
      2. 若两者都是 archive → 删非 canonical 的那个
      3. 若两者均非 archive → 删非 canonical 文件名的那个
    """
    a_arch = is_archive_path(pa)
    b_arch = is_archive_path(pb)

    if a_arch and not b_arch:
        return pa
    if b_arch and not a_arch:
        return pb
    # 两者都是 archive 或都不是 → 按 canonical 文件名决定
    if canonical_name and pa.name == canonical_name:
        return pb   # B 是非 canonical
    return pa       # A 是非 canonical（或默认）


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve TIER_A D-class overlaps (Phase 3.1d)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--triage-json",
        type=Path,
        default=STATE_DIR / "BLUEPRINT_D_OVERLAP_TRIAGE_20260413.json",
    )
    args = parser.parse_args()

    if not args.triage_json.exists():
        print(f"ERROR: {args.triage_json} not found")
        return

    print(f"Loading triage data from {args.triage_json.name} ...")
    data = json.loads(args.triage_json.read_text(encoding="utf-8"))
    tier_a = [r for r in data["records"] if r["triage_tier"] == "TIER_A_AUTO"]
    print(f"  TIER_A pairs: {len(tier_a)}")
    print()

    results = []
    deleted = 0
    skipped = 0
    errors  = 0

    for i, rec in enumerate(tier_a, 1):
        pa       = REPO_ROOT / rec["path_a"]
        pb       = REPO_ROOT / rec["path_b"]
        canon    = rec.get("suggested_canonical", "")
        score    = rec["score"]
        priority = rec.get("second_pass_priority", "")

        target = identify_delete_target(pa, pb, canon)
        keep   = pb if target == pa else pa

        if not target.exists():
            skipped += 1
            results.append({
                "pair": i, "score": score, "priority": priority,
                "action": "SKIPPED", "target": str(target.relative_to(REPO_ROOT)),
                "keep":   str(keep.relative_to(REPO_ROOT)),
                "reason": "target already gone",
            })
            print(f"#{i:2d} SKIP  (already gone) {target.relative_to(REPO_ROOT)}")
            continue

        try:
            if not args.dry_run:
                target.unlink()
            deleted += 1
            results.append({
                "pair": i, "score": score, "priority": priority,
                "action": "DELETED" if not args.dry_run else "DRY_DELETE",
                "target": str(target.relative_to(REPO_ROOT)),
                "keep":   str(keep.relative_to(REPO_ROOT)),
            })
            mode = "DEL " if not args.dry_run else "WDEL"
            print(f"#{i:2d} {mode}  score={score:.3f}  {target.relative_to(REPO_ROOT)}")
            print(f"         KEEP: {keep.relative_to(REPO_ROOT)}")
        except Exception as e:
            errors += 1
            results.append({
                "pair": i, "score": score, "priority": priority,
                "action": "ERROR", "target": str(target.relative_to(REPO_ROOT)),
                "reason": str(e),
            })
            print(f"#{i:2d} ERR   {e}")

    # ── Write reports ─────────────────────────
    timestamp   = datetime.now().strftime("%Y%m%d")
    report_json = STATE_DIR / f"TIER_A_OVERLAP_RESOLVE_{timestamp}.json"
    report_md   = STATE_DIR / f"TIER_A_OVERLAP_RESOLVE_{timestamp}.md"

    with open(report_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "dry_run":   args.dry_run,
            "total":     len(tier_a),
            "deleted":   deleted,
            "skipped":   skipped,
            "errors":    errors,
            "results":   results,
        }, f, indent=2, ensure_ascii=False)

    with open(report_md, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("module_id: AUDIT_TIER_A_OVERLAP_RESOLVE\n")
        f.write("standard_type: audit_action\n")
        f.write(f"generated_at: {timestamp}\n")
        f.write("---\n\n")
        f.write("# D-类蓝图 TIER_A 重叠解决报告（Phase 3.1d）\n\n")
        f.write(f"> **模式**: {'DRY-RUN' if args.dry_run else 'APPLY'}\n")
        f.write(f"> **执行时间**: {timestamp}\n\n")
        f.write("## 统计\n\n")
        f.write(f"| 指标 | 值 |\n|------|----|\n")
        f.write(f"| 总 TIER_A 对数 | {len(tier_a)} |\n")
        f.write(f"| 已删除冗余版本 | {deleted} |\n")
        f.write(f"| 跳过（已不存在）| {skipped} |\n")
        f.write(f"| 错误 | {errors} |\n\n")
        f.write("## 执行明细\n\n")
        for r in results:
            action_label = r["action"]
            target = r.get("target", "")
            keep   = r.get("keep", "")
            reason = r.get("reason", "")
            f.write(f"### Pair #{r['pair']} (score={r['score']:.3f})\n\n")
            f.write(f"- **行动**: {action_label}\n")
            f.write(f"- **删除**: `{target}`\n")
            if keep:
                f.write(f"- **保留**: `{keep}`\n")
            if reason:
                f.write(f"- **原因**: {reason}\n")
            f.write("\n")

    print(f"\nWrote {report_json.name}")
    print(f"Wrote {report_md.name}")
    mode_label = "DRY-RUN" if args.dry_run else "APPLY"
    print(f"\n[{mode_label}] deleted={deleted}  skipped={skipped}  errors={errors}")


if __name__ == "__main__":
    main()
