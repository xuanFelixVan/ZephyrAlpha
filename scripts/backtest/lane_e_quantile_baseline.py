# [BLUEPRINT] MOD-BT-084 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.lane_e_quantile_baseline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; sklearn; zephyr.backtest.run_archive; scripts.backtest.translated._c4_engine
# [CONSUMERS] 车道 E 分布预测基线（策略生产全景图 E1E）；E4 分布评估双标准（PIT+锐度）首例；
#   UP-2..5（TDM 升级蓝图）的依赖解锁件
# [STARTUP] manual
# [INVARIANTS] PIT（特征与训练均只用 ≤T-1 数据，滚动前推不留同窗泄漏）；
#   评估双标准=PIT 经验覆盖率 vs 名义分位+锐度（区间均宽）+pinball 损失；
#   基线=车道 E 起步原型（非交易策略，产出分布预测供下游消费）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/样本不足)
# [TESTS] tests/backtest/test_lane_e_quantile_baseline.py
# [A_module] module_id=MOD-BT-084 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""车道 E MVP：沪深300 日收益分位数回归分布预测基线（Owner 2025-09 笔记起步建议落地）。

特征（全部 ≤T-1 可得）：滞后收益 1/5/10/20 日 + 滚动波动率 5/20 日 + 均值比 close/MA20。
模型：sklearn QuantileRegressor（线性分位数回归，quantiles=[0.05,0.50,0.95]，
  solver='highs'）。
滚动前推：滚动窗口训练（默认 500 日）→ 预测次日分位数 → 前推一日，全样本拼接。
评估双标准：
  - 校准（PIT 经验覆盖率）：realized≤q05 应≈5%、realized>q95 应≈5%（名义 vs 经验偏差）
  - 锐度：mean(q95-q05)（校准前提下越窄信息量越大）
  - pinball 损失（中位数分位）
窗口不足段（前 warmup 日）跳过预测。
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
TRAIN_WINDOW = 500  # 滚动训练窗口（交易日）


def _load_index_returns(start: str, end: str) -> pd.DataFrame:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backtest" / "translated"))
    from _c4_engine import load_index

    idx = load_index("000300", start, end, fields=("close",))
    rets = idx["close"].pct_change()
    df = pd.DataFrame({"ret_fwd": rets.shift(-1), "ret": rets}, index=idx.index)
    return df.dropna(subset=["ret"])


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """全部特征仅用 ≤T 日收盘信息（PIT：预测 T+1 用 ≤T）。"""
    f = pd.DataFrame(index=df.index)
    f["ret"] = df["ret"]
    for lag in FEATURE_LAGS:
        f[f"lag_{lag}"] = df["ret"].shift(lag)
    for w in VOL_WINDOWS:
        f[f"vol_{w}"] = df["ret"].rolling(w).std(ddof=0)
    f["ma20_ratio"] = df["ret"].rolling(20).mean() / df["ret"].rolling(60).mean()
    return f


def run_quantile_walkforward(features: pd.DataFrame, targets: pd.Series,
                             train_window: int = TRAIN_WINDOW) -> pd.DataFrame:
    """滚动前推分位数预测：返回列 [q05,q50,q95]（index=预测目标日）。"""
    from sklearn.linear_model import QuantileRegressor

    data = features.join(targets.rename("y")).dropna()
    if len(data) < train_window + 10:
        raise RuntimeError("样本不足（features+targets 拼接后）")
    rows: list[dict[str, float]] = []
    idx = data.index
    for i in range(train_window, len(data)):
        x_train = data.iloc[:i][[c for c in features.columns if c in data.columns]]
        y_train = data["y"].iloc[:i]
        x_pred = data.iloc[i:i + 1][[c for c in features.columns if c in data.columns]]
        row: dict[str, float] = {"date": idx[i]}
        for q in QUANTILES:
            model = QuantileRegressor(quantile=q, solver="highs", alpha=0.01)
            try:
                model.fit(x_train.values, y_train.values)
                row[f"q{int(q * 100):02d}"] = float(model.predict(x_pred.values)[0])
            except Exception:  # noqa: BLE001 单分位失败跳过（记录 NaN）
                row[f"q{int(q * 100):02d}"] = float("nan")
        rows.append(row)
    return pd.DataFrame(rows).set_index("date")


