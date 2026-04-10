# -*- coding: utf-8 -*-
"""
索引健全性扫描（只读）：在约定范围内找出「零入链」Markdown 候选（无其他 .md 指向该文件）。

说明：
- **不做**「该文件应出现在哪份 INDEX」的语义裁决；仅基于**已存在的**仓库内相对链接统计入链。
- 与 L1（断链检查）互补：L1 看链是否解析；本脚本看**目标文件是否被任何文挡引用**。
- 入口文件、总门脸常会被报为孤儿，请用 --ignore-path / --ignore-glob 排除。

仓库根执行示例:
  python scripts/governance/scan_index_health.py
  python scripts/governance/scan_index_health.py --prefix docs/05_IMPLEMENTATION/
  python scripts/governance/scan_index_health.py --link-source same-as-candidates --date 20260410

输出:
  docs/09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_<date>.json
  docs/09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_<date>.md
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GEN = "scripts/governance/scan_index_health.py"
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def git_ls_tracked_files(repo: Path) -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=repo)
    return [p.decode("utf-8", errors="replace") for p in raw.split(b"\0") if p]


def normalize_posix(p: str) -> str:
    return p.replace("\\", "/")


def path_excluded(rel: str, exclude_prefixes: list[str], exclude_globs: list[str]) -> bool:
    rel_n = normalize_posix(rel)
    for pre in exclude_prefixes:
        pre_n = normalize_posix(pre).rstrip("/")
        if pre_n and (rel_n == pre_n or rel_n.startswith(pre_n + "/")):
            return True
    for g in exclude_globs:
        if fnmatch.fnmatch(rel_n, g) or fnmatch.fnmatch(rel_n.lower(), g.lower()):
            return True
    return False


def build_lower_index(md_paths: list[str]) -> dict[str, str]:
    """lower(relposix) -> canonical relposix（与 sentinel 思路一致，仅 .md）。"""
    idx: dict[str, str] = {}
    for rel in md_paths:
        idx[rel.lower()] = rel
        idx[Path(rel).name.lower()] = rel
    return idx


def resolve_link_target(repo: Path, source_rel: str, url: str) -> str | None:
    u = url.strip()
    if not u or u.startswith(("#", "mailto:", "tel:", "http://", "https://", "file:")):
        return None
    u = u.split("#", 1)[0].strip()
    if not u:
        return None
    src = repo / source_rel
    if u.startswith("/") and not u.startswith("//"):
        cand = (repo / u.lstrip("/")).resolve()
    else:
        try:
            cand = (src.parent / u).resolve()
        except OSError:
            return None
    try:
        trel = cand.relative_to(repo).as_posix()
    except ValueError:
        return None
    if not trel.endswith(".md"):
        return None
    if not cand.is_file():
        # 尝试通过 lower 索引对齐大小写
        return trel
    return trel


def canonical_md_target(repo: Path, trel: str, lower_idx: dict[str, str]) -> str | None:
    """返回存在的 .md 的规范相对路径，否则 None。"""
    p = repo / trel
    if p.is_file():
        return trel
    c = lower_idx.get(trel.lower())
    if c and (repo / c).is_file():
        return c
    return None


def collect_links(
    repo: Path,
    source_rels: list[str],
    lower_idx: dict[str, str],
) -> dict[str, set[str]]:
    """target_rel -> set of source_rel that link to it (excluding self-reference)."""
    inbound: dict[str, set[str]] = defaultdict(set)
    for srel in source_rels:
        spath = repo / srel
        try:
            lines = spath.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            if "](" not in line:
                continue
            for m in LINK_RE.finditer(line):
                url = m.group(2).strip()
                trel_raw = resolve_link_target(repo, srel, url)
                if not trel_raw:
                    continue
                canon = canonical_md_target(repo, trel_raw, lower_idx)
                if not canon:
                    continue
                if canon == normalize_posix(srel):
                    continue
                inbound[canon].add(normalize_posix(srel))
    return inbound


def default_exclude_prefixes() -> list[str]:
    return [
        "docs/06_ARCHIVE/",
        "docs/09_ARCHIVE/",
        "docs/09_AUDIT/STATE/overnight_runs/",
    ]


def default_ignore_paths() -> list[str]:
    """常见门脸：无「其他 md 入链」属正常。"""
    return [
        "README.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "docs/INDEX.md",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="索引健全性：统计 md 入链，报告零入链候选（可配置范围与排除）",
    )
    parser.add_argument(
        "--prefix",
        action="append",
        default=[],
        help="候选文件须在此路径前缀下（可多次）；默认 docs/",
    )
    parser.add_argument(
        "--link-source",
        choices=("all-tracked", "same-as-candidates"),
        default="all-tracked",
        help="解析哪些文件里的链接作为入链来源；默认全库已跟踪 md",
    )
    parser.add_argument(
        "--exclude-prefix",
        action="append",
        default=[],
        help="候选与（默认）来源均排除此前缀（可多次）；内置仍含 archive 等",
    )
    parser.add_argument(
        "--exclude-glob",
        action="append",
        default=[],
        help="对相对路径作 fnmatch 排除（可多次），如 '**/TEMP_*.md'",
    )
    parser.add_argument(
        "--ignore-path",
        action="append",
        default=[],
        help="零入链报告中强制忽略的路径（相对仓库根）；默认含 README.md、docs/INDEX.md 等",
    )
    parser.add_argument(
        "--ignore-glob",
        action="append",
        default=[],
        help="零入链报告中 fnmatch 忽略（可多次）",
    )
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    parser.add_argument("--out-dir", default="docs/09_AUDIT/STATE")
    parser.add_argument(
        "--max-list",
        type=int,
        default=400,
        help="Markdown 报告中列出零入链路径条数上限",
    )
    args = parser.parse_args()

    candidate_prefixes = args.prefix if args.prefix else ["docs/"]
    exclude_prefixes = default_exclude_prefixes() + list(args.exclude_prefix)
    ignore_paths = set(normalize_posix(p) for p in (default_ignore_paths() + args.ignore_path))
    ignore_globs = list(args.ignore_glob)

    all_tracked = git_ls_tracked_files(REPO)
    md_all = [normalize_posix(p) for p in all_tracked if p.lower().endswith(".md")]

    def is_candidate(rel: str) -> bool:
        r = normalize_posix(rel)
        ok_pre = False
        for pre in candidate_prefixes:
            pn = normalize_posix(pre).rstrip("/")
            if r == pn or r.startswith(pn + "/"):
                ok_pre = True
                break
        if not ok_pre:
            return False
        if path_excluded(r, exclude_prefixes, args.exclude_glob):
            return False
        return True

    candidates = sorted([r for r in md_all if is_candidate(r)])
    if args.link_source == "same-as-candidates":
        link_sources = list(candidates)
    else:
        link_sources = [
            r
            for r in md_all
            if not path_excluded(r, exclude_prefixes, args.exclude_glob)
        ]

    lower_idx = build_lower_index(md_all)
    inbound = collect_links(REPO, link_sources, lower_idx)

    zero_inbound: list[str] = []
    for rel in candidates:
        if rel in ignore_paths:
            continue
        if any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel.lower(), g.lower()) for g in ignore_globs):
            continue
        if len(inbound.get(rel, set())) == 0:
            zero_inbound.append(rel)

    payload = {
        "generated_date": args.date,
        "generator": GEN,
        "candidate_prefixes": [normalize_posix(p) for p in candidate_prefixes],
        "link_source": args.link_source,
        "exclude_prefixes": [normalize_posix(p) for p in exclude_prefixes],
        "ignore_paths_default_plus_cli": sorted(ignore_paths),
        "candidate_md_count": len(candidates),
        "link_source_md_count": len(link_sources),
        "zero_inbound_count": len(zero_inbound),
        "zero_inbound_paths": zero_inbound,
        "notes": [
            "入链仅统计仓库内 .md 文件正文中的 Markdown 相对链接；不含 HTML <a>、wiki 链、代码块内路径。",
            "门脸文件默认已 ignore；其余零入链需人工判断是否应被某 INDEX/SITEMAP 引用。",
        ],
    }

    out_dir = REPO / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"INDEX_HEALTH_ORPHAN_{args.date}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md_lines = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: 索引健全性（零入链候选 · 路径级）",
        f"generated_date: '{args.date}'",
        f"generated_by: {GEN}",
        "---",
        "",
        "# 索引健全性扫描报告（零入链候选）",
        "",
        f"> **机器真源**：[`INDEX_HEALTH_ORPHAN_{args.date}.json`](./INDEX_HEALTH_ORPHAN_{args.date}.json)",
        f"> **候选范围**：`{', '.join(normalize_posix(p) for p in candidate_prefixes)}` ｜ **候选 md 数**：{len(candidates)} ｜ **入链来源**：{args.link_source}（{len(link_sources)} 个 md）",
        f"> **零入链（已应用 ignore 后）**：**{len(zero_inbound)}**",
        "",
        "## 说明",
        "",
        "- **零入链** = 无**其他**已跟踪 `.md` 通过正文 Markdown 相对链接指向该文件（不含自身、不含 http(s)）。",
        "- **不等于**应删除；常见于待挂链的新稿、仅被代码或非 md 引用、或应从父级 `INDEX.md` 补链。",
        "- 与 [文档地图与放置规则](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§5** 一致：本报告为**健全性信号**，裁决仍须人工 + 域规则。",
        "",
        "## 零入链路径（节选）",
        "",
    ]
    for p in zero_inbound[: args.max_list]:
        md_lines.append(f"- `{p}`")
    if len(zero_inbound) > args.max_list:
        md_lines.append("")
        md_lines.append(f"> 仅列出前 {args.max_list} 条，共 {len(zero_inbound)} 条，详见 JSON。")
    md_lines.append("")

    md_path = out_dir / f"INDEX_HEALTH_ORPHAN_{args.date}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote: {json_path.relative_to(REPO)}")
    print(f"Wrote: {md_path.relative_to(REPO)}")
    print(
        f"candidates={len(candidates)} link_sources={len(link_sources)} "
        f"zero_inbound={len(zero_inbound)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
