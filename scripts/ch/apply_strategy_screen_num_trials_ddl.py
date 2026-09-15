# [BLUEPRINT] MOD-TDMVAL-001 | schemas/categories/backtest/backtest_strategy_screen.py
# [MODULE] scripts.ch.apply_strategy_screen_num_trials_ddl
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.infrastructure.database_service; schemas.categories.backtest.backtest_strategy_screen
# [CONSUMERS] c1_backtest.strategy_screen（num_trials 加列部署+探针验证，S03-N1）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] DDL 用 base(admin) 账号执行（#ARCH-CH-027）；ADD COLUMN IF NOT EXISTS 幂等；
#   Nullable 追加列零回填（历史行 NULL 留痕）；执行后必须 system.columns 探针验证列名+类型
#   （ALTER 假成功事故教训：query 失败不抛异常，探针是唯一可信回执）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)(ALTER 失败或列/类型探针不符)
# [TESTS] manual（对生产 CH 只加列，不进单测）
# [A_module] module_id=MOD-TDMVAL-001 | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""strategy_screen 加列 num_trials 部署+探针验证（S03-N1：DSR 冻结根因的 N 账本地基）。

用法: python scripts/ch/apply_strategy_screen_num_trials_ddl.py
幂等: ADD COLUMN IF NOT EXISTS；重跑零副作用。
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.backtest.backtest_strategy_screen import (  # noqa: E402
    DATABASE,
    TABLE_NAME,
)

ALTER_SQL = (
    f"ALTER TABLE {DATABASE}.{TABLE_NAME} "
    "ADD COLUMN IF NOT EXISTS num_trials Nullable(UInt32) "
    "COMMENT '多重比较试次数(批内实际参考策略数,DSR N 口径,批级属性;NULL=2026-09-15 前历史批)'"
)
EXPECT_TYPE = "Nullable(UInt32)"


def apply() -> int:
    from zephyr.infrastructure.database_service import get_db_service

    c = get_db_service().get_clickhouse_conn(role="admin")
    c.execute(ALTER_SQL)
    # 探针验证（唯一可信回执）：列存在 + 类型一致
    rows = c.execute(
        f"SELECT name, type FROM system.columns "
        f"WHERE database='{DATABASE}' AND table='{TABLE_NAME}'")
    cols = {str(r[0]): str(r[1]) for r in rows}
    if "num_trials" not in cols:
        print(f"FAIL: 探针未见 num_trials 列（ALTER 假成功）: {DATABASE}.{TABLE_NAME}")
        return 1
    if cols["num_trials"] != EXPECT_TYPE:
        print(f"FAIL: num_trials 类型漂移: DB={cols['num_trials']} 期望={EXPECT_TYPE}")
        return 1
    print(f"OK {DATABASE}.{TABLE_NAME} num_trials {cols['num_trials']} 列数={len(cols)}")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
