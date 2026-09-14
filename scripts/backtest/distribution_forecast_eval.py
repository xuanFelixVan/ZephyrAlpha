# [BLUEPRINT] MOD-BT-194 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.distribution_forecast_eval
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] 策略生产全景图 E4 考试咽喉（分布预测双标准考尺，图纸 E1E/E4 在案）；
#   车道 E 基线（MOD-BT-084/后续 Kronos MOD-BT-195）；纯函数零 IO
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 双标准必须同时用（校准会得出"宽而无用分布也好"的假阳性，只看锐度会过拟合）；
#   纯函数零 IO；分位水平真源=QUANTILE_LEVELS；经验覆盖率=P(realized ≤ 分位预测)；
#   PIT=跨分位水平插值的 F̂(y)；校准判定容差 CALIBRATION_TOL
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(分位水平/数组形状非法)
# [TESTS] tests/backtest/test_distribution_forecast_eval.py
# [A_module] module_id=MOD-BT-194 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""E4 分布预测双标准考尺——PIT 校准度 + 锐度 + pinball 损失（图纸 E1E/E4 定稿落地）。

任何产出分位预测的模型（车道 E 分位数回归/Kronos/未来 PDF 模型）都交本考尺评分：
  输入 = {分位水平 q: 预测数组} + 实现值数组；
  输出 = 校准表（名义 vs 经验覆盖率）+ 平均校准偏差 + 锐度（[q05,q95] 均宽）
        + pinball 损失 + 双标准判定（校准∧锐度优于无信息基准）。
纯函数零 IO；语义对齐论文/图纸：校准=PIT 经验覆盖率 vs 名义、锐度=区间均宽。

用法（库调用，无 CLI）:
  from scripts.backtest.distribution_forecast_eval import evaluate_distribution_forecast
  report = evaluate_distribution_forecast({"0.05": lo, "0.5": med, "0.95": hi}, realized)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

QUANTILE_LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
CALIBRATION_TOL = 0.05   # 经验覆盖率与名义水平容差（±5pp 记校准）
PINBALL_QUANTILES = (0.1, 0.5, 0.9)


def _validate(quantile_preds: dict[float, np.ndarray], realized: np.ndarray) -> tuple[dict, np.ndarray]:
    if not quantile_preds:
        raise ValueError("quantile_preds 为空")
    qp: dict[float, np.ndarray] = {}
    for q, arr in quantile_preds.items():
        qf = float(q)
        if not 0 < qf < 1:
            raise ValueError(f"分位水平越界: {qf}")
        a = np.asarray(arr, dtype=float)
        if realized is not None and a.shape != np.asarray(realized).shape:
            raise ValueError(f"分位 {qf} 形状 {a.shape} 与 realized 不一致")
        qp[qf] = a
    r = np.asarray(realized, dtype=float) if realized is not None else None
    if r is not None and len(r) < 10:
        raise ValueError(f"样本不足: {len(r)} < 10")
    return qp, r


def empirical_coverage(quantile_preds: dict[float, np.ndarray],
                       realized: np.ndarray) -> pd.DataFrame:
    """每个分位水平的经验覆盖率 P(realized ≤ pred_q) vs 名义。"""
    qp, r = _validate(quantile_preds, realized)
    rows = []
    for q in sorted(qp):
        pred = qp[q]
        fin = np.isfinite(pred) & np.isfinite(r)
        if fin.sum() == 0:
            cov = np.nan
        else:
            cov = float(np.mean(r[fin] <= pred[fin]))
        rows.append({"quantile": q, "nominal": q, "empirical": cov,
                     "deviation": None if np.isnan(cov) else cov - q,
                     "calibrated": bool(abs((cov or np.nan) - q) <= CALIBRATION_TOL)
                     if not np.isnan(cov) else False})
    return pd.DataFrame(rows)


def pit_values(quantile_preds: dict[float, np.ndarray], realized: np.ndarray) -> np.ndarray:
    """PIT = 跨分位水平线性插值的 F̂(y)（逐样本；越界裁剪到 [0,1]）。"""
    qp, r = _validate(quantile_preds, realized)
    qs = np.array(sorted(qp))
    mat = np.vstack([qp[q] for q in qs])  # (n_q, n)
    pits = np.empty(mat.shape[1])
    for i in range(mat.shape[1]):
        y, row = r[i], mat[:, i]
        fin = np.isfinite(row)
        pits[i] = np.interp(y, row[fin], qs[fin]) if fin.sum() >= 2 else 0.5
    return np.clip(pits, 0.0, 1.0)


def pit_uniformity_ks(pits: np.ndarray) -> float:
    """PIT 均匀性 KS 统计量（vs U[0,1]；手算 D 统计量，零 scipy 依赖）。"""
    x = np.sort(np.asarray(pits, dtype=float))
    n = len(x)
    if n < 10:
        return np.nan
    cdf = np.arange(1, n + 1) / n
    d_plus = np.max(cdf - x)
    d_minus = np.max(x - np.arange(0, n) / n)
    return float(max(d_plus, d_minus))


def sharpness(quantile_preds: dict[float, np.ndarray],
              lower: float = 0.05, upper: float = 0.95) -> float:
    """锐度=区间均宽（校准前提下越窄信息量越大）。"""
    qp, _ = _validate(quantile_preds, None)
    for q in (lower, upper):
        if float(q) not in qp:
            raise ValueError(f"缺少分位 {q}，无法计算区间宽")
    widths = qp[float(upper)] - qp[float(lower)]
    return float(np.nanmean(widths))


def pinball_loss(quantile_preds: dict[float, np.ndarray], realized: np.ndarray,
                 q: float) -> float:
    """pinball 损失（分位回归标准损失，越低越好）。"""
    qp, r = _validate(quantile_preds, realized)
    if float(q) not in qp:
        raise ValueError(f"缺少分位 {q}")
    pred = qp[float(q)]
    fin = np.isfinite(pred) & np.isfinite(r)
    diff = r[fin] - pred[fin]
    return float(np.mean(np.maximum(q * diff, (q - 1) * diff)))


def evaluate_distribution_forecast(quantile_preds: dict[float, np.ndarray],
                                   realized: np.ndarray) -> dict:
    """双标准总评：校准表+KS+锐度+pinball+判定。锐度基准=同窗样本标准差比例。"""
    calib = empirical_coverage(quantile_preds, realized)
    pits = pit_values(quantile_preds, realized)
    ks = pit_uniformity_ks(pits)
    qp, r = _validate(quantile_preds, realized)
    sd = float(np.nanstd(r))
    sharp = sharpness(quantile_preds)
    sharpness_ratio = round(sharp / sd, 4) if sd > 0 else np.nan
    avail = set(quantile_preds)
    pinballs = {q: pinball_loss(quantile_preds, r, q)
                for q in PINBALL_QUANTILES if float(q) in avail}
    calibrated_share = float(calib["calibrated"].mean())
    return {
        "n": int(len(r)),
        "calibration_table": calib.to_dict("records"),
        "calibrated_share": round(calibrated_share, 4),
        "pit_ks": round(ks, 4) if np.isfinite(ks) else None,
        "sharpness": round(sharp, 6),
        "realized_std": round(sd, 6),
        "sharpness_ratio": sharpness_ratio,  # 越窄越好（<1 表示窄于无信息波动）  # 信息性：校准无条件预测器≈3.29；条件预测器<3.29
        "pinball": {str(q): round(v, 6) for q, v in pinballs.items()},
        "verdict": {
            "calibrated": calibrated_share >= 0.6,
        },
    }