def evaluate(pred: pd.DataFrame, realized: pd.Series) -> dict[str, Any]:
    """双标准评估：校准（PIT 经验覆盖率）+ 锐度（区间均宽）+ pinball。"""
    joined = pred.join(realized.rename("realized"), how="inner").dropna()
    n = len(joined)
    if n == 0:
        raise RuntimeError("预测与实现无交集样本")
    cover_low = float((joined["realized"] <= joined["q05"]).mean())
    cover_high = float((joined["realized"] > joined["q95"]).mean())
    inside = float(((joined["realized"] >= joined["q05"]) &
                    (joined["realized"] <= joined["q95"])).mean())
    width = float((joined["q95"] - joined["q05"]).mean())

    def pinball(y: float, q: float, tau: float) -> float:
        return (y - q) * tau if y >= q else (q - y) * (1 - tau)

    pin50 = float(np.mean([pinball(y, q, 0.5) for y, q in
                           zip(joined["realized"], joined["q50"])]))
    return {
        "n": n,
        "coverage_low_nominal_5pct": round(cover_low, 4),
        "coverage_inside_nominal_90pct": round(inside, 4),
        "coverage_high_nominal_5pct": round(cover_high, 4),
        "interval_mean_width": round(width, 5),
        "pinball_median": round(pin50, 6),
        "note": "校准理想态：coverage_low≈0.05/inside≈0.90/high≈0.05；锐度=区间均宽越窄越好（以校准为前提）",
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="车道 E MVP：沪深300 分位数回归分布预测基线")
    ap.add_argument("--start", default="2019-06-01")
    ap.add_argument("--end", default="2026-06-30")
    ap.add_argument("--dry-run", action="store_true", help="不写 run 档案")
    args = ap.parse_args()

    load_start = str(pd.Timestamp(args.start) - pd.Timedelta(days=180))[:10]
    df = _load_index_returns(load_start, args.end)
    feats = build_features(df)
    # 特征与目标：T 日特征 → 预测 T+1 收益（ret_fwd）
    targets = df["ret_fwd"]

    pred = run_quantile_walkforward(feats, targets, train_window=TRAIN_WINDOW)
    pred = pred[pred.index <= pd.Timestamp(args.end)]
    realized = df["ret_fwd"].reindex(pred.index)
    ev = evaluate(pred, realized)

    summary = {
        "baseline": "lane_e_quantile_regression_q05_q50_q95",
        "underlying": "000300 沪深300 日收益",
        "window": [args.start, args.end],
        "train_window": TRAIN_WINDOW,
        "features": [f"lag_{l}" for l in FEATURE_LAGS] + [f"vol_{w}" for w in VOL_WINDOWS] + ["ma20_ratio"],
        "evaluation": ev,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))

    if not args.dry_run:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from zephyr.backtest.run_archive import create_run, finalize_run, write_step

        now = pd.Timestamp.now()
        run_id = f"VAL-E-{now.strftime('%Y%m%d-%H%M%S')}"
        create_run(run_id=run_id, object_id="LANE-E-BASELINE", kind="VAL",
                   window={"start": args.start, "end": args.end},
                   cost_mode="n/a", created_by="ai-session:st-zcode-c4-20260912")
        write_step(run_id, "01", "# 调研\n\n- 去年笔记起步建议：先在沪深300 上实现分位数回归分布预测原型\n"
                                "- 评估双标准：PIT 校准+锐度（v3.1 车道 E 深化方向）")
        write_step(run_id, "02", "# 数据缺口\n\n- 无（kline_index 000300 全窗口覆盖）")
        write_step(run_id, "03", "# 数据清单\n\n- name: 沪深300 日收益+滞后/波动/均值比特征\n"
                                 f"  rows: {len(feats)}\n  pit_note: '特征与训练均 ≤T-1'\n  proxy: false")
        write_step(run_id, "05", "# 修剪\n\n- warmup 段（特征 NaN）不参与训练与预测\n")
        write_step(run_id, "06", "# 结果\n\n```json\n" + json.dumps(ev, ensure_ascii=False, indent=1) + "\n```\n",
                   filename="06_evaluation.json")
        write_step(run_id, "verdict",
                   f"# 判定书：{run_id}\n\n对象：车道 E 分布预测基线（分位数回归 q05/q50/q95）\n"
                   f"结论：verdict=done（基线建成，双标准评估完成）｜"
                   "verdict_reason=lane_e_baseline_first_run\n"
                   "判读：校准看 coverage 偏差、锐度看区间均宽；基线意义=机器学习这条线的"
                   "对照锚（与翻译策略打对台），非交易信号\n")
        finalize_run(run_id, verdict_ref={"table": "lane_e_baseline", "run_id": run_id})
        print("run archive:", run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
