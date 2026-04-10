#!/usr/bin/env python3
"""
按「文件内容 SHA256」查找重复。

默认仅 **Git 已跟踪**路径；可选 `--include-untracked` 合并
`git ls-files --others --exclude-standard`（仍尊重 `.gitignore`，不含被忽略的未跟踪文件）。

必须显式指定后缀白名单，避免误扫二进制与大文件。默认仅 .md。

仓库根执行示例:
  python scripts/governance/scan_duplicate_file_content.py --ext md
  python scripts/governance/scan_duplicate_file_content.py --ext md --include-untracked
  python scripts/governance/scan_duplicate_file_content.py --ext md --ext yaml --ext yml
  python scripts/governance/scan_duplicate_file_content.py --ext md --max-mb 5 --date 20260410

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

GEN = "scripts/governance/scan_duplicate_file_content.py"


def git_ls_files(repo_root: Path) -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=repo_root, text=True)
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def git_ls_untracked_not_ignored(repo_root: Path) -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=repo_root,
        text=True,
    )
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def normalize_exts(raw: list[str]) -> set[str]:
    out: set[str] = set()
    for x in raw:
        e = x.lower().strip().lstrip(".")
        if e:
            out.add(e)
    return out


def collect_candidates(
    repo_root: Path,
    exts: set[str],
    include_untracked: bool,
) -> list[tuple[str, str]]:
    """(relative_posix_path, git_source) 其中 git_source 为 tracked 或 untracked。"""
    selected: list[tuple[str, str]] = []
    for rel in git_ls_files(repo_root):
        low = rel.lower()
        if any(low.endswith(f".{e}") for e in exts):
            selected.append((rel, "tracked"))
    if include_untracked:
        tracked_set = {p for p, _ in selected}
        for rel in git_ls_untracked_not_ignored(repo_root):
            if rel in tracked_set:
                continue
            low = rel.lower()
            if any(low.endswith(f".{e}") for e in exts):
                selected.append((rel, "untracked"))
    selected.sort(key=lambda x: x[0])
    return selected


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
        description="按内容 hash 找重复（后缀白名单必填，默认 md）；可选纳入未跟踪但未被 ignore 的路径",
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
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="额外纳入 git ls-files --others --exclude-standard 中与 --ext 匹配的路径",
    )
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    parser.add_argument("--out-dir", default="docs/09_AUDIT/STATE")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    exts = normalize_exts(args.ext)
    if not exts:
        print("error: at least one --ext required")
        return 2

    max_bytes = int(args.max_mb * 1024 * 1024) if args.max_mb is not None else None

    out_dir = repo_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = collect_candidates(repo_root, exts, args.include_untracked)
    n_tracked = sum(1 for _, s in candidates if s == "tracked")
    n_untracked = sum(1 for _, s in candidates if s == "untracked")

    hash_to_members: dict[str, list[tuple[str, str]]] = defaultdict(list)
    skipped_large: list[str] = []
    read_errors: list[str] = []

    for rel, source in candidates:
        abs_path = repo_root / Path(rel)
        if not abs_path.is_file():
            read_errors.append(rel)
            continue
        digest = file_sha256(abs_path, max_bytes)
        if digest is None:
            skipped_large.append(rel)
            continue
        hash_to_members[digest].append((rel, source))

    duplicates = {h: members for h, members in hash_to_members.items() if len(members) > 1}
    dup_clusters = sorted(duplicates.items(), key=lambda x: (-len(x[1]), x[1][0][0]))

    cluster_rows: list[dict] = []
    for h, members in dup_clusters:
        members_sorted = sorted(members, key=lambda t: t[0])
        paths = [p for p, _ in members_sorted]
        cluster_rows.append(
            {
                "sha256": h,
                "paths": paths,
                "members": [{"path": p, "git_source": src} for p, src in members_sorted],
                "count": len(members_sorted),
            }
        )

    payload = {
        "generated_date": args.date,
        "generator": GEN,
        "include_untracked": args.include_untracked,
        "extensions": sorted(exts),
        "max_mb": args.max_mb,
        "candidate_count_tracked": n_tracked,
        "candidate_count_untracked": n_untracked,
        "total_candidates_scanned": len(candidates),
        "duplicate_cluster_count": len(duplicates),
        "duplicate_file_path_count": sum(len(m) for m in duplicates.values()),
        "skipped_over_max_mb": skipped_large,
        "read_errors": read_errors,
        "clusters": cluster_rows,
    }

    json_path = out_dir / f"DUPLICATE_CONTENT_BY_HASH_{args.date}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    scope_note = (
        "Git **已跟踪** + `--others --exclude-standard` 未跟踪候选（与 `--ext` 匹配）。"
        if args.include_untracked
        else "仅 **Git 已跟踪**且后缀匹配的文件。"
    )
    md_lines = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: 内容级重复（按后缀白名单）",
        f"generated_date: '{args.date}'",
        f"generated_by: {GEN}",
        "---",
        "",
        "# 内容重复扫描报告（SHA256）",
        "",
        f"> **机器真源**：[`DUPLICATE_CONTENT_BY_HASH_{args.date}.json`](./DUPLICATE_CONTENT_BY_HASH_{args.date}.json)",
        f"> **后缀白名单**：`{', '.join(sorted(exts))}` ｜ **候选**：已跟踪 {n_tracked}"
        + (f" + 未跟踪 {n_untracked}" if args.include_untracked else "")
        + f" ｜ **重复簇数**：{len(duplicates)}",
        "",
        "## 说明",
        "",
        f"- {scope_note}",
        "- 每条路径在 JSON `members[].git_source` 中标注 **tracked** / **untracked**（便于优先处理「该入库却未 add」的重复）。",
        "- **合并/删稿**须按 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§3**（C1）与 [文件删除与保留裁决 Playbook](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/FILE_DELETION_OR_RETENTION_PLAYBOOK.md) 执行，勿仅凭本报告自动删除。",
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
    for i, row in enumerate(cluster_rows[:200], 1):
        h = row["sha256"]
        md_lines.append(f"### 簇 {i} · `{h[:16]}…` · {row['count']} 个路径")
        md_lines.append("")
        for m in row["members"]:
            tag = m["git_source"]
            md_lines.append(f"- `{m['path']}` （{tag}）")
        md_lines.append("")
    if len(cluster_rows) > 200:
        md_lines.append(f"> 仅展示前 200 簇，共 {len(cluster_rows)} 簇，详见 JSON。")
        md_lines.append("")

    md_path = out_dir / f"DUPLICATE_CONTENT_BY_HASH_{args.date}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote: {json_path.relative_to(repo_root)}")
    print(f"Wrote: {md_path.relative_to(repo_root)}")
    print(
        f"extensions={sorted(exts)} include_untracked={args.include_untracked} "
        f"candidates={len(candidates)} duplicate_clusters={len(duplicates)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
