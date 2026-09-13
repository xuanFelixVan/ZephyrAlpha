#!/usr/bin/env python
# [BLUEPRINT] MOD-L04-001
# [MODULE] scripts.ch.apply_financial_derived_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; schemas.categories.fundamental.financial_derived
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: financial_derived DDL 真源为 schemas/categories/fundamental/financial_derived.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: DDL 部署/验证 CLI（A 类一次性运维，建表+--verify 按需手动执行）
"""financial_derived 建表 DDL 部署 + 验证脚本（财报消费端 F1-M1，DS-230）。

DDL 真源：schemas/categories/fundamental/financial_derived.py（DDL-as-Code）。
施工方案：docs/_working/2026-09-12-fundamental-consumption-design.md §M1。
裁定沿用：writer 账号无 CREATE 权限，DDL 用 base 账号直连（#ARCH-CH-027 RBAC 三账号体系，
同 scripts/ch/apply_research_report_ddl.py 先例）。

用法::

    python scripts/ch/apply_financial_derived_ddl.py           # 建表 + 验证
    python scripts/ch/apply_financial_derived_ddl.py --verify  # 仅验证（表存在且引擎正确）
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.fundamental.financial_derived import (  # noqa: E402
    FINANCIAL_DERIVED_DDL,
    TABLE_NAME,
)
from zephyr.data import ch_reader  # noqa: E402


def apply() -> int:
    """DDL 用 base 账号执行（writer 账号无 CREATE 权限，#ARCH-CH-027 RBAC 三账号体系）。"""
    try:
        from clickhouse_driver import Client

        from zephyr.data.ch_config import load_ch_config

        cfg = load_ch_config()
        c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)), user=cfg["user"],
                   password=cfg.get("password", ""), connect_timeout=5)
        c.execute(FINANCIAL_DERIVED_DDL)
        # v1.1 增列（CREATE IF NOT EXISTS 不会给存量表加列；幂等）
        c.execute(
            "ALTER TABLE c3_fundamental.financial_derived "
            "ADD COLUMN IF NOT EXISTS total_shares Nullable(Float64) "
            "COMMENT '总股本（时点，F-Score 无增发项，v1.1）'"
        )
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
