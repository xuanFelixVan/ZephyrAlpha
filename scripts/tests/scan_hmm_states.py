#!/usr/bin/env python
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-REGIME-001-SCAN | 13_regime_phase3_engineering_plan §2.1.5 / §2.1.6 步骤1-2
# [ARCH-REF] #13_regime_phase3_engineering_plan §2.1 #12_regime_phase2_validation §4
# [TTL] permanent
"""HMM 状态数 BIC 扫描脚本（13_regime_phase3_engineering_plan §2.1.5 / §2.1.6 步骤 1-2）.

数据驱动选择 HMM 最优态数（2-9 态），用 BIC elbow method 找拐点。
复用 C1 真实模式特征管线（RegimeFeatureBuilder）保证与生产 HMM 可比。

核心动作（对齐 13_regime_phase3_engineering_plan §2.1.6 施工顺序）：
  步骤 1：全历史 BIC 扫描（2-9 态）→ BIC/AIC/LL 曲线 + 拐点判定
  步骤 2 输入：用拐点 n_states 做 Viterbi 解码全历史 → 各态统计特征
              （出现天数 / 频率 / 各特征均值 / 1日&5日 forward return 均值）
              → 供 §2.1.6.2 重设计 _STATE_RISK_FACTORS 的态语义判定

BIC = -2 * log_likelihood + k * ln(n)
  k（GaussianHMM full 协方差自由参数数）:
    (n_states - 1)                              # 初始状态分布
    + n_states * (n_states - 1)                 # 转移矩阵
    + n_states * n_features                     # 均值向量
    + n_states * n_features * (n_features + 1) / 2   # full 协方差

拐点判定（三重信号交叉验证）:
  ① Kneedle：归一化 BIC 曲线，找距首尾弦最大距离点（标准 knee 算法）
  ② 改善比：ΔBIC(k) / ΔBIC(k-1) < 0.5 → 收益递减拐点
  ③ 全局最小 BIC：BIC 单调下降时取改善骤减处，非单调时取最小值

数据链（与 run_phase2_validation.py 完全一致）:
  ClickHouse → RegimeFeatureBuilder(指数K线 → HMM 6 特征)
    → RobustScaler 标准化（全历史 fit，与 A1 一致）
    → 各 n_states fit GaussianHMM(n_init=3 取最优 LL)
    → score(X) 取 LL → 算 BIC/AIC

Usage:
  python scripts/tests/scan_hmm_states.py                    # 全历史 BIC 扫描（步骤1）
  python scripts/tests/scan_hmm_states.py --walk-forward     # 加跑季度 BIC 稳定性（步骤7）
  python scripts/tests/scan_hmm_states.py --mock             # 合成数据冒烟
  python scripts/tests/scan_hmm_states.py --states 2,3,4,5,6 # 自定义态数列表

依据: 13_regime_phase3_engineering_plan §2.1.5 / §2.1.6
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

# real 模式才 import（避免依赖 ClickHouse/hmmlearn）
REAL_DEPS_OK = False
try:
    from zephyr.data import ch_reader  # noqa: F401
    from zephyr.regime.core.regime_detector import RegimeDetector  # noqa: F401
    from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

    REAL_DEPS_OK = True
except Exception as _exc:  # pragma: no cover
    _REAL_IMPORT_ERROR = _exc

_logger = logging.getLogger("scan_hmm_states")

# 扫描的默认态数列表（对齐 13_regime_phase3_engineering_plan §2.1.5：2-9 态，含 9 作基线对照）
DEFAULT_STATES: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 9)


# ── 报告数据结构 ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class StateScanResult:
    """单个 n_states 的扫描结果。"""

    n_states: int
    log_likelihood: float  # HMM score(X)，越高越好
    n_params: int  # 自由参数数 k
    bic: float  # -2*LL + k*ln(n)，越低越好
    aic: float  # -2*LL + 2*k，越低越好
    converged: bool  # 是否收敛（n_init 中至少一次成功）
    n_samples: int


@dataclass(frozen=True)
class StateStats:
    """单态 Viterbi 统计特征（步骤2 态语义设计输入）。"""

    state_label: str  # r1, r2, ...
    state_idx: int  # 0-based
    count: int
    frequency: float
    feature_means: dict[str, float]  # 各特征均值
    forward_return_1d_mean: float  # 1 日 forward return 均值
    forward_return_5d_mean: float  # 5 日 forward return 均值


@dataclass
class ScanReport:
    """BIC 扫描综合报告。"""

    results: list[StateScanResult] = field(default_factory=list)
    elbow_kneedle: int | None = None  # Kneedle 拐点
    elbow_improvement: int | None = None  # 改善比拐点
    min_bic_states: int | None = None  # 全局最小 BIC
    recommendation: int | None = None  # 最终推荐态数
    recommendation_reason: str = ""
    state_stats: list[StateStats] = field(default_factory=list)  # 推荐态数的 Viterbi 统计
    walk_forward_stability: dict[str, Any] | None = None  # 季度 BIC 稳定性（--walk-forward）
    degraded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "results": [asdict(r) for r in self.results],
            "elbow_kneedle": self.elbow_kneedle,
            "elbow_improvement": self.elbow_improvement,
            "min_bic_states": self.min_bic_states,
            "recommendation": self.recommendation,
            "recommendation_reason": self.recommendation_reason,
            "state_stats": [asdict(s) for s in self.state_stats],
            "walk_forward_stability": self.walk_forward_stability,
            "degraded": self.degraded,
        }


# ── BIC 参数计数 ──────────────────────────────────────────────────────


def count_hmm_params(n_states: int, n_features: int, covariance_type: str = "full") -> int:
    """计算 GaussianHMM 自由参数数。

    Args:
        n_states: 隐状态数。
        n_features: 观测特征维数。
        covariance_type: 协方差类型（full/diag/spherical/tied）。

    Returns:
        自由参数总数 k。
    """
    # 初始状态分布 + 转移矩阵
    k = (n_states - 1) + n_states * (n_states - 1)
    # 均值向量
    k += n_states * n_features
    # 协方差参数
    if covariance_type == "full":
        k += n_states * n_features * (n_features + 1) // 2
    elif covariance_type == "diag":
        k += n_states * n_features
    elif covariance_type == "spherical":
        k += n_states
    elif covariance_type == "tied":
        k += n_features * (n_features + 1) // 2
    return k


# ── 拐点检测 ──────────────────────────────────────────────────────────


def kneedle_elbow(states: list[int], bic: list[float]) -> int | None:
    """Kneedle 拐点检测：归一化后找距首尾弦最大距离点。

    BIC 越低越好，曲线通常先陡降后变缓，拐点在"降速骤减"处。

    Args:
        states: n_states 列表（升序）。
        bic: 对应 BIC 列表。

    Returns:
        拐点对应的 n_states，无法判定返回 None。
    """
    if len(states) < 3:
        return None
    x = np.array(states, dtype=float)
    y = np.array(bic, dtype=float)
    # 归一化到 [0, 1]
    x_n = (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else np.zeros_like(x)
    y_n = (y - y.min()) / (y.max() - y.min()) if y.max() > y.min() else np.zeros_like(y)
    # 首尾弦：从 (x_n[0], y_n[0]) 到 (x_n[-1], y_n[-1])
    # 每点到弦的距离（BIC 下降型，拐点在弦下方，距离为正）
    distances = []
    for i in range(len(x_n)):
        # 弦上对应 y
        if x_n[-1] > x_n[0]:
            chord_y = y_n[0] + (y_n[-1] - y_n[0]) * (x_n[i] - x_n[0]) / (x_n[-1] - x_n[0])
        else:
            chord_y = y_n[i]
        # 距离：点在弦下方为正（BIC 曲线下凸）
        dist = chord_y - y_n[i]
        distances.append(dist)
    distances = np.array(distances)
    # 拐点 = 最大正距离点（排除首尾）
    if distances.max() <= 0:
        return None
    # 仅在中间点中选（排除两端）
    interior_idx = np.argmax(distances)
    if interior_idx == 0 or interior_idx == len(states) - 1:
        return None
    return int(states[interior_idx])


def improvement_ratio_elbow(states: list[int], bic: list[float], threshold: float = 0.5) -> int | None:
    """改善比拐点：ΔBIC(k)/ΔBIC(k-1) < threshold → 收益递减拐点。

    Args:
        states: n_states 列表（升序）。
        bic: 对应 BIC 列表。
        threshold: 改善比阈值（默认 0.5，即改善幅度不及前一步一半）。

    Returns:
        第一个收益递减拐点的 n_states，无法判定返回 None。
    """
    if len(states) < 3:
        return None
    deltas = []  # ΔBIC(k) = BIC(k-1) - BIC(k) > 0 表示改善
    for i in range(1, len(bic)):
        deltas.append(bic[i - 1] - bic[i])
    # 找第一个 ΔBIC(k) / ΔBIC(k-1) < threshold 且 ΔBIC(k-1) > 0 的点
    for i in range(1, len(deltas)):
        if deltas[i - 1] > 0 and deltas[i] >= 0:
            ratio = deltas[i] / deltas[i - 1] if deltas[i - 1] != 0 else 1.0
            if ratio < threshold:
                # 拐点 = states[i+1]（改善骤减的那个态数）
                return int(states[i + 1])
    return None


def recommend_states(report: ScanReport) -> tuple[int, str]:
    """综合三重信号给推荐态数。

    优先级：
      1. 三信号一致 → 直接取
      2. Kneedle 与改善比一致 → 取该值（比 min_bic 更保守，防过拟合）
      3. 否则取 Kneedle（若有），否则取 min_bic，并标注不确定性
    """
    k = report.elbow_kneedle
    imp = report.elbow_improvement
    mn = report.min_bic_states
    signals = [s for s in (k, imp, mn) if s is not None]
    if not signals:
        return 0, "无可用信号（数据不足或拟合失败）"
    # 三信号一致
    if k is not None and imp is not None and mn is not None and k == imp == mn:
        return k, f"三信号一致（Kneedle=改善比=minBIC={k}）→ 高置信推荐"
    # Kneedle 与改善比一致（最可靠组合，防过拟合）
    if k is not None and imp is not None and k == imp:
        return k, f"Kneedle 与改善比一致（={k}），minBIC={mn}（可能偏大防过拟合取保守值）"
    # Kneedle 与 min_bic 一致
    if k is not None and mn is not None and k == mn:
        return k, f"Kneedle 与 minBIC 一致（={k}），改善比={imp}"
    # 改善比与 min_bic 一致
    if imp is not None and mn is not None and imp == mn:
        return imp, f"改善比与 minBIC 一致（={imp}），Kneedle={k}"
    # 信号不一致 → 取 Kneedle（最保守，防过拟合），标注
    if k is not None:
        return k, (f"信号不一致（Kneedle={k}/改善比={imp}/minBIC={mn}），取 Kneedle（保守防过拟合）")
    if imp is not None:
        return imp, (f"信号不一致（Kneedle={k}/改善比={imp}/minBIC={mn}），取改善比拐点")
    return int(mn), f"仅 minBIC 可用（={mn}），Kneedle/改善比未检出，需人工复核"


# ── HMM 拟合 + BIC 计算 ───────────────────────────────────────────────


def fit_and_score(
    X: np.ndarray,
    n_states: int,
    covariance_type: str = "full",
    n_iter: int = 100,
    n_init: int = 3,
    random_state: int = 42,
) -> tuple[float, bool]:
    """fit GaussianHMM（n_init 次取最优 LL），返回 (log_likelihood, converged)。

    复用 RegimeDetector.fit 的 n_init 多次重启逻辑（保证与生产拟合一致）。
    """
    from hmmlearn.hmm import GaussianHMM

    best_score = -np.inf
    converged = False
    last_exc: Exception | None = None
    for k in range(max(1, n_init)):
        try:
            m = GaussianHMM(
                n_components=n_states,
                covariance_type=covariance_type,
                n_iter=n_iter,
                random_state=random_state + k,
            )
            m.fit(X)
            s = float(m.score(X))
            if s > best_score:
                best_score = s
                converged = True
        except Exception as exc:
            last_exc = exc
    if not converged and last_exc is not None:
        raise last_exc
    return best_score, converged


def scan_bic(
    X: np.ndarray,
    states: list[int],
    covariance_type: str = "full",
    n_iter: int = 100,
    n_init: int = 3,
    random_state: int = 42,
) -> list[StateScanResult]:
    """对每个 n_states fit HMM 并计算 BIC/AIC。"""
    n_samples, n_features = X.shape
    results: list[StateScanResult] = []
    for ns in states:
        try:
            ll, converged = fit_and_score(
                X,
                ns,
                covariance_type,
                n_iter,
                n_init,
                random_state,
            )
            k = count_hmm_params(ns, n_features, covariance_type)
            bic = -2.0 * ll + k * np.log(n_samples)
            aic = -2.0 * ll + 2.0 * k
            results.append(
                StateScanResult(
                    n_states=ns,
                    log_likelihood=round(ll, 4),
                    n_params=k,
                    bic=round(bic, 4),
                    aic=round(aic, 4),
                    converged=converged,
                    n_samples=n_samples,
                )
            )
            _logger.info("n_states=%d: LL=%.2f, k=%d, BIC=%.2f, AIC=%.2f", ns, ll, k, bic, aic)
        except Exception as exc:
            _logger.warning("n_states=%d 拟合失败: %s", ns, exc)
            results.append(
                StateScanResult(
                    n_states=ns,
                    log_likelihood=float("nan"),
                    n_params=0,
                    bic=float("nan"),
                    aic=float("nan"),
                    converged=False,
                    n_samples=n_samples,
                )
            )
    return results


# ── Viterbi 解码 + 态统计特征（步骤2 输入）────────────────────────────


def viterbi_state_stats(
    X: np.ndarray,
    feature_names: list[str],
    n_states: int,
    close: Any | None = None,
    covariance_type: str = "full",
    n_iter: int = 100,
    n_init: int = 3,
    random_state: int = 42,
) -> list[StateStats]:
    """用推荐 n_states fit + Viterbi 解码全历史，算各态统计特征。

    统计内容（供 §2.1.6.2 重设计 _STATE_RISK_FACTORS）:
      - count / frequency：态出现天数与占比
      - feature_means：各特征均值（realized_vol_pct=波动率, kalman_slope=趋势斜率,
        ad_ratio=涨跌家数比, volume_anomaly=量能异动 等）
      - forward_return_1d/5d_mean：态内 1日/5日 forward return 均值
        → 正值大=牛市态，负值大=熊市态，近0=震荡态

    Args:
        X: 标准化后的特征矩阵 (T, F)。
        feature_names: 特征列名。
        n_states: 推荐态数。
        close: 指数收盘价 Series（index 与 X 行对齐），算 forward return 用。
            None 时 forward return 填 NaN。
    """
    from hmmlearn.hmm import GaussianHMM

    # fit（与 scan_bic 同参数）
    best_model = None
    best_score = -np.inf
    for k in range(max(1, n_init)):
        try:
            m = GaussianHMM(
                n_components=n_states,
                covariance_type=covariance_type,
                n_iter=n_iter,
                random_state=random_state + k,
            )
            m.fit(X)
            s = float(m.score(X))
            if s > best_score:
                best_score = s
                best_model = m
        except Exception as exc:
            _logger.warning("Viterbi stats fit (n_init=%d) 失败: %s", k, exc)
    if best_model is None:
        return []

    state_seq = best_model.predict(X)  # Viterbi (T,)
    total = len(state_seq)

    # forward returns（需 close 对齐 X 行）
    fr_1d = np.full(total, np.nan)
    fr_5d = np.full(total, np.nan)
    if close is not None and len(close) >= total:
        try:
            import pandas as pd

            close_arr = np.asarray(close, dtype=float)
            if len(close_arr) > total:
                close_arr = close_arr[-total:]  # 末段对齐
            # forward return = close[t+n]/close[t] - 1
            for shift, arr in ((1, fr_1d), (5, fr_5d)):
                if len(close_arr) > shift:
                    shifted = np.roll(close_arr, -shift)
                    shifted[-shift:] = np.nan
                    arr[:] = np.where(close_arr > 0, shifted / close_arr - 1.0, np.nan)
        except Exception as exc:
            _logger.warning("forward return 计算失败: %s", exc)

    stats: list[StateStats] = []
    for i in range(n_states):
        mask = state_seq == i
        count = int(mask.sum())
        freq = count / total if total > 0 else 0.0
        if count > 0:
            feat_means = {
                fn: float(np.mean(X[mask, j])) if j < X.shape[1] else 0.0 for j, fn in enumerate(feature_names)
            }
            fr1 = float(np.nanmean(fr_1d[mask])) if np.isfinite(fr_1d[mask]).any() else float("nan")
            fr5 = float(np.nanmean(fr_5d[mask])) if np.isfinite(fr_5d[mask]).any() else float("nan")
        else:
            feat_means = {fn: 0.0 for fn in feature_names}
            fr1 = float("nan")
            fr5 = float("nan")
        stats.append(
            StateStats(
                state_label=f"r{i + 1}",
                state_idx=i,
                count=count,
                frequency=round(freq, 4),
                feature_means={k: round(v, 4) for k, v in feat_means.items()},
                forward_return_1d_mean=round(fr1, 6),
                forward_return_5d_mean=round(fr5, 6),
            )
        )
    return stats


# ── walk-forward 季度 BIC 稳定性（步骤7）──────────────────────────────


def walk_forward_bic_stability(
    features: Any,
    feature_names: list[str],
    states: list[int],
    builder: Any,
    train_years: int = 5,
    refit_freq: str = "QE",
    covariance_type: str = "full",
    n_iter: int = 100,
    n_init: int = 3,
) -> dict[str, Any]:
    """walk-forward 各季度窗口跑 BIC，确认拐点跨期一致（13_regime_phase3_engineering_plan §2.1.6 步骤7）。

    每个 walk-forward 季度：
      - 取 train_years 年训练数据
      - RobustScaler fit on train（PIT，与 C1/walk-forward 一致）
      - 各 n_states fit + BIC
      - 记录本季度 min-BIC 态数与 Kneedle 拐点

    Returns:
        {quarters: [...], per_quarter: [{quarter, min_bic_states, kneedle, bic_by_states}],
         stability: 拐点跨季度一致率}
    """
    import pandas as pd

    try:
        from sklearn.preprocessing import RobustScaler
    except ImportError:  # pragma: no cover
        RobustScaler = None  # type: ignore[assignment]

    features_shifted = features.shift(1)  # PIT
    quarter_ends = list(
        pd.date_range(
            start=pd.Timestamp(builder.data_load_start) + pd.DateOffset(years=train_years),
            end=pd.Timestamp(builder.backtest_end),
            freq=refit_freq,
        )
    )
    per_quarter: list[dict[str, Any]] = []
    elbow_counts: dict[int, int] = {}

    for i, q in enumerate(quarter_ends):
        train_start = (q - pd.DateOffset(years=train_years)).strftime("%Y-%m-%d")
        train_end = q.strftime("%Y-%m-%d")
        try:
            train_matrix = builder.build_train_matrix(train_start, train_end)
            X_train = train_matrix["X"]
            if getattr(builder, "standardize_features", False) and RobustScaler is not None:
                scaler = RobustScaler().fit(X_train)
                X_train = scaler.transform(X_train)
            X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
        except Exception as exc:
            _logger.warning("walk-forward Q%d [%s,%s] 取数失败: %s", i + 1, train_start, train_end, exc)
            continue

        # 各 n_states BIC
        q_results = scan_bic(X_train, states, covariance_type, n_iter, n_init)
        valid = [(r.n_states, r.bic) for r in q_results if r.converged and np.isfinite(r.bic)]
        if not valid:
            continue
        q_states = [v[0] for v in valid]
        q_bic = [v[1] for v in valid]
        min_states = int(q_states[int(np.argmin(q_bic))])
        kneedle = kneedle_elbow(q_states, q_bic)
        per_quarter.append(
            {
                "quarter": q.strftime("%Y-%m-%d"),
                "train_start": train_start,
                "train_end": train_end,
                "n_samples": int(X_train.shape[0]),
                "min_bic_states": min_states,
                "kneedle": kneedle,
                "bic_by_states": {str(s): round(b, 2) for s, b in valid},
            }
        )
        if kneedle is not None:
            elbow_counts[kneedle] = elbow_counts.get(kneedle, 0) + 1
        _logger.info("walk-forward Q%d [%s]: minBIC=%d, kneedle=%s", i + 1, train_end, min_states, kneedle)

    # 稳定性：拐点最常见值占比
    total_q = len(per_quarter)
    stability = {
        "total_quarters": total_q,
        "elbow_distribution": {str(k): v for k, v in sorted(elbow_counts.items())},
        "most_common_elbow": max(elbow_counts, key=elbow_counts.get) if elbow_counts else None,
        "most_common_ratio": (max(elbow_counts.values()) / total_q) if elbow_counts and total_q > 0 else 0.0,
    }
    return {"per_quarter": per_quarter, "stability": stability}


# ── 数据加载 ──────────────────────────────────────────────────────────


def _get_feature_names(builder: Any) -> list[str]:
    """从 builder 获取 FEATURE_NAMES（兼容 builder.feature_names / 模块常量）。"""
    names = getattr(builder, "feature_names", None)
    if names is not None:
        return list(names)
    from zephyr.regime.regime_feature_builder import FEATURE_NAMES

    return list(FEATURE_NAMES)


def _get_index_close(builder: Any) -> Any:
    """从 builder 获取 market_proxy 的 close 序列（forward return 用）。

    复刻 phase2_runner.Phase2Runner._get_index_close。
    """
    import pandas as pd

    try:
        kline = builder.get_index_kline()
        if kline is None or kline.empty:
            return None
        proxy = builder.market_proxy
        if isinstance(kline.index, pd.MultiIndex):
            try:
                proxy_df = kline.xs(proxy, level="symbol")
            except KeyError:
                return None
        else:
            proxy_df = (
                kline[kline.index.get_level_values("symbol") == proxy] if "symbol" in kline.index.names else kline
            )
        close = proxy_df["close"].astype(float).sort_index()
        close = close[~close.index.duplicated(keep="last")]
        return close
    except Exception as exc:
        _logger.warning("获取 index close 失败: %s", exc)
        return None


def _clean_matrix(X: np.ndarray) -> np.ndarray:
    """清理特征矩阵：2D float + dropna 行 + 钳 inf（复刻 A1._clean_matrix）。"""
    if not isinstance(X, np.ndarray):
        X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    valid = np.isfinite(X).all(axis=1)
    X_clean = X[valid]
    return np.nan_to_num(X_clean, nan=0.0, posinf=0.0, neginf=0.0)


# ── 运行入口 ──────────────────────────────────────────────────────────


def run_mock(states: list[int]) -> int:
    """合成数据冒烟：验证 BIC 扫描 + 拐点检测 + Viterbi 统计端到端跑通。

    合成 3 个高斯簇（序列拼接，含时序结构利于 HMM 建模），预期拐点 ∈ {3, 4}。
    mock 用较高 n_init（8）让 EM 有足够重启跳出局部最优；生产扫描用 n_init=3
    与 A1/walk-forward 可比（13_regime_phase3_engineering_plan §2.1.6 步骤1）。
    """
    # mock 用较高 n_init 避免 EM 局部最优（数据小，开销可接受）
    mock_n_init = 8
    print(f"[mock] BIC 扫描冒烟：合成 3 簇特征矩阵，扫描 states={states}, n_init={mock_n_init}")
    rng = np.random.default_rng(42)
    # 合成 3 个明显不同的高斯簇（序列拼接：前段簇0/中段簇3/末段簇-3，含时序结构）
    n_per = 500
    X = np.vstack(
        [
            rng.normal([0, 0, 0, 0, 0, 0], 0.3, (n_per, 6)),
            rng.normal([3, 3, 3, 3, 3, 3], 0.3, (n_per, 6)),
            rng.normal([-3, -3, -3, -3, -3, -3], 0.3, (n_per, 6)),
        ]
    )
    feature_names = [f"f{i}" for i in range(6)]
    results = scan_bic(X, states, n_init=mock_n_init)
    print("\n[mock] BIC 扫描结果:")
    print(f"  {'n_states':>9} {'LL':>10} {'k':>5} {'BIC':>12} {'AIC':>12} {'conv':>5}")
    for r in results:
        print(
            f"  {r.n_states:>9} {r.log_likelihood:>10.2f} {r.n_params:>5} "
            f"{r.bic:>12.2f} {r.aic:>12.2f} {str(r.converged):>5}"
        )

    valid = [(r.n_states, r.bic) for r in results if r.converged and np.isfinite(r.bic)]
    v_states = [v[0] for v in valid]
    v_bic = [v[1] for v in valid]
    elbow_k = kneedle_elbow(v_states, v_bic)
    elbow_i = improvement_ratio_elbow(v_states, v_bic)
    min_s = int(v_states[int(np.argmin(v_bic))]) if v_bic else None
    print(f"\n[mock] Kneedle={elbow_k}, 改善比={elbow_i}, minBIC={min_s}")

    # 合成 3 簇：EM 充分重启后 n=3 应找到真解（LL≈-1935），拐点 ∈ {3,4}
    # （n=4 因多 1 态参数 LL 略高但 BIC 惩罚后可能略高于 n=3，两者皆合理）
    report = ScanReport(
        results=results,
        elbow_kneedle=elbow_k,
        elbow_improvement=elbow_i,
        min_bic_states=min_s,
    )
    rec, reason = recommend_states(report)
    print(f"[mock] 推荐={rec}（{reason}）")
    ok = rec in (3, 4)
    print(f"[mock] 预期拐点 ∈ {{3,4}}（合成 3 簇）→ {'✓' if ok else '✗'}")

    # Viterbi 统计冒烟（用推荐态数；若推荐为 4 则取 3 验证 3 簇恢复）
    stats_n = 3 if rec in (3, 4) else (rec or 3)
    stats = viterbi_state_stats(X, feature_names, n_states=stats_n, n_init=mock_n_init)
    print(f"\n[mock] Viterbi {stats_n} 态统计:")
    for s in stats:
        print(
            f"  {s.state_label}: count={s.count} freq={s.frequency:.1%} feat_mean_f0={s.feature_means.get('f0', 0):.2f}"
        )
    # 3 簇恢复校验：每态样本应接近 500（允许 EM 偶发合并，验证至少 2 态 ≥ 400）
    big_states = [s for s in stats if s.count >= 400]
    print(f"[mock] 3 簇恢复：≥400 样本的态数 = {len(big_states)} ({'✓' if len(big_states) >= 2 else '⚠'})")
    print("[mock] BIC 扫描冒烟跑通 ✓")
    return 0 if ok else 1


def run_real(
    states: list[int],
    walk_forward: bool = False,
    train_years: int = 5,
    n_init: int = 3,
    covariance_type: str = "full",
) -> int:
    """真实数据 BIC 扫描（2010-2026 全历史）。"""
    if not REAL_DEPS_OK:
        print(f"[real] 依赖导入失败: {_REAL_IMPORT_ERROR}")
        print("[real] 请确认 zephyr.regime / zephyr.data 模块可用（需 ClickHouse + hmmlearn）")
        return 1

    warnings.filterwarnings("ignore", message=".*not converging.*")
    logging.getLogger("hmmlearn").setLevel(logging.ERROR)

    print(f"[real] 配置: states={states}, covariance={covariance_type}, n_init={n_init}")
    print("[real] 构建 RegimeFeatureBuilder（复用 C1 真实模式配置）...")
    builder = RegimeFeatureBuilder(
        backtest_start="2015-01-01",
        backtest_end="2026-06-30",
        data_load_start="2010-01-01",
        enable_full_risk=True,
        enable_overlay=True,
    )

    print("[real] 构建特征矩阵...")
    features = builder.build_features()
    feature_names = _get_feature_names(builder)
    X_full = features[feature_names].to_numpy(dtype=float)
    X_clean = _clean_matrix(X_full)
    print(
        f"[real] 特征: {X_clean.shape[0]} 行 × {X_clean.shape[1]} 特征 "
        f"[{features.index.min()} ~ {features.index.max()}]"
    )
    print(f"[real] 特征列: {feature_names}")

    # RobustScaler 标准化（全历史 fit，与 A1 一致）
    try:
        from sklearn.preprocessing import RobustScaler

        scaler = RobustScaler().fit(X_clean)
        X_fit = scaler.transform(X_clean)
        print("[real] RobustScaler 标准化（与 A1/walk-forward 一致）")
    except ImportError:  # pragma: no cover
        scaler = None
        X_fit = X_clean

    # ── 步骤1：BIC 扫描 ──
    print(f"\n[real] 步骤1: BIC 扫描（states={states}, n_init={n_init}），预计 3-8 分钟...")
    results = scan_bic(X_fit, states, covariance_type, n_iter=100, n_init=n_init)

    print("\n" + "=" * 78)
    print("BIC 扫描结果（全历史 2010-2026）")
    print("=" * 78)
    print(f"  {'n_states':>9} {'LL':>12} {'k':>6} {'BIC':>14} {'AIC':>14} {'conv':>5}")
    print("  " + "-" * 70)
    for r in results:
        ll_str = f"{r.log_likelihood:.2f}" if np.isfinite(r.log_likelihood) else "NaN"
        bic_str = f"{r.bic:.2f}" if np.isfinite(r.bic) else "NaN"
        aic_str = f"{r.aic:.2f}" if np.isfinite(r.aic) else "NaN"
        print(f"  {r.n_states:>9} {ll_str:>12} {r.n_params:>6} {bic_str:>14} {aic_str:>14} {str(r.converged):>5}")

    # ── 拐点判定 ──
    valid = [(r.n_states, r.bic) for r in results if r.converged and np.isfinite(r.bic)]
    if not valid:
        print("\n⛔ 无有效拟合结果，无法判定拐点")
        return 1
    v_states = [v[0] for v in valid]
    v_bic = [v[1] for v in valid]
    elbow_k = kneedle_elbow(v_states, v_bic)
    elbow_i = improvement_ratio_elbow(v_states, v_bic)
    min_s = int(v_states[int(np.argmin(v_bic))])

    print("\n" + "-" * 78)
    print("拐点判定（三重信号）:")
    print(f"  ① Kneedle 拐点       = {elbow_k}")
    print(f"  ② 改善比拐点(<0.5)   = {elbow_i}")
    print(f"  ③ 全局最小 BIC 态数  = {min_s}")

    report = ScanReport(
        results=results,
        elbow_kneedle=elbow_k,
        elbow_improvement=elbow_i,
        min_bic_states=min_s,
    )
    rec, reason = recommend_states(report)
    report.recommendation = rec
    report.recommendation_reason = reason
    print(f"\n  ★ 推荐态数 = {rec}")
    print(f"    理由: {reason}")

    # ── 步骤2输入：Viterbi 解码 + 态统计特征 ──
    if rec and rec > 0:
        print(f"\n[real] 步骤2输入: Viterbi 解码（n_states={rec}）+ 各态统计特征...")
        close = _get_index_close(builder)
        # close 对齐到 X_clean（dropna 后的行）。X_clean 末段对齐 features 末段，
        # close 也取同范围末段。
        close_aligned = None
        if close is not None and len(close) >= len(X_clean):
            close_aligned = close.iloc[-len(X_clean) :].to_numpy(dtype=float)
        stats = viterbi_state_stats(
            X_fit,
            feature_names,
            n_states=rec,
            close=close_aligned,
            covariance_type=covariance_type,
            n_iter=100,
            n_init=n_init,
        )
        report.state_stats = stats

        print("\n  各态统计特征（供重设计 _STATE_RISK_FACTORS 态语义）:")
        print(
            f"  {'态':>4} {'天数':>6} {'占比':>7} {'vol_pct':>9} {'slope':>8} "
            f"{'ad_ratio':>9} {'vol_anom':>9} {'fr_1d':>9} {'fr_5d':>9}"
        )
        print("  " + "-" * 74)
        for s in stats:
            fm = s.feature_means
            print(
                f"  {s.state_label:>4} {s.count:>6} {s.frequency:>6.1%} "
                f"{fm.get('realized_vol_pct', 0):>9.3f} {fm.get('kalman_slope', 0):>8.3f} "
                f"{fm.get('ad_ratio', 0):>9.3f} {fm.get('volume_anomaly', 0):>9.3f} "
                f"{s.forward_return_1d_mean:>9.4f} {s.forward_return_5d_mean:>9.4f}"
            )
        print("\n  态语义判读指引:")
        print("    - forward_return_5d_mean 大正 → 牛市态（shrinkage≈1.0 不收缩）")
        print("    - forward_return_5d_mean 大负 → 熊市态（shrinkage≈0.30-0.50 大幅收缩）")
        print("    - realized_vol_pct 高 + fr_5d 负 → 危机态（shrinkage≈0.30）")
        print("    - forward_return 近0 + 低 vol → 震荡态（shrinkage≈0.80-0.90）")
        print("    - 按 kalman_slope/ad_ratio 排序辅助区分趋势/非趋势态")

    # ── 步骤7：walk-forward 季度 BIC 稳定性 ──
    if walk_forward:
        print(f"\n[real] 步骤7: walk-forward 季度 BIC 稳定性验证（train_years={train_years}）...")
        print("[real] 预计 5-15 分钟（每季度 × {} 态 × n_init={}）...".format(len(states), n_init))
        wf = walk_forward_bic_stability(
            features,
            feature_names,
            states,
            builder,
            train_years=train_years,
            covariance_type=covariance_type,
            n_iter=100,
            n_init=n_init,
        )
        report.walk_forward_stability = wf
        stab = wf["stability"]
        print(f"\n  walk-forward 覆盖 {stab['total_quarters']} 个季度")
        print(f"  拐点分布: {stab['elbow_distribution']}")
        print(f"  最常见拐点: {stab['most_common_elbow']} (占比 {stab['most_common_ratio']:.1%})")
        print(f"  拐点跨期一致性: {'✓ 稳定' if stab['most_common_ratio'] >= 0.6 else '⚠ 不稳定'}")

    # ── 写 JSON 报告 ──
    out = Path("runtime/phase2_reports")
    out.mkdir(parents=True, exist_ok=True)
    ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    wf_tag = "_wf" if walk_forward else ""
    json_path = out / f"bic_scan{wf_tag}_{ts}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2, default=str)
    print(f"\n[real] JSON 报告: {json_path}")

    print("\n" + "=" * 78)
    if rec and rec > 0:
        print(f"★ BIC 扫描完成：推荐 HMM 态数 9 → {rec}")
        print("  下一步（步骤2）：用上述 Viterbi 统计特征重设计 _STATE_RISK_FACTORS + TRANSITION_CONFIG")
    else:
        print("⛔ BIC 扫描未给出明确推荐，需人工复核")
    print("=" * 78)
    return 0 if rec and rec > 0 else 1


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="HMM 状态数 BIC 扫描（13_regime_phase3_engineering_plan §2.1.5）")
    parser.add_argument("--mock", action="store_true", help="合成数据冒烟")
    parser.add_argument("--walk-forward", action="store_true", help="加跑 walk-forward 季度 BIC 稳定性（步骤7）")
    parser.add_argument(
        "--states",
        type=str,
        default=None,
        help=f"自定义态数列表（逗号分隔，默认 {','.join(map(str, DEFAULT_STATES))}）",
    )
    parser.add_argument("--train-years", type=int, default=5, help="walk-forward 训练窗口年数（默认 5）")
    parser.add_argument("--n-init", type=int, default=3, help="HMM n_init（多次 EM 重启取最优，默认 3，与生产一致）")
    parser.add_argument(
        "--covariance", type=str, default="full", help="协方差类型（full/diag/spherical/tied，默认 full）"
    )
    args = parser.parse_args()

    states = DEFAULT_STATES
    if args.states:
        states = tuple(int(s.strip()) for s in args.states.split(",") if s.strip())

    if args.mock:
        sys.exit(run_mock(list(states)))
    sys.exit(
        run_real(
            states=list(states),
            walk_forward=args.walk_forward,
            train_years=args.train_years,
            n_init=args.n_init,
            covariance_type=args.covariance,
        )
    )


if __name__ == "__main__":
    main()
