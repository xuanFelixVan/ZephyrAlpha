# [TTL] permanent
"""E10 数据健康修复 — 技术指标数值防护 + 写链 isfinite 闸测试（2026-10-01）。

背景：c1_market.technical_indicator 12 列含 ±Inf（普查真源
docs/_working/lane_c_chain_night_20261001/e10_data_health.md §1/§6）。
本文件逐列构造能触发旧逻辑产 Inf 的红输入，断言修复后输出全有限；
另测 internal_compute_provider 写链 isfinite 闸（±Inf → NaN → NULL）。

红输入设计（断层/除零对抗，均经现行代码实证可复现旧逻辑 Inf）：
- pvt/pvi/nvi：前收 0 → pct_change=±Inf → cumsum/cumprod 整链毒化
- vr：26 窗全涨 → 分母 0（缩窗 period=3 实证）
- roc：shift 前收 0 → C/0=Inf
- trix：EMA 链种子 0（close 前段 0）→ pct_change 除 0
- cvi：EMA 基期 0（前段 H=L 零区间）→ shift 比值除 0
- cti/correl：零方差窗浮点尘（常数 close c=0.1/0.3 实证 ±Inf）
- vip/vim：close 列 NaN（停牌）+ H=L 变价 → TR 的 max(skipna)=0 而 Σ|H−L_prev|>0
- boll_pctb：零带宽（一字板窗）——旧逻辑产 Inf 依赖浮点尘平台行为，
  本测锁定语义：带宽 ≤0/非有限 → NaN（防御性，census 2 行 Inf 为历史遗留）
- md_14：断层发散（已由同会话 E1 夜修重置播种落地）——回归锚

设计文档：docs/_working/lane_c_chain_night_20261001/e10_data_health.md §6
"""

from __future__ import annotations

import datetime

import numpy as np
import pandas as pd
import pytest

from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
from zephyr.factor.technical_indicators import (  # noqa: F401 — 注册副作用
    momentum,
    statistics,
    trend,
    volatility,
    volume,
)
from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)

_IDX = pd.date_range("2026-01-01", periods=40, freq="D")


def _df(close, volume=None, spread=0.1, index=None):
    """OHLCV 构造器（index 对齐，close/volume 可含 0/NaN）。"""
    n = len(close)
    idx = index if index is not None else _IDX[:n]
    close = pd.Series([float(c) for c in close], index=idx)
    vol_list = [1000.0] * n if volume is None else list(volume)
    vol = pd.Series([float(v) for v in vol_list], index=idx)
    return pd.DataFrame(
        {
            "open": close,
            "high": close + spread,
            "low": close - spread,
            "close": close,
            "volume": vol,
        },
        index=idx,
    )


def _assert_no_inf(df: pd.DataFrame) -> None:
    """断言输出无 ±Inf（NaN=Nullable 合法值，不判罚）。"""
    arr = df.to_numpy(dtype=float)
    assert not np.isinf(arr).any(), f"输出含 ±Inf {int(np.isinf(arr).sum())} 格"


# ===========================================================================
# 逐列数值防护（红→绿：红证据见本文件 docstring 与 e10_fix.md 环节簿）
# ===========================================================================


