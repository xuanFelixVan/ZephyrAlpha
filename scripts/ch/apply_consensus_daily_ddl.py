# [BLUEPRINT] MOD-L04-001
# [MODULE] scripts.ch.apply_consensus_daily_ddl
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; schemas.categories.fundamental.consensus_daily
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: consensus_daily DDL 真源为 schemas/categories/fundamental/consensus_daily.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动 DDL 部署脚本（A 类一次性运维，幂等按需手动执行）
"""consensus_daily 建表 DDL 部署 + 验证脚本（消费端 C1，2026-09-12）。

DDL 真源：schemas/categories/fundamental/consensus_daily.py（DDL-as-Code）。
设计真源：docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md §M1。
裁定沿用：DDL 用 base 账号执行（writer 无 CREATE 权限，#ARCH-CH-027）。

用法::

    python scripts/ch/apply_consensus_daily_ddl.py           # 建表 + 验证
    python scripts/ch/apply_consensus_daily_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.fundamental.consensus_daily import (  # noqa: E402
    CONSENSUS_DAILY_DDL,
    TABLE_NAME,
)
from zephyr.data import ch_reader  # noqa: E402


def apply() -> int:
    """DDL 用 base 账号执行（writer 账号无 CREATE 权限，#ARCH-CH-027 RBAC 三账号体系）。"""
    try:
        from zephyr.infrastructure.database_service import get_db_service

        c = get_db_service().get_clickhouse_conn(role="admin")
        c.execute(CONSENSUS_DAILY_DDL)
        print(f"OK: {TABLE_NAME} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    """验证表存在且引擎正确（ch_reader.query 只读查询，CH-FINAL-GATE 合规）。"""
    out = ch_reader.query(
        "SELECT engine FROM system.tables WHERE database = 'c3_fundamental' AND name = '" + TABLE_NAME + "'"
    )
    if not out:
        print(f"VERIFY FAIL: c3_fundamental.{TABLE_NAME} 不存在")
        return 1
    engine = out.strip().split("\t")[0]
    ok = "MergeTree" in engine
    print(f"VERIFY {'OK' if ok else 'FAIL'}: c3_fundamental.{TABLE_NAME} engine={engine}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else apply())
