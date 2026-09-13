# [BLUEPRINT] MOD-PA-020 | docs/03_modules/_domain_portfolio_alloc/forward_stop_loss/blueprint.md
# [MODULE] zephyr.pf_alloc.core.forward_stop_loss
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] TDM 出场流（UP-2 前瞻概率止损）；策略工厂 E8 组装分配
# [STARTUP] manual
# [INVARIANTS] 纯函数无 IO；概率阈值可配置；保守语义（P(跌)≥阈值→建议减仓）；
#   止损评审≠强制平仓——输出信号供上游决策，不直接操作仓位
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(参数非法)
# [TESTS] tests/pf_alloc/test_forward_stop_loss.py
# [A_module] module_id=MOD-PA-020 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""前瞻概率止损模块（TDM 升级蓝图 UP-2）——用分布预测 P(跌) 替代固定百分比止损。

原理（v0.1 蓝图 UP-2）：
  传统止损 = 固定百分比（如 -5% 砍仓），不区分正常回撤和趋势反转。
  前瞻概率止损 = 用分布预测的 P(跌) 判断当前是否处于高概率下跌状态，
  超过阈值（默认 65%）→ 输出止损评审信号（供上游决策减仓/对冲）。

来源：Owner 2025-09 笔记 UP-2 前瞻概率止损 + TDM 升级蓝图 v0.1；
  前沿互证 = AlphaAgent（正则化探索抗衰减）、harbourfront（停损规则区分正常回撤
  与真衰减）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def forward_stop_signal(
    returns: pd.Series,
    window: int = 20,
    decline_threshold: float = 0.65,
    min_observations: int = 5,
) -> pd.DataFrame:
    """前瞻概率止损信号生成。

    用滚动窗口估算日收益为负的无条件概率，当该概率超过 decline_threshold 时
    输出止损评审信号。

    Args:
        returns: 日收益率序列。
        window: 滚动窗口大小。
        decline_threshold: 止损触发概率阈值（如 0.65=65%）。
        min_observations: 最少有效观测数（低于此不输出信号）。

    Returns:
        DataFrame with columns [neg_prob, stop_review]。
        neg_prob = 滚动窗口内负收益占比（0~1）。
        stop_review = True 表示建议止损评审。
    """
    if window < min_observations:
        raise ValueError(f"window({window}) < min_observations({min_observations})")
    if not (0.5 < decline_threshold <= 1.0):
        raise ValueError(f"decline_threshold 需在 (0.5, 1.0] 内: {decline_threshold}")

    rets = pd.to_numeric(returns, errors="coerce")
    neg = (rets < 0).astype(float)
    neg_prob = neg.rolling(window, min_periods=min_observations).mean()
    stop_review = (neg_prob >= decline_threshold).fillna(False)
    return pd.DataFrame({"neg_prob": neg_prob, "stop_review": stop_review})


def composite_stop_score(
    quantile_predictions: pd.DataFrame,
    realized: pd.Series,
    p_decline_threshold: float = 0.65,
) -> pd.DataFrame:
    """基于分位数预测的复合止损评分（升级版，需分布预测模型产出）。

    当车道 E 分布预测产出 q05/q50/q95 时，可以计算：
    - P(跌) ≈ 从分位数插值得到的 P(realized < 0)
    - 尾部风险比 = (q50 - q05) / (q95 - q50)，比值越大左尾越厚
    综合两个指标生成止损评审信号。

    Args:
        quantile_predictions: DataFrame with columns [q05, q50, q95]。
        realized: 实际收益率序列（用于验证，不用于信号生成）。
        p_decline_threshold: P(跌) 阈值（默认 0.65）。

    Returns:
        DataFrame with columns [p_decline, tail_ratio, stop_review]。
    """
    q05 = quantile_predictions["q05"]
    q50 = quantile_predictions["q50"]
    q95 = quantile_predictions["q95"]

    # 从三分布位点插值 P(R<0)：假设 q05<0<q95 段内近似线性
    p_decline = pd.Series(index=quantile_predictions.index, dtype=float)
    for i in range(len(q05)):
        lo, mid, hi = q05.iloc[i], q50.iloc[i], q95.iloc[i]
        if mid <= 0:
            p_decline.iloc[i] = 0.75  # 中位数<0 → 至少 75%
        elif lo >= 0:
            p_decline.iloc[i] = 0.25  # q05≥0 → 下跌概率很低
        else:
            # 在 [lo, mid] 段内线性插值找零点
            p_decline.iloc[i] = 0.25 + 0.25 * (0 - lo) / (mid - lo) if mid != lo else 0.5

    # 尾部风险比：左尾宽 / 全宽
    spread = q95 - q05
    tail_ratio = pd.Series(index=quantile_predictions.index, dtype=float)
    for i in range(len(q05)):
        full = q95.iloc[i] - q05.iloc[i]
        if full == 0:
            tail_ratio.iloc[i] = 0.5
        else:
            left_tail = max(0.0, q50.iloc[i] - q05.iloc[i])
            tail_ratio.iloc[i] = left_tail / full

    stop_review = (p_decline >= p_decline_threshold) | (tail_ratio >= 0.60)
    return pd.DataFrame({
        "p_decline": p_decline,
        "tail_ratio": tail_ratio,
        "stop_review": stop_review,
    })
