#!/usr/bin/env python3
"""
按「文件名 basename」查找 Git 已跟踪路径中的同名不同路径（C2 输入）。

默认仅统计 `docs/` 下、后缀白名单匹配的路径（与整仓文档治理口径一致）；
可选 `--all-repo` 扫全库已跟踪路径。

仓库根执行示例:
  python scripts/governance/scan_basename_collisions.py --ext md --date 20260411
  python scripts/governance/scan_basename_collisions.py --ext md --all-repo
  python scripts/governance/scan_basename_collisions.py --ext md --include-nav-names

输出:
  docs/09_AUDIT/STATE/BASENAME_COLLISIONS_<date>.json
  docs/09_AUDIT/STATE/BASENAME_COLLISIONS_<date>.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

GEN = "scripts/governance/scan_basename_collisions.py"

# 预期在多个目录重复出现的导航名；默认 MD 正文拆表展示，避免淹没「意外同名」
DEFAULT_NAV_NAMES = frozenset(
    {
        "index.md",
        "readme.md",
        "sitemap.md",
        "changelog.md",
        "license.md",
        "contributing.md",
    }
)


def git_ls_files(repo_root: Path) -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=repo_root, text=True)
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def normalize_exts(raw: list[str]) -> set[str]:
    out: set[str] = set()
    for x in raw:
        e = x.lower().strip().lstrip(".")
        if e:
            out.add(e)
    return out


def collect_paths(
    repo_root: Path,
    exts: set[str],
    prefix: str | None,
) -> list[str]:
    selected: list[str] = []
    pre = (prefix or "").replace("\\", "/")
    if pre and not pre.endswith("/"):
        pre += "/"
    for rel in git_ls_files(repo_root):
        if pre and not rel.startswith(pre):
            continue
        low = rel.lower()
        if not any(low.endswith(f".{e}") for e in exts):
            continue
        selected.append(rel)
    selected.sort()
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="按 basename 找同名不同路径（C2 报表）；默认 docs/ + 后缀白名单",
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        default=["md"],
        help="扩展名（可多个），不含点",
    )
    parser.add_argument(
        "--prefix",
        default="docs/",
        help="仅包含该路径前缀（POSIX）；空字符串表示不限。默认 docs/",
    )
    parser.add_argument(
        "--all-repo",
        action="store_true",
        help="忽略 --prefix，扫描仓库内所有已跟踪且后缀匹配的路径",
    )
    parser.add_argument(
        "--include-nav-names",
        action="store_true",
        help="在 MD「意外同名」一节也展开 INDEX/README 等导航名（默认仅统计表）",
    )
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    parser.add_argument("--out-dir", default="docs/09_AUDIT/STATE")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    exts = normalize_exts(args.ext)
    if not exts:
        print("error: at least one --ext required")
        return 2

    prefix = None if args.all_repo else args.prefix
    paths = collect_paths(repo_root, exts, prefix)

    base_to_paths: dict[str, list[str]] = defaultdict(list)
    for rel in paths:
        b = os.path.basename(rel)
        base_to_paths[b].append(rel)

    collisions = {b: ps for b, ps in base_to_paths.items() if len(ps) > 1}
    clusters = sorted(collisions.items(), key=lambda x: (-len(x[1]), x[0].lower()))

    nav_collisions = [(b, ps) for b, ps in clusters if b.lower() in DEFAULT_NAV_NAMES]
    other_collisions = [(b, ps) for b, ps in clusters if b.lower() not in DEFAULT_NAV_NAMES]

    payload = {
        "generated_date": args.date,
        "generator": GEN,
        "prefix_filter": prefix if prefix else "(all tracked)",
        "extensions": sorted(exts),
        "path_count": len(paths),
        "basename_collision_count": len(collisions),
        "collision_path_total": sum(len(ps) for _, ps in clusters),
        "nav_name_collision_basenames": len(nav_collisions),
        "non_nav_collision_basenames": len(other_collisions),
        "clusters": [
            {"basename": b, "count": len(ps), "paths": sorted(ps)} for b, ps in clusters
        ],
    }

    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"BASENAME_COLLISIONS_{args.date}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    rel_json = f"./BASENAME_COLLISIONS_{args.date}.json"
    md_lines = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: 同名不同路径（basename · C2 输入）",
        f"generated_date: '{args.date}'",
        f"generated_by: {GEN}",
        "---",
        "",
        "# Basename 碰撞报表（同名不同路径）",
        "",
        f"> **机器真源**：[`BASENAME_COLLISIONS_{args.date}.json`]({rel_json})",
        f"> **范围**：{payload['prefix_filter']} ｜ **后缀**：`{', '.join(sorted(exts))}`",
        f"> **候选路径数**：{len(paths)} ｜ **发生碰撞的 basename 数**：{len(collisions)}",
        "",
        "## 说明",
        "",
        "- 与 **C1（内容 hash 相同）** 不同：basename 相同**不**表示正文相同，**禁止自动合并**；处置见 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3.3**。",
        "- 下列 **`INDEX.md` / `README.md` 等**在机构式文档树中**常**多份并存；默认单独统计，避免与「意外同名」混淆。",
        "",
        "## 摘要",
        "",
        f"| 类别 | basename 数 |",
        f"|------|------------:|",
        f"| 非导航名（优先人工审） | {len(other_collisions)} |",
        f"| 导航名（`{', '.join(sorted(DEFAULT_NAV_NAMES))}`） | {len(nav_collisions)} |",
        "",
        "## 非导航名碰撞（逐条展开）",
        "",
    ]

    if not other_collisions:
        md_lines.append("*（无 — 当前前缀与后缀下，除导航名外无 basename 碰撞。）*")
        md_lines.append("")
    else:
        for b, ps in other_collisions:
            md_lines.append(f"### `{b}` · {len(ps)} 条路径")
            md_lines.append("")
            for p in sorted(ps):
                md_lines.append(f"- `{p}`")
            md_lines.append("")

    md_lines.extend(
        [
            "## 导航名碰撞（统计表）",
            "",
            "| basename | 路径条数 |",
            "|----------|----------:|",
        ]
    )
    for b, ps in sorted(nav_collisions, key=lambda x: (-len(x[1]), x[0].lower())):
        md_lines.append(f"| `{b}` | {len(ps)} |")
    if not nav_collisions:
        md_lines.append("| — | 0 |")
    md_lines.append("")

    if args.include_nav_names and nav_collisions:
        md_lines.append("## 导航名碰撞（逐条展开，由 `--include-nav-names` 开启）")
        md_lines.append("")
        for b, ps in nav_collisions:
            md_lines.append(f"### `{b}` · {len(ps)} 条路径")
            md_lines.append("")
            for p in sorted(ps):
                md_lines.append(f"- `{p}`")
            md_lines.append("")

    md_path = out_dir / f"BASENAME_COLLISIONS_{args.date}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote: {json_path.relative_to(repo_root)}")
    print(f"Wrote: {md_path.relative_to(repo_root)}")
    print(
        f"prefix={payload['prefix_filter']} ext={sorted(exts)} "
        f"paths={len(paths)} collision_basenames={len(collisions)} "
        f"non_nav={len(other_collisions)} nav={len(nav_collisions)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
