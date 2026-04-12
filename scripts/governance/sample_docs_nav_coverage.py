#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
P3 辅助：从主要导航 Markdown 中抽样检查 docs/ 下 .md 是否「被提到」。

口径（故意宽松、可复跑）：
- 读取若干导航文件全文，合并为小写 blob；
- 若样本路径、去掉 docs/ 后的后缀、最后两段路径、或 basename（长度>6）任一子串出现在 blob 中，则计为「导航中可见」。

不承诺：不等于「必须在某 INDEX 列出」；与 scan_index_health（入链统计）互补。
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from pathlib import Path


DEFAULT_NAV_REL = [
    "docs/INDEX.md",
    "docs/SITEMAP.md",
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md",
    "docs/05_IMPLEMENTATION/SITEMAP.md",
    "docs/09_AUDIT/INDEX.md",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def git_ls_docs_md(root: Path) -> list[str]:
    out = subprocess.check_output(
        ["git", "-c", "core.quotePath=false", "ls-files"],
        text=True,
        cwd=root,
        encoding="utf-8",
        errors="replace",
    )
    return sorted(
        line.strip()
        for line in out.splitlines()
        if line.startswith("docs/") and line.strip().endswith(".md")
    )


def load_nav_blob(root: Path, extra: list[str]) -> tuple[str, list[str]]:
    used: list[str] = []
    parts: list[str] = []
    for rel in DEFAULT_NAV_REL + extra:
        p = root / rel
        if not p.is_file():
            continue
        used.append(rel)
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts).lower(), used


def mentioned_in_nav(path: str, mega: str) -> bool:
    p = path.replace("\\", "/").lower()
    if p in mega:
        return True
    if p.startswith("docs/"):
        tail = p[5:]
        if tail in mega:
            return True
    parts = p.split("/")
    if len(parts) >= 2:
        tail2 = "/".join(parts[-2:])
        if tail2 in mega:
            return True
    base = parts[-1] if parts else ""
    if len(base) > 6 and base in mega:
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Sample docs/*.md nav visibility (P3).")
    ap.add_argument("--sample", type=int, default=200, help="Sample size (capped by population).")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility.")
    ap.add_argument("--date", default="20260410", help="Output filename date tag YYYYMMDD.")
    ap.add_argument(
        "--extra-nav",
        default="",
        help="Comma-separated extra nav paths under repo root (optional).",
    )
    args = ap.parse_args()
    root = repo_root()
    extra = [x.strip() for x in args.extra_nav.split(",") if x.strip()]
    mega, nav_used = load_nav_blob(root, extra)
    if not mega.strip():
        print("No navigation files found; abort.", file=sys.stderr)
        return 1

    all_md = git_ls_docs_md(root)
    if not all_md:
        print("No tracked docs/**/*.md", file=sys.stderr)
        return 1

    n = min(args.sample, len(all_md))
    random.seed(args.seed)
    sample = random.sample(all_md, n)

    hits = [p for p in sample if mentioned_in_nav(p, mega)]
    misses = [p for p in sample if p not in hits]
    rate = len(hits) / n if n else 0.0

    out_dir = root / "docs" / "09_AUDIT" / "STATE"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_md = out_dir / f"DOCS_NAV_COVERAGE_SAMPLE_{args.date}.md"
    lines = [
        "---",
        f"module_id: DOCS_NAV_COVERAGE_SAMPLE_{args.date}",
        "standard_type: audit_state",
        "applicable_scope: REPO_WIDE P3 抽样（导航可见性 · 宽松口径）",
        f"generated_date: '{args.date}'",
        "---",
        "",
        f"# docs/ 导航可见性抽样（n={n}，seed={args.seed}）",
        "",
        "> **方法**：见 `scripts/governance/sample_docs_nav_coverage.py`。",
        "",
        "## 导航源文件",
        "",
        *[f"- `{p}`" for p in nav_used],
        "",
        "## 结果摘要",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| 抽样命中（宽松子串匹配） | {len(hits)} |",
        f"| 抽样未命中 | {len(misses)} |",
        f"| 命中率 | {rate:.1%} |",
        "",
        "## 未命中样本（最多 40 条）",
        "",
        *[f"- `{p}`" for p in misses[:40]],
        "",
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_md}")
    print(f"hit_rate={rate:.3f} hits={len(hits)} misses={len(misses)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
