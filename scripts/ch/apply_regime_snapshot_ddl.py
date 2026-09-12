# [BLUEPRINT] MOD-BT-031
# [MODULE] scripts.ch.apply_regime_snapshot_ddl
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; schemas.categories.regime_snapshot_history
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: regime_snapshot_history DDL 真源为 schemas/categories/regime_snapshot_history.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
"""regime_snapshot_history 建表 DDL 部署 + 验证脚本（P0 印教材，P-BT-001）。

DDL 真源：schemas/categories/regime_snapshot_history.py（DDL-as-Code）。
裁定来源：docs/_working/2026-09-11-backtest-evidence-log-discussion.md §八 R3 同族（Owner R1-R5 全认）。

用法::

    python scripts/ch/apply_regime_snapshot_ddl.py           # 建表 + 验证
    python scripts/ch/apply_regime_snapshot_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.regime_snapshot_history import (  # noqa: E402
    REGIME_SNAPSHOT_HISTORY_DDL,
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
        c.execute(REGIME_SNAPSHOT_HISTORY_DDL)
        print(f"OK: {TABLE_NAME} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    """验证表存在且引擎正确（ch_reader.query只读查询，CH-FINAL-GATE 合规）。"""
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
