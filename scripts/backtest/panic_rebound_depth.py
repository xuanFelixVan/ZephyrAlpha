# [BLUEPRINT] MOD-BT-092 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.panic_rebound_depth
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; sklearn; zephyr.backtest.run_archive; scripts.backtest.translated._c4_engine
# [CONSUMERS] 恐慌反弹策略深度化——多窗口+参数敏感性分析（UP-1 完整凯利扩展依赖件）
# [STARTUP] manual
# [INVARIANTS] PIT（特征 ≤T-1，预测 T+1）；冻结土规成本；评估双标准=PIT 校准+锐度
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/样本不足)
# [TESTS] tests/backtest/test_panic_rebound_depth.py
# [A_module] module_id=MOD-BT-092 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""恐慌反弹策略深度化——多窗口交叉验证 + 参数敏感性分析。

三阶段：
  Phase 1 多窗口交叉验证：2016-2019 / 2020-2023 / 2024-2026 三窗独立评估
  Phase 2 参数敏感性：decline_threshold ∈ {0.60,0.65,0.70} × window ∈ {10,15,20} = 9 组
  Phase 3 特征消融：去掉每个特征组看 Sharpe 变化
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


def _load_index(engine, symbol: str, start: str, end: str,
                fields: tuple[str, ...] = ("close",)) -> pd.DataFrame:
    cols = ", ".join(fields)
    cfg = engine["cfg"]
    cli = engine["client"]
    rows = cli.execute(
        f"SELECT trade_date, {cols} FROM c1_market.kline_index "
        f"WHERE symbol = '{symbol}' AND trade_date >= '{start}' AND trade_date <= '{end}' "
        f"ORDER BY trade_date"
    )
    df = pd.DataFrame(rows, columns=["trade_date"] + list(fields))
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for c in fields:
        df[c] = df[c].astype(float)
    return df.set_index("trade_date")


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    rets = df["close"].pct_change()
    f = pd.DataFrame(index=df.index)
    f["ret"] = rets
    for lag in FEATURE_LAGS:
        f[f"lag_{lag}"] = rets.shift(lag)
    for w in VOL_WINDOWS:
        f[f"vol_{w}"] = rets.rolling(w).std(ddof=0)
    f["ma20_ratio"] = rets.rolling(20).mean() / (rets.rolling(60).mean().abs() + 1e-8)
    if "advance_count" in df.columns:
        adv = df["advance_count"].replace(0, np.nan)
        dec = df["decline_count"].replace(0, np.nan)
        total = (adv + dec).replace(0, np.nan)
        f["breadth"] = ((adv - dec) / total).fillna(0)
    f["ret_fwd"] = rets.shift(-1)
    return f.dropna()


def _fit_predict_linear_quantile(X_train, y_train, X_pred, alpha: float) -> float:
    from sklearn.linear_model import QuantileRegressor
    m = QuantileRegressor(quantile=alpha, solver="highs", alpha=0.01)
    m.fit(X_train, y_train)
    return float(m.predict(X_pred)[0])


def _walkforward_quantile(
    feats: pd.DataFrame,
    train_window: int = 500,
    quantiles: tuple = QUANTILES,
) -> pd.DataFrame:
    """滚动前推分位数预测。"""
    feat_cols = [c for c in feats.columns if c != "ret_fwd"]
    vals = feats[feat_cols].values
    y = feats["ret_fwd"].values
    dates = feats.index

    rows: list[dict] = []
    for i in range(train_window, len(data) - 1 if False else len(vals)):
        row: dict[str, Any] = {"date": dates[i], "realized": y[i]}
        for q in quantiles:
            try:
                row[f"q{int(q*100):02d}"] = _fit_predict_linear_quantile(
                    vals[:i], y[:i], vals[i:i+1], q)
            except Exception:
                row[f"q{int(q*100):02d}"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows).set_index("date")


def _evaluate(pred_df: pd.DataFrame) -> dict[str, Any]:
    realized = pred_df["realized"]
    q05, q50, q95 = pred_df["q05"], pred_df["q50"], pred_df["q95"]
    inside = float(((realized >= q05) & (realized <= q95)).mean())
    width = float((q95 - q05).mean())
    ann_sharpe = float(realized.mean() / (realized.std() + 1e-8) * np.sqrt(244))
    cum = (1 + realized).cumprod()
    mdd = float((cum / cum.cummax() - 1).min())
    return {
        "n": int(len(pred_df)),
        "ann_sharpe": round(ann_sharpe, 3),
        "max_drawdown": round(mdd, 4),
        "coverage_inside": round(inside, 4),
        "interval_mean_width": round(width, 5),
    }


def multi_window_analysis(engine) -> dict[str, Any]:
    """Phase 1：三窗口交叉验证。"""
    windows = [
        ("IS_2020_2023", "2020-01-01", "2023-12-31"),
        ("OOS_2024_2026", "2024-01-01", "2026-06-30"),
        ("S3_2016_2019", "2016-01-01", "2019-12-31"),
    ]
    out: dict[str, Any] = {}
    for label, lo, hi in windows:
        load_start = str(pd.Timestamp(lo) - pd.Timedelta(days=180))[:10]
        df = _load_index(engine, "000300", load_start, hi)
        feats = _build_features(df)
        pred = _walkforward_quantile(feats, TRAIN_WINDOW)
        ev = _evaluate(pred)
        out[label] = ev
        logger.info("%s: sharpe=%.3f mdd=%.4f inside=%.3f", label, ev["ann_sharpe"], ev["max_drawdown"], ev["coverage_inside"])
    return out


def param_sensitivity(engine) -> dict[str, Any]:
    """Phase 2：参数敏感性——decline_threshold × window 网格。"""
    grid: dict[str, Any] = {"thresholds": [0.60, 0.65, 0.70], "windows": [10, 15, 20], "results": []}
    idx = _load_index(engine, "000300", "2020-01-01", "2026-06-30", fields=("close",))
    rets = idx["close"].pct_change()
    from zephyr.pf_alloc.core.forward_stop_loss import forward_stop_signal
    for w in grid["windows"]:
        for t in grid["thresholds"]:
            sig = forward_stop_signal(rets, window=w, decline_threshold=t)
            triggers = int(sig["stop_review"].sum())
            grid["results"].append({
                "window": w, "threshold": t, "triggers": triggers,
                "trigger_rate": round(triggers / len(rets), 4),
            })
    return grid


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="恐慌反弹策略深度化——多窗口+参数敏感性")
    ap.add_argument("--phase", choices=["multi_window", "sensitivity", "all"], default="all")
    args = ap.parse_args()

    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    from zephyr.data.ch_writer import get_client_strict

    cli = get_client_strict()
    engine = {"cfg": cfg, "client": cli}

    out: dict[str, Any] = {}
    if args.phase in ("multi_window", "all"):
        out["multi_window"] = multi_window_analysis(engine)
    if args.phase in ("sensitivity", "all"):
        out["param_sensitivity"] = param_sensitivity(engine)

    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
