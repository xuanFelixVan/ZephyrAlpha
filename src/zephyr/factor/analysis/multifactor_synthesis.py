# [BLUEPRINT] MOD-L02-011 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-10
# [MODULE] zephyr.factor.analysis.multifactor_synthesis
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.ic_ir_calc
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——合成仅使用同期因子值; IC加权权重来自历史IC(不引入未来函数)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空Series; 权重不匹配->等权兜底; 回归失败->等权兜底
# [TESTS] tests/factor/test_multifactor_synthesis.py
# [A_module] module_id=MOD-L02-011 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-10 多因子合成——将多个因子值合成为综合信号。

提供三种合成方法：
1. 等权合成（synthesize_equal_weight）：所有因子等权平均，最简单的基线
2. IC加权合成（synthesize_ic_weighted）：按历史 IC 均值分配权重
3. 回归优化合成（synthesize_regression）：用历史前向收益回归求权重

统一入口 synthesize() 通过 method 参数选择。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 多因子值字典 dict[str, pd.Series]
#   fields: factor_id → 因子值序列（index 对齐）
#   code: factor_values 函数参数
# - id: I2
#   name: IC权重字典 dict[str, float]
#   fields: factor_id → 历史IC均值权重（ic_weighted 方法用）
#   code: ic_weights 函数参数
# - id: I3
#   name: 前向收益 pd.Series
#   fields: 已实现前向收益，index 与因子值对齐（regression 方法用）
#   code: forward_returns 函数参数
# 层: 算法
# - id: A1
#   name_zh: ① 等权合成
#   name_en: synthesize_equal_weight
#   intro: 所有因子等权平均，最简单的基线合成
#   desc: panel=DataFrame(factor_values) → panel.mean(axis=1)（L46-49）；空输入返回空Series
#   inputs: I1
#   outputs: 合成信号 pd.Series
# - id: A2
#   name_zh: ② IC加权合成
#   name_en: synthesize_ic_weighted
#   intro: 按历史IC均值归一化分配权重后加权求和
#   desc: 过滤零权重 → w/Σ|w| 归一化 → Σ wi·fi（L65-78）；无有效权重退等权
#   inputs: I1 I2
#   outputs: 合成信号 pd.Series
#   invariant: 权重来自历史IC不引入未来函数；权重不匹配退等权
# - id: A3
#   name_zh: ③ 回归优化合成
#   name_en: synthesize_regression
#   intro: 用历史前向收益对因子面板做OLS回归，拿回归系数当权重
#   desc: 取交集对齐 → w=(XᵀX)⁻¹Xᵀy 经 np.linalg.lstsq 求解 → panel@coeffs（L97-112）；数据不足/求解失败退等权
#   inputs: I1 I3
#   outputs: 合成信号 pd.Series
# - id: A4
#   name_zh: ④ 合成统一入口分发
#   name_en: synthesize
#   intro: 按method参数把调用分发到等权/IC加权/回归三种合成
#   desc: method=equal_weight/ic_weighted/regression 分别调A1/A2/A3；未知方法或regression缺forward_returns退等权（L130-142）
#   inputs: I1 I2 I3 A1 A2 A3
#   outputs: 合成信号 pd.Series
#   invariant: INV-004 PIT铁律——合成仅用同期因子值
# 层: 输出
# - id: O1
#   name_zh: 多因子合成信号 pd.Series
#   name_en: synthesized signal
#   intro: 多因子合成后的综合信号序列，供信号提供与策略执行使用
#   downstream: signal_providers MOD-L06-001；strategy_runner MOD-L05-001；factor_optimization MOD-L02-012
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I3 --> A3
# A1 --> A4
# A2 --> A4
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from zephyr.factor.analysis import load_analysis_config

log = logging.getLogger(__name__)


def _get_default_method() -> str:
    """从配置读取默认合成方法（analysis/_config.yaml multifactor_synthesis 节）。"""
    cfg = load_analysis_config()
    return str(cfg.get("multifactor_synthesis", {}).get("default_method", "ic_weighted"))


