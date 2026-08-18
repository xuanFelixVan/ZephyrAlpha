# [BLUEPRINT] MOD-GOV_MIG_ACQ | scripts/governance/migrations/add_acquisition_fields.py | §acquisition-field
# [MODULE] scripts.governance.migrations.add_acquisition_fields
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.depgraph_schema; scripts.governance._shared.constants (EXIT_PASS, EXIT_FINDINGS); scripts.governance.meta.backup_runtime_state (backup_pg_architecture, 事件触发备份)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等迁移脚本：为 nodes_metadata 表添加 acquisition_method(含枚举CHECK)+acquisition_source 两列；规范化 '' → NULL；IF NOT EXISTS/DO 块可重复执行
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=失败
# [TESTS]
# [A_module] module_id=MOD-GOV_MIG_ACQ | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""add_acquisition_fields.py — 为 nodes_metadata 表添加 acquisition 字段 + 枚举 CHECK 约束

为 nodes_metadata 表添加两列 + 一条 CHECK 约束：
  - acquisition_method  TEXT   获取方式：self_build/opensource/borrow/deprecate
  - acquisition_source  TEXT   获取来源：开源链接/借鉴组件名/空
  - CHECK (acquisition_method IS NULL OR acquisition_method IN
           ('self_build','opensource','borrow','deprecate'))

枚举真源 = DDL CHECK 约束（depgraph_schema._DDL_NODES_METADATA + 02_create_pg_schema.sql
对齐）。本脚本负责对现有库做 ALTER TABLE——CREATE TABLE IF NOT EXISTS 不会为已存在表
加新列/约束，故需本迁移。

数据规范化（治本 2026-08-05）：加 CHECK 前，将历史 acquisition_method='' (空串) 规范化为
NULL——空串既非 NULL 又不在枚举内，会被 CHECK 拒绝。空串来源于 update_module_metadata 的
UPSERT（空值直写）。规范化后 NULL=未设置，与 reader 的 ``or ""`` 回退语义等价。同时
apply_depgraph.update_module_metadata 已对齐：acquisition_method='' → None（防未来 '' 写入
被 CHECK 拒绝）。

配合 apply_depgraph.py --update-module-metadata 使用，让每个模块能登记"怎么搞到手"
（自建/开源替代/借鉴/弃用）+ 开源链接，供后续 AI 开发时查询。

权限说明（裁定#ARCH-DEPGRAPH_ACCESS_CONTROL）：
  ALTER TABLE ADD COLUMN/ADD CONSTRAINT 是 DDL 操作，需要表属主权限。nodes_metadata 属主是
  ``zephyr`` 角色，depgraph_reader（SELECT only）/depgraph_writer（DML）均无权
  ALTER——故本脚本必须用 ``superuser=True``（postgres DDL 角色）。本脚本已在
  DEPGRAPH-WRITE-PATH gate 白名单中（schema 迁移合法 DDL 入口）。

备份（trae_054 v1.6.0 STEP0）：DDL+数据规范化提交成功后，事件触发 backup_pg_architecture()
做 PG 架构库物理快照（全景 19 表）。DDL 在事务内（autocommit=False），失败回滚无副作用；
成功后快照保证可恢复。

用法::

    python scripts/governance/migrations/add_acquisition_fields.py
    python scripts/governance/migrations/add_acquisition_fields.py --dry-run

幂等：IF NOT EXISTS + DO 块（pg_constraint 探测）可重复执行，已存在列/约束不会报错。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: add_acquisition_fields.py — 为 nodes_metadata 表添加 acquisition 字段 + 枚举
  CHECK 约束
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
# _shared 模块位于 scripts/governance/_shared，需将其父目录加入 sys.path
_GOV_DIR = _THIS_FILE.parents[1]  # scripts/governance
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

_DDL_ADD_ACQUISITION_METHOD = "ALTER TABLE nodes_metadata ADD COLUMN IF NOT EXISTS acquisition_method TEXT"
_DDL_ADD_ACQUISITION_SOURCE = "ALTER TABLE nodes_metadata ADD COLUMN IF NOT EXISTS acquisition_source TEXT"

# 规范化历史空串 → NULL（治本：空串会被 CHECK 拒绝；NULL=未设置）
_DDL_NORMALIZE_EMPTY_METHOD = "UPDATE nodes_metadata SET acquisition_method = NULL WHERE acquisition_method = ''"

