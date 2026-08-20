# [BLUEPRINT] MOD-L02-005 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-04
# [MODULE] zephyr.factor.analysis.correlation_analyzer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS] zephyr.factor.analysis.correlation_dedup
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数——无IO依赖; 输入因子值对齐后计算Spearman相关性
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空DataFrame; 单因子->1x1矩阵; 数据不足->NaN
# [TESTS] tests/factor/test_correlation_analyzer.py
# [A_module] module_id=MOD-L02-005 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-04 因子相关性分析——计算因子间相关性矩阵。

纯函数模块，无 IO 依赖。计算多个因子值序列之间的 Spearman rank correlation，
用于识别冗余因子（高相关的因子提供相似信号）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 多因子值序列 factor_values
#   fields: dict[factor_id → pd.Series]，index 对齐、值为因子值
#   code: compute_factor_correlation L26-44
# - id: I2
#   name: 滚动窗口 window
#   fields: int 滚动窗口期数，默认 60
#   code: compute_rolling_correlation L47-49
# 层: 算法
# - id: A1
#   name_zh: ① Spearman 因子相关性矩阵
#   name_en: compute_factor_correlation
#   intro: 把多个因子值序列拼成面板算 Spearman 秩相关矩阵，找提供相似信号的冗余因子
#   desc: 空输入返回空 DataFrame；pd.DataFrame(factor_values) 组装面板自动对齐 index（缺失为 NaN）；panel.corr(method="spearman") 得对称矩阵（L38-44）
#   inputs: I1
#   outputs: 对称相关性矩阵（index/columns=factor_id）
#   invariant: 纯函数无 IO；空输入→空DataFrame，单因子→1x1矩阵，数据不足→NaN
# - id: A2
#   name_zh: ② 因子对滚动 Pearson 相关性
#   name_en: compute_rolling_correlation
#   intro: 每个时间点用过去 window 期数据算两两因子的滚动相关性，看相关关系随时间变化
#   desc: 因子数<2 返回空 DataFrame；组装面板后双重循环取 i<j 因子对，逐对 panel[f1].rolling(window).corr(panel[f2])，结果列名 "f1_f2"（L62-79）
#   inputs: I1 I2
#   outputs: 滚动相关性 DataFrame（index=时间，columns=因子对）
#   invariant: 纯函数无 IO
# 层: 输出
# - id: O1
#   name_zh: 因子相关性矩阵
#   name_en: Spearman correlation DataFrame
#   intro: 因子间秩相关对称矩阵，高相关因子对即冗余候选
#   downstream: zephyr.factor.analysis.correlation_dedup MOD-L02-006（[CONSUMERS]）
# - id: O2
#   name_zh: 因子对滚动相关性时序
#   name_en: rolling correlation DataFrame
#   intro: 因子两两相关性随时间变化的时序面板，供相关性稳定性分析
#   downstream: 无下游/内部使用（分析工具）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> O1
# A2 --> O2
"""

from __future__ import annotations

import pandas as pd


def compute_factor_correlation(
    factor_values: dict[str, pd.Series],
) -> pd.DataFrame:
    """计算多因子值的相关性矩阵（Spearman rank correlation）。

    Args:
        factor_values: factor_id → pd.Series（index 对齐，值为因子值）

    Returns:
        对称相关性矩阵 DataFrame，index/columns=factor_id。
        空输入返回空 DataFrame。
    """
    if not factor_values:
        return pd.DataFrame()
    # 组装为 DataFrame，自动对齐 index（缺失为 NaN）
    panel = pd.DataFrame(factor_values)
    if panel.empty:
        return pd.DataFrame()
    return panel.corr(method="spearman")


def compute_rolling_correlation(
    factor_values: dict[str, pd.Series],
    window: int = 60,
) -> pd.DataFrame:
    """计算因子间滚动相关性（Pearson）。

    在每个时间点，用过去 window 期的数据计算两两因子相关性。

    Args:
        factor_values: factor_id → pd.Series
        window: 滚动窗口大小，默认 60

    Returns:
        DataFrame，index=时间，columns=因子对（如 "f1_f2"），values=滚动相关性。
    """
    if len(factor_values) < 2:
        return pd.DataFrame()
    panel = pd.DataFrame(factor_values)
    if panel.empty:
        return pd.DataFrame()
    # 两两计算滚动相关性
    cols = list(panel.columns)
    pairs: list[tuple[str, str]] = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append((cols[i], cols[j]))
    if not pairs:
        return pd.DataFrame()
    result: dict[str, pd.Series] = {}
    for f1, f2 in pairs:
        roll_corr = panel[f1].rolling(window).corr(panel[f2])
        result[f"{f1}_{f2}"] = roll_corr
    return pd.DataFrame(result)
