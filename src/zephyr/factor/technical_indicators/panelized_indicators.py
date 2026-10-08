# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.panelized_indicators
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.trend; zephyr.factor.technical_indicators.momentum; zephyr.data.implementations.internal_compute_provider(sanitize_indicator_matrix); pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（指标链行物化向量化路径，st-mx07-L5 切挂）; zephyr.factor.technical_indicators.parity_check; zephyr.factor.technical_indicators.bench_scaling
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三层结构 L1 compute（逐指标复用生产注册表类，递推族整列一次循环原样复用）/L2 window-vec（rolling.apply Python 回调→sliding_window_view 批量列运算：_wma/_linreg_endpoint 经 in-memory 换补丁 patch→compute→restore 零文件改动，CCI/AROON/AROONOSC/CONNORSRSI/RVGI 影子等价重实现公式照抄）/L3 materialize（整面 panel 一次 to_numpy→isfinite 掩码→object 置 None→元数据整列广播→C 级逐行 tuple，输出与生产 _build_row 逐列等值 NaN/±Inf→None 模式全等）; 换补丁域=compute_indicator_matrix 调用期且非线程安全（生产消费=盘后单线程批处理，禁多线程并发调用本模块）; 出口同一 sanitize_indicator_matrix（±Inf→NaN 与生产共享真源）; 对拍锚定 438/438 列 |Δ|≤1e-9（st-matrix-20261007 影子期 500bar×2 标的×219 列，max|Δ|=9.9e-14）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute_indicator_matrix 输入空 DataFrame→返回空 DataFrame 不抛；materialize_rows_vectorized 空 merged→返回 []；指标单族异常→跳过该族不炸整批（NotImplementedError continue）
# [TESTS] tests/zephyr/factor/technical_indicators/test_panelized_indicators.py
# [A_module] module_id=MOD-L02-TI-PANELIZED | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
panelized_indicators — 指标链"行物化"向量化实现（st-matrix-20261007 影子抢救，st-mx07-L5 转正）。

背景（I 道探针实锤）：internal_compute_provider 指标链瓶颈=行物化
（_build_row 逐格 Python 52.9% + iterrows 4.6%），CH 读取仅 4.2%。

三层结构：
  L1 compute：逐指标复用生产注册表类（其族函数本身已向量化：rolling/ewm 列运算；
     递推族 SAR/KAMA/SUPERTREND/MCGINLEY/FISHER/QQE/KVO/chips/cycle 保持"整列一次循环"——
     与生产同语义，本件原样复用不复制）。
  L2 window-vec：把生产里残余的"逐窗 Python 回调"（rolling.apply(np.dot/argmax/lambda)）
     换成 sliding_window_view 批量列运算，等价口径逐窗一致：
       - trend._wma（WMA/HMA 列）            → 滑窗矩阵乘
       - trend._linreg_endpoint（INERTIA 列） → 滑窗闭式最小二乘
       - CCI 的 AVEDEV                        → 滑窗平均绝对偏差
       - AROON/AROONOSC 的 argmax/argmin      → 滑窗 argmax（NaN 窗置 NaN 对齐 min_periods 门）
       - CONNORSRSI 的 PercentRank            → 滑窗比较计数（streak 递推保持整列一次循环）
       - RVGI 的 swma                         → 滑窗固定权重点积
     前两个经 in-memory 换补丁（patch→compute→restore，零文件改动）；后五个为
     等价重实现（公式照抄生产类，经对拍 1e-9 验证）。
  L3 materialize：核心收益。生产路径 iterrows()×_build_row() 逐格取值+逐格 isfinite 判空，
     本件换成整面 panel 一次性构建：
       merged 全量 to_numpy(float64) → isfinite 掩码 → astype(object) 非有限置 None
       → 五个元数据列（trade_date/trade_time/symbol/period/data_source）整列广播
       → 逐行 tuple 打包（C 级迭代，无逐格 Python）。
     输出与生产 _build_row 逐列等值（NaN/±Inf→None 模式全等）。

对拍与计时：parity_check.py（生产路径 vs 本件路径，|Δ|≤1e-9 + NaN 模式全等）；
影子期证据（2026-10-07）：438/438 列 PASS，max|Δ|=9.948e-14；物化段提速 25-42x。

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/panelized_indicators.yaml
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

__all__: Final = [
    "compute_indicator_matrix",
    "materialize_rows_vectorized",
    "build_rows_vectorized",
]

# 行元数据列（_build_row 特判的 5 列；其余列=指标值，NaN/±Inf→None）
_META_COLUMNS = frozenset({"trade_date", "trade_time", "symbol", "period", "data_source"})


# ---------------------------------------------------------------------------
# L2 window-vec：滑窗向量化基元（等价口径见各 docstring）
# ---------------------------------------------------------------------------


