# [BLUEPRINT] 32_firm_risk_aggregator §6（T+1 可卖持仓口径假设）+ 31_position_sizing §1 结案遗留 #30
# [MODULE] zephyr.position.core.t1_sellable
# [DOMAIN] D_POSITION
# [DEPENDENCIES] 无（纯函数口径工具）
# [CONSUMERS] 持仓对账/供数方（position_reconciler 等）→ FirmRiskAggregator.current_holdings 供数口径
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 今日买入 T+1 前不可卖（A股结算）；可卖权重=昨仓−今日已卖，负值兜底 0；只缩不增
# [MODIFY-GUARD] 32号 §6 T+1 口径行 + 31号 遗留 #30
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（权重为负/非有限值）
# [TESTS] tests/position/test_t1_sellable.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: last_session_weights（T-1 收盘持仓权重 {symbol: weight}）
# I2: today_sold_weights（今日已卖出权重 {symbol: weight}，可选）
# A1: t1_sellable_weights（可卖_i = max(0, 昨仓_i − 今卖_i)；今买不在输入域——T+1 冻结）
# O1: {symbol: 可卖权重}（供 FirmRiskAggregator §2.3 净额截断 current_holdings 口径）
# [/ALGO_FLOW]
"""T+1 可卖持仓口径工具（31号 遗留 #30 / 32号 §6 T+1 口径行）。

A 股 T+1 结算：当日买入的标的当日不可卖。FirmRiskAggregator §2.3 冲突净额截断
`max(0, net + current_holdings)` 假设 current_holdings 全部可卖——若快照含今日
买入部分，极端场景会允许"卖出超过可卖量"的意愿进入下游。32号 §6 裁定口径：
current_holdings 应为 **T+1 口径可卖权重（昨持仓 − 今日已卖）**，数据供给方
（持仓对账/position_reconciler）按此口径供数。本模块是该口径的函数级工具。

Version: 1.0.0
"""

from __future__ import annotations

import math


def t1_sellable_weights(
    last_session_weights: dict[str, float],
    today_sold_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """计算 T+1 口径可卖权重（昨持仓 − 今日已卖，负值兜底 0）。

    口径声明（32号 §6）：
      - 输入必须是 **T-1 收盘持仓** 权重（昨仓），不含今日买入部分——
        今日买入 T+1 前冻结不可卖，不属于本函数输入域；
      - 今日已卖出部分从可卖量中扣减；
      - 结果负值（数据异常：卖出>昨仓）兜底 0（只缩不增，Fail-Closed）。

    Args:
        last_session_weights: {symbol: 昨仓权重}（相对总资金口径）
        today_sold_weights: {symbol: 今日已卖权重}，None=今日无卖出

    Returns:
        {symbol: T+1 可卖权重}，仅含昨仓中的标的（今卖中出现的非持仓标的忽略）

    Raises:
        ValueError: 权重为负或非有限值（NaN/Inf）
    """
    for sym, w in last_session_weights.items():
        if not math.isfinite(w) or w < 0:
            raise ValueError(f"{sym} 昨仓权重非法（须为有限非负值），got {w}")

    sold = today_sold_weights or {}
    for sym, w in sold.items():
        if not math.isfinite(w) or w < 0:
            raise ValueError(f"{sym} 今日已卖权重非法（须为有限非负值），got {w}")

    return {sym: max(0.0, w - sold.get(sym, 0.0)) for sym, w in last_session_weights.items()}
