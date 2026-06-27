"""一次性批量提交助手——读取文件清单调用 GitCommitGateway。

用法:
  python docs/_working/_commit_batch.py --session <id> --message <msg> --list-file <path> [--allow-promote]

文件清单格式: 每行一个相对/绝对路径，#开头注释，空行跳过。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.git_commit_gateway import GitCommitGateway  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--list-file", required=True)
    parser.add_argument("--allow-promote", action="store_true")
    args = parser.parse_args()

    files: list[str] = []
    with open(args.list_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            files.append(os.path.abspath(line))

    if not files:
        print("[ERR] empty file list", file=sys.stderr)
        return 1

    print(f"[INFO] submitting {len(files)} files via GitCommitGateway...")
    gw = GitCommitGateway(project_root=str(_PROJECT_ROOT))
    result = gw.commit(
        session_id=args.session,
        files=files,
        message=args.message,
        allow_promote=args.allow_promote,
    )
    print(f"[RESULT] status={result.status} message={result.message}")
    if result.commit_hash:
        print(f"[HASH] {result.commit_hash}")
    return 0 if str(result.status) == "CommitStatus.SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())
