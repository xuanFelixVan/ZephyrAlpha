#!/usr/bin/env python3
"""
按目录前缀深度聚合 git 已跟踪文件数量，用于整仓治理排期（深度优于仅二级目录）。

仓库根执行:
  python scripts/export_repo_directory_rollup.py
  python scripts/export_repo_directory_rollup.py --date 20260410

输出（默认）:
  docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_<date>.json
  docs/09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_<date>.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path


def git_ls_files(repo_root: Path) -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files"],
        cwd=repo_root,
        text=True,
    )
    return [ln for ln in out.splitlines() if ln.strip()]


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
    lines = ["| 目录前缀（深度固定） | 已跟踪文件数 |", "|---|---:|"]
    for k, c in rows[:max_rows]:
        lines.append(f"| `{k}` | {c} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Git 跟踪路径按目录深度聚合")
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
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    paths = git_ls_files(repo_root)
    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    depths = {str(d): rollup(paths, d) for d in (2, 3, 4, 5, 6)}
    payload = {
        "generated_date": args.date,
        "total_tracked": len(paths),
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

    md_lines = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: 全仓库已跟踪路径目录聚合",
        f"generated_date: '{args.date}'",
        "---",
        "",
        f"# 仓库目录深度聚合（已跟踪文件数）",
        "",
        f"> 由 `scripts/export_repo_directory_rollup.py` 生成；**总计 {len(paths)}** 个已跟踪路径。",
        f"> JSON 真源：[`REPO_DIRECTORY_ROLLUP_{args.date}.json`](./REPO_DIRECTORY_ROLLUP_{args.date}.json)",
        "",
        "## 使用说明",
        "",
        "- **深度 2**：适合一级排期（与任务清单 §1 节选表同量级）。",
        "- **深度 3～6**：把大目录（如 `docs/09_AUDIT`、`docs/05_IMPLEMENTATION`）拆成**可分批啃完的子队列**，支撑「按最深前缀尽治」而不是只扫表面。",
        "- 治理时按前缀从大到小或按业务优先级排序；每一前缀「清空」的标准见 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§7**。",
        "",
    ]
    for dep in ("3", "4", "5", "6"):
        rows = docs_prefix_rows(dep)
        md_lines.append(f"## `docs/` 下深度 {dep} 前缀 Top {args.top}（按文件数降序）")
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
