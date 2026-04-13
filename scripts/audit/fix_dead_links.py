#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
断链批量修复脚本（F1）：消费 sentinel_l1_governance_scan.py 的 JSON 输出，
对每条无效 Markdown 内链尝试 fuzzy 路径匹配，生成 dry-run 修复方案或移除建议。

策略优先级（每条断链依次尝试，首次命中即停）：
  1. 同目录同名文件（大小写差异）
  2. 同目录 basename 搜索（移动过但留在同级）
  3. 从仓库全局 basename 索引搜索（文件被迁移到其他目录）
  4. 父级/子级相对路径重算（../变更）
  5. 无法自动修复 → 标记 REMOVE_LINK

模式：
  --dry-run (默认)  只生成方案报告（JSON + Markdown），不修改任何文件
  --apply           实际写入修复（需先 dry-run 确认）
  --prefix <path>   仅处理 source 在指定前缀下的断链（分批执行）
  --skip-backup     跳过 .audit_fix_backup 内的断链
  --skip-archive    跳过 docs/06_ARCHIVE + docs/09_ARCHIVE 内的断链

仓库根执行:
  python scripts/audit/fix_dead_links.py --dry-run
  python scripts/audit/fix_dead_links.py --dry-run --prefix docs/09_AUDIT/REPORTS
  python scripts/audit/fix_dead_links.py --apply --prefix docs/05_IMPLEMENTATION
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
L1_JSON = REPO / "docs" / "09_AUDIT" / "STATE" / "SENTINEL_L1_SCAN_20260408.json"
OUT_DIR = REPO / "docs" / "09_AUDIT" / "STATE"
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


# ---------------------------------------------------------------------------
# Index building
# ---------------------------------------------------------------------------

def build_basename_index(repo: Path) -> dict[str, list[str]]:
    """basename.lower() -> list of repo-relative posix paths."""
    idx: dict[str, list[str]] = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [
            d for d in dirnames
            if d not in {".git", ".venv", ".pytest_cache", "__pycache__", "node_modules"}
        ]
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


def build_full_path_index(repo: Path) -> dict[str, str]:
    """lower(relposix) -> canonical relposix (for case-insensitive match)."""
    idx: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [
            d for d in dirnames
            if d not in {".git", ".venv", ".pytest_cache", "__pycache__", "node_modules"}
        ]
        for fn in filenames:
            full = Path(dirpath) / fn
            try:
                rel = full.relative_to(repo).as_posix()
            except ValueError:
                continue
            idx[rel.lower()] = rel
    return idx


# ---------------------------------------------------------------------------
# Resolution strategies
# ---------------------------------------------------------------------------

def resolve_url_to_target(source_rel: str, url: str) -> str:
    """Given source file relpath and the broken url, compute the intended target relpath."""
    url_clean = url.split("#")[0].strip()
    if url_clean.startswith("/"):
        return url_clean.lstrip("/")
    source_dir = str(Path(source_rel).parent)
    if source_dir == ".":
        source_dir = ""
    combined = (Path(source_dir) / url_clean).as_posix()
    parts = []
    for p in combined.split("/"):
        if p == "..":
            if parts:
                parts.pop()
        elif p and p != ".":
            parts.append(p)
    return "/".join(parts)


def strategy_case_insensitive(target_rel: str, full_idx: dict[str, str]) -> str | None:
    """Strategy 1: exact path but different case."""
    return full_idx.get(target_rel.lower())


NAV_BASENAMES = {"index.md", "readme.md"}

def strategy_same_dir_basename(source_rel: str, url: str, basename_idx: dict[str, list[str]]) -> str | None:
    """Strategy 2: same basename in the same directory as source.
    Excludes navigation files (INDEX.md, README.md) which exist in almost every directory."""
    bn = Path(url.split("#")[0].strip()).name.lower()
    if not bn or bn in NAV_BASENAMES:
        return None
    candidates = basename_idx.get(bn, [])
    source_dir = Path(source_rel).parent.as_posix()
    for c in candidates:
        if Path(c).parent.as_posix() == source_dir:
            return c
    return None


def strategy_global_basename_unique(url: str, basename_idx: dict[str, list[str]]) -> str | None:
    """Strategy 3: if the basename exists exactly once in the repo, it's unambiguous."""
    bn = Path(url.split("#")[0].strip()).name.lower()
    if not bn:
        return None
    candidates = basename_idx.get(bn, [])
    if len(candidates) == 1:
        return candidates[0]
    return None


