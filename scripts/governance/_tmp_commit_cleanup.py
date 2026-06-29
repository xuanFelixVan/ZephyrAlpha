# -*- coding: utf-8 -*-
"""提交 L1 reconciler 清理变更 + 迁移脚本（排除永久区新文件）。执行后删除。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.git_commit_gateway import CommitStatus, GitCommitGateway

SESSION_ID = "l1_reconciler_cleanup"
PERMANENT_PREFIXES = (
    "docs/01_policies_and_standards/",
    "docs/02_enterprise_architecture/",
    "docs/03_modules/",
    "docs/08_knowledge/",
)

def main():
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(_PROJECT_ROOT),
    )
    files = []
    skipped = []
    for line in result.stdout.splitlines():
        line = line.rstrip()
        if not line:
            continue
        status_code = line[:2]
        filepath = line[3:]
        # 跳过 data/ 目录
        if filepath.startswith("data/"):
            continue
        # 永久区新文件（?? 或 A）需 --allow-promote，AI 不可自批准
        is_new = status_code in ("??", "A ", "AM")
        if is_new and filepath.startswith(PERMANENT_PREFIXES):
            skipped.append(filepath)
            continue
        abs_f = str(_PROJECT_ROOT / filepath)
        # 对于删除的文件（已跟踪但工作区不存在），也加入提交
        if os.path.isfile(abs_f) or _is_tracked(filepath):
            files.append(abs_f)

    print(f"提交文件数: {len(files)}, 跳过永久区新文件: {len(skipped)}")
    for s in skipped:
        print(f"  SKIP: {s}")

    if not files:
        print("无文件可提交")
        return 0

    gw = GitCommitGateway(project_root=str(_PROJECT_ROOT))
    claimed = gw.claim_files(SESSION_ID, files)
    try:
        result = gw.commit(
            session_id=SESSION_ID,
            files=files,
            message="L1 reconciler清理+迁移脚本入库\n\n"
                    "- 删除 95 个 docs/_working/ 过期工作文档(reconciler清理)\n"
                    "- 新增 migrate_domain_id_hyphen_to_underscore.py 迁移脚本\n"
                    "- 新增 check_directory_contract.py\n"
                    "- 5 个永久区新文件(vocabulary/contract)待用户 --allow-promote 批准",
        )
    finally:
        gw.release_files(SESSION_ID, claimed)

    if result.status == CommitStatus.OK:
        print(f"OK: {result.message} (hash={result.commit_hash[:8]})")
        return 0
    else:
        print(f"FAIL [{result.status}]: {result.message}", file=sys.stderr)
        return 2

def _is_tracked(filepath):
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", filepath],
        capture_output=True, cwd=str(_PROJECT_ROOT),
    )
    return r.returncode == 0

if __name__ == "__main__":
    sys.exit(main())