class TestE10ColumnGuards:
    def test_pvt_zero_prev_close_inf_filtered(self):
        """pvt：前收 0 → 步进 ±Inf 被 cumsum 前过滤，尾链不再毒化。"""
        d = _df([10, 11, 0, 12, 13, 14, 15])
        out = TechnicalIndicatorRegistry.get("pvt")().compute(d)
        _assert_no_inf(out)

    def test_pvi_zero_prev_close_inf_neutralized(self):
        """pvi：前收 0 且放量 bar → 非有限因子 → 中性元 1.0，cumprod 尾链有限。"""
        d = _df([10, 11, 12, 0, 13, 14, 15], volume=[1, 1, 1, 1, 2, 2, 2])
        out = TechnicalIndicatorRegistry.get("pvi")().compute(d)
        _assert_no_inf(out)

    def test_nvi_zero_prev_close_inf_neutralized(self):
        """nvi：与 pvi 同型（缩量 bar 分支），同雷同修。"""
        d = _df([10, 11, 12, 0, 13, 14, 15], volume=[2, 2, 2, 2, 1, 1, 1])
        out = TechnicalIndicatorRegistry.get("nvi")().compute(d)
        _assert_no_inf(out)

    def test_vr_all_rising_window_den_zero_nan(self):
        """vr：窗口全涨 → 分母 0 → NaN（无值语义），禁 inf。"""
        d = _df([10 + i for i in range(10)])
        out = TechnicalIndicatorRegistry.get("vr")().compute(d, period=3)
        _assert_no_inf(out)
        # 全涨窗的 vr 应为 NaN（无值），而非 inf
        assert out.iloc[:, 0].isna().iloc[2:].all()

    def test_roc_zero_prev_close_nan(self):
        """roc：shift 前收 0 → NaN（无值语义），禁 C/0=Inf。"""
        d = _df([0] * 12 + [5] * 6)
        out = TechnicalIndicatorRegistry.get("roc")().compute(d)
        _assert_no_inf(out)

    def test_trix_zero_ema_base_nan(self):
        """trix：EMA 链种子 0 → pct_change 分母 0 → NaN。"""
        d = _df([0] * 13 + [1] * 7)
        out = TechnicalIndicatorRegistry.get("trix")().compute(d)
        _assert_no_inf(out)

    def test_cvi_zero_ema_base_nan(self):
        """cvi：EMA 基期 0（前段一字零区间）→ shift 比值分母 0 → NaN。"""
        n = 20
        closes = [10.0] * 16 + [11.0 - i * 0.1 for i in range(4)]
        d = pd.DataFrame(
            {
                "open": closes,
                "high": [c + (0.0 if i < 16 else 0.5) for i, c in enumerate(closes)],
                "low": [c - (0.0 if i < 16 else 0.5) for i, c in enumerate(closes)],
                "close": closes,
                "volume": [1000.0] * n,
            },
            index=_IDX[:n],
        )
        out = TechnicalIndicatorRegistry.get("cvi")().compute(d)
        _assert_no_inf(out)

    def test_cti_zero_variance_window_no_inf(self):
        """cti：零方差窗（常数 close 浮点尘实证产 ±Inf）→ NaN。"""
        d = _df([0.1] * 20, spread=0.0)
        out = TechnicalIndicatorRegistry.get("cti")().compute(d)
        _assert_no_inf(out)

    def test_cti_normal_trend_unchanged(self):
        """cti：正常趋势数据不受伤（值域 [-1,1] 保持）。"""
        d = _df([10 + i * 0.5 for i in range(20)])
        out = TechnicalIndicatorRegistry.get("cti")().compute(d)
        valid = out["cti_12"].dropna()
        assert len(valid) > 0
        assert ((valid >= -1) & (valid <= 1)).all()

    def test_correl_zero_variance_window_no_inf(self):
        """correl：零方差窗（常数 close 浮点尘实证产 ±Inf）→ NaN。"""
        d = _df([0.3] * 40, volume=list(range(40)), spread=0.0)
        out = TechnicalIndicatorRegistry.get("correl")().compute(d)
        _assert_no_inf(out)

    def test_vortex_nan_close_tr_zero_no_inf(self):
        """vip/vim：close 列 NaN + H=L 变价 → TR skipna=0 而 Σvmp>0 → 旧逻辑 inf；修后 NaN。"""
        n = 20
        h = pd.Series([10.0 + i for i in range(n)], index=_IDX[:n])
        d = pd.DataFrame({"high": h, "low": h, "close": np.full(n, np.nan)}, index=_IDX[:n])
        out = TechnicalIndicatorRegistry.get("vortex")().compute(d)
        _assert_no_inf(out)

    def test_vortex_partial_nan_close_no_inf(self):
        """vip/vim：close 部分缺失（更贴近真实停牌态）同样不产 Inf。"""
        n = 20
        h = pd.Series([10.0 + i for i in range(n)], index=_IDX[:n])
        close = pd.Series([10.0, 11.0] + [np.nan] * (n - 2), index=_IDX[:n])
        d = pd.DataFrame({"high": h, "low": h, "close": close}, index=_IDX[:n])
        out = TechnicalIndicatorRegistry.get("vortex")().compute(d)
        _assert_no_inf(out)

    def test_boll_pctb_zero_bandwidth_nan_no_inf(self):
        """boll_pctb：零带宽窗（一字板）→ NaN；防御锁定禁尘 Inf（census 2 行历史遗留）。"""
        d = _df([12.34] * 30, spread=0.0)
        out = TechnicalIndicatorRegistry.get("percent_b")().compute(d)
        _assert_no_inf(out)
        # 零带宽窗的 %B 应为 NaN（无值语义），而非 0/0 平台依赖结果
        assert out["boll_pctb"].isna().iloc[19:].all()

    def test_boll_pctb_normal_data_unchanged(self):
        """boll_pctb：正常波动数据不受伤（有限值保持）。"""
        d = _df([100 + i + np.sin(i) for i in range(30)])
        out = TechnicalIndicatorRegistry.get("percent_b")().compute(d)
        assert out["boll_pctb"].dropna().shape[0] >= 10
        _assert_no_inf(out)

    def test_md_14_fault_regression_anchor(self):
        """md_14：断层 44→12.6（920729 原型）→ 有限（同会话 E1 重置播种修复的回归锚）。"""
        closes = [44.0] * 5 + [12.6] * 25
        d = _df(closes)
        out = TechnicalIndicatorRegistry.get("mcginley")().compute(d)
        _assert_no_inf(out)