def _sliding(a: np.ndarray, n: int) -> np.ndarray:
    """一维数组 → 形状 (T-n+1, n) 的滑窗视图（零拷贝）。"""
    return np.lib.stride_tricks.sliding_window_view(a, n)


def _wma_vec(series: pd.Series, n: int) -> pd.Series:
    """等价 trend._wma：rolling(n).apply(np.dot(w)/sum, raw=True) → 滑窗矩阵乘。

    NaN 语义对齐：pandas min_periods=n 门（窗含 NaN 不产出）≡ 滑窗含 NaN → NaN
    （点积自然传播 NaN，双保险同值）。
    """
    a = series.to_numpy(dtype=float)
    w = np.arange(1, n + 1, dtype=float)
    out = np.full(a.shape, np.nan)
    if a.size >= n:
        out[n - 1 :] = _sliding(a, n) @ w / w.sum()
    return pd.Series(out, index=series.index)


def _linreg_endpoint_vec(series: pd.Series, length: int) -> pd.Series:
    """等价 trend._linreg_endpoint：滑窗闭式 OLS 端点拟合值（公式照抄生产）。"""
    a = series.to_numpy(dtype=float)
    x = np.arange(length, dtype=float)
    x_sum = x.sum()
    x2_sum = np.square(x).sum()
    divisor = length * x2_sum - x_sum**2
    out = np.full(a.shape, np.nan)
    if a.size >= length:
        sw = _sliding(a, length)
        bad = np.isnan(sw).any(axis=1)  # 对齐 pandas min_periods 门
        y_sum = sw.sum(axis=1)
        xy_sum = sw @ x
        slope = (length * xy_sum - x_sum * y_sum) / divisor
        intercept = (y_sum * x2_sum - x_sum * xy_sum) / divisor
        res = slope * (length - 1) + intercept
        res[bad] = np.nan
        out[length - 1 :] = res
    return pd.Series(out, index=series.index)


def _avedev_vec(tp: pd.Series, n: int) -> pd.Series:
    """等价 CCI 的 AVEDEV：rolling(n).apply(mean|x-mean|) → 滑窗平均绝对偏差。"""
    a = tp.to_numpy(dtype=float)
    out = np.full(a.shape, np.nan)
    if a.size >= n:
        sw = _sliding(a, n)
        bad = np.isnan(sw).any(axis=1)
        m = sw.mean(axis=1, keepdims=True)
        res = np.abs(sw - m).mean(axis=1)
        res[bad] = np.nan
        out[n - 1 :] = res
    return pd.Series(out, index=tp.index)


def _argpos_vec(s: pd.Series, n: int, kind: str) -> pd.Series:
    """等价 rolling(n+1).apply(np.argmax/np.argmin, raw=True)。

    对齐两点：① min_periods 门——窗含 NaN → NaN（np.argmax 遇 NaN 会返回首个 NaN 位，
    必须显式掩掉）；② 平局取窗内首个极值（np.argmax 语义一致）。
    """
    a = s.to_numpy(dtype=float)
    out = np.full(a.shape, np.nan)
    if a.size >= n:
        sw = _sliding(a, n)
        bad = np.isnan(sw).any(axis=1)
        pos = sw.argmax(axis=1) if kind == "max" else sw.argmin(axis=1)
        res = pos.astype(float)
        res[bad] = np.nan
        out[n - 1 :] = res
    return pd.Series(out, index=s.index)


def _pctrank_vec(ret: pd.Series, n: int) -> pd.Series:
    """等价 CONNORSRSI 的 PercentRank：rolling(n).apply((x<x[-1]).sum()/(n-1)*100)。"""
    a = ret.to_numpy(dtype=float)
    out = np.full(a.shape, np.nan)
    if a.size >= n:
        sw = _sliding(a, n)
        bad = np.isnan(sw).any(axis=1)
        res = (sw < sw[:, -1:]).sum(axis=1) / (n - 1) * 100
        res[bad] = np.nan
        out[n - 1 :] = res
    return pd.Series(out, index=ret.index)


def _swma_vec(series: pd.Series) -> pd.Series:
    """等价 RVGI 的 swma：rolling(4).apply(np.dot(w=[1,2,2,1]/6)) → 滑窗固定权重点积。

    生产窗含 NaN 时 min_periods 门产出 NaN；滑窗点积遇 NaN 自然传播 NaN，同值。
    """
    a = series.to_numpy(dtype=float)
    w = np.array([1.0, 2.0, 2.0, 1.0]) / 6.0
    out = np.full(a.shape, np.nan)
    if a.size >= 4:
        out[3:] = _sliding(a, 4) @ w
    return pd.Series(out, index=series.index)


# ---------------------------------------------------------------------------
# L2 等价重实现（生产类中含逐窗 Python 回调的 5 个指标；公式照抄，窗运算向量化）
# ---------------------------------------------------------------------------


