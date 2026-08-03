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
"""D-FACTOR-ANA-04 因子相关性分析——计算因子间相关性矩阵。

纯函数模块，无 IO 依赖。计算多个因子值序列之间的 Spearman rank correlation，
用于识别冗余因子（高相关的因子提供相似信号）。
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
