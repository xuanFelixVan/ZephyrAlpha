# [BLUEPRINT] MOD-BT-086 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] src.zephyr.pf_alloc.core.synergy_dedup
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] 策略工厂 E5 协同去重（考试→去重→入库）；C5 差异化分析；
#   zephyr.strategy_pipeline.intake.cluster_heads（C6 自动入库编排器，裁定后追加令接线）
# [STARTUP] manual
# [INVARIANTS] 纯函数无 IO；两种输入契约=同一去重职责：①returns+sharpe（星形贪心，
#   簇首=Sharpe 最高者，历史 API 原样保留）②corr-pairs+strength（并查集核
#   cluster_heads_from_corr，E5 管线唯一算法实现，intake 薄委托消费）；
#   簇成员不删除只标注 redundant_of
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
        return (
            [{"head": next(iter(returns), ""), "members": list(returns.keys()), "cluster_type": "single"}]
            if returns
            else []
        )

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
        clusters.append(
            {
                "head": head,
                "head_sharpe": sharpe.get(head, 0.0),
                "members": cluster_members,
                "correlations": {m: round(float(corr.loc[head, m]), 3) for m in cluster_members if m != head},
            }
        )

    return clusters


# ---------- E5 管线唯一算法核（自 intake.py MOD-BT-189 逐字迁入，2026-10-04 收敛；蒸发后重施）----------
def cluster_heads_from_corr(
    corr: dict[tuple[str, str], float],
    passed: set[str],
    rho: float = 0.70,
    strength: dict[str, float] | None = None,
) -> tuple[set[str], dict[str, str]]:
    """ρ>阈值 贪心聚类（并查集核，E5 唯一算法实现）。

    Args:
        corr: {(a, b): ρ} 无序对相关矩阵（PIT 活矩阵/历史矩阵均可，由调用方注入）。
        passed: 参与聚类的及格集。
        rho: 相关系数阈值（默认 0.70，只取正相关；负相关不聚——对冲是价值不是冗余）。
        strength: 语义=越小越强（传 p 值即「簇首=证据最强」——C5 人工先例「簇首=Sharpe
            最高」的 p 值等价）；平局/缺省回落 sid 最小，保证确定性。

    Returns:
        (簇首集, redundant→簇首 映射)。
    """
    order = sorted(passed)
    parent: dict[str, str] = {s: s for s in order}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), r in sorted(corr.items()):
        if a in passed and b in passed and r > rho:
            ra, rb = find(a), find(b)
            if ra != rb:
                lo, hi = sorted((ra, rb))
                parent[hi] = lo
    heads: set[str] = set()
    redundant: dict[str, str] = {}
    members: dict[str, list[str]] = {}
    for s in order:
        members.setdefault(find(s), []).append(s)
    for root, mem in members.items():
        if strength:
            head = min(mem, key=lambda s: (strength.get(s, float("inf")), s))
        else:
            head = min(mem)
        heads.add(head)
        for s in mem:
            if s != head:
                redundant[s] = head
    return heads, redundant
