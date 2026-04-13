#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
按目录前缀深度聚合 Git 路径数量，用于整仓治理排期（深度优于仅二级目录）。

默认仅 **git ls-files**（已跟踪）。可选 `--include-untracked` 再并入
`git ls-files --others --exclude-standard`（尊重 `.gitignore`）。

仓库根执行:
  python scripts/governance/export_repo_directory_rollup.py
  python scripts/governance/export_repo_directory_rollup.py --date 20260410
  python scripts/governance/export_repo_directory_rollup.py --include-untracked

输出（默认）:
  docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_<date>.json
  docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_<date>.md
"""

from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

GEN = "scripts/governance/export_repo_directory_rollup.py"


def git_ls_files(repo_root: Path) -> list[str]:
    # core.quotePath=false：避免非 ASCII 路径在输出中被引号+八进制转义，导致 rollup 误分桶
    out = subprocess.check_output(
        ["git", "-c", "core.quotePath=false", "ls-files"],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def git_ls_untracked_not_ignored(repo_root: Path) -> list[str]:
    out = subprocess.check_output(
        ["git", "-c", "core.quotePath=false", "ls-files", "--others", "--exclude-standard"],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def rollup(paths: list[str], depth: int) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for p in paths:
        norm = p.replace("\\", "/")
        parts = norm.split("/")
        if not parts or parts == [""]:
            continue
        d = min(depth, len(parts))
        key = "/".join(parts[:d])
        counts[key] += 1
    return dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))


def md_table(rows: list[tuple[str, int]], max_rows: int) -> str:
    lines = ["| 目录前缀（深度固定） | 路径条数 |", "|---|---:|"]
    for k, c in rows[:max_rows]:
        lines.append(f"| `{k}` | {c} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Git 路径按目录深度聚合（可含未跟踪）")
    parser.add_argument(
        "--date",
        default=date.today().strftime("%Y%m%d"),
        help="输出文件名日期戳（默认今天）",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/09_AUDIT/STATE",
        help="相对仓库根的输出目录",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="Markdown 中每个深度下 docs/ 前缀展示前 N 条",
    )
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="在已跟踪之外追加 git ls-files --others --exclude-standard",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    tracked = git_ls_files(repo_root)
    if args.include_untracked:
        extra = git_ls_untracked_not_ignored(repo_root)
        tracked_set = set(tracked)
        paths = tracked + [p for p in extra if p not in tracked_set]
    else:
        paths = list(tracked)

    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    depths = {str(d): rollup(paths, d) for d in (2, 3, 4, 5, 6)}
    payload = {
        "generated_date": args.date,
        "generator": GEN,
        "include_untracked": args.include_untracked,
        "total_tracked": len(tracked),
        "total_untracked_merged": len(paths) - len(tracked) if args.include_untracked else 0,
        "total_paths": len(paths),
        "depths": depths,
    }
    json_path = out_dir / f"REPO_DIRECTORY_ROLLUP_{args.date}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    def docs_prefix_rows(dep: str) -> list[tuple[str, int]]:
        m = depths[dep]
        return [(k, v) for k, v in m.items() if k.startswith("docs/")]

    scope = (
        f"**已跟踪 {len(tracked)}** + **未跟踪（未 ignore）{payload['total_untracked_merged']}**"
        if args.include_untracked
        else f"**仅已跟踪**，共 **{len(paths)}**"
    )
    md_lines = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: 全仓库路径目录聚合（git ls-files，可选未跟踪）",
        f"generated_date: '{args.date}'",
        "---",
        "",
        f"# 仓库目录深度聚合（路径条数）",
        "",
        f"> 由 `{GEN}` 生成；{scope} 条路径。",
        f"> JSON 真源：[`REPO_DIRECTORY_ROLLUP_{args.date}.json`](./REPO_DIRECTORY_ROLLUP_{args.date}.json)",
        "",
        "## 使用说明",
        "",
        "- **深度 2**：适合一级排期（与任务清单 §1 节选表同量级）。",
        "- **深度 3～6**：把大目录（如 `docs/09_AUDIT`、`docs/05_IMPLEMENTATION`）拆成**可分批啃完的子队列**，支撑「按最深前缀尽治」而不是只扫表面。",
        "- 治理时按前缀从大到小或按业务优先级排序；每一前缀「清空」的标准见 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§7**。",
        "- 未跟踪路径仅在使用 `--include-untracked` 时出现；适合治理「工作区里已存在、尚未 add」的文档。",
        "",
    ]
    for dep in ("3", "4", "5", "6"):
        rows = docs_prefix_rows(dep)
        md_lines.append(f"## `docs/` 下深度 {dep} 前缀 Top {args.top}（按路径条数降序）")
        md_lines.append("")
        md_lines.append(md_table(rows, args.top))
        md_lines.append("")

    md_path = out_dir / f"REPO_DIRECTORY_ROLLUP_{args.date}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote: {json_path.relative_to(repo_root)}")
    print(f"Wrote: {md_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
