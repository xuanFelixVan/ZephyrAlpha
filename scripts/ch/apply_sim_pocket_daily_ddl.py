# [BLUEPRINT] MOD-BT-083 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.ch.apply_sim_pocket_daily_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] clickhouse_driver; schemas.categories.sim_pocket_daily
# [CONSUMERS] c1_backtest.sim_pocket_daily（表部署+验证）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] DDL 用 base 账号执行（writer 无 CREATE 权限，#ARCH-CH-027）；IF NOT EXISTS 幂等
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)(DDL 失败)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-083 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_pocket_daily 建表 DDL 部署+验证（模拟盘方案 C，2026-09-14 Owner 批先C后A）。"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.sim_pocket_daily import DDL, TABLE_NAME  # noqa: E402


def apply() -> int:
    from clickhouse_driver import Client

    from zephyr.data.ch_config import load_ch_config

    cfg = load_ch_config()
    c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
               user=cfg.get("user", "default"), password=cfg.get("password", ""),
               connect_timeout=5)
    c.execute(DDL)
    cols = c.execute(
        "SELECT name FROM system.columns WHERE database='c1_backtest' AND table='sim_pocket_daily'")
    names = [r[0] for r in cols]
    required = {"trade_date", "strategy_id", "equity", "signal", "mode"}
    missing = required - set(names)
    if missing:
        print(f"FAIL: 列缺失 {missing}")
        return 1
    print(f"OK {TABLE_NAME} 列数={len(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
