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
"""

D-FACTOR-ANA-05 因子相关性去重——基于相关性矩阵去除冗余因子。

贪心算法：按 factor_values 的插入顺序遍历，若当前因子与已保留因子的相关性
绝对值均低于阈值，则保留；否则丢弃（已被高相关因子覆盖）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子值字典 dict[str, pd.Series]
#   fields: factor_id → 因子值序列（插入顺序即优先级）
#   code: factor_values 函数参数
# - id: I2
#   name: 相关性阈值 float
#   fields: 相关性绝对值阈值，默认 0.7
#   code: threshold=0.7
# 层: 算法
# - id: A1
#   name_zh: ① 因子相关性矩阵计算
#   name_en: compute_factor_correlation
#   intro: 调 correlation_analyzer 算出 N×N 因子相关系数矩阵
#   desc: 对 factor_values 两两算相关系数（L43/L77 调用）；空矩阵走兜底分支
#   inputs: I1
#   outputs: N×N 相关性矩阵 DataFrame
# - id: A2
#   name_zh: ② 冗余因子对扫描
#   name_en: find_redundant_pairs
#   intro: 上三角扫描矩阵，揪出所有相关性绝对值超阈值的因子对
#   desc: 遍历上三角，|corr|≥threshold 收集 (f1,f2,corr)，按 |corr| 降序排序（L46-54）
#   inputs: A1 I2
#   outputs: 冗余因子对列表 list[tuple]
# - id: A3
#   name_zh: ③ 贪心去重
#   name_en: dedup_factors
#   intro: 按插入顺序遍历，与已保留因子相关性都低于阈值才保留
#   desc: 贪心保留先出现因子；当前因子与任一已保留因子 |corr|≥threshold 即丢弃（L80-89）
#   inputs: A1 I2
#   outputs: 保留因子ID列表 list[str]
#   invariant: 纯函数无IO；保留先出现因子，删除后续高相关因子
# 层: 输出
# - id: O1
#   name_zh: 冗余因子对列表
#   name_en: list[tuple[str, str, float]]
#   intro: (因子1, 因子2, 相关系数) 三元组，按相关性绝对值降序
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 去重后保留因子ID列表
#   name_en: list[str]
#   intro: 保持插入顺序的存活因子清单
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A1 --> A3
# I2 --> A3
# A2 --> O1
# A3 --> O2
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
