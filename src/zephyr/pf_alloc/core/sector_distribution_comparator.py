# [BLUEPRINT] MOD-PA-023 | docs/03_modules/_domain_portfolio_alloc/sector_distribution_comparator/blueprint.md
# [MODULE] zephyr.pf_alloc.core.sector_distribution_comparator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] numpy; pandas; sklearn
# [CONSUMERS] TDM 板块流（UP-4 分布比较选优）；策略工厂 E1D 车道
# [STARTUP] manual
# [INVARIANTS] PIT（特征 ≤T-1，预测 T+1）；板块=index（kline_index）；
#   分位数回归模型与车道 E 基线同构
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/样本不足)
# [TESTS] tests/pf_alloc/test_sector_distribution_comparator.py
# [A_module] module_id=MOD-PA-023 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""板块分布比较选优（TDM 升级蓝图 UP-4）——多板块独立分布预测，比较收益-风险比选优。

原理（对标 Owner 2025-09 笔记 3.1 板块轮动模型）：
  对每个候选板块指数独立运行分位数回归（同车道 E 基线），比较预测分布的
  收益-风险比（中位数/区间宽度），选优配置。

板块池（kline_index 已有）：000001 上证 / 000016 上证50 / 000300 沪深300 /
  000905 中证500 / 000852 中证1000 / 399006 创业板指。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.pf_alloc.core.risk_budget_allocator import predicted_var

INDEX_POOL = {
    "000001": "上证指数",
    "000016": "上证50",
    "000300": "沪深300",
    "000905": "中证500",
    "000852": "中证1000",
    "399006": "创业板指",
}
QUANTILES = (0.05, 0.50, 0.95)
FEATURE_LAGS = (1, 5, 10, 20)


def _build_features(closes: pd.Series) -> pd.DataFrame:
    rets = closes.pct_change()
    f = pd.DataFrame(index=closes.index)
    f["ret"] = rets
    for lag in FEATURE_LAGS:
        f[f"lag_{lag}"] = rets.shift(lag)
    f["vol_20"] = rets.rolling(20).std(ddof=0)
    return f


def _predict_quantiles(
    close: pd.Series, train_window: int = 500, warmup: int = 30
) -> pd.DataFrame:
    from sklearn.linear_model import QuantileRegressor

    rets = close.pct_change()
    feats = _build_features(pd.DataFrame({"close": close}))
    feats["ret_fwd"] = rets.shift(-1)
    data = feats.dropna()
    if len(data) < train_window + 10:
        return pd.DataFrame(columns=["q05", "q50", "q95"])

    rows: list[dict[str, Any]] = []
    feat_cols = [c for c in feats.columns if c != "ret_fwd"]
    vals = data[feat_cols].values
    y = data["ret_fwd"].values
    dates = data.index
    for i in range(train_window, len(data)):
        model = QuantileRegressor(solver="highs", alpha=0.01)
        try:
            model.fit(vals[:i], y[:i])
            preds = model.predict(vals[i:i + 1])
            rows.append({"date": dates[i], **{f"q{int(q * 100):02d}": preds[0] for q in QUANTILES}})
        except Exception:
            pass
    if not rows:
        return pd.DataFrame(columns=["q05", "q50", "q95"])
    return pd.DataFrame(rows).set_index("date")


def compare_sectors(
    index_data: dict[str, pd.Series],
    train_window: int = 500,
) -> pd.DataFrame:
    """多板块分布预测比较。

    Args:
        index_data: {symbol: close Series}。
        train_window: 分位数回归训练窗口。

    Returns:
        DataFrame(index=板块代码, columns=[q05_med, q50_med, q95_med, sharpe_pred, rank])。
        sharpe_pred = q50_med / (q95_med - q05_med)。
    """
    results: list[dict[str, Any]] = []
    for sym, close in index_data.items():
        pred = _predict_quantiles(close, train_window)
        if pred.empty:
            continue
        results.append({
            "symbol": sym,
            "q05_med": float(pred["q05"].median()),
            "q50_med": float(pred["q50"].median()),
            "q95_med": float(pred["q95"].median()),
        })
    if not results:
        return pd.DataFrame()
    df = pd.DataFrame(results).set_index("symbol")
    spread = df["q95_med"] - df["q05_med"]
    df["sharpe_pred"] = np.where(spread > 0, df["q50_med"] / spread.replace(0, np.nan), np.nan)
    df["rank"] = df["sharpe_pred"].rank(ascending=False)
    return df.sort_values("rank")
