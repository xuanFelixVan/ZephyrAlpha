# [BLUEPRINT] MOD-SIG-145
# [MODULE] scripts.ch.apply_pattern_win_rate_ddl
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.data.ch_writer; schemas.categories.market.market_pattern_win_rate
# [CONSUMERS] scripts/data/pattern_win_rate_materialize.py; pattern_win_rate_provider
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: market_pattern_win_rate DDL 真源为 schemas/categories/market/market_pattern_win_rate.py；本脚本只执行 IF NOT EXISTS 幂等建表，禁止改列/删数据
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
"""market_pattern_win_rate 建表 DDL 部署 + 验证脚本（MOD-SIG-145 W3）。

DDL 真源：schemas/categories/market/market_pattern_win_rate.py（DDL-as-Code）。

用法::

    python scripts/ch/apply_pattern_win_rate_ddl.py           # 建表 + 验证
    python scripts/ch/apply_pattern_win_rate_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.market.market_pattern_win_rate import (  # noqa: E402
    MARKET_PATTERN_WIN_RATE_DDL,
    TABLE_NAME,
)
from zephyr.data import ch_writer  # noqa: E402


def apply() -> int:
    try:
        ch_writer.query(MARKET_PATTERN_WIN_RATE_DDL)
        print(f"OK: {TABLE_NAME} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    """验证表存在且引擎正确。注意 ch_writer.query 失败/空结果返回 ''（不抛异常）。"""
    out = ch_writer.query(
        "SELECT engine FROM system.tables WHERE database = 'c1_market' AND name = '" + TABLE_NAME + "'"
    )
    if not out:
        print(f"VERIFY FAIL: c1_market.{TABLE_NAME} 不存在")
        return 1
    engine = out.strip().split("\t")[0]
    ok = "ReplacingMergeTree" in engine
    print(f"VERIFY {'OK' if ok else 'FAIL'}: c1_market.{TABLE_NAME} engine={engine}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else apply())
