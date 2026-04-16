#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# [Phase2 裁决] 本脚本与 scripts/governance/triage_blueprint_d_overlap_pairs.py 同名但功能不同：
#   本脚本（audit/）：按置信度评分将候选对分档（TIER_A/B/C），输出 JSON + MD 摘要。
#   governance/ 版：提取每对文档的内容摘要，生成供大模型二审的 JSONL 队列。
#   两者协作：先运行本脚本分档 → 再运行 governance/ 版对 TIER_B 二审。
"""
D 类蓝图重叠候选 A 档分流脚本（F5）。
消费 scan_blueprint_d_overlap_candidates.py 的 JSON 输出，
按置信度将 400 对候选分为三档：

  TIER_A_AUTO    (score >= 0.85): 极高相似 → 建议自动合并或 stub 化（需 Owner 签核）
  TIER_B_SECOND  (0.5 <= score < 0.85): 中等相似 → 输入二审队列
  TIER_C_LOW     (score < 0.5): 低相似 → 暂缓，记录备查

路径规则修正（在评分基础上调整 second_pass_priority）：
  - 两条路径均在 06_ARCHIVE / 09_ARCHIVE → priority 降为 LOW（已归档，紧迫度低）
  - 一条在活跃目录、一条在 Archive → priority 升为 HIGH（存在非预期幽灵引用风险）
  - 两条路径均在活跃目录 docs/05_IMPLEMENTATION/.../01_BLUEPRINTS → priority HIGH

输出：
  docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_<date>.json     全量档案
  docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_TRIAGE_<date>.md       可读摘要
  docs/09_AUDIT/STATE/SECOND_PASS_QUEUE_<date>.jsonl             TIER_B 二审队列

仓库根执行:
  python scripts/audit/triage_blueprint_d_overlap_pairs.py
  python scripts/audit/triage_blueprint_d_overlap_pairs.py --min-score-a 0.85 --min-score-b 0.5
  python scripts/audit/triage_blueprint_d_overlap_pairs.py --input docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_20260413.json
"""

from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs" / "09_AUDIT" / "STATE"
C4_GLOB = "BLUEPRINT_D_OVERLAP_CANDIDATES_*.json"
ARCHIVE_PREFIXES = ("docs/06_ARCHIVE/", "docs/09_ARCHIVE/", ".audit_fix_backup/")
ACTIVE_BLUEPRINT_PREFIX = "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS"


