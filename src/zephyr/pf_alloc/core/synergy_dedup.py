# [BLUEPRINT] MOD-BT-086 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] src.zephyr.pf_alloc.core.synergy_dedup
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] 策略工厂 E5 协同去重（考试→去重→入库）；C5 差异化分析
# [STARTUP] manual
# [INVARIANTS] 纯函数无 IO；贪心聚类按 Sharpe 降序；相关性阈值可配置；
#   簇首=Sharpe 最高者；簇成员不删除只标注 redundant_of
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(参数非法)
# [TESTS] tests/backtest/test_synergy_dedup.py
# [A_module] module_id=MOD-BT-086 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""策略协同去重——相关性聚类+簇首选择，消除冗余策略。

原理：多策略组合的价值来自低相关性。当两条策略日收益相关系数 |ρ|>threshold 时，
保留 Sharpe 较高者为簇首，较低者标 redundant_of=簇首。贪心聚类确保 O(n²) 单遍。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def synergy_dedup(
    returns: dict[str, pd.Series],
    sharpe: dict[str, float],
    corr_threshold: float = 0.70,
) -> list[dict[str, any]]:
    """相关性聚类去重。

    Args:
        returns: {strategy_id: 日收益 Series}。
        sharpe: {strategy_id: Sharpe}。
        corr_threshold: 相关系数阈值（默认 0.70）。

    Returns:
        聚类结果列表，每簇含 head + members（含 redundant_of 指针）。
    """
    if len(returns) < 2:
        return [{"head": next(iter(returns), ""), "members": list(returns.keys()), "cluster_type": "single"}] if returns else []

    df = pd.DataFrame(returns).dropna()
    if len(df) < 10:
        return [{"head": sid, "members": [sid], "cluster_type": "single"} for sid in returns]

    corr = df.corr()
    order = sorted(returns.keys(), key=lambda s: -sharpe.get(s, 0.0))
    assigned: dict[str, str] = {}  # sid -> head_sid
    clusters: list[dict] = []

    for head in order:
        if head in assigned:
            continue
        cluster_members = [head]
        for other in order:
            if other == head or other in assigned:
                continue
            rho = float(corr.loc[head, other])
            if abs(rho) >= corr_threshold:
                assigned[other] = head
                cluster_members.append(other)
        for m in cluster_members:
            assigned[m] = head
        clusters.append({
            "head": head,
            "head_sharpe": sharpe.get(head, 0.0),
            "members": cluster_members,
            "correlations": {m: round(float(corr.loc[head, m]), 3) for m in cluster_members if m != head},
        })

    return clusters
