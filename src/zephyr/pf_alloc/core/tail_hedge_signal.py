# [BLUEPRINT] MOD-PA-024 | docs/03_modules/_domain_portfolio_alloc/tail_hedge_signal/blueprint.md
# [MODULE] zephyr.pf_alloc.core.tail_hedge_signal
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] TDM 风控层（UP-5 尾部对冲指令）；策略工厂 E8 组装分配
# [STARTUP] manual
# [INVARIANTS] 纯函数无 IO；CVaR 阈值可配置；信号仅供决策参考非执行指令
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(参数非法)
# [TESTS] tests/pf_alloc/test_tail_hedge_signal.py
# [A_module] module_id=MOD-PA-024 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""尾部对冲信号生成器（TDM 升级蓝图 UP-5）——预测 CVaR 破阈值时生成对冲建议。

原理（对标 Owner 2025-09 笔记 9.1 尾部风险对冲）：
  组合预测 CVaR（条件 VaR）超过风控阈值 → 输出对冲建议。
  CVaR 用分布预测的分位数计算（非历史回溯）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def tail_hedge_signal(
    portfolio_returns: pd.Series,
    cvar_threshold: float = -0.03,
    confidence: float = 0.05,
    window: int = 60,
) -> pd.DataFrame:
    """尾部对冲信号（预测 CVaR 破阈值→对冲建议）。

    Args:
        portfolio_returns: 组合日收益率序列。
        cvar_threshold: CVaR 阈值（如 -0.03 = 日损失 3%）。
        confidence: VaR/CVaR 置信水平（默认 5%）。
        window: 滚动窗口。

    Returns:
        DataFrame with columns [cvar_pred, hedge_signal, cvar_excess]。
        hedge_signal = True 表示建议对冲。
        cvar_excess = cvar_pred - cvar_threshold（正=超限）。
    """
    if window < 10:
        raise ValueError("window 需 ≥10")
    if not (0.0 < confidence < 0.5):
        raise ValueError(f"confidence 需在 (0, 0.5) 内: {confidence}")

    rets = pd.to_numeric(portfolio_returns, errors="coerce")
    var_level = rets.rolling(window).quantile(confidence)
    # CVaR 近似 = 窗口内低于 VaR 分位的均值
    cvar_pred: list[float | None] = []
    v = var_level.values
    r = rets.values
    for i in range(len(rets)):
        if i < window or np.isnan(v[i]):
            cvar_pred.append(None)
            continue
        tail = r[max(0, i - window):i + 1]
        tail = tail[tail <= v[i]]
        cvar_pred.append(float(tail.mean()) if len(tail) > 0 else None)
    cvar_series = pd.Series(cvar_pred, index=rets.index)
    hedge = (cvar_series < cvar_threshold).fillna(False)
    excess = cvar_series - cvar_threshold
    return pd.DataFrame({
        "cvar_pred": cvar_series,
        "hedge_signal": hedge,
        "cvar_excess": excess,
    })