# ===========================================================================
# 写链 isfinite 闸（internal_compute_provider）
# ===========================================================================


class TestWriteChainIsfiniteGate:
    def test_sanitize_inf_to_nan_with_count(self):
        """闸：±Inf → NaN，返回拦截格数。"""
        from zephyr.data.implementations.internal_compute_provider import sanitize_indicator_matrix

        df = pd.DataFrame(
            {
                "a": [1.0, np.inf, -np.inf, 2.0],
                "b": [np.nan, 5.0, 6.0, 7.0],
                "c": [0.0, 0.0, 0.0, 0.0],
            }
        )
        out, n = sanitize_indicator_matrix(df)
        assert n == 2
        assert np.isinf(out.to_numpy(dtype=float)).sum() == 0
        assert np.isnan(out["a"].to_numpy(dtype=float)).sum() == 2  # 原 NaN + 拦截 2 格
        assert out["b"].isna().iloc[0]  # 合法 NaN 保留
        assert out["c"].to_list() == [0.0, 0.0, 0.0, 0.0]

    def test_sanitize_clean_frame_zero_copy(self):
        """闸：干净帧零拦截 → 原对象返回（快路径）。"""
        from zephyr.data.implementations.internal_compute_provider import sanitize_indicator_matrix

        df = pd.DataFrame({"a": [1.0, 2.0], "b": [np.nan, 3.0]})
        out, n = sanitize_indicator_matrix(df)
        assert n == 0
        assert out is df

    def test_sanitize_empty_and_nonfloat(self):
        """闸：空帧/无浮点列 → 原样返回。"""
        from zephyr.data.implementations.internal_compute_provider import sanitize_indicator_matrix

        empty = pd.DataFrame()
        out, n = sanitize_indicator_matrix(empty)
        assert n == 0 and out is empty

        ints = pd.DataFrame({"a": [1, 2, 3]})
        out, n = sanitize_indicator_matrix(ints)
        assert n == 0 and out is ints

    def test_build_row_inf_and_nan_to_none(self):
        """_build_row 兜底：标量 ±Inf/NaN → None（非有限一律不入行）。"""
        row_data = {"ma_5": float("inf"), "obv": float("-inf"), "rsi_6": float("nan"), "pvt": 12.5}
        columns = ["symbol", "trade_date", "trade_time", "period", "ma_5", "obv", "rsi_6", "pvt"]
        row = InternalComputeProvider()._build_row(datetime.datetime(2026, 10, 1), "000001", "daily", row_data, columns)
        assert row[4] is None  # +Inf → None
        assert row[5] is None  # -Inf → None
        assert row[6] is None  # NaN → None
        assert row[7] == 12.5  # 有限值保留

    def test_compute_all_indicators_gate_integration(self):
        """集成：单标的指标矩阵含 Inf → _compute_all_indicators 出口全有限。"""
        registry = TechnicalIndicatorRegistry

        class _InfSpitter(TechnicalIndicatorBase):
            """测试替身：恒输出含 ±Inf 的列。"""

            meta = TechnicalIndicatorMeta(
                indicator_id="e10_inf_spitter",
                name="E10 测试替身",
                category="trend",
                output_columns=["e10_inf_col"],
                input_columns=["close"],
                params={},
            )

            def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
                vals = np.arange(len(data), dtype=float)
                vals[1] = np.inf
                vals[2] = -np.inf
                vals[3] = np.nan
                return pd.DataFrame({"e10_inf_col": vals}, index=data.index)

        registry.register(_InfSpitter)
        try:
            d = _df([10, 11, 12, 13, 14, 15])
            provider = InternalComputeProvider()
            merged = provider._compute_all_indicators(d, [_InfSpitter.meta])
            arr = merged["e10_inf_col"].to_numpy(dtype=float)
            assert np.isinf(arr).sum() == 0, "写链出口不得含 ±Inf"
            assert np.isnan(arr[3])  # 合法 NaN 保留
            assert arr[0] == 0.0 and arr[4] == 4.0  # 有限值保留
        finally:
            registry._registry.pop("e10_inf_spitter", None)

    def test_real_fault_series_full_pipeline_finite(self):
        """端到端：断层序列（44→12.6）全注册指标跑一遍，出口矩阵全有限。"""
        d = _df([44.0] * 5 + [12.6] * 25)
        d["amount"] = d["close"] * d["volume"]  # chips 族（cyc 等）需要 amount（真实 daily 链并入）
        provider = InternalComputeProvider()
        registry = TechnicalIndicatorRegistry
        registered = registry.list_all()
        merged = provider._compute_all_indicators(d, registered)
        assert not merged.empty
        arr = merged.to_numpy(dtype=float)
        assert np.isinf(arr).sum() == 0, "全指标出口矩阵不得含 ±Inf"


# ===========================================================================
# 周期覆盖冒烟（红输入 × 多周期形态不炸）
# ===========================================================================


@pytest.mark.parametrize(
    "indicator_id,kwargs",
    [
        ("pvt", {}),
        ("pvi", {}),
        ("nvi", {}),
        ("roc", {}),
        ("trix", {}),
        ("cti", {}),
        ("correl", {}),
        ("vortex", {}),
        ("cvi", {}),
        ("percent_b", {}),
        ("vr", {"period": 3}),
    ],
)
def test_guard_indicators_accept_short_fault_series(indicator_id, kwargs):
    """短序列/全零/全 NaN 边界：防护后不炸不产 Inf。"""
    for closes in ([0.0] * 8, [np.nan] * 8, [3.3] * 8):
        d = _df(closes, spread=0.0)
        out = TechnicalIndicatorRegistry.get(indicator_id)().compute(d, **kwargs)
        arr = out.to_numpy(dtype=float)
        assert np.isinf(arr).sum() == 0, f"{indicator_id} 在边界输入 {closes[:2]}... 产 Inf"
