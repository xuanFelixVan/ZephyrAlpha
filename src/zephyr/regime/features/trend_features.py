# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §3 F2a/F2b
# [MODULE] zephyr.regime.features.trend_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder消费F2a hurst_dfa + F2b kalman_slope)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] hurst_dfa ∈ (0,1); kalman_slope ∈ [-1,1]; PIT严格(t-1及以前)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_trend_features.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
趋势特征：Hurst DFA 指数 + Kalman 自适应斜率（MOD-REGIME-002 §3 F2a/F2b）。

2026-08-06 修正：替换"250日均线斜率"（依赖量纲/图表比例 = 伪精确）。
- F2a hurst_dfa: DFA法Hurst指数，衡量趋势持久性（>0.5趋势 / <0.5均值回归 / ≈0.5随机游走）
- F2b kalman_slope: Kalman滤波自适应斜率，归一化[-1,1]，不依赖固定窗口

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: prices 参数
#   fields: 参数 prices，类型注解 np.ndarray
#   code: trend_features.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: window 参数
#   fields: 参数 window，类型注解 int | None
#   code: trend_features.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: h_early 参数
#   fields: 参数 h_early，类型注解 float
#   code: trend_features.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: h_late 参数
#   fields: 参数 h_late，类型注解 float
#   code: trend_features.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① hurst_dfa
#   name_en: hurst_dfa
#   intro: DFA (Detrended Fluctuation Analysis) 法计算 Hurst 指数。
#   desc: DFA (Detrended Fluctuation Analysis) 法计算 Hurst 指数。 算法步骤： 1. 对数收益率 r = diff(log(prices)) 2…；源码 L99-L166
#   inputs: prices window
#   outputs: float
# - id: A2
#   name_zh: ② kalman_slope
#   name_en: kalman_slope
#   intro: Kalman 滤波估计趋势斜率，归一化至 [-1, 1]。
#   desc: Kalman 滤波估计趋势斜率，归一化至 [-1, 1]。 状态空间模型： 状态: s(t) = s(t-1) + w(t) （潜在趋势斜率，随机游走） 观测: y(t) = s…；源码 L195-L249
#   inputs: prices
#   outputs: float
# - id: A3
#   name_zh: ③ detect_hurst_decay
#   name_en: detect_hurst_decay
#   intro: 检测 Hurst 指数衰退（趋势衰竭信号）。
#   desc: 检测 Hurst 指数衰退（趋势衰竭信号）。 蓝图 §5.1.10：Hurst 从趋势态（>0.65）衰退到随机态（<0.50）= 趋势衰竭。 判定逻辑（双重条件，比绝对阈值更稳…；源码 L257-L275
#   inputs: h_early h_late
#   outputs: bool
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-REGIME-002(RegimeFeatureBuilder消费F2a hurst_dfa + F2b kalman_slope)
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-REGIME-002(RegimeFeatureBuilder消费F2a hurst_dfa + F2b kalman_slope)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import numpy as np

__all__ = ["hurst_dfa", "kalman_slope", "detect_hurst_decay"]


# ---------------------------------------------------------------------------
# F2a: Hurst 指数（DFA 法）
# ---------------------------------------------------------------------------