def _cci_vec(data: pd.DataFrame) -> pd.DataFrame:
    """CCI（trend.CCI 等价）：AVEDEV 段向量化，其余公式不变。"""
    n = 14
    tp = (data["high"] + data["low"] + data["close"]) / 3
    ma_tp = tp.rolling(window=n).mean()
    avedev = _avedev_vec(tp, n)
    cci = (tp - ma_tp) / (0.015 * avedev)
    return pd.DataFrame({"cci_14": cci}, index=data.index)


def _aroon_vec(data: pd.DataFrame) -> pd.DataFrame:
    """AROON（momentum.AROON 等价）：argmax/argmin 段向量化。"""
    n = 14
    pos_hh = _argpos_vec(data["high"], n + 1, "max")
    pos_ll = _argpos_vec(data["low"], n + 1, "min")
    return pd.DataFrame({"aroon_up": 100 * pos_hh / n, "aroon_down": 100 * pos_ll / n}, index=data.index)


def _aroonosc_vec(data: pd.DataFrame) -> pd.DataFrame:
    """AROONOSC（momentum.AROONOSC 等价）：同上。"""
    n = 14
    pos_hh = _argpos_vec(data["high"], n + 1, "max")
    pos_ll = _argpos_vec(data["low"], n + 1, "min")
    return pd.DataFrame({"aroonosc": 100 * (pos_hh - pos_ll) / n}, index=data.index)


def _connorsrsi_vec(data: pd.DataFrame) -> pd.DataFrame:
    """CONNORSRSI（momentum.CONNORSRSI 等价）：PercentRank 段向量化。

    streak 连涨跌天数=递推状态机，保持整列一次循环（与生产同语义同循环体）。
    """
    from zephyr.factor.technical_indicators.momentum import _rsi

    rsi_n, streak_n, rank_n = 3, 2, 100
    close = data["close"]
    rsi_1 = _rsi(close, rsi_n)
    delta = close.diff()
    sign = np.sign(delta).to_numpy(dtype=float)
    streak = np.zeros(len(close))
    for i in range(1, len(close)):
        if np.isnan(sign[i]) or sign[i] == 0:
            streak[i] = 0
        elif sign[i] == sign[i - 1] and streak[i - 1] != 0:
            streak[i] = streak[i - 1] + sign[i]
        else:
            streak[i] = sign[i]
    streak_s = pd.Series(streak, index=data.index)
    rsi_streak = _rsi(streak_s, streak_n)
    ret = close.pct_change()
    pct_rank = _pctrank_vec(ret, rank_n)
    crsi = (rsi_1 + rsi_streak + pct_rank) / 3
    return pd.DataFrame({"crsi": crsi}, index=data.index)


def _rvgi_vec(data: pd.DataFrame) -> pd.DataFrame:
    """RVGI（momentum.RVGI 等价）：swma 段向量化。"""
    n, sig_n = 10, 4
    num = _swma_vec(data["close"] - data["open"]).rolling(window=n).mean()
    den = _swma_vec(data["high"] - data["low"]).rolling(window=n).mean()
    rvgi = num / den
    return pd.DataFrame(
        {"rvgi_10": rvgi, "rvgi_sig": rvgi.rolling(window=sig_n).mean()},
        index=data.index,
    )


# indicator_id → 向量化 compute（覆盖生产类的仅这 5 个；其余全走生产类原样复用）
_SHADOW_COMPUTE: Final = {
    "cci": _cci_vec,
    "aroon": _aroon_vec,
    "aroonosc": _aroonosc_vec,
    "connorsrsi": _connorsrsi_vec,
    "rvgi": _rvgi_vec,
}


class _PatchedHelpers:
    """trend 模块级帮助函数 in-memory 换补丁（patch→yield→restore，零文件改动）。

    覆盖 trend._wma（WMA/HMA 两列）与 trend._linreg_endpoint（INERTIA 列）——
    生产类 compute 运行时经模块全局名解析调用，换补丁即生效。
    非线程安全：patch 域=with 块；生产消费=盘后单线程批处理（见 INVARIANTS）。
    """

    def __enter__(self):
        from zephyr.factor.technical_indicators import trend

        self._trend = trend
        self._saved = (trend._wma, trend._linreg_endpoint)
        trend._wma = _wma_vec
        trend._linreg_endpoint = _linreg_endpoint_vec
        return self

    def __exit__(self, exc_type, exc, tb):
        self._trend._wma, self._trend._linreg_endpoint = self._saved
        return False


# ---------------------------------------------------------------------------
# L1 compute：镜像生产 _compute_all_indicators（递推族保持整列一次循环）
# ---------------------------------------------------------------------------


