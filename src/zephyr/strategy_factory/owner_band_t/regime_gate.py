# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.regime_gate
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas; zephyr.infrastructure.database_service
# [CONSUMERS] zephyr.strategy_factory.owner_band_t.data_loader; zephyr.strategy_factory.owner_band_t.engine; tests/strategy_factory/test_s_owner_001_engine.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 第 t 日门状态=trade_date 严格早于 t 的最近一行快照（翻转次日生效，防未来函数）；缺失快照段=门开（缺数据不构成趋势上证据，冻结口径）；闭门集={r3,r12} 且 confidence>=min_confidence
# [MODIFY-GUARD] 语义变更=考试冻结口径变更，冻结期禁改
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(空快照)
# [TESTS] tests/strategy_factory/test_s_owner_001_engine.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""regime 门——读 c1_backtest.regime_snapshot_history（现役判定器 walk-forward 印教材）。

冻结口径（E4 冻结文档 §2）：
  * trend_up 闭门集 = {r3 牛市趋势, r12 BREAKOUT}；dominant∈闭门集 且
    confidence >= min_confidence → 门关（卡停用）。
  * 其余态 / 低置信 / 无快照 → 门开（震荡/不确定均启用）。
"""

from __future__ import annotations

import pandas as pd

TREND_UP_STATES = frozenset({"r3", "r12"})
PINNED_RUN_ID = "VAL-P0-20260916-230726"


def gate_open_series(
    trade_days: pd.DatetimeIndex,
    snapshots: pd.DataFrame,
    min_confidence: float,
) -> pd.Series:
    """构建逐日门开布尔序列。

    :param trade_days: 交易日索引（执行面日历）
    :param snapshots: 快照行（trade_date, dominant, confidence；单 run，升序）
    :param min_confidence: 门最小置信度（dominant∈闭门集但低于此值=不确定=门开）
    """
    if snapshots.empty:
        raise RuntimeError("regime_snapshot_history 快照为空——检查 run_id/数据链路")
    snap = snapshots.sort_values("trade_date")
    dates = pd.DatetimeIndex(pd.to_datetime(snap["trade_date"]))
    dominant = snap["dominant"].to_numpy()
    conf = snap["confidence"].to_numpy(dtype=float)

    open_flags = []
    j = -1  # 指向最后一个 trade_date < 当日 的快照行
    for day in trade_days:
        d = pd.Timestamp(day)
        while j + 1 < len(dates) and dates[j + 1] < d:
            j += 1
        if j < 0:
            open_flags.append(True)  # 冻结口径: 无快照=不确定=门开
            continue
        closes = dominant[j] in TREND_UP_STATES and conf[j] >= min_confidence
        open_flags.append(not closes)
    return pd.Series(open_flags, index=trade_days, name="gate_open")
