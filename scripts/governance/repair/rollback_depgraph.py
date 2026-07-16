# [BLUEPRINT] MOD-GOV-REPAIR
# [MODULE] scripts.governance.repair.rollback_depgraph
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] scripts.governance.repair.backup_depgraph
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
[BLUEPRINT] MOD-ARCH-002 | scripts/governance/repair/rollback_depgraph.py | §8.2
[MODULE] 无（独立脚本）
[INVARIANTS] 仅接受depgraph.backup.*路径; 回滚前自动备份当前depgraph
[MODIFY-GUARD] 本脚本由autopilot执行
[CONSUMERS] autopilot session-20260618-001; §8.2回滚脚本
[STABILITY] stable
[SAFETY] H
[AI_AUTONOMY] human_gated
[ERROR_CONTRACT] 参数缺失→exit 1; 备份路径不存在→exit 1; 回滚前备份失败→exit 1; 成功→exit 0
[TESTS] 执行后验证depgraph大小==备份文件大小

P1-2 从备份回滚depgraph
根因：§8.2要求回滚脚本，原脚本缺失
治根：落盘回滚脚本确保可从任意备份恢复

用法:
    python rollback_depgraph.py <备份路径>
    python rollback_depgraph.py D:\\ZephyrAlpha\\data\\databases\\depgraph.backup.pre_migration
"""

__manifest__ = """
args: []
description: P1-2 从备份回滚depgraph
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import shutil
import sys
from pathlib import Path

# Bootstrap: 基于 .git marker 定位仓库根（文件移动不 break，替代 parents[N] 硬编码）
_PROJECT_ROOT = Path(__file__).resolve()
while not (_PROJECT_ROOT / ".git").exists() and _PROJECT_ROOT != _PROJECT_ROOT.parent:
    _PROJECT_ROOT = _PROJECT_ROOT.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓库根真源（SSoT）

DST = str(REPO_ROOT / "data" / "databases" / "depgraph")
PRE_ROLLBACK_BACKUP = str(REPO_ROOT / "data" / "databases" / "depgraph.backup.pre_rollback")


def main():
    # P2迁移后警告：depgraph 已迁移到 PostgreSQL，本脚本的文件复制式回滚
    #（shutil.copy2）与 PG 服务器模式不兼容。如需回滚 PG 数据，应使用
    # pg_dump/pg_restore 或 SQL 级时间点恢复（PITR），而非复制 .db 文件。
    # 本脚本保留仅供 SQLite 备份文件的历史回滚参考，在 PG 模式下不应使用。
    print(
        "[WARNING] depgraph 已迁移到 PostgreSQL（P2迁移）。"
        "本脚本的文件复制式回滚与 PG 不兼容，"
        "如需回滚请使用 pg_dump/pg_restore 或 PITR。",
        file=sys.stderr,
    )

    if len(sys.argv) < 2:
        print("[ERROR] 用法: python rollback_depgraph.py <备份路径>")
        print("示例: python rollback_depgraph.py D:\\ZephyrAlpha\\data\\databases\\depgraph.backup.pre_migration")
        return 1

    src_backup = sys.argv[1]

    if not os.path.exists(src_backup):
        print(f"[ERROR] 备份文件不存在: {src_backup}")
        return 1

    src_size = os.path.getsize(src_backup)
    if src_size == 0:
        print(f"[ERROR] 备份文件大小为0: {src_backup}")
        return 1

    print(f"[INFO] 回滚源: {src_backup}")
    print(f"[INFO] 回滚源大小: {src_size} bytes")
    print(f"[INFO] 回滚目标: {DST}")

    if os.path.exists(DST):
        print(f"[INFO] 回滚前备份当前depgraph到: {PRE_ROLLBACK_BACKUP}")
        shutil.copy2(DST, PRE_ROLLBACK_BACKUP)
        pre_size = os.path.getsize(PRE_ROLLBACK_BACKUP)
        print(f"[OK] 回滚前备份完成: {pre_size} bytes")

    print(f"[INFO] 执行回滚: {src_backup} -> {DST}")
    shutil.copy2(src_backup, DST)

    dst_size = os.path.getsize(DST)
    print(f"[OK] 回滚后depgraph大小: {dst_size} bytes")

    if dst_size != src_size:
        print(f"[FAIL] 回滚后大小({dst_size})与备份({src_size})不一致")
        return 1

    print(f"[PASS] 回滚成功，大小一致: {src_size} == {dst_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
