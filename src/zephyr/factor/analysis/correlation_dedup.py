# [BLUEPRINT] MOD-L02-006 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-05
# [MODULE] zephyr.factor.analysis.correlation_dedup
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.correlation_analyzer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数——无IO依赖; 贪心去重——保留先出现的因子，删除后续高相关因子
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空列表; 阈值无效->默认0.7
# [TESTS] tests/factor/test_correlation_dedup.py
# [A_module] module_id=MOD-L02-006 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-FACTOR-ANA-05 因子相关性去重——基于相关性矩阵去除冗余因子。

贪心算法：按 factor_values 的插入顺序遍历，若当前因子与已保留因子的相关性
绝对值均低于阈值，则保留；否则丢弃（已被高相关因子覆盖）。
"""
from __future__ import annotations

import pandas as pd

from zephyr.factor.analysis.correlation_analyzer import compute_factor_correlation


def find_redundant_pairs(
    factor_values: dict[str, pd.Series],
    threshold: float = 0.7,
) -> list[tuple[str, str, float]]:
    """找出所有相关性绝对值超过阈值的因子对。

    Args:
        factor_values: factor_id → pd.Series
        threshold: 相关性阈值（绝对值），默认 0.7

    Returns:
        列表 of (factor_id_1, factor_id_2, correlation)，按相关性绝对值降序。
    """
    if len(factor_values) < 2:
        return []
    corr = compute_factor_correlation(factor_values)
    if corr.empty:
        return []
    pairs: list[tuple[str, str, float]] = []
    cols = list(corr.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = float(corr.iloc[i, j])
            if abs(val) >= threshold:
                pairs.append((cols[i], cols[j], val))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    return pairs


def dedup_factors(
    factor_values: dict[str, pd.Series],
    threshold: float = 0.7,
) -> list[str]:
    """基于相关性去重，返回保留的因子 ID 列表（贪心算法）。

    按 factor_values 的插入顺序遍历，若当前因子与已保留因子的相关性绝对值
    均低于阈值，则保留；否则丢弃。

    Args:
        factor_values: factor_id → pd.Series（插入顺序即优先级）
        threshold: 相关性阈值（绝对值），默认 0.7

    Returns:
        保留的 factor_id 列表（保持插入顺序）。
    """
    if not factor_values:
        return []
    if len(factor_values) == 1:
        return list(factor_values.keys())
    corr = compute_factor_correlation(factor_values)
    if corr.empty:
        return list(factor_values.keys())
    kept: list[str] = []
    for fid in factor_values:
        is_redundant = False
        for k in kept:
            val = corr.loc[fid, k]
            if pd.notna(val) and abs(float(val)) >= threshold:
                is_redundant = True
                break
        if not is_redundant:
            kept.append(fid)
    return kept