def strategy_global_basename_closest(
    source_rel: str, url: str, basename_idx: dict[str, list[str]]
) -> str | None:
    """Strategy 4: among multiple basename matches, pick the one with shortest path distance."""
    bn = Path(url.split("#")[0].strip()).name.lower()
    if not bn:
        return None
    candidates = basename_idx.get(bn, [])
    if len(candidates) < 2:
        return None

    source_parts = Path(source_rel).parts
    best: str | None = None
    best_score = 999

    for c in candidates:
        c_parts = Path(c).parts
        common = 0
        for s, t in zip(source_parts, c_parts):
            if s == t:
                common += 1
            else:
                break
        distance = (len(source_parts) - common) + (len(c_parts) - common)
        if distance < best_score:
            best_score = distance
            best = c
    return best


def strategy_directory_guided_nav(
    source_rel: str, url: str, basename_idx: dict[str, list[str]]
) -> str | None:
    """Strategy for nav files (INDEX.md/README.md): use directory components from the
    broken URL to find the correct target among hundreds of same-named files.
    e.g., URL '10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md' from docs/01_FRAMEWORK/
    should match docs/10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md."""
    url_clean = url.split("#")[0].strip()
    bn = Path(url_clean).name.lower()
    if bn not in NAV_BASENAMES:
        return None
    url_dir_parts = [p.lower() for p in Path(url_clean).parent.parts if p not in (".", "..")]
    if not url_dir_parts:
        return None
    candidates = basename_idx.get(bn, [])
    if not candidates:
        return None

    scored: list[tuple[int, str]] = []
    for c in candidates:
        c_parts = [p.lower() for p in Path(c).parent.parts]
        match_count = sum(1 for dp in url_dir_parts if dp in c_parts)
        if match_count > 0:
            scored.append((match_count, c))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], len(x[1])))
    if scored[0][0] >= len(url_dir_parts):
        return scored[0][1]
    if scored[0][0] >= 1 and (len(scored) == 1 or scored[0][0] > scored[1][0]):
        return scored[0][1]
    return None