def hurst_dfa(prices: np.ndarray, window: int | None = None) -> float:
    """DFA (Detrended Fluctuation Analysis) 法计算 Hurst 指数。

    算法步骤：
    1. 对数收益率 r = diff(log(prices))
    2. 累积和序列（profile） Y = cumsum(r - mean(r))
    3. 分割为等长窗口 w，每窗口做线性去趋势
    4. 计算均方根波动 F(w)
    5. log(F(w)) vs log(w) 线性回归，斜率 = Hurst 指数

    Parameters
    ----------
    prices : 序列（价格）
    window : 取最近 window 个价格点；None 表示用全部

    Returns
    -------
    Hurst 指数 ∈ (0, 1)
      H > 0.5  趋势持久（正相关收益率）
      H < 0.5  均值回归（负相关收益率）
      H ≈ 0.5  随机游走
    """
    prices = np.asarray(prices, dtype=float)
    if window is not None and len(prices) > window:
        prices = prices[-window:]

    # 降级：序列太短无法可靠估计
    if len(prices) < 50:
        return 0.5

    # 1. 对数收益率
    log_prices = np.log(prices)
    returns = np.diff(log_prices)
    n = len(returns)
    if n < 20:
        return 0.5

    # 2. 累积和序列（profile）
    profile = np.cumsum(returns - np.mean(returns))

    # 3. 选择窗口尺度（scales）：对数等间距，从 4 到 n//4
    min_scale = 4
    max_scale = max(min_scale + 1, n // 4)
    scales = np.unique(np.logspace(np.log10(min_scale), np.log10(max_scale), 20).astype(int))
    scales = scales[scales >= min_scale]

    valid_scales = []
    fluctuations = []
    for s in scales:
        n_windows = n // s
        if n_windows < 2:
            continue
        # 截断为完整窗口
        truncated = profile[: n_windows * s].reshape(n_windows, s)
        # 向量化线性去趋势
        rms = _detrended_rms(truncated, s)
        if rms > 0 and np.isfinite(rms):
            valid_scales.append(s)
            fluctuations.append(rms)

    if len(valid_scales) < 4:
        return 0.5

    # 5. log-log 线性回归，斜率 = Hurst
    log_s = np.log(np.array(valid_scales, dtype=float))
    log_f = np.log(np.array(fluctuations, dtype=float))
    hurst = float(np.polyfit(log_s, log_f, 1)[0])
    return float(np.clip(hurst, 0.0, 1.0))


def _detrended_rms(segments: np.ndarray, s: int) -> float:
    """对每个窗口做线性去趋势，返回各窗口 RMS 的均方根。"""
    x = np.arange(s, dtype=float)
    x_mean = x.mean()
    x_dev = x - x_mean
    x_var = float((x_dev**2).sum())

    if x_var < 1e-15:
        return 0.0

    # 向量化最小二乘：slope = sum(x_dev * y_dev) / sum(x_dev^2)
    y_mean = segments.mean(axis=1, keepdims=True)
    y_dev = segments - y_mean
    slopes = (x_dev[None, :] * y_dev).sum(axis=1) / x_var
    intercepts = y_mean.flatten() - slopes * x_mean
    trends = slopes[:, None] * x[None, :] + intercepts[:, None]
    residuals = segments - trends
    rms_per_window = np.sqrt((residuals**2).mean(axis=1))
    return float(np.sqrt((rms_per_window**2).mean()))


# ---------------------------------------------------------------------------
# F2b: Kalman 滤波自适应斜率
# ---------------------------------------------------------------------------


def kalman_slope(prices: np.ndarray) -> float:
    """Kalman 滤波估计趋势斜率，归一化至 [-1, 1]。

    状态空间模型：
        状态: s(t) = s(t-1) + w(t)        （潜在趋势斜率，随机游走）
        观测: y(t) = s(t) + v(t)          （对数收益率）

    Kalman 递推估计 s(t)，自适应追踪斜率变化，不依赖固定窗口。
    归一化: kalman_slope = clamp(s / (10 × std(r)), -1, 1)

    Parameters
    ----------
    prices : 序列（价格）

    Returns
    -------
    归一化斜率 ∈ [-1, 1]（正=上涨趋势，负=下跌趋势，0=震荡）
    """
    prices = np.asarray(prices, dtype=float)
    if len(prices) < 5:
        return 0.0

    # 对数收益率作为观测
    returns = np.diff(np.log(prices))
    if len(returns) < 4:
        return 0.0

    # 观测噪声方差
    obs_var = float(np.var(returns))
    if obs_var < 1e-15:
        return 0.0

    # Kalman 参数：Q 与 R 成比例，保证不同噪声水平下增益一致
    # Q/R = 0.01 → 稳态增益 K ≈ 0.095，有效平滑窗口 ~10 期
    # （Q 固定值会导致 R 小时增益过高，追踪噪声而非趋势）
    Q = 0.01 * obs_var  # 过程噪声（斜率漂移）
    R = obs_var  # 观测噪声
    s = 0.0  # 初始斜率估计
    P = 1.0  # 初始估计不确定度

    for y in returns:
        # Predict
        s_pred = s
        P_pred = P + Q
        # Update
        K = P_pred / (P_pred + R)
        s = s_pred + K * (y - s_pred)
        P = (1.0 - K) * P_pred

    # 归一化到 [-1, 1]
    std_r = float(np.std(returns))
    if std_r < 1e-10:
        return 0.0
    normalized = s / (10.0 * std_r)
    return float(np.clip(normalized, -1.0, 1.0))


# ---------------------------------------------------------------------------
# #10 趋势衰竭：Hurst 衰退检测
# ---------------------------------------------------------------------------


def detect_hurst_decay(h_early: float, h_late: float) -> bool:
    """检测 Hurst 指数衰退（趋势衰竭信号）。

    蓝图 §5.1.10：Hurst 从趋势态（>0.65）衰退到随机态（<0.50）= 趋势衰竭。

    判定逻辑（双重条件，比绝对阈值更稳健）：
    1. 早期处于趋势态：h_early > 0.6
    2. 显著衰退：h_early - h_late > 0.15

    Parameters
    ----------
    h_early : 早期 Hurst 值
    h_late  : 晚期 Hurst 值

    Returns
    -------
    True = 检测到趋势衰竭
    """
    return h_early > 0.6 and (h_early - h_late) > 0.15
