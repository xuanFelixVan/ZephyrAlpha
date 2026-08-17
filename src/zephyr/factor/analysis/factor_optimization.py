# [BLUEPRINT] MOD-L02-012 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-11
# [MODULE] zephyr.factor.analysis.factor_optimization
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.multifactor_synthesis
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——优化仅使用历史已实现收益
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据不足->等权兜底; 优化失败->等权兜底
# [TESTS] tests/factor/test_factor_optimization.py
# [A_module] module_id=MOD-L02-012 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-11 因子优化——优化多因子合成权重以最大化目标函数。

提供两种优化目标：
1. max_ir：最大化合成因子的信息比率 IR
2. min_variance：最小化合成因子的收益方差

用 scipy.optimize 网格搜索/约束优化求权重。权重非负且和为1。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 多因子值字典 dict[str, pd.Series]
#   fields: factor_id → 因子值序列，组装成面板
#   code: factor_values 函数参数
# - id: I2
#   name: 前向收益面板 DataFrame
#   fields: index=date，columns=symbol 的已实现前向收益
#   code: forward_returns 函数参数
# - id: I3
#   name: 优化目标配置 str
#   fields: factor_optimization.default_objective，默认 max_ir
#   code: _config.yaml L21-22
# 层: 算法
# - id: A1
#   name_zh: ① 负IR损失函数
#   name_en: _neg_ir
#   intro: 用当前权重合成信号算IC序列和IR，取负号供最小化
#   desc: synth=panel.fillna0@w → compute_ic_series(horizon=5) → compute_ir → -ir（L44-59）
#   inputs: I1 I2
#   outputs: -IR 标量
#   invariant: INV-004 PIT铁律——仅用历史已实现收益
# - id: A2
#   name_zh: ② SLSQP约束权重优化
#   name_en: optimize_weights
#   intro: 在权重非负且和为1的约束下优化合成权重
#   desc: scipy minimize(method=SLSQP)，约束Σw=1、0≤w≤1；max_ir走A1损失，min_variance走var(panel@w)；scipy缺失/不收敛/异常→等权兜底（L62-115）
#   inputs: I1 I2 I3 A1
#   outputs: 权重字典 dict[factor_id→weight]
#   invariant: 权重非负且和为1；失败一律等权
# - id: A3
#   name_zh: ③ 组合信号合成
#   name_en: evaluate_portfolio
#   intro: 按给定权重把多因子面板加权成一条合成信号
#   desc: 过滤有效因子 → 权重归一化（Σ<1e-10退等权）→ panel.fillna0@w（L118-143）
#   inputs: I1 A2
#   outputs: 合成信号 pd.Series
# 层: 输出
# - id: O1
#   name_zh: 优化后因子权重
#   name_en: dict[str, float]
#   intro: factor_id→权重，非负和为1，优化失败返回等权
#   invariant: Σw=1，w≥0
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 加权合成信号 pd.Series
#   name_en: synthesized signal
#   intro: 用指定权重合成的组合信号序列
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I1 --> A2
# I2 --> A2
# I3 --> A2
# A2 --> A3
# I1 --> A3
# A2 --> O1
# A3 --> O2
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from zephyr.factor.analysis import load_analysis_config
from zephyr.factor.analysis.multifactor_synthesis import synthesize_equal_weight
from zephyr.factor.core.evaluation.metrics import compute_ic_series, compute_ir

log = logging.getLogger(__name__)


def _get_default_objective() -> str:
    """从配置读取默认优化目标。"""
    cfg = load_analysis_config()
    return str(cfg.get("factor_optimization", {}).get("default_objective", "max_ir"))


def _neg_ir(
    weights: np.ndarray,
    factor_panel: pd.DataFrame,
    return_panel: pd.DataFrame,
) -> float:
    """计算 -IR（用于最小化 = 最大化 IR）。"""
    synth = factor_panel.fillna(0).to_numpy() @ weights
    # 组装面板用于 IC 计算
    synth_panel = pd.DataFrame(
        np.outer(synth, np.ones(factor_panel.shape[1])),
        index=factor_panel.index, columns=factor_panel.columns,
    )
    ic_series = compute_ic_series(synth_panel, return_panel, 5)
    ir = compute_ir(ic_series)
    return -ir


def optimize_weights(
    factor_values: dict[str, pd.Series],
    forward_returns: pd.DataFrame,
    objective: str | None = None,
) -> dict[str, float]:
    """优化多因子合成权重。

    Args:
        factor_values: factor_id → pd.Series（index=date, values=symbol→因子值）
            注意：这里期望的是面板形式，每个 pd.Series 是某日期的截面因子值
        forward_returns: 前向收益面板，index=date, columns=symbol
        objective: 优化目标 "max_ir" / "min_variance"，None 时从配置读取

    Returns:
        factor_id → 权重（非负，和为1）。优化失败返回等权。
    """
    if objective is None:
        objective = _get_default_objective()
    if not factor_values:
        return {}
    fids = list(factor_values.keys())
    n = len(fids)
    if n == 1:
        return {fids[0]: 1.0}
    # 组装因子面板
    panel = pd.DataFrame(factor_values)
    if panel.empty:
        return {fid: 1.0 / n for fid in fids}
    try:
        from scipy.optimize import minimize
    except ImportError:
        log.warning("factor_optimization: scipy 不可用，返回等权")
        return {fid: 1.0 / n for fid in fids}
    # 初始权重：等权
    x0 = np.full(n, 1.0 / n)
    # 约束：权重和=1，权重>=0
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = [(0.0, 1.0)] * n
    if objective == "max_ir":
        def loss(w: np.ndarray) -> float:
            return _neg_ir(w, panel, forward_returns)
    elif objective == "min_variance":
        def loss(w: np.ndarray) -> float:
            return float(np.var(panel.fillna(0).to_numpy() @ w))
    else:
        log.warning("factor_optimization: 未知目标 '%s'，返回等权", objective)
        return {fid: 1.0 / n for fid in fids}
    try:
        result = minimize(loss, x0, method="SLSQP", bounds=bounds, constraints=constraints)
        if result.success:
            w = result.x
            return {fids[i]: float(w[i]) for i in range(n)}
        log.warning("factor_optimization: 优化未收敛，返回等权")
    except Exception:
        log.exception("factor_optimization: 优化失败，返回等权")
    return {fid: 1.0 / n for fid in fids}


def evaluate_portfolio(
    weights: dict[str, float],
    factor_values: dict[str, pd.Series],
) -> pd.Series:
    """用给定权重合成因子组合信号。

    Args:
        weights: factor_id → 权重
        factor_values: factor_id → pd.Series

    Returns:
        合成信号 pd.Series
    """
    if not weights or not factor_values:
        return pd.Series(dtype=float)
    # 过滤有效因子
    valid = {k: v for k, v in factor_values.items() if k in weights}
    if not valid:
        return pd.Series(dtype=float)
    panel = pd.DataFrame(valid)
    w = np.array([weights[k] for k in panel.columns])
    total = w.sum()
    if total < 1e-10:
        return synthesize_equal_weight(valid)
    w = w / total
    return pd.Series(panel.fillna(0).to_numpy() @ w, index=panel.index)