def ensure_registry():
    """自动发现并返回注册表元数据列表（镜像生产 _fetch_single_period 的初始化序）。"""
    from zephyr.factor.technical_indicators import (
        TechnicalIndicatorRegistry,
        autodiscover_technical_indicators,
    )

    autodiscover_technical_indicators()
    return TechnicalIndicatorRegistry.list_all()


def compute_indicator_matrix(symbol_data: pd.DataFrame, registered=None) -> pd.DataFrame:
    """向量化版 _compute_all_indicators：输出与生产逐列等值的合并指标矩阵。

    差异仅两处：① _SHADOW_COMPUTE 覆盖的 5 个窗回调指标走向量化实现；
    ② trend._wma/_linreg_endpoint 经 in-memory 补丁向量化（patch 域=本函数调用期）。
    递推族（SAR/KAMA/SUPERTREND/MCGINLEY/FISHER/QQE/KVO/chips/cycle 等）原样复用
    生产 compute——它们本身已是"整列一次循环"，无逐格浪费。
    出口同一 sanitize_indicator_matrix（±Inf→NaN，与生产共享真源）。
    """
    from zephyr.data.implementations.internal_compute_provider import sanitize_indicator_matrix
    from zephyr.factor.technical_indicators import TechnicalIndicatorRegistry

    if registered is None:
        registered = ensure_registry()

    results = []
    with _PatchedHelpers():
        for meta in registered:
            try:
                shadow_fn = _SHADOW_COMPUTE.get(meta.indicator_id)
                if shadow_fn is not None:
                    result_df = shadow_fn(symbol_data)
                else:
                    result_df = TechnicalIndicatorRegistry.get(meta.indicator_id)().compute(symbol_data)
                if result_df is not None and not result_df.empty:
                    results.append(result_df)
            except NotImplementedError:
                continue

    if not results:
        return pd.DataFrame(index=symbol_data.index)
    merged = pd.concat(results, axis=1)
    merged, _ = sanitize_indicator_matrix(merged)
    return merged


# ---------------------------------------------------------------------------
# L3 materialize：行物化向量化（核心收益，替换 iterrows+_build_row 逐格 Python）
# ---------------------------------------------------------------------------


def materialize_rows_vectorized(
    merged: pd.DataFrame,
    symbol: str,
    period: str,
    columns: list[str],
) -> list[tuple]:
    """行物化向量化：输出与生产 iterrows+_build_row 逐格等值的 tuple 行清单。

    生产：每 bar 构造 Series（iterrows）→ 每列 row_data.get(col)+isfinite 逐格判空。
    本件：整面 merged 一次性 to_numpy(float64) → isfinite 掩码 → object 面板
    非有限置 None → 元数据列整列广播 → C 级逐行 tuple 打包。零逐格 Python。

    等值口径（对齐 _build_row）：
      - trade_date = bar_ts 的 date；trade_time = bar_ts 的 datetime
      - symbol/period/data_source = 常量
      - 指标列：有限值原样（np.float64），NaN/±Inf→None；缺失列→None
    """
    n = len(merged)
    if n == 0:
        return []
    idx = merged.index
    if not isinstance(idx, pd.DatetimeIndex):
        idx = pd.DatetimeIndex(idx)

    # 全量指标面板 → object 面板（非有限→None），单次向量化完成全部逐格判空
    vals = merged.to_numpy(dtype=np.float64)
    panel = vals.astype(object)
    panel[~np.isfinite(vals)] = None

    # 源列名→面板列号（首现胜出；生产重复列场景 Series.get 语义退化，真实数据不触发）
    src_pos: dict[str, int] = {}
    for i, c in enumerate(merged.columns):
        if c not in src_pos:
            src_pos[c] = i

    out = np.empty((n, len(columns)), dtype=object)
    col_arrays: dict[str, np.ndarray] = {
        "trade_date": idx.date,  # C 级 datetime64→date，逐值等价 pd.Timestamp(ts).to_pydatetime().date()
        "trade_time": idx.to_pydatetime(),  # 等价 to_pydatetime()
        "symbol": np.full(n, symbol, dtype=object),
        "period": np.full(n, period, dtype=object),
        "data_source": np.full(n, "internal", dtype=object),
    }
    none_col = np.full(n, None, dtype=object)
    for j, col in enumerate(columns):
        if col in col_arrays:
            out[:, j] = col_arrays[col]
        elif col in src_pos:
            out[:, j] = panel[:, src_pos[col]]
        else:
            out[:, j] = none_col
    return list(map(tuple, out))


def build_rows_vectorized(
    symbol_data: pd.DataFrame,
    symbol: str,
    period: str,
    columns: list[str],
    registered=None,
) -> tuple[pd.DataFrame, list[tuple]]:
    """组合入口：compute（L1+L2）+ materialize（L3），向量化全路径。"""
    merged = compute_indicator_matrix(symbol_data, registered)
    rows = materialize_rows_vectorized(merged, symbol, period, columns)
    return merged, rows
