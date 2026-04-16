#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trace_file_provenance.py — 查询文件在 git 中的搬迁/重命名历史（File Provenance）

用法:
  python scripts/governance/trace_file_provenance.py <相对仓库根的路径>
  python scripts/governance/trace_file_provenance.py docs/01_FRAMEWORK/foo.md

说明:
  封装 `git log --follow`，供搬迁前置检查（File Movement Protocol）使用。
  退出码: 0 成功；1 参数错误；2 git 命令失败。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path | None:
    cur = start.resolve()
    for _ in range(20):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="查询文件在 git 中的搬迁/重命名历史（git log --follow）"
    )
    parser.add_argument(
        "path",
        type=str,
        help="相对仓库根的路径，例如 docs/02_ARCHITECTURE/MODULE_INVENTORY.md",
    )
    parser.add_argument(
        "--rename-only",
        action="store_true",
        help="仅显示重命名类提交（--diff-filter=R），与 File Movement Protocol Step 1 一致",
    )
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = find_repo_root(script_path.parent)
    if not repo_root:
        print("错误: 未找到仓库根目录（缺少 .git）", file=sys.stderr)
        return 2

    rel = args.path.replace("\\", "/").strip()
    if rel.startswith("/"):
        print("错误: 请使用相对仓库根的路径，不要以 / 开头", file=sys.stderr)
        return 1

    target = repo_root / rel
    if not target.exists():
        print(f"提示: 工作区中不存在该路径: {rel}（仍可查询 git 历史中的旧路径）\n")

    cmd = [
        "git",
        "-C",
        str(repo_root),
        "log",
        "--follow",
        "--name-status",
        "--oneline",
    ]
    if args.rename_only:
        cmd.insert(cmd.index("--follow") + 1, "--diff-filter=R")
    cmd.extend(["--", rel])

    print("命令:", " ".join(cmd))
    print("-" * 72)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"错误: 无法执行 git: {e}", file=sys.stderr)
        return 2

    sys.stdout.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    if r.returncode != 0 and not r.stdout.strip():
        print(f"git 退出码: {r.returncode}", file=sys.stderr)
        return 2

    # 统计重命名行（git name-status: R100\told\tnew）
    rename_lines = [
        ln for ln in r.stdout.splitlines()
        if ln.split("\t", 1)[0].startswith("R")
    ]
    if args.rename_only:
        print("-" * 72)
        print(f"重命名相关输出行数: {len(rename_lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
