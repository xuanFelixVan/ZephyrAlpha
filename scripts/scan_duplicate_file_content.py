#!/usr/bin/env python3
"""
按「文件内容 SHA256」查找重复（仅处理 Git 已跟踪文件）。

必须显式指定后缀白名单，避免误扫二进制与大文件。默认仅 .md。

仓库根执行示例:
  python scripts/scan_duplicate_file_content.py --ext md
  python scripts/scan_duplicate_file_content.py --ext md --ext yaml --ext yml
  python scripts/scan_duplicate_file_content.py --ext md --max-mb 5 --date 20260410

输出:
  docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_<date>.json
  docs/09_AUDIT/STATE/DUPLICATE_CONTENT_BY_HASH_<date>.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path


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


def file_sha256(path: Path, max_bytes: int | None) -> str | None:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            n += len(chunk)
            if max_bytes is not None and n > max_bytes:
                return None
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Git 已跟踪文件中，按内容 hash 找重复（后缀白名单必填，默认 md）",
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        default=["md"],
        help="扩展名（可多个），不含点，例如: md yaml yml json",
    )
    parser.add_argument(
        "--max-mb",
        type=float,
        default=None,
        help="单文件超过此大小（MiB）则跳过内容 hash，避免大文件占内存",
    )
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    parser.add_argument("--out-dir", default="docs/09_AUDIT/STATE")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    exts = normalize_exts(args.ext)
    if not exts:
        print("error: at least one --ext required")
        return 2

    max_bytes = int(args.max_mb * 1024 * 1024) if args.max_mb is not None else None

    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = git_ls_files(repo_root)
    selected: list[str] = []
    for p in paths:
        low = p.lower()
        for e in exts:
            if low.endswith(f".{e}"):
                selected.append(p)
                break

    hash_to_paths: dict[str, list[str]] = defaultdict(list)
    skipped_large: list[str] = []
    read_errors: list[str] = []

    for rel in sorted(selected):
        abs_path = repo_root / Path(rel)
        if not abs_path.is_file():
            read_errors.append(rel)
            continue
        digest = file_sha256(abs_path, max_bytes)
        if digest is None:
            skipped_large.append(rel)
            continue
        hash_to_paths[digest].append(rel)

    duplicates = {h: ps for h, ps in hash_to_paths.items() if len(ps) > 1}
    dup_clusters = sorted(duplicates.items(), key=lambda x: (-len(x[1]), x[1][0]))

    payload = {
        "generated_date": args.date,
        "generator": "scripts/scan_duplicate_file_content.py",
        "extensions": sorted(exts),
        "max_mb": args.max_mb,
        "total_tracked_scanned_candidates": len(selected),
        "duplicate_cluster_count": len(duplicates),
        "duplicate_file_path_count": sum(len(ps) for ps in duplicates.values()),
        "skipped_over_max_mb": skipped_large,
        "read_errors": read_errors,
        "clusters": [
            {"sha256": h, "paths": sorted(ps), "count": len(ps)} for h, ps in dup_clusters
        ],
    }

    json_path = out_dir / f"DUPLICATE_CONTENT_BY_HASH_{args.date}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md_lines = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: 内容级重复（按后缀白名单）",
        f"generated_date: '{args.date}'",
        "generated_by: scripts/scan_duplicate_file_content.py",
        "---",
        "",
        "# 内容重复扫描报告（SHA256）",
        "",
        f"> **机器真源**：[`DUPLICATE_CONTENT_BY_HASH_{args.date}.json`](./DUPLICATE_CONTENT_BY_HASH_{args.date}.json)",
        f"> **后缀白名单**：`{', '.join(sorted(exts))}` ｜ **已跟踪候选数**：{len(selected)} ｜ **重复簇数**：{len(duplicates)}",
        "",
        "## 说明",
        "",
        "- 仅包含 **Git 已跟踪**且后缀匹配的文件。",
        "- **合并/删稿**须按 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3**（C1）执行，勿仅凭本报告自动删除。",
        "",
    ]
    if skipped_large:
        md_lines.append("## 跳过大文件（未计 hash）")
        md_lines.append("")
        for s in skipped_large[:50]:
            md_lines.append(f"- `{s}`")
        if len(skipped_large) > 50:
            md_lines.append(f"- … 共 {len(skipped_large)} 条，见 JSON")
        md_lines.append("")
    if read_errors:
        md_lines.append("## 读盘失败（路径不在工作区或非文件）")
        md_lines.append("")
        for s in read_errors:
            md_lines.append(f"- `{s}`")
        md_lines.append("")

    md_lines.extend(
        [
            "## 重复簇（仅 count>1）",
            "",
        ]
    )
    for i, (h, ps) in enumerate(dup_clusters[:200], 1):
        md_lines.append(f"### 簇 {i} · `{h[:16]}…` · {len(ps)} 个路径")
        md_lines.append("")
        for p in ps:
            md_lines.append(f"- `{p}`")
        md_lines.append("")
    if len(dup_clusters) > 200:
        md_lines.append(f"> 仅展示前 200 簇，共 {len(dup_clusters)} 簇，详见 JSON。")
        md_lines.append("")

    md_path = out_dir / f"DUPLICATE_CONTENT_BY_HASH_{args.date}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote: {json_path.relative_to(repo_root)}")
    print(f"Wrote: {md_path.relative_to(repo_root)}")
    print(f"extensions={sorted(exts)} candidates={len(selected)} duplicate_clusters={len(duplicates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
