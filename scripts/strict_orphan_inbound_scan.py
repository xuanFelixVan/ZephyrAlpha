# -*- coding: utf-8 -*-
"""
严格孤儿（入度）扫描：与 Sentinel L1 相同的相对链接解析方式，统计 docs/**/*.md 被链入次数。

- 链入来源：**仓库内全部** `.md`（与日常编辑一致）；**目标**仅统计 `docs/**/*.md` 的入度。
- 排除入口（不计入「孤儿」名单）：文件名 INDEX.md / README.md / SITEMAP.md，
  以及 docs/01_FRAMEWORK/ARCHITECTURE.md、MODULE_RESPONSIBILITY_BOUNDARIES.md、
  BLUEPRINT_ARCHITECTURE_MAPPING.md（与 STRICT_ORPHAN_FILES_REPORT_20260408 口径对齐）。

用法（仓库根目录）：
  python scripts/strict_orphan_inbound_scan.py
  python scripts/strict_orphan_inbound_scan.py --date 20260408

默认输出（**不覆盖**既有 `STRICT_ORPHAN_FILES_LIST_20260408.txt` 基线）：
  docs/09_AUDIT/STATE/STRICT_ORPHAN_FILES_LIST_REGEN_<date>.txt
  docs/09_AUDIT/STATE/STRICT_ORPHAN_FILES_REPORT_REGEN_<date>.md

若需显式覆盖基线文件名：
  python scripts/strict_orphan_inbound_scan.py --date 20260408 --basename STRICT_ORPHAN_FILES_LIST_20260408
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
SKIP_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__"}
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

HUB_BASENAMES = frozenset({"INDEX.md", "README.md", "SITEMAP.md"})
HUB_EXACT = frozenset(
    {
        "docs/01_FRAMEWORK/ARCHITECTURE.md",
        "docs/01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md",
        "docs/01_FRAMEWORK/BLUEPRINT_ARCHITECTURE_MAPPING.md",
    }
)


def iter_docs_md() -> list[Path]:
    out: list[Path] = []
    for p in DOCS.rglob("*.md"):
        if not p.is_file():
            continue
        if any(x in p.parts for x in SKIP_PARTS):
            continue
        out.append(p)
    return sorted(out)


def iter_all_md() -> list[Path]:
    """全仓库 .md（链入来源），与 sentinel_l1 范围一致。"""
    out: list[Path] = []
    for p in REPO.rglob("*.md"):
        if not p.is_file():
            continue
        if any(x in p.parts for x in SKIP_PARTS):
            continue
        out.append(p)
    return sorted(out)


def build_index_merged(all_files: list[Path]) -> dict[str, str]:
    """解析链接时需全仓库路径索引；入度目标仍只认 docs 下 .md。"""
    idx: dict[str, str] = {}
    for p in all_files:
        rel = p.relative_to(REPO).as_posix()
        idx[rel.lower()] = rel
        idx[Path(rel).name.lower()] = rel
    return idx


def resolve_target(source: Path, url: str) -> Path | None:
    u = url.strip()
    if not u or u.startswith(("#", "mailto:", "tel:", "http://", "https://", "file:")):
        return None
    u = u.split("#", 1)[0].strip()
    if not u:
        return None
    if u.startswith("/") and not u.startswith("//"):
        try:
            return (REPO / u.lstrip("/")).resolve()
        except OSError:
            return None
    base = source.parent
    try:
        return (base / u).resolve()
    except OSError:
        return None


def normalize_existing_md(target: Path, idx: dict[str, str]) -> str | None:
    """返回 docs/ 下已存在 .md 的 repo 相对路径，否则 None。"""
    if not target.exists() or not target.is_file():
        try:
            trel = target.relative_to(REPO).as_posix()
        except ValueError:
            return None
        cand = idx.get(trel.lower())
        if cand and (REPO / cand).is_file():
            return cand if cand.startswith("docs/") else None
        return None
    trel = target.relative_to(REPO).as_posix()
    if not trel.startswith("docs/") or not trel.endswith(".md"):
        return None
    return trel


def scan_inbound(link_sources: list[Path], idx: dict[str, str]) -> defaultdict[str, int]:
    inbound: defaultdict[str, int] = defaultdict(int)
    for md in link_sources:
        rel = md.relative_to(REPO).as_posix()
        try:
            lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for line in lines:
            if "](" not in line:
                continue
            for m in LINK_RE.finditer(line):
                url = m.group(2).strip()
                target = resolve_target(md, url)
                if target is None:
                    continue
                trel = normalize_existing_md(target, idx)
                if trel:
                    inbound[trel] += 1
    return inbound


def is_excluded_hub(rel_posix: str) -> bool:
    name = Path(rel_posix).name
    if name in HUB_BASENAMES:
        return True
    if rel_posix in HUB_EXACT:
        return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--date",
        default=datetime.now(timezone.utc).strftime("%Y%m%d"),
        help="输出文件名日期戳（默认 UTC 今日）",
    )
    ap.add_argument(
        "--basename",
        default="",
        help="清单/报告主名前缀（默认 STRICT_ORPHAN_FILES_LIST_REGEN_<date>，避免覆盖人工基线）",
    )
    args = ap.parse_args()
    date_tag: str = args.date

    all_docs = iter_docs_md()
    all_md = iter_all_md()
    idx = build_index_merged(all_md)
    inbound = scan_inbound(all_md, idx)

    orphans: list[str] = []
    for p in all_docs:
        rel = p.relative_to(REPO).as_posix()
        if is_excluded_hub(rel):
            continue
        if inbound.get(rel, 0) == 0:
            orphans.append(rel)

    orphans.sort()
    out_dir = REPO / "docs" / "09_AUDIT" / "STATE"
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.basename.strip():
        stem = args.basename.strip().removesuffix(".txt")
        list_path = out_dir / f"{stem}.txt"
        report_stem = stem.replace("STRICT_ORPHAN_FILES_LIST", "STRICT_ORPHAN_FILES_REPORT", 1)
        report_path = out_dir / f"{report_stem}.md"
    else:
        list_path = out_dir / f"STRICT_ORPHAN_FILES_LIST_REGEN_{date_tag}.txt"
        report_path = out_dir / f"STRICT_ORPHAN_FILES_REPORT_REGEN_{date_tag}.md"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_body = f"""---
module_id: 09_AUDIT_STATE_STRICT_ORPHAN_FILES_REPORT_{date_tag}
version: 1.0.0
status: Active
generated_by: scripts/strict_orphan_inbound_scan.py
---

# 严格孤儿扫描（机器生成）— {date_tag}

> **UTC**: {ts}
> **范围**: 链入来源为**全仓库** `.md`；入度目标为 `docs/**/*.md`；孤儿候选为 docs 内文件
> **孤儿定义**: 入链次数 = 0，且非排除入口（INDEX/README/SITEMAP + 3 个框架枢纽）

## 摘要

| 指标 | 数值 |
|------|------|
| docs 内 .md 总数 | {len(all_docs)} |
| 严格孤儿（去排除后） | {len(orphans)} |

## 纯路径清单

- `{list_path.relative_to(REPO).as_posix()}`（每行一个路径）

## 说明

- 与 `sentinel_l1_governance_scan.py` 使用相同的 `](path)` 解析与相对路径规则。
- **分桶（A/B/C）**需人工在报告后续版本补充，或沿用上一份人工标注的分桶规则。
"""
    list_path.write_text("\n".join(orphans) + ("\n" if orphans else ""), encoding="utf-8")
    report_path.write_text(report_body, encoding="utf-8")
    print(f"Wrote {list_path} ({len(orphans)} orphans)")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
