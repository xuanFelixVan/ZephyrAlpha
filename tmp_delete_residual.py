"""一次性脚本：通过 session_worktree 删除残留文件 一键备份.ps1。"""
import sys
from pathlib import Path

ROOT = Path(r"d:\ZephyrAlpha")
sys.path.insert(0, str(ROOT / "src"))

from zephyr.gov_enforcement.rule_bridge.session_worktree import (
    session_worktree_start,
    session_worktree_commit,
    session_worktree_merge,
    generate_session_id,
)

TARGET = ROOT / "scripts" / "backup" / "一键备份.ps1"
REL_FILE = "scripts/backup/一键备份.ps1"

# 1. 删除主工作区文件
print(f"[STEP1] deleting {TARGET}")
if TARGET.exists():
    TARGET.unlink()
    print(f"  deleted: exists={TARGET.exists()}")
else:
    print(f"  already gone")

# 2. 启动 session
sid = generate_session_id()
print(f"[STEP2] session_worktree_start -> sid={sid}")
r = session_worktree_start(sid)
print(f"  start result: {r}")

# 3. 提交（_sync_files_to_worktree 会检测源缺失+dst被tracked -> _delete_worktree_file）
commit_msg = "chore(infra): MOD-INF-043——删除残留一键备份.ps1（重复手动触发入口，统一使用backup_manual.ps1）"
print(f"[STEP3] session_worktree_commit")
r = session_worktree_commit(sid, [REL_FILE], commit_msg, allow_overlap=True, allow_promote=True)
print(f"  commit result: {r}")

# 4. merge
print(f"[STEP4] session_worktree_merge")
r = session_worktree_merge(sid)
print(f"  merge result: {r}")

# 5. 验证
print(f"[STEP5] verify")
print(f"  file exists in main workspace: {TARGET.exists()}")
import subprocess
ls = subprocess.run(
    ["git", "ls-files", "--", REL_FILE],
    cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
)
print(f"  git ls-files output: {ls.stdout!r}")
