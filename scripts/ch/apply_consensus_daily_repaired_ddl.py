# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md | §consensus
# [MODULE] scripts.ch.apply_consensus_daily_repaired_ddl
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.infrastructure.database_service; schemas.categories.fundamental.consensus_daily_repaired
# [CONSUMERS] (手动 DDL 部署/验证；重建前先跑本脚本建表)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: consensus_daily_repaired 真源=schemas/categories/fundamental/consensus_daily_repaired.py；
#              只建 repaired 新表，禁对 DS-229 consensus_daily 做任何 DDL（双轨物理隔离，方案 §L48）；
#              CREATE IF NOT EXISTS 幂等，重建走 builder 覆盖同键而非 DROP
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎非 MergeTree->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动 DDL 部署脚本（A 类一次性运维，幂等按需手动执行）
"""consensus_daily_repaired 建表 DDL 部署 + 验证脚本（C4 历史修复双轨重建，2026-09-16）。

DDL 真源：schemas/categories/fundamental/consensus_daily_repaired.py（DDL-as-Code）。
施工依据：docs/_working/2026-09-14-c4-history-repair-plan.md §2-L4（新表，原表不动）+ §6 验收。
裁定沿用：DDL 用 admin 账号执行（writer 无 CREATE 权限，#ARCH-CH-027 RBAC 三账号体系）。

用法::

    python scripts/ch/apply_consensus_daily_repaired_ddl.py           # 建表 + 验证
    python scripts/ch/apply_consensus_daily_repaired_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.fundamental.consensus_daily_repaired import (  # noqa: E402
    CONSENSUS_DAILY_REPAIRED_DDL,
    TABLE_NAME,
)
from zephyr.data import ch_reader  # noqa: E402


def apply() -> int:
    """DDL 用 admin 账号执行（writer 账号无 CREATE 权限，#ARCH-CH-027）。"""
    try:
        from zephyr.infrastructure.database_service import get_db_service

        c = get_db_service().get_clickhouse_conn(role="admin")
        c.execute(CONSENSUS_DAILY_REPAIRED_DDL)
        print(f"OK: {TABLE_NAME} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    """验证表存在且引擎正确，并核实 DS-229 未被本表 DDL 波及（双轨隔离自证）。"""
    out = ch_reader.query(
        "SELECT engine FROM system.tables WHERE database = 'c3_fundamental' AND name = '"
        + TABLE_NAME + "'"
    )
    if not out:
        print(f"VERIFY FAIL: c3_fundamental.{TABLE_NAME} 不存在")
        return 1
    engine = out.strip().split("\t")[0]
    if "MergeTree" not in engine:
        print(f"VERIFY FAIL: c3_fundamental.{TABLE_NAME} engine={engine}")
        return 1
    cols = int(ch_reader.query(
        "SELECT count() FROM system.columns WHERE database='c3_fundamental' "
        f"AND table='{TABLE_NAME}'"
    ).strip() or 0)
    partner = ch_reader.query(
        "SELECT engine FROM system.tables WHERE database='c3_fundamental' AND name='consensus_daily'"
    ).strip().split("\t")[0]
    print(
        f"VERIFY OK: c3_fundamental.{TABLE_NAME} engine={engine} columns={cols}"
        f"（DS-229 仍在位 engine={partner}，双轨并存）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else apply())
