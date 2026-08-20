# [BLUEPRINT] MOD-REGIME-VAL | docs/03_modules/_domain_regime/blueprint.md | 14 号 §4.5
# [MODULE] zephyr.regime.validation.overfitting_guard
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] P1-E9 验证闭环 / 策略验收流程
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 预注册记录不可覆盖(禁看结果后调参); MinTRL SR<=0->inf; WFE IS<=0->undefined; 事件研究基线严格在事件窗口之前(PIT)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 预注册重名->RuntimeError; 未知名->KeyError; MinTRL 无输入->ValueError
# [TESTS] tests/regime/validation/test_overfitting_guard.py
# [A_module] module_id=MOD-REGIME-VAL-OFIT | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #14_regime_s2_diagnosis §4.5 防过拟合方法论栈
# [ALGO_FLOW]
# I1: score 序列+事件日期（事件研究）/ params dict（预注册）/ Sharpe+矩或收益序列（MinTRL）/ IS+OOS Sharpe（WFE）
# F1: event_study（事件日 asof 对齐 → ±窗口评分极值 vs 事件前全历史滚动窗口极值的分位）
# F2: PreRegistrationRegistry（JSON 文件级参数 hash 锁定：register 禁覆盖 / verify 一致性）
# F3: min_track_record_length（MinTRL=1+[1-γ3·SR+(γ4-1)/4·SR²]·(Z_α/SR)²，Bailey & López de Prado 2014）
# F4: walk_forward_efficiency/assess_wfe（WFE=OOS/IS，≥0.6 pass / 0.5-0.6 marginal / <0.5 red_flag）
# O1: 事件研究 DataFrame / verify bool / MinTRL 年数 / WFE 裁决 dict
# [/ALGO_FLOW]
"""防过拟合方法论栈 MVP（14_regime_s2_diagnosis §4.5，N=3 小样本专用）。

核心挑战：S2 仅 3 个历史事件，传统 PBO/CSCV 需 N≥10-12 样本才统计有效
（archimedes #819 2026-06），不可用。本模块落地 6 层栈中的 4 层函数级 MVP
（**不 vendor 外部库**——Neyt/How-To-Backtest-Correctly 仅作方法参考）：

  ① 事件研究法（event_study）——主验证方法：事件日 ±10/±20 窗口评分异常表现
     vs 全历史基线（基线严格在事件窗口之前，PIT 安全）。
  ② 预注册协议（PreRegistrationRegistry）——防确认偏误：看事件数据前锁定全部
     阈值/参数为 hash 登记；register 禁覆盖（防"看到结果后回头调参数"）。
  ⑤ MinTRL（min_track_record_length）——最小可信记录长度：诚实标注"统计置信度
     低"，不作通过门槛。
  ⑥ WFE（walk_forward_efficiency/assess_wfe）——OOS/IS Sharpe ≥0.6 量化验收
     门槛（digitalninjasystems 2026-07），<0.5 红旗。

  ③ DSR 与 ④ CPCV 已有仓内实现，直接引用不重复造：
     - DSR: zephyr.simulation.deflated_sharpe_calculator.DeflatedSharpeCalculator
     - CPCV: zephyr.backtest.core.cpcv.generate_cpcv_splits（N=10,k=2→45 组合）

依据: 14_regime_s2_diagnosis v0.5.2 §4.5
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

__all__ = [
    "PreRegistrationRegistry",
    "assess_wfe",
    "event_study",
    "min_track_record_length",
    "walk_forward_efficiency",
]


# ---------------------------------------------------------------------------
# ① 事件研究法（Event Study，主验证方法）
# ---------------------------------------------------------------------------


def event_study(
    score: pd.Series,
    event_dates,
    pre_window: int = 10,
    post_window: int = 10,
    min_baseline: int = 5,
) -> pd.DataFrame:
    """事件研究：事件日 t=0，±窗口评分极值 vs 全历史基线分位。

    以事件日为锚，计算 [t-pre_window, t+post_window] 窗口内 score 的最大值/均值，
    并与**事件窗口之前**的全历史同宽滚动窗口最大值分布对比（baseline_pct =
    历史窗口极值 ≤ 事件窗口极值的比例，PIT 安全：基线不含事件后数据）。

    Args:
        score: 评分序列（index 为日期，如 S2 维度评分）。
        event_dates: 事件日期列表（不在索引上的日期 asof 对齐到最近前一点）。
        pre_window / post_window: 事件窗口半宽（交易日）。
        min_baseline: 最少基线窗口数（不足 → baseline_pct=NaN，诚实标注不可判）。

    Returns:
        pd.DataFrame：event_date / aligned_date / window_max / window_mean /
        baseline_pct / n_baseline。
    """
    idx = score.index
    values = score.to_numpy(dtype=float)
    width = pre_window + post_window + 1
    # 全历史滚动窗口极值序列（终点位置 pos → 窗口 [pos-width+1, pos]）
    rolling_max = score.rolling(width).max().to_numpy(dtype=float)
    rows = []
    for ev in event_dates:
        ev_ts = pd.Timestamp(ev)
        pos = int(idx.searchsorted(ev_ts, side="right")) - 1  # asof：<= ev 的最近点
        if pos < 0:
            rows.append({"event_date": ev_ts, "aligned_date": None, "window_max": np.nan,
                         "window_mean": np.nan, "baseline_pct": np.nan, "n_baseline": 0})
            continue
        lo, hi = max(0, pos - pre_window), min(len(values) - 1, pos + post_window)
        window = values[lo: hi + 1]
        w_max = float(np.nanmax(window))
        w_mean = float(np.nanmean(window))
        # 基线：终点在事件窗口起点之前的滚动极值（严格 PIT）
        baseline = rolling_max[width - 1: lo]
        baseline = baseline[~np.isnan(baseline)]
        n_base = len(baseline)
        pct = float((baseline <= w_max).mean()) if n_base >= min_baseline else np.nan
        rows.append({"event_date": ev_ts, "aligned_date": idx[pos], "window_max": w_max,
                     "window_mean": w_mean, "baseline_pct": pct, "n_baseline": n_base})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# ② 预注册协议（Pre-registration，防确认偏误）
# ---------------------------------------------------------------------------


class PreRegistrationRegistry:
    """预注册登记（JSON 文件级参数 hash 锁定）。

    语义（Neyt 2026-03 "The Second Law"）：看事件数据**之前**先锁定全部阈值/参数；
    register 后禁止覆盖同名注册（防"看到结果后回头调参数"）；verify 供实现后
    核验当前参数与预注册一致。
    """

    def __init__(self, path) -> None:
        self._path = Path(path)
        self._records: dict[str, dict] = {}
        if self._path.exists():
            self._records = json.loads(self._path.read_text(encoding="utf-8"))

    @staticmethod
    def _hash(params: dict) -> str:
        blob = json.dumps(params, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._records, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def register(self, name: str, params: dict, note: str = "") -> None:
        """登记预注册参数（同名已存在 → RuntimeError，不可覆盖）。"""
        if name in self._records:
            raise RuntimeError(f"预注册 '{name}' 已注册，禁止覆盖（防确认偏误）")
        self._records[name] = {
            "params": params,
            "params_hash": self._hash(params),
            "registered_at": pd.Timestamp.now(tz="UTC").isoformat(),
            "note": note,
        }
        self._flush()

    def verify(self, name: str, params: dict) -> bool:
        """核验当前参数与预注册一致（未知名 → KeyError）。"""
        if name not in self._records:
            raise KeyError(f"预注册 '{name}' 不存在")
        return self._records[name]["params_hash"] == self._hash(params)


# ---------------------------------------------------------------------------
# ⑤ MinTRL（Minimum Track Record Length，Bailey & López de Prado 2014）
# ---------------------------------------------------------------------------


def min_track_record_length(
    returns: pd.Series | None = None,
    *,
    sharpe: float | None = None,
    skew: float | None = None,
    kurtosis: float | None = None,
    alpha: float = 0.95,
    periods_per_year: int = 252,
) -> float:
    """MinTRL（年）：给定 Sharpe 与置信度，统计可信所需的最短跟踪记录。

    公式：MinTRL = 1 + [1 − γ3·SR_a + (γ4−1)/4·SR_a²]·(Z_α/SR_a)²
    （SR_a=年化 Sharpe；γ3=偏度；γ4=峰度（非超额，正态=3））。

    N=3 事件下 MinTRL 会诚实标注"统计置信度低"——用作披露而非通过门槛。
    SR_a ≤ 0 → inf（任何长度记录都无法证明）。returns 与 (sharpe,skew,kurtosis)
    二选一；returns 优先（内部年化：SR_a = mean/std×√periods_per_year）。
    """
    if returns is not None:
        r = pd.Series(returns, dtype=float).dropna()
        if len(r) < 3:
            raise ValueError("returns 样本 < 3，无法估计矩")
        mu, sigma = float(r.mean()), float(r.std(ddof=1))
        sharpe = mu / sigma * math.sqrt(periods_per_year) if sigma > 0 else 0.0
        skew = float(r.skew())
        kurtosis = float(r.kurt()) + 3.0  # pandas kurt 为超额峰度 → +3 还原
    if sharpe is None or skew is None or kurtosis is None:
        raise ValueError("需传 returns 或显式 (sharpe, skew, kurtosis)")
    if sharpe <= 0:
        return float("inf")
    z = NormalDist().inv_cdf(alpha)
    return 1.0 + (1.0 - skew * sharpe + (kurtosis - 1.0) / 4.0 * sharpe**2) * (z / sharpe) ** 2


# ---------------------------------------------------------------------------
# ⑥ WFE（Walk-Forward Efficiency，OOS/IS Sharpe 验收门槛）
# ---------------------------------------------------------------------------


def walk_forward_efficiency(oos_sharpe: float, is_sharpe: float) -> float:
    """WFE = OOS Sharpe / IS Sharpe。is_sharpe<=0 → NaN（用 assess_wfe 得裁决）。"""
    if is_sharpe <= 0:
        return float("nan")
    return oos_sharpe / is_sharpe


def assess_wfe(
    oos_sharpe: float,
    is_sharpe: float,
    pass_threshold: float = 0.6,
    red_flag_threshold: float = 0.5,
) -> dict:
    """WFE 裁决（digitalninjasystems 2026-07）：≥0.6 pass / <0.5 red_flag / 其间 marginal。

    Returns:
        {"wfe": float|None, "verdict": "pass"|"marginal"|"red_flag"|"undefined"}
    """
    wfe = walk_forward_efficiency(oos_sharpe, is_sharpe)
    if math.isnan(wfe):
        return {"wfe": None, "verdict": "undefined"}
    if wfe >= pass_threshold:
        verdict = "pass"
    elif wfe >= red_flag_threshold:
        verdict = "marginal"
    else:
        verdict = "red_flag"
    return {"wfe": wfe, "verdict": verdict}
