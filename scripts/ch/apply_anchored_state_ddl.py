#!/usr/bin/env python
# [BLUEPRINT] MOD-REGIME-001
# [MODULE] scripts.ch.apply_anchored_state_ddl
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] regime_state_anchored 表 DDL 唯一真源=本文件 DDL 常量（regime 家族先例：apply_regime_snapshot_ddl.py）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: DDL 部署/验证 CLI（A 类一次性运维，建表+--verify 按需手动执行）
"""regime_state_anchored 建表 DDL 部署 + 验证脚本（P0-002 重印批，裁定#229）。

裁定沿用：writer 账号无 CREATE 权限，DDL 用 base 账号直连（#ARCH-CH-027 RBAC，
同 apply_regime_snapshot_ddl.py 先例）。

用法::

    python scripts/ch/apply_anchored_state_ddl.py           # 建表 + 验证
    python scripts/ch/apply_anchored_state_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.data import ch_reader  # noqa: E402

TABLE_NAME = "regime_state_anchored"

ANCHORED_STATE_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.regime_state_anchored
(
    trade_date Date                            COMMENT '交易日',
    dominant   LowCardinality(String)          COMMENT '锚定态（r1 低波震荡/r2 中波震荡/r3 牛市趋势/r4 熊市阴跌，固定阈值零拟合）',
    vol_pct    Nullable(Float64)               COMMENT '20日HV的250日滚动分位（锚定特征）',
    close      Nullable(Float64)               COMMENT '收盘价',
    ma20       Nullable(Float64)               COMMENT 'MA20',
    ma60       Nullable(Float64)               COMMENT 'MA60',
    ma120      Nullable(Float64)               COMMENT 'MA120',
    data_source LowCardinality(String) DEFAULT 'anchored_state_machine' COMMENT '数据来源',
    ingest_ts  DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY trade_date
SETTINGS index_granularity = 8192
"""


def apply() -> int:
    try:
        from zephyr.infrastructure.database_service import get_db_service

        c = get_db_service().get_clickhouse_conn(role="admin")
        c.execute(ANCHORED_STATE_DDL)
        print(f"OK: {TABLE_NAME} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    out = ch_reader.query(
        "SELECT engine FROM system.tables WHERE database = 'c1_backtest' AND name = '" + TABLE_NAME + "'"
    )
    if not out:
        print(f"VERIFY FAIL: c1_backtest.{TABLE_NAME} 不存在")
        return 1
    engine = out.strip().split("\t")[0]
    ok = "MergeTree" in engine
    print(f"VERIFY {'OK' if ok else 'FAIL'}: c1_backtest.{TABLE_NAME} engine={engine}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else apply())
