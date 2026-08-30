# [BLUEPRINT] MOD-L02-002 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-01
# [MODULE] zephyr.factor.analysis.multifactor_tradability_mask
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; numpy
# [CONSUMERS] ic_ir_calc/multifactor_synthesis(IC计算前置门控)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——mask仅用t日及之前可观测状态(停牌/涨跌停/成交额); 仅在可交易池内计算IC
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 可交易标的<min_names->IC返回NaN; 全False mask->空截面
# [TESTS] tests/factor/test_multifactor_tradability_mask.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: is_suspended/is_limit_up/is_limit_down(bool DataFrame 日期×标的) + daily_amount(成交额) + min_amount(流动性阈值)
# F1: build_tradability_mask(可交易=未停牌 ∧ 未涨停 ∧ 未跌停 ∧ 成交额≥阈值; 防IC计算上游污染)
# F2: masked_rank_ic(仅可交易截面 spearman IC; 可交易数<min_names→NaN)
# O1: tradability_mask(bool DataFrame) + 掩码后 rank IC float
# [/ALGO_FLOW]
"""
25号memo Phase 4.1 Mask-First 可交易性掩码（tradability_mask，MVP 最高优先）。

解决 A 股因子 IC 计算的"上游污染"——停牌/涨跌停/流动性不足标的未排除导致
IC 虚高。消融实证（arXiv:2507.07107）：mask 合约是单一最大贡献者（+0.44 Sharpe），
忽略上游污染使表观 IC 虚高 18% 但实现 Sharpe -0.44。

因子工坊 IC 计算前置门控：仅在可交易池中计算 IC。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: is_suspended 参数
#   fields: 参数 is_suspended，类型注解 pd.DataFrame
#   code: multifactor_tradability_mask.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: is_limit_up 参数
#   fields: 参数 is_limit_up，类型注解 pd.DataFrame
#   code: multifactor_tradability_mask.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: is_limit_down 参数
#   fields: 参数 is_limit_down，类型注解 pd.DataFrame
#   code: multifactor_tradability_mask.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: daily_amount 参数
#   fields: 参数 daily_amount，类型注解 pd.DataFrame | None
#   code: multifactor_tradability_mask.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_tradability_mask
#   name_en: build_tradability_mask
#   intro: 构造可交易性掩码——可交易 = 未停牌 ∧ 未涨停 ∧ 未跌停 ∧ 成交额≥阈值。
#   desc: 构造可交易性掩码——可交易 = 未停牌 ∧ 未涨停 ∧ 未跌停 ∧ 成交额≥阈值。 Args: is_suspended/is_limit_up/is_limit_down: b…；源码 L101-L121
#   inputs: is_suspended is_limit_up is_limit_down daily_amount min_amount
#   outputs: pd.DataFrame
# - id: A2
#   name_zh: ② masked_rank_ic
#   name_en: masked_rank_ic
#   intro: 仅在可交易截面内计算 rank IC（spearman）。
#   desc: 仅在可交易截面内计算 rank IC（spearman）。 Args: factor_values: 单日期截面因子值（index=标的） forward_returns: 同截…；源码 L124-L150
#   inputs: factor_values forward_returns mask min_names
#   outputs: float
# 层: 输出
# - id: O1
#   name_zh: pd.DataFrame
#   name_en: pd.DataFrame
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: ic_ir_calc/multifactor_synthesis(IC计算前置门控)
# - id: O2
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: ic_ir_calc/multifactor_synthesis(IC计算前置门控)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "DEFAULT_MIN_AMOUNT",
    "MIN_IC_NAMES",
    "build_tradability_mask",
    "masked_rank_ic",
]

DEFAULT_MIN_AMOUNT = 1e7  # 日成交额 ≥1000 万视为流动性可交易
MIN_IC_NAMES = 5  # 可交易截面 <5 只不计算 IC（统计不可靠）


def build_tradability_mask(
    is_suspended: pd.DataFrame,
    is_limit_up: pd.DataFrame,
    is_limit_down: pd.DataFrame,
    daily_amount: pd.DataFrame | None = None,
    min_amount: float = DEFAULT_MIN_AMOUNT,
) -> pd.DataFrame:
    """构造可交易性掩码——可交易 = 未停牌 ∧ 未涨停 ∧ 未跌停 ∧ 成交额≥阈值。

    Args:
        is_suspended/is_limit_up/is_limit_down: bool DataFrame（日期×标的，index/columns 对齐）
        daily_amount: 日成交额 DataFrame（可选；None→不做流动性过滤）
        min_amount: 流动性阈值（默认 1000 万）

    Returns:
        bool DataFrame，True=可交易。
    """
    mask = ~(is_suspended | is_limit_up | is_limit_down)
    if daily_amount is not None:
        mask = mask & (daily_amount >= min_amount)
    return mask.fillna(False).astype(bool)


def masked_rank_ic(
    factor_values: pd.Series,
    forward_returns: pd.Series,
    mask: pd.Series,
    min_names: int = MIN_IC_NAMES,
) -> float:
    """仅在可交易截面内计算 rank IC（spearman）。

    Args:
        factor_values: 单日期截面因子值（index=标的）
        forward_returns: 同截面已实现前向收益（INV-004）
        mask: 同截面可交易掩码（True=可交易）
        min_names: 最小可交易标的数，不足返回 NaN

    Returns:
        spearman 相关系数；可交易数不足或常数列返回 NaN。
    """
    tradable = mask[mask].index
    f = factor_values.reindex(tradable).dropna()
    r = forward_returns.reindex(tradable).dropna()
    common = f.index.intersection(r.index)
    if len(common) < min_names:
        return float("nan")
    fc, rc = f.loc[common], r.loc[common]
    if fc.nunique() < 2 or rc.nunique() < 2:
        return float("nan")
    return float(fc.corr(rc, method="spearman"))
