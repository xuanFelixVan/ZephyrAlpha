# [BLUEPRINT] MOD-BT-082 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] src.zephyr.pf_alloc.core.vol_target_allocator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] TDM-E-L1 大盘总闸（UP-1 凯利简版仓位系数）；策略工厂 E8 组装分配（未来）
# [STARTUP] manual
# [INVARIANTS] 纯函数无 IO 无 datetime.now；K∈[min_weight,max_weight] 恒成立；
#   窗口不足/波动率为零时输出 min_weight（不可测量=不满仓）；平滑抑制换手
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(参数非法)
# [TESTS] tests/pf_alloc/test_vol_target_allocator.py
# [A_module] module_id=MOD-BT-082 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""波动率目标化仓位计算器（UP-1 凯利简版，TDM 升级蓝图 708342357f 批准待建项）。

原理：仓位系数 K = min(max, max(min, target_vol / realized_vol))，realized_vol 为
滚动窗口年化波动率，K 再经 EWMA 平滑抑制换手。窗口不足或波动率为零 → K=min_weight
（不可测量=不满仓，保守语义）。

Phase 2 升级位：K=E(R)/σ² 完整凯利版待车道 E 分布预测模型接入后扩展（蓝图 v0.1）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ANNUALIZATION = 244.0  # A 股年化交易日


def vol_target_weight(
    returns: pd.Series,
    target_vol: float = 0.15,
    window: int = 20,
    max_weight: float = 1.0,
    min_weight: float = 0.0,
    smooth_span: int = 5,
) -> pd.Series:
    """滚动波动率目标化仓位系数序列。

    Args:
        returns: 周期收益率序列（日频）。
        target_vol: 年化目标波动率（如 0.15=15%）。
        window: 滚动窗口（交易日）。
        max_weight: 仓位上限。
        min_weight: 仓位下限。
        smooth_span: K 的 EWMA 平滑跨度。

    Returns:
        与 returns 同索引的仓位系数序列（窗口不足段=min_weight）。
    """
    if window < 2:
        raise ValueError("window 需 ≥2")
    if not (0.0 < target_vol <= 5.0):
        raise ValueError("target_vol 需在 (0, 5.0] 内")
    if max_weight < min_weight:
        raise ValueError("max_weight 不得小于 min_weight")

    rets = pd.to_numeric(returns, errors="coerce")
    realized = rets.rolling(window).std(ddof=0) * np.sqrt(ANNUALIZATION)
    k = target_vol / realized.replace(0.0, np.nan)
    k = k.clip(lower=min_weight, upper=max_weight)
    k = k.ewm(span=smooth_span, adjust=False).mean()
    k = k.clip(lower=min_weight, upper=max_weight)
    return k.fillna(min_weight)


def latest_weight(returns: pd.Series, **kwargs) -> float:
    """便捷入口：返回最新一根的仓位系数。"""
    return float(vol_target_weight(returns, **kwargs).iloc[-1])
