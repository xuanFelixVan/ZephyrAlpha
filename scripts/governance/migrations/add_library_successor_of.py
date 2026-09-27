# [BLUEPRINT] MOD-GOV_MIG_SUCC | scripts/governance/migrations/add_library_successor_of.py | §successor-of
# [MODULE] scripts.governance.migrations.add_library_successor_of
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; scripts.governance._shared.constants (EXIT_PASS, EXIT_FINDINGS); zephyr.governance.depgraph_schema (get_depgraph_pg_connection); scripts.backup.library_ledger_backup (library_ledger_backup, 事件触发备份)
# [CONSUMERS] src/zephyr/library/ledger_schema.py（_SQL_ENSURE_ASSETS 同列对齐）；src/zephyr/library/librarian.py；src/zephyr/library/lookup.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等迁移：ADD COLUMN IF NOT EXISTS successor_of TEXT NULL 可重复执行零副作用；纯增量可回滚（DROP COLUMN 仅丢去向指针，lib_events 只追加全程留痕可重建）；不写任何行数据（回填走 Librarian.act delete 处置链）
# [MODIFY-GUARD] 白名单登记通道=depgraph_write_path_gate（DDL 入口合法化，由总筹批落地）
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=失败
# [TESTS] tests/library/test_successor_of_migration.py
# [A_module] module_id=MOD-GOV_MIG_SUCC | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""add_library_successor_of.py — lib_assets 增枝 successor_of 墓碑去向指针列（S5 图书馆接线①）

对标先例：add_acquisition_fields.py（superuser DDL 迁移）+ potential_consumers 增枝五步
（裁定#410）。本次为增枝制（08 字段词典 §6）：successor_of 两态纪律——

  - ``NULL``   = 未评估（默认；历史 deceased 存量兼容态）
  - ``''``     = 确认无后继（显式表态）
  - 非空串     = 后继资产 asset_id（墓碑去向指针）

写入路径唯一=Librarian.act("delete", ..., authority=死亡证明, fields={"successor_of": ...})
（事件与状态同事务）；消费面=lookup CLI 墓碑显示 / moved 墓碑卡 / tri-consistency 检查器 /
S1 FMS-HYGIENE 门（死引用报"迁往何处"）。

DDL（幂等可重跑，已存在列零副作用）::

    ALTER TABLE lib_assets ADD COLUMN IF NOT EXISTS successor_of TEXT NULL;
    COMMENT ON COLUMN lib_assets.successor_of IS '墓碑去向：deceased 时指向后继资产
      asset_id；两态对标 potential_consumers 纪律：NULL=未评估，''=''=确认无后继';

回滚说明（纯增量，回滚零破坏）::

    ALTER TABLE lib_assets DROP COLUMN IF EXISTS successor_of;

  - 数据侧：仅丢去向指针本身；lib_events 只追加全程留痕（delete 事件 detail），可重建。
  - 代码侧：ledger_schema.py / librarian.py / lookup.py 三件 git revert；
    更符合"只增不改语义"的选择是列保留、代码回退（列空置无害）。
  - CREATE TABLE 常量（ledger_schema._SQL_ENSURE_ASSETS）已同步补列：
    新库 ensure 建表与迁移后老库对齐，单一真源（对标 potential_consumers 先例第⑤步）。

权限说明（对标 add_acquisition_fields 裁定#ARCH-DEPGRAPH_ACCESS_CONTROL）：
  ALTER TABLE 需表属主权限；lib_assets 属主非 depgraph_reader（SELECT only）/
  depgraph_writer（DML）——故本脚本用 ``superuser=True``（DDL 角色），
  DEPGRAPH-WRITE-PATH gate 白名单通道（schema 迁移合法 DDL 入口）。

前置（RULE-DATA-OPS 三步验证+备份）::

    python scripts/backup/library_ledger_backup.py backup   # 总账物理备份先行

用法::

    python scripts/governance/migrations/add_library_successor_of.py --dry-run
    python scripts/governance/migrations/add_library_successor_of.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: add_library_successor_of.py — lib_assets 增枝 successor_of 墓碑去向指针列
  （幂等 ADD COLUMN IF NOT EXISTS + 注释，纯增量可回滚）
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

# 增枝①：幂等加列（TEXT NULL；NULL=未评估默认态，历史存量零迁移负担）
_SQL_DDL_ADD_SUCCESSOR_OF = "ALTER TABLE lib_assets ADD COLUMN IF NOT EXISTS successor_of TEXT NULL"

# 列语义注释（两态纪律真源挂列上，禁只活在代码注释里）。
# SQL 字面量内 '''' = 存储两个单引号（空串记法），入库后显示为：…NULL=未评估，''（空串）=确认无后继
_SQL_DDL_COMMENT_ON_COLUMN = (
    "COMMENT ON COLUMN lib_assets.successor_of IS "
    "'墓碑去向：deceased 时指向后继资产 asset_id；两态对标 potential_consumers 纪律："
    "NULL=未评估，''''（空串）=确认无后继'"
)

_SQL_VERIFY_COLUMNS = (
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name = 'lib_assets' AND column_name = 'successor_of'"
)


def migrate(dry_run: bool = False) -> int:
    """为 lib_assets 增枝 successor_of 列（幂等）。

    步骤：
      1. ADD COLUMN IF NOT EXISTS（幂等加列）
      2. COMMENT ON COLUMN（语义真源挂列）
      3. information_schema 验证列存在
      4. dry_run=True 则回滚零副作用，否则提交

    Args:
        dry_run: True=只执行后回滚（验证 DDL 合法性，零持久副作用）。

    Returns:
        0=成功, 1=失败。
    """
    # superuser=True：ALTER TABLE 需属主/DDL 权限（reader 只读、writer 仅 DML）
    conn = get_depgraph_pg_connection(autocommit=False, superuser=True)
    try:
        cur = conn.cursor()
        print("[MIGRATE] Adding successor_of to lib_assets (tombstone successor pointer)...")
        cur.execute(_SQL_DDL_ADD_SUCCESSOR_OF)
        print("[MIGRATE]   ALTER TABLE ADD COLUMN IF NOT EXISTS 已执行（幂等）")
        cur.execute(_SQL_DDL_COMMENT_ON_COLUMN)
        print("[MIGRATE]   COMMENT ON COLUMN 已执行（两态纪律真源挂列）")

        cur.execute(_SQL_VERIFY_COLUMNS)
        cols = [r[0] for r in cur.fetchall()]
        print(f"[MIGRATE]   验证：lib_assets.successor_of 列 = {cols}")

        if dry_run:
            print("[MIGRATE] DRY RUN — 回滚（零副作用）")
            conn.rollback()
        else:
            conn.commit()
            print("[MIGRATE] 提交完成")
            print(
                "[MIGRATE] 回滚说明: ALTER TABLE lib_assets DROP COLUMN IF EXISTS successor_of;"
                "（lib_events 只追加留痕可重建；代码回退=ledger_schema/librarian/lookup 三件 revert）"
            )

        ok = cols == ["successor_of"]
        if not ok:
            print(f"[MIGRATE] WARNING: 期望 1 列 successor_of，实际 {cols}", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="lib_assets 增枝 successor_of 墓碑去向指针列（幂等）")
    parser.add_argument("--dry-run", action="store_true", help="只执行后回滚（零持久副作用）")
    args = parser.parse_args()
    sys.exit(migrate(dry_run=args.dry_run))
