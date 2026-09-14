# [BLUEPRINT] MOD-BT-086 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.ch.apply_sim_trade_log_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service; schemas.categories.sim_trade_log
# [CONSUMERS] c1_backtest.sim_trade_log（表部署+验证）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] DDL 用 base 账号执行（writer 无 CREATE 权限，#ARCH-CH-027）；IF NOT EXISTS 幂等
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)(DDL 失败)
# [TESTS] tests/backtest/test_sim_paper_ledger.py
# [A_module] module_id=MOD-BT-132 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_trade_log 建表 DDL 部署+验证（平台蓝图批 1：成交事件流水）。"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.sim_trade_log import DDL, TABLE_NAME  # noqa: E402


def apply() -> int:
    from zephyr.infrastructure.database_service import get_db_service

    c = get_db_service().get_clickhouse_conn(role="admin")
    c.execute(DDL)
    cols = c.execute(
        "SELECT name FROM system.columns WHERE database='c1_backtest' AND table='sim_trade_log'")
    names = [r[0] for r in cols]
    required = {"trade_date", "strategy_id", "action", "price", "signal_reason"}
    missing = required - set(names)
    if missing:
        print(f"FAIL: 列缺失 {missing}")
        return 1
    print(f"OK {TABLE_NAME} 列数={len(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