def find_latest_c4(out_dir: Path) -> Path | None:
    matches = sorted(out_dir.glob(C4_GLOB), reverse=True)
    for m in matches:
        try:
            with open(m, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("candidate_pair_count", 0) > 0:
                return m
        except Exception:
            continue
    return matches[0] if matches else None


def is_archive(path: str) -> bool:
    return any(path.startswith(p) for p in ARCHIVE_PREFIXES)


def assign_tier(pair: dict, min_score_a: float, min_score_b: float) -> tuple[str, str]:
    """Returns (triage_tier, second_pass_priority)."""
    score = pair["score"]
    path_a: str = pair["path_a"]
    path_b: str = pair["path_b"]

    a_archived = is_archive(path_a)
    b_archived = is_archive(path_b)

    if score >= min_score_a:
        tier = "TIER_A_AUTO"
    elif score >= min_score_b:
        tier = "TIER_B_SECOND"
    else:
        tier = "TIER_C_LOW"

    # Path-rule adjustments for second_pass_priority
    if a_archived and b_archived:
        priority = "LOW"
    elif (not a_archived and b_archived) or (a_archived and not b_archived):
        priority = "HIGH" if score >= min_score_b else "MEDIUM"
    elif path_a.startswith(ACTIVE_BLUEPRINT_PREFIX) and path_b.startswith(ACTIVE_BLUEPRINT_PREFIX):
        priority = "HIGH"
    else:
        if tier == "TIER_A_AUTO":
            priority = "HIGH"
        elif tier == "TIER_B_SECOND":
            priority = "MEDIUM"
        else:
            priority = "LOW"

    return tier, priority


def build_triage_record(pair: dict, tier: str, priority: str, pair_id: int) -> dict:
    metrics = pair.get("metrics", {})
    return {
        "pair_id": pair_id,
        "triage_tier": tier,
        "second_pass_priority": priority,
        "score": pair["score"],
        "path_a": pair["path_a"],
        "path_b": pair["path_b"],
        "title_a": pair.get("titles", {}).get("a", ""),
        "title_b": pair.get("titles", {}).get("b", ""),
        "module_id_a": pair.get("module_ids", {}).get("a", ""),
        "module_id_b": pair.get("module_ids", {}).get("b", ""),
        "heading_jaccard": metrics.get("heading_jaccard", 0),
        "token_jaccard": metrics.get("token_jaccard", 0),
        "token_intersection": metrics.get("token_intersection", 0),
        "suggested_canonical": pair.get("suggested_canonical", ""),
        "suggested_canonical_reasons_zh": pair.get("suggested_canonical_reasons_zh", []),
        "suggested_merge_outline": pair.get("suggested_merge_outline", []),
        "a_archived": is_archive(pair["path_a"]),
        "b_archived": is_archive(pair["path_b"]),
    }


def write_triage_md(records: list[dict], ts: str, stats: dict, path: Path) -> None:
    tier_counts = Counter(r["triage_tier"] for r in records)
    priority_counts = Counter(r["second_pass_priority"] for r in records)

    lines = [
        "---",
        f"module_id: AUDIT_BLUEPRINT_D_OVERLAP_TRIAGE_{ts}",
        "standard_type: audit_state",
        "generated_by: scripts/audit/triage_blueprint_d_overlap_pairs.py",
        "---",
        "",
        "# D 类蓝图重叠 A 档分流报告（F5）",
        "",
        f"> **生成时间**: {ts}",
        f"> **候选对总数**: {stats['total']}",
        f"> **评分阈值**: TIER_A ≥ {stats['min_score_a']}，TIER_B ≥ {stats['min_score_b']}",
        "",
        "## 档位分布",
        "",
        "| 档位 | 数量 | 说明 |",
        "|------|------|------|",
        f"| TIER_A_AUTO | {tier_counts.get('TIER_A_AUTO', 0)} | score ≥ {stats['min_score_a']}，建议 auto-merge / stub（需 Owner 签核） |",
        f"| TIER_B_SECOND | {tier_counts.get('TIER_B_SECOND', 0)} | 中等相似，输入二审队列 |",
        f"| TIER_C_LOW | {tier_counts.get('TIER_C_LOW', 0)} | 低相似，暂缓备查 |",
        "",
        "## 二审优先级分布",
        "",
        "| 优先级 | 数量 |",
        "|--------|------|",
    ]
    for prio, cnt in priority_counts.most_common():
        lines.append(f"| {prio} | {cnt} |")

    # TIER_A section
    tier_a = [r for r in records if r["triage_tier"] == "TIER_A_AUTO"]
    if tier_a:
        lines.extend(["", f"## TIER_A_AUTO（{len(tier_a)} 对，score ≥ {stats['min_score_a']}）", ""])
        lines.append("| # | Score | Path A | Path B | Canonical | Priority |")
        lines.append("|---|-------|--------|--------|-----------|----------|")
        for r in tier_a:
            pa = r["path_a"].replace("docs/06_ARCHIVE/blueprints/", "…/06_ARCHIVE/")
            pb = r["path_b"].replace("docs/06_ARCHIVE/blueprints/", "…/06_ARCHIVE/")
            can = r["suggested_canonical"].split("/")[-1] if r["suggested_canonical"] else "-"
            lines.append(f"| {r['pair_id']} | {r['score']:.3f} | `{pa}` | `{pb}` | `{can}` | {r['second_pass_priority']} |")

    # TIER_B section (HIGH priority only, rest truncated)
    tier_b = [r for r in records if r["triage_tier"] == "TIER_B_SECOND"]
    tier_b_high = [r for r in tier_b if r["second_pass_priority"] == "HIGH"]
    if tier_b:
        lines.extend(["", f"## TIER_B_SECOND（{len(tier_b)} 对，仅展示 HIGH 优先级 {len(tier_b_high)} 条）", ""])
        if tier_b_high:
            lines.append("| # | Score | Path A | Path B | Canonical | A_arch | B_arch |")
            lines.append("|---|-------|--------|--------|-----------|--------|--------|")
            for r in tier_b_high[:30]:
                pa = "/".join(r["path_a"].split("/")[-2:])
                pb = "/".join(r["path_b"].split("/")[-2:])
                can = r["suggested_canonical"].split("/")[-1] if r["suggested_canonical"] else "-"
                lines.append(
                    f"| {r['pair_id']} | {r['score']:.3f} | `…/{pa}` | `…/{pb}` | `{can}` "
                    f"| {'✓' if r['a_archived'] else '✗'} | {'✓' if r['b_archived'] else '✗'} |"
                )
        lines.append("")
        lines.append(f"_完整列表见 `BLUEPRINT_D_OVERLAP_TRIAGE_{ts}.json` 和 `SECOND_PASS_QUEUE_{ts}.jsonl`_")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="D 类蓝图重叠 A 档分流（F5）")
    parser.add_argument("--input", default=None, help="指定 C4 JSON 路径（默认取最新）")
    parser.add_argument("--min-score-a", type=float, default=0.85, help="TIER_A 分数阈值（默认 0.85）")
    parser.add_argument("--min-score-b", type=float, default=0.5, help="TIER_B 分数阈值（默认 0.5）")
    args = parser.parse_args()

    c4_path = Path(args.input) if args.input else find_latest_c4(OUT_DIR)
    if not c4_path or not c4_path.is_file():
        print("ERROR: C4 JSON not found. Run scan_blueprint_d_overlap_candidates.py first.")
        sys.exit(1)

    print(f"Loading C4 data from {c4_path} ...")
    with open(c4_path, encoding="utf-8") as f:
        c4 = json.load(f)

    pairs = c4.get("candidates", [])
    print(f"  Total pairs: {len(pairs)}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    records: list[dict] = []
    for i, pair in enumerate(pairs):
        tier, priority = assign_tier(pair, args.min_score_a, args.min_score_b)
        records.append(build_triage_record(pair, tier, priority, i + 1))

    tier_counts = Counter(r["triage_tier"] for r in records)
    priority_counts = Counter(r["second_pass_priority"] for r in records)
    print("  Tier distribution:", dict(tier_counts.most_common()))
    print("  Priority distribution:", dict(priority_counts.most_common()))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write full JSON
    json_path = OUT_DIR / f"BLUEPRINT_D_OVERLAP_TRIAGE_{ts}.json"
    json_payload = {
        "generated_date": ts,
        "generator": "scripts/audit/triage_blueprint_d_overlap_pairs.py",
        "source_c4": c4_path.name,
        "min_score_a": args.min_score_a,
        "min_score_b": args.min_score_b,
        "total_pairs": len(records),
        "tier_summary": dict(tier_counts.most_common()),
        "priority_summary": dict(priority_counts.most_common()),
        "records": records,
    }
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {json_path}")

    # Write second-pass JSONL (TIER_B HIGH + MEDIUM + TIER_A HIGH)
    second_pass = [
        r for r in records
        if (r["triage_tier"] == "TIER_B_SECOND" and r["second_pass_priority"] in ("HIGH", "MEDIUM"))
        or (r["triage_tier"] == "TIER_A_AUTO" and r["second_pass_priority"] == "HIGH")
    ]
    jsonl_path = OUT_DIR / f"SECOND_PASS_QUEUE_{ts}.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in second_pass:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {jsonl_path} ({len(second_pass)} pairs for second pass)")

    # Write MD report
    stats = {
        "total": len(records),
        "min_score_a": args.min_score_a,
        "min_score_b": args.min_score_b,
    }
    md_path = OUT_DIR / f"BLUEPRINT_D_OVERLAP_TRIAGE_{ts}.md"
    write_triage_md(records, ts, stats, md_path)
    print(f"Wrote {md_path}")

    # Summary
    tier_a = [r for r in records if r["triage_tier"] == "TIER_A_AUTO"]
    tier_b = [r for r in records if r["triage_tier"] == "TIER_B_SECOND"]
    tier_c = [r for r in records if r["triage_tier"] == "TIER_C_LOW"]
    both_archived = sum(1 for r in tier_a if r["a_archived"] and r["b_archived"])
    print()
    print(f"TIER_A_AUTO   : {len(tier_a):3d}  (其中两端均已归档: {both_archived}，低紧迫)")
    print(f"TIER_B_SECOND : {len(tier_b):3d}  → {len(second_pass)} 条进入二审队列")
    print(f"TIER_C_LOW    : {len(tier_c):3d}  暂缓")


if __name__ == "__main__":
    main()
