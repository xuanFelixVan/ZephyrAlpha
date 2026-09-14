# [BLUEPRINT] MOD-SIG-145
# [MODULE] scripts.ch.apply_pattern_event_ddl
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.data.ch_writer; schemas.categories.market.market_pattern_event
# [CONSUMERS] src/zephyr/signal_ashare/strategy_signal/pattern_event_store.py（写入口）；W2 回填/W4 增量任务前置
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: market_pattern_event DDL 真源为 schemas/categories/market/market_pattern_event.py；本脚本只执行 IF NOT EXISTS 幂等建表，禁止改列/删数据
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
"""market_pattern_event 建表 DDL 部署 + 验证脚本（MOD-SIG-145 W1）。

DDL 真源：schemas/categories/market/market_pattern_event.py（DDL-as-Code）。
蓝图：docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md
（2026-09-14 图形库全链批立项）。

用法::

    python scripts/ch/apply_pattern_event_ddl.py           # 建表 + 验证
    python scripts/ch/apply_pattern_event_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.market.market_pattern_event import (  # noqa: E402
    MARKET_PATTERN_EVENT_DDL,
    TABLE_NAME,
)
from zephyr.data import ch_writer  # noqa: E402


def apply() -> int:
    try:
        ch_writer.query(MARKET_PATTERN_EVENT_DDL)
        print(f"OK: {TABLE_NAME} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    """验证表存在且引擎正确。注意 ch_writer.query(sql, timeout) 返回 TSV 字符串、
    失败/空结果返回 ''（不抛异常）——不能传 params dict。"""
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
