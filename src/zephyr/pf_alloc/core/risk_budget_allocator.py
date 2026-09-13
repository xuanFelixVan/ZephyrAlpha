# [BLUEPRINT] MOD-PA-022 | docs/03_modules/_domain_portfolio_alloc/risk_budget_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.core.risk_budget_allocator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] TDM 组合流（UP-3 前瞻风险预算）；策略工厂 E8 组装分配
# [STARTUP] manual
# [INVARIANTS] 纯函数无 IO；权重 = 风险贡献归一化（sum=1.0）；预测分布由车道 E 分位数回归产出；
#   风险度量 = 预测分布的 VaR/CVaR（非历史回溯）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(参数非法)
# [TESTS] tests/pf_alloc/test_risk_budget_allocator.py
# [A_module] module_id=MOD-PA-022 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""前瞻风险预算分配器（TDM 升级蓝图 UP-3）——用预测分布的 VaR/CVaR 分配资本。

三种分配模式：
  inverse_var  = 反 VaR 加权（VaR 越低权重越高）
  risk_parity  = 等风险贡献近似
  sharpe_weight = 预测 Sharpe 加权（E(R)/VaR softmax）
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def risk_budget_allocate(
    var_estimates: dict[str, float],
    er_estimates: dict[str, float] | None = None,
    mode: str = "inverse_var",
) -> dict[str, float]:
    """前瞻风险预算分配（权重和=1.0）。

    Args:
        var_estimates: {symbol: 预测 VaR(5%)} 正值（风险越大值越大）。
        er_estimates: {symbol: 预测 E(R)}（仅 sharpe_weight 模式需要）。
        mode: inverse_var | risk_parity | sharpe_weight。
    """
    if not var_estimates:
        raise ValueError("var_estimates 不得为空")
    if mode == "sharpe_weight" and not er_estimates:
        raise ValueError("sharpe_weight 模式需要 er_estimates")

    syms = sorted(var_estimates.keys())
    vars_arr = np.array([max(var_estimates[s], 1e-8) for s in syms])

    if mode == "inverse_var":
        inv = 1.0 / vars_arr
        raw = inv / inv.sum()
    elif mode == "risk_parity":
        raw = 1.0 / vars_arr
        raw = raw / raw.sum()
    elif mode == "sharpe_weight":
        sharpes = np.array([
            er_estimates.get(s, 0.0) / max(vars_arr[i], 1e-8)
            for i, s in enumerate(syms)
        ])
        sharpes = np.clip(sharpes, -5.0, 5.0)
        exp_s = np.exp(sharpes - sharpes.max())
        raw = exp_s / exp_s.sum()
    else:
        raise ValueError(f"未知 mode: {mode}")

    return {s: round(float(w), 6) for s, w in zip(syms, raw)}


def predicted_var(
    returns: pd.Series,
    confidence: float = 0.05,
    window: int = 60,
) -> pd.Series:
    """滚动预测 VaR（历史模拟法，PIT 安全）。"""
    rets = pd.to_numeric(returns, errors="coerce")
    return rets.rolling(window).quantile(confidence)


def predicted_cvar(
    returns: pd.Series,
    confidence: float = 0.05,
    window: int = 60,
) -> pd.Series:
    """滚动预测 CVaR（条件 VaR = 破位尾部均值）。"""
    rets = pd.to_numeric(returns, errors="coerce")
    var = rets.rolling(window).quantile(confidence)
    cvar_vals: list[float | None] = []
    for i in range(len(rets)):
        if i < window:
            cvar_vals.append(None)
            continue
        w = rets.iloc[i - window + 1: i + 1].dropna()
        threshold = var.iloc[i]
        tail = w[w <= threshold]
        cvar_vals.append(float(tail.mean()) if len(tail) > 0 else None)
    return pd.Series(cvar_vals, index=rets.index)
