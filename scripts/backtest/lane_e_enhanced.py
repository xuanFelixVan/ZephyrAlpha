# [BLUEPRINT] MOD-BT-089 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.lane_e_enhanced
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; sklearn; lightgbm; zephyr.backtest.run_archive; scripts.backtest.translated._c4_engine
# [CONSUMERS] 车道 E 分布预测完整化——分位数回归增强（LightGBM/GBR vs 线性 QR 对比实验）
# [STARTUP] manual
# [INVARIANTS] PIT（特征 ≤T-1，预测 T+1）；滚动前推不留同窗泄漏；评估双标准=PIT 校准+锐度
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/样本不足)
# [TESTS] tests/backtest/test_lane_e_enhanced.py
# [A_module] module_id=MOD-BT-089 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""车道 E 分布预测完整化——三种模型 IS+OOS 对比实验。

对比矩阵：
  M1 linear_qr   = sklearn QuantileRegressor（线性基线）
  M2 gbr_quantile = GradientBoostingRegressor(loss=quantile)（非线性增强）
  M3 lgbm_quantile = LightGBM LGBMRegressor(objective=quantile)（梯度提升增强）
三模型在 IS+OOS 全窗口评估，报告 PIT 校准覆盖率 + 区间锐度。
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

QUANTILES = (0.05, 0.50, 0.95)
FEATURE_LAGS = (1, 5, 10, 20)
VOL_WINDOWS = (5, 20)
TRAIN_WINDOW = 500


def _load_features(engine, start: str, end: str) -> pd.DataFrame:
    idx = engine.load_index("000300", start, end, fields=("close", "advance_count", "decline_count"))
    rets = idx["close"].pct_change()
    f = pd.DataFrame(index=idx.index)
    f["ret"] = rets
    for lag in FEATURE_LAGS:
        f[f"lag_{lag}"] = rets.shift(lag)
    for w in VOL_WINDOWS:
        f[f"vol_{w}"] = rets.rolling(w).std(ddof=0)
    f["ma20_ratio"] = rets.rolling(20).mean() / (rets.rolling(60).mean().abs() + 1e-8)
    adv = idx["advance_count"].replace(0, np.nan)
    dec = idx["decline_count"].replace(0, np.nan)
    total = (adv + dec).replace(0, np.nan)
    f["breadth"] = ((adv - dec) / total).fillna(0)
    f["mom_5_20"] = rets.rolling(5).sum() / (rets.rolling(20).sum().abs() + 1e-8)
    f["ret_fwd"] = rets.shift(-1)
    return f.dropna()


def _predict_quantile_set(model_cls, X_train, y_train, X_pred, quantiles) -> dict[str, float]:
    out = {}
    for q in quantiles:
        if model_cls == "lgbm":
            import lightgbm as lgb
            m = lgb.LGBMRegressor(objective="quantile", alpha=q, n_estimators=100,
                                  max_depth=4, learning_rate=0.05, verbose=-1)
        elif model_cls == "gbr":
            from sklearn.ensemble import GradientBoostingRegressor
            m = GradientBoostingRegressor(loss="quantile", alpha=q, n_estimators=100,
                                          max_depth=3, learning_rate=0.05, random_state=42)
        else:
            from sklearn.linear_model import QuantileRegressor
            m = QuantileRegressor(quantile=q, solver="highs", alpha=0.01)
        m.fit(X_train, y_train)
        out[f"q{int(q*100):02d}"] = float(m.predict(X_pred)[0])
    return out


def run_experiment(engine, start: str, end: str, models: list[str],
                   train_window: int = 500) -> dict[str, Any]:
    f = _load_features(engine, start, end)
    feat_cols = [c for c in f.columns if c not in ("ret_fwd", "ret")]
    data = f.dropna()
    if len(data) < train_window + 50:
        raise RuntimeError(f"样本不足: {len(data)}")

    vals = data[feat_cols].values
    y_fwd = data["ret_fwd"].values
    dates = data.index

    results: dict[str, Any] = {"models": {}}
    for mtype in models:
        rows: list[dict] = []
        for i in range(train_window, len(data) - 1):
            X_tr = vals[:i]
            y_tr = y_fwd[:i]
            x_pd = vals[i:i + 1]
            try:
                preds = _predict_quantile_set(mtype, X_tr, y_tr, x_pd, QUANTILES)
                preds["realized"] = y_fwd[i + 1] if i + 1 < len(y_fwd) else np.nan
                preds["date"] = dates[i + 1] if i + 1 < len(dates) else dates[-1]
                rows.append(preds)
            except Exception:
                continue
        pdf = pd.DataFrame(rows).set_index("date").dropna(subset=["realized"])
        realized = pdf["realized"]
        q05, q50, q95 = pdf["q05"], pdf["q50"], pdf["q95"]

        inside = float(((realized >= q05) & (realized <= q95)).mean())
        cover_lo = float((realized <= q05).mean())
        cover_hi = float((realized >= q95).mean())
        width = float((q95 - q05).mean())
        pin50 = float(np.mean([max(t - q, q - t) for t, q in zip(realized, pdf["q50"])]))

        results["models"][mtype] = {
            "n_preds": len(pdf),
            "coverage_inside": round(inside, 4),
            "coverage_low_tail": round(cover_lo, 4),
            "coverage_high_tail": round(cover_hi, 4),
            "interval_mean_width": round(width, 5),
            "pinball_median": round(pin50, 6),
        }
        logger.info("%s: inside=%.4f width=%.5f pin50=%.6f", mtype, inside, width, pin50)

    return results