def strategy_kebab_case_fallback(
    source_rel: str, url: str, basename_idx: dict[str, list[str]]
) -> str | None:
    """Strategy 5: UPPER_SNAKE_CASE.md -> kebab-case.md conversion (common after repo naming normalization).
    Also handles 01_FOO -> 01-foo style conversions."""
    bn = Path(url.split("#")[0].strip()).name
    if not bn:
        return None
    stem, ext = os.path.splitext(bn)
    kebab = re.sub(r"_", "-", stem).lower()
    if kebab == stem.lower():
        return None
    kebab_bn = kebab + ext.lower()
    candidates = basename_idx.get(kebab_bn, [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    source_parts = Path(source_rel).parts
    best: str | None = None
    best_score = 999
    for c in candidates:
        c_parts = Path(c).parts
        common = sum(1 for s, t in zip(source_parts, c_parts) if s == t)
        distance = (len(source_parts) - common) + (len(c_parts) - common)
        if distance < best_score:
            best_score = distance
            best = c
    return best


def compute_relative_url(source_rel: str, target_rel: str) -> str:
    """Compute the relative URL from source file to target file."""
    source_dir = Path(source_rel).parent
    target_path = Path(target_rel)
    try:
        rel = os.path.relpath(target_path, source_dir).replace("\\", "/")
    except ValueError:
        return target_rel
    if not rel.startswith("."):
        rel = "./" + rel
    return rel


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

def classify_and_fix(
    items: list[dict],
    basename_idx: dict[str, list[str]],
    full_idx: dict[str, str],
) -> list[dict]:
    """For each broken link, attempt resolution. Returns enriched list."""
    results = []
    for item in items:
        source = item["source"]
        url = item["url"]
        target_rel = resolve_url_to_target(source, url)
        result = {
            "source": source,
            "url": url,
            "resolved_target": target_rel,
            "action": "REMOVE_LINK",
            "strategy": None,
            "new_url": None,
            "confidence": "low",
        }

        # Strategy 1: case-insensitive full path
        match = strategy_case_insensitive(target_rel, full_idx)
        if match:
            new_url = compute_relative_url(source, match)
            frag = ""
            if "#" in url:
                frag = "#" + url.split("#", 1)[1]
            result.update(
                action="REPLACE",
                strategy="case_insensitive_path",
                new_url=new_url + frag,
                confidence="high",
            )
            results.append(result)
            continue

        # Strategy 2: same-dir basename
        match = strategy_same_dir_basename(source, url, basename_idx)
        if match:
            new_url = compute_relative_url(source, match)
            frag = ""
            if "#" in url:
                frag = "#" + url.split("#", 1)[1]
            result.update(
                action="REPLACE",
                strategy="same_dir_basename",
                new_url=new_url + frag,
                confidence="high",
            )
            results.append(result)
            continue

        # Strategy 3: global unique basename
        match = strategy_global_basename_unique(url, basename_idx)
        if match:
            new_url = compute_relative_url(source, match)
            frag = ""
            if "#" in url:
                frag = "#" + url.split("#", 1)[1]
            result.update(
                action="REPLACE",
                strategy="global_unique_basename",
                new_url=new_url + frag,
                confidence="medium",
            )
            results.append(result)
            continue

        # Strategy 3b: directory-guided nav file match (INDEX.md/README.md)
        match = strategy_directory_guided_nav(source, url, basename_idx)
        if match:
            new_url = compute_relative_url(source, match)
            frag = ""
            if "#" in url:
                frag = "#" + url.split("#", 1)[1]
            result.update(
                action="REPLACE",
                strategy="directory_guided_nav",
                new_url=new_url + frag,
                confidence="medium",
            )
            results.append(result)
            continue

        # Strategy 4: global closest basename
        match = strategy_global_basename_closest(source, url, basename_idx)
        if match:
            new_url = compute_relative_url(source, match)
            frag = ""
            if "#" in url:
                frag = "#" + url.split("#", 1)[1]
            result.update(
                action="REPLACE",
                strategy="global_closest_basename",
                new_url=new_url + frag,
                confidence="low",
            )
            results.append(result)
            continue

        # Strategy 5: UPPER_SNAKE_CASE -> kebab-case fallback
        match = strategy_kebab_case_fallback(source, url, basename_idx)
        if match:
            new_url = compute_relative_url(source, match)
            frag = ""
            if "#" in url:
                frag = "#" + url.split("#", 1)[1]
            result.update(
                action="REPLACE",
                strategy="kebab_case_fallback",
                new_url=new_url + frag,
                confidence="medium",
            )
            results.append(result)
            continue

        # No match found
        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Apply fixes
# ---------------------------------------------------------------------------

def apply_fixes(results: list[dict], repo: Path) -> dict[str, int]:
    """Actually modify files. Returns stats.
    NOTE: caller passes pre-filtered list; accept all entries passed in.
    """
    stats = {"replaced": 0, "removed": 0, "skipped": 0, "errors": 0}
    by_source: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r["action"] == "REPLACE":
            by_source[r["source"]].append(r)

    for source_rel, fixes in by_source.items():
        fpath = repo / source_rel
        if not fpath.is_file():
            stats["errors"] += 1
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            stats["errors"] += 1
            continue

        changed = False
        for fix in fixes:
            old_url = fix["url"]
            new_url = fix["new_url"]
            old_pattern = f"]({old_url})"
            new_pattern = f"]({new_url})"
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern, 1)
                changed = True
                stats["replaced"] += 1
            else:
                stats["skipped"] += 1

        if changed:
            try:
                fpath.write_text(content, encoding="utf-8")
            except Exception:
                stats["errors"] += 1

    return stats


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_report(results: list[dict], ts: str, mode: str, out_dir: Path) -> tuple[Path, Path]:
    """Write JSON + Markdown report."""
    from collections import Counter

    action_counts = Counter(r["action"] for r in results)
    strategy_counts = Counter(r["strategy"] for r in results if r["strategy"])
    confidence_counts = Counter(r["confidence"] for r in results if r["action"] == "REPLACE")

    payload = {
        "generated_date": ts,
        "generator": "scripts/audit/fix_dead_links.py",
        "mode": mode,
        "total_broken_links": len(results),
        "action_summary": dict(action_counts.most_common()),
        "strategy_summary": dict(strategy_counts.most_common()),
        "confidence_summary": dict(confidence_counts.most_common()),
        "details": results,
    }

    json_path = out_dir / f"FIX_DEAD_LINKS_{ts[:8]}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "---",
        f"module_id: AUDIT_FIX_DEAD_LINKS_{ts[:8]}",
        "standard_type: audit_state",
        "generated_by: scripts/audit/fix_dead_links.py",
        "---",
        "",
        f"# 断链修复报告（{mode}）",
        "",
        f"> **生成时间**: {ts}",
        f"> **断链总数**: {len(results)}",
        "",
        "## 操作统计",
        "",
        "| 操作 | 数量 |",
        "|------|------|",
    ]
    for action, cnt in action_counts.most_common():
        md_lines.append(f"| {action} | {cnt} |")

    md_lines.extend(["", "## 策略命中分布", "", "| 策略 | 数量 |", "|------|------|"])
    for strat, cnt in strategy_counts.most_common():
        md_lines.append(f"| {strat} | {cnt} |")

    md_lines.extend(["", "## 置信度分布（仅 REPLACE）", "", "| 置信度 | 数量 |", "|--------|------|"])
    for conf, cnt in confidence_counts.most_common():
        md_lines.append(f"| {conf} | {cnt} |")

    # High-confidence replacements
    high_conf = [r for r in results if r["action"] == "REPLACE" and r["confidence"] == "high"]
    md_lines.extend([
        "",
        f"## 高置信修复样本（共 {len(high_conf)} 条，展示前 30）",
        "",
    ])
    for r in high_conf[:30]:
        md_lines.append(f"- `{r['source']}`: `{r['url']}` → `{r['new_url']}` ({r['strategy']})")

    # Low-confidence / REMOVE
    removes = [r for r in results if r["action"] == "REMOVE_LINK"]
    md_lines.extend([
        "",
        f"## 无法自动修复（REMOVE_LINK，共 {len(removes)} 条，展示前 30）",
        "",
    ])
    for r in removes[:30]:
        md_lines.append(f"- `{r['source']}`: `{r['url']}`")

    md_path = out_dir / f"FIX_DEAD_LINKS_{ts[:8]}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return json_path, md_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="断链批量修复脚本（F1）")
    parser.add_argument("--dry-run", action="store_true", default=True, help="只生成方案报告（默认）")
    parser.add_argument("--apply", action="store_true", help="实际写入修复")
    parser.add_argument("--prefix", type=str, default=None, help="仅处理 source 在指定前缀下的断链")
    parser.add_argument("--skip-backup", action="store_true", help="跳过 .audit_fix_backup 内的断链")
    parser.add_argument("--skip-archive", action="store_true", help="跳过 06_ARCHIVE + 09_ARCHIVE 内的断链")
    parser.add_argument("--min-confidence", choices=["high", "medium", "low"], default="medium",
                        help="--apply 时仅修复此置信度以上的链接（默认 medium）")
    parser.add_argument("--l1-json", type=str, default=str(L1_JSON), help="L1 扫描 JSON 路径")
    args = parser.parse_args()

    if args.apply:
        args.dry_run = False

    print(f"Loading L1 data from {args.l1_json} ...")
    with open(args.l1_json, encoding="utf-8") as f:
        l1 = json.load(f)

    items = l1["links"]["invalid_details_sample"]
    print(f"  Total broken links in L1: {len(items)}")

    if args.skip_backup:
        items = [it for it in items if ".audit_fix_backup" not in it["source"]]
        print(f"  After skip-backup: {len(items)}")

    if args.skip_archive:
        items = [
            it for it in items
            if not it["source"].startswith("docs/06_ARCHIVE")
            and not it["source"].startswith("docs/09_ARCHIVE")
        ]
        print(f"  After skip-archive: {len(items)}")

    if args.prefix:
        items = [it for it in items if it["source"].startswith(args.prefix)]
        print(f"  After prefix filter '{args.prefix}': {len(items)}")

    if not items:
        print("No broken links to process after filtering.")
        return

    print("Building file indexes ...")
    basename_idx = build_basename_index(REPO)
    full_idx = build_full_path_index(REPO)
    print(f"  basename index: {len(basename_idx)} entries")
    print(f"  full path index: {len(full_idx)} entries")

    print("Classifying and resolving broken links ...")
    results = classify_and_fix(items, basename_idx, full_idx)

    from collections import Counter
    actions = Counter(r["action"] for r in results)
    print(f"  Results: {dict(actions.most_common())}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    mode = "dry-run" if args.dry_run else "apply"

    if not args.dry_run:
        conf_levels = {"high": 3, "medium": 2, "low": 1}
        min_level = conf_levels[args.min_confidence]
        apply_items = [
            r for r in results
            if r["action"] == "REPLACE"
            and conf_levels.get(r["confidence"], 0) >= min_level
        ]
        print(f"Applying {len(apply_items)} fixes (min_confidence={args.min_confidence}) ...")
        apply_stats = apply_fixes(apply_items, REPO)
        print(f"  Apply stats: {apply_stats}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path, md_path = write_report(results, ts, mode, OUT_DIR)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