def synthesize_equal_weight(
    factor_values: dict[str, pd.Series],
) -> pd.Series:
    """等权合成——所有因子值等权平均。

    Args:
        factor_values: factor_id → pd.Series（index 对齐）

    Returns:
        合成信号 pd.Series。空输入返回空 Series。
    """
    if not factor_values:
        return pd.Series(dtype=float)
    panel = pd.DataFrame(factor_values)
    return panel.mean(axis=1)


def synthesize_ic_weighted(
    factor_values: dict[str, pd.Series],
    ic_weights: dict[str, float],
) -> pd.Series:
    """IC 加权合成——按历史 IC 均值分配权重。

    Args:
        factor_values: factor_id → pd.Series
        ic_weights: factor_id → 权重（历史 IC 均值，会归一化）

    Returns:
        合成信号 pd.Series。权重不匹配时退化为等权。
    """
    if not factor_values:
        return pd.Series(dtype=float)
    # 过滤出有权重的因子
    weights = {k: float(v) for k, v in ic_weights.items() if k in factor_values and v != 0}
    if not weights:
        log.warning("ic_weighted: 无有效权重，退化为等权")
        return synthesize_equal_weight(factor_values)
    # 归一化权重（保证和为1）
    total = sum(abs(w) for w in weights.values())
    if total < 1e-10:
        return synthesize_equal_weight(factor_values)
    norm_weights = {k: w / total for k, w in weights.items()}
    panel = pd.DataFrame({k: factor_values[k] * norm_weights[k] for k in norm_weights})
    return panel.sum(axis=1)


def synthesize_regression(
    factor_values: dict[str, pd.Series],
    forward_returns: pd.Series,
) -> pd.Series:
    """回归优化合成——用历史前向收益对因子值做回归求权重。

    将多因子面板作为自变量，前向收益作为因变量，做 OLS 回归，
    用回归系数作为权重合成信号。

    Args:
        factor_values: factor_id → pd.Series
        forward_returns: 前向收益，index 与因子值对齐

    Returns:
        合成信号 pd.Series。回归失败时退化为等权。
    """
    if not factor_values:
        return pd.Series(dtype=float)
    panel = pd.DataFrame(factor_values)
    common = panel.index.intersection(forward_returns.dropna().index)
    if len(common) < len(panel.columns) + 1:
        log.warning("regression: 数据不足，退化为等权")
        return synthesize_equal_weight(factor_values)
    X = panel.loc[common].fillna(0).to_numpy()
    y = forward_returns.loc[common].to_numpy()
    try:
        # OLS: w = (X^T X)^-1 X^T y
        coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError:
        log.warning("regression: 矩阵求解失败，退化为等权")
        return synthesize_equal_weight(factor_values)
    return panel.fillna(0) @ coeffs


def synthesize(
    factor_values: dict[str, pd.Series],
    method: str | None = None,
    **kwargs,
) -> pd.Series:
    """多因子合成统一入口。

    Args:
        factor_values: factor_id → pd.Series
        method: 合成方法 "equal_weight" / "ic_weighted" / "regression"；
            None 时从 analysis/_config.yaml 的 multifactor_synthesis.default_method 读取
        **kwargs: 方法特定参数（如 ic_weights, forward_returns）

    Returns:
        合成信号 pd.Series
    """
    if method is None:
        method = _get_default_method()
    if method == "equal_weight":
        return synthesize_equal_weight(factor_values)
    if method == "ic_weighted":
        ic_weights = kwargs.get("ic_weights", {})
        return synthesize_ic_weighted(factor_values, ic_weights)
    if method == "regression":
        forward_returns = kwargs.get("forward_returns")
        if forward_returns is None:
            log.warning("synthesize: regression 需要 forward_returns 参数，退化为等权")
            return synthesize_equal_weight(factor_values)
        return synthesize_regression(factor_values, forward_returns)
    log.warning("synthesize: 未知方法 '%s'，退化为等权", method)
    return synthesize_equal_weight(factor_values)