# 幂等加 CHECK 约束（DO 块探测 pg_constraint；PG 不支持 ADD CONSTRAINT IF NOT EXISTS）。
# 约束名 nodes_metadata_acquisition_method_check 与 02_create_pg_schema.sql 内联列约束
# 自动命名一致——fresh install 与迁移后库对齐，单一真源。
_DDL_ADD_ACQUISITION_METHOD_CHECK = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'nodes_metadata_acquisition_method_check'
          AND conrelid = 'nodes_metadata'::regclass
    ) THEN
        ALTER TABLE nodes_metadata
            ADD CONSTRAINT nodes_metadata_acquisition_method_check
            CHECK (acquisition_method IS NULL OR acquisition_method IN
                   ('self_build', 'opensource', 'borrow', 'deprecate'));
    END IF;
END $$;
"""


def migrate(dry_run: bool = False) -> int:
    """为 nodes_metadata 表添加 acquisition_method(含CHECK)+acquisition_source 两列。

    步骤：
      1. ADD COLUMN IF NOT EXISTS（加列，幂等）
      2. 规范化 acquisition_method='' → NULL（治本，让 CHECK 能通过）
      3. ADD CONSTRAINT CHECK（DO 块，幂等）
      4. 验证列 + 约束存在
      5. 提交后事件触发 backup_pg_architecture() 物理快照

    Args:
        dry_run: True=只打印不执行（回滚事务）
    Returns:
        0=成功, 1=失败
    """
    # superuser=True：ALTER TABLE 需属主权限（owner=zephyr，仅 postgres 可 ALTER）
    conn = get_depgraph_pg_connection(autocommit=False, superuser=True)
    try:
        cur = conn.cursor()
        print("[MIGRATE] Adding acquisition_method + acquisition_source to nodes_metadata...")
        cur.execute(_DDL_ADD_ACQUISITION_METHOD)
        cur.execute(_DDL_ADD_ACQUISITION_SOURCE)
        print("[MIGRATE]   ALTER TABLE ADD COLUMN 已执行（IF NOT EXISTS，幂等）")

        # 规范化历史空串 → NULL（治本 2026-08-05，让 CHECK 能通过）
        cur.execute(_DDL_NORMALIZE_EMPTY_METHOD)
        normalized = cur.rowcount
        print(f"[MIGRATE]   规范化 acquisition_method='' → NULL：{normalized} 行")

        # 加 CHECK 约束（DO 块幂等，pg_constraint 探测）
        cur.execute(_DDL_ADD_ACQUISITION_METHOD_CHECK)
        print("[MIGRATE]   CHECK 约束 nodes_metadata_acquisition_method_check 已确保存在（DO 块幂等）")

        # 验证列已加
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'nodes_metadata' "
            "AND column_name IN ('acquisition_method', 'acquisition_source') "
            "ORDER BY column_name"
        )
        cols = [r[0] for r in cur.fetchall()]
        print(f"[MIGRATE]   验证：nodes_metadata 现有 acquisition 列 = {cols}")

        # 验证 CHECK 约束已加
        cur.execute(
            "SELECT conname FROM pg_constraint "
            "WHERE conrelid = 'nodes_metadata'::regclass "
            "AND conname = 'nodes_metadata_acquisition_method_check'"
        )
        ck = [r[0] for r in cur.fetchall()]
        print(f"[MIGRATE]   验证：CHECK 约束 = {ck}")

        if dry_run:
            print("[MIGRATE] DRY RUN — 回滚")
            conn.rollback()
        else:
            conn.commit()
            print("[MIGRATE] 提交完成")
            # 事件触发 PG 架构库备份（trae_054 v1.6.0 STEP0，写入后快照，非 git commit）
            try:
                try:
                    from scripts.governance.meta.backup_runtime_state import backup_pg_architecture
                except ImportError:
                    from meta.backup_runtime_state import backup_pg_architecture
                backup_pg_architecture(throttle_seconds=60)
                print("[MIGRATE]   backup_pg_architecture 快照已生成")
            except Exception as be:  # noqa: BLE001 — 备份失败不阻断迁移（DB 已提交）
                print(f"[MIGRATE] WARNING: backup_pg_architecture 失败（不阻断）: {be}", file=sys.stderr)
            print("[MIGRATE] 下一步: 用 apply_depgraph.py --update-module-metadata 填充数据")

        # 判定：列(2) + 约束(1) 齐全
        ok = len(cols) == 2 and len(ck) == 1
        if not ok:
            print(
                f"[MIGRATE] WARNING: 期望 2 列 + 1 约束，实际 {len(cols)} 列 + {len(ck)} 约束",
                file=sys.stderr,
            )
            return EXIT_FINDINGS
        return EXIT_PASS
    except Exception as e:  # noqa: BLE001 — 顶层错误兜底：rollback + 打印，迁移脚本的 DB 异常需全捕获
        conn.rollback()
        print(f"[MIGRATE] ERROR: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="为 nodes_metadata 表添加 acquisition_method(含CHECK)+acquisition_source 两列"
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印不执行")
    args = parser.parse_args()
    sys.exit(migrate(dry_run=args.dry_run))
