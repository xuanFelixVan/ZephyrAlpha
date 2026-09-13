# [BLUEPRINT] MOD-BT-153 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.ch.apply_hypothesis_precheck_ddl
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] clickhouse_driver; schemas.categories.backtest_hypothesis_precheck
# [CONSUMERS] c1_backtest.hypothesis_precheck（表部署+逐列探针验证）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] DDL 用 base 账号执行（writer 无 CREATE 权限，#ARCH-CH-027）；IF NOT EXISTS 幂等；
#   建表后必须 system.columns 逐列探针（ALTER 假成功事故教训）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)(DDL 失败或列缺失)
# [TESTS] tests/backtest/test_hypothesis_precheck.py
# [A_module] module_id=MOD-BT-153 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""hypothesis_precheck 建表 DDL 部署+逐列探针验证（图9 FAC-E2 判定记录台账）。"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.backtest_hypothesis_precheck import (  # noqa: E402
    BACKTEST_HYPOTHESIS_PRECHECK_DDL,
    DATABASE,
    TABLE_NAME,
)

REQUIRED_COLUMNS = {
    "ingest_ts", "precheck_batch", "candidate_id", "birth_channel", "birth_batch",
    "hypothesis_zh", "model", "verdict", "verdict_reason", "confidence",
    "rationale_zh", "latency_ms", "prechecked_at", "notes",
}


def apply() -> int:
    from clickhouse_driver import Client

    from zephyr.data.ch_config import load_ch_config

    cfg = load_ch_config()
    c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
               user=cfg.get("user", "default"), password=cfg.get("password", ""),
               connect_timeout=5)
    c.execute(BACKTEST_HYPOTHESIS_PRECHECK_DDL)
    cols = c.execute(
        f"SELECT name FROM system.columns WHERE database='{DATABASE}' AND table='{TABLE_NAME}'")
    names = {r[0] for r in cols}
    missing = REQUIRED_COLUMNS - names
    if missing:
        print(f"FAIL: 列缺失 {missing}")
        return 1
    print(f"OK {DATABASE}.{TABLE_NAME} 列数={len(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
