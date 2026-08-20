# [A_test] module_id: MOD-TEST-S2-CAPITULATION | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 P1-E9a
# [MODULE] tests.regime.features.test_s2_capitulation_score
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_s2_capitulation_score.py
# [TTL] permanent
# [ARCH-REF] #P1-E9a #14_regime_s2_diagnosis §4.1
# [ALGO_FLOW]
# 层: 输入
# - I1: vol_z/pct_change（量价基础分输入）+ OHLCV 五序列（三过滤器）+ 可选 put_call/new_low
# 层: 算法
# - A1: _capitulation_daily 单日多维度共振（基础分 50/70/90 ∧ 量2.0×∧实体40%ATR∧下影>50%）
# - A2: 衰减加权和（e^(-i/τ) 归一化权重，rolling(lookback) 卷积，防状态粘滞）
# 层: 输出
# - O1: pd.Series 0-100（warmup 期 NaN，单日 90 仅贡献 ~8 分，簇集才达 trigger 60）
"""test_s2_capitulation_score.py — P1-E9a capitulation 衰减加权多过滤器单元测试。

覆盖（14_regime_s2_diagnosis §4.1 + §4.5 step 1 stub 要求）：
  1. 衰减加权不粘滞：单日 90 分后逐日衰减（非恒 90，rolling max 粘滞已消除）
  2. 数值边界：halflife=10/lookback=20 时单日 90 分贡献 ~8 分（<60），多日簇集才抬升
  3. 多维度过滤器共振：缺量能/缺实体/缺下影线 → 基础分归零
  4. 三过滤器全共振 → 当日 90 分进入衰减加权和
  5. 可选第 5/6 维（put/call + 新低占比）：enable_options_filter=True 时未达标归零
  6. 降级路径：缺 OHLCV → 回退瞬时两维版（治标 z>1，commit 93a25890 一致）
  7. NaN 容错 / warmup 期行为

依据: 14_regime_s2_diagnosis v0.4.5 §4.1 / §4.5
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.overlay_features import _atr, s2_capitulation_score

# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

_N = 85  # 序列长度（> 事件日 60 + lookback 20，验证信号滑出窗口后归零）


def _flat_ohlcv(n: int = _N) -> dict[str, np.ndarray]:
    """常态 OHLCV：close=3000 平盘，量 1e8（无任何 capitulation 信号）。"""
    return {
        "open": np.full(n, 3000.0),
        "high": np.full(n, 3005.0),
        "low": np.full(n, 2995.0),
        "close": np.full(n, 3000.0),
        "volume": np.full(n, 1e8),
    }


def _set_capitulation_day(d: dict[str, np.ndarray], i: int) -> None:
    """把第 i 日改成三过滤器全共振的 capitulation 日（-4.5% + 3×量 + 长下影）。

    close 2865（-4.5%）/ low 2700（下影 165，占 range 54%>50%）/ 量 3e8（>2×均量）/
    实体 135（>> 40% ATR）。
    """
    d["open"][i] = 3000.0
    d["high"][i] = 3005.0
    d["low"][i] = 2700.0
    d["close"][i] = 2865.0  # 前日 3000 → -4.5%
    d["volume"][i] = 3e8


def _series(d: dict[str, np.ndarray]) -> dict[str, pd.Series]:
    return {k: pd.Series(v, dtype=float) for k, v in d.items()}


def _run(d: dict[str, np.ndarray], vol_z_val: float = 3.5, **kw) -> pd.Series:
    s = _series(d)
    n = len(s["close"])
    vol_z = pd.Series(0.0, index=s["close"].index)
    pct = s["close"].pct_change().fillna(0.0)
    crash_mask = pct < -0.04
    vol_z[crash_mask] = vol_z_val  # 暴跌日给 z>3（90 分档）
    return s2_capitulation_score(vol_z, pct, s["volume"], s["high"], s["low"], s["open"], s["close"], **kw)


# ---------------------------------------------------------------------------
# 1. 衰减加权：不粘滞 + 数值边界
# ---------------------------------------------------------------------------


class TestDecayWeighting:
    """§4.5 stub ①③：衰减不粘滞 + 单日数值边界。"""

    def test_single_day_not_sticky_decays(self):
        """单日 90 分：事件日后逐日衰减（非恒 90），滑出 lookback 窗口后归零。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        out = _run(d)
        peak = out.iloc[60]
        assert peak > 0, "事件日应有正贡献"
        # 后续逐日严格递减（衰减曲线），事件滑出 20 日窗口（iloc 80+）后归零
        assert out.iloc[61] < peak
        assert out.iloc[70] < out.iloc[61]
        assert out.iloc[79] < out.iloc[70]
        assert out.iloc[80] == pytest.approx(0.0, abs=1e-9), "事件滑出窗口后应归零（不粘滞）"
        assert (out.iloc[80:] == 0.0).all()

    def test_single_day_numeric_boundary(self):
        """单日 90 分贡献 ≈ 90×w₀ ≈ 8 分（<< trigger 60，设计意图：需多日簇集）。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        out = _run(d)
        w0 = 1.0 / float(np.exp(-np.arange(20)[::-1] / (10 / 0.693)).sum())
        assert out.iloc[60] == pytest.approx(90 * w0, rel=1e-6)
        assert out.iloc[60] < 60, "单日 90 不足以触发 trigger≥60"

    def test_cluster_scores_higher_than_single(self):
        """3 日 capitulation 簇集 > 单日（过程语义：簇集抬升衰减和）。"""
        single = _flat_ohlcv()
        _set_capitulation_day(single, 60)
        out_single = _run(single).iloc[60]
        cluster = _flat_ohlcv()
        # 3 日级联暴跌（每日 -5%），各自满足三过滤器（长下影/实体/3×量）
        prev = 3000.0
        for i in (58, 59, 60):
            o, c = prev * 0.99, prev * 0.94
            cluster["open"][i] = o
            cluster["close"][i] = c
            cluster["high"][i] = prev * 1.001
            cluster["low"][i] = c * 0.92  # 下影占比 ~57%>50%
            cluster["volume"][i] = 3e8
            prev = c
        out_cluster = _run(cluster).iloc[60]
        assert out_cluster > out_single

    def test_halflife_stage_parameterization(self):
        """halflife 越大衰减越慢（trigger=10 / confirm=30 分阶段参数化）。

        同 lookback 下，事件后第 15 日：halflife=30 保留的信号 > halflife=10
        （归一化权重下峰更低但尾更厚，远日交叉后慢衰减占优）。
        """
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        fast = _run(d, lookback=40, halflife=10)
        slow = _run(d, lookback=40, halflife=30)
        assert slow.iloc[75] > fast.iloc[75] > 0


# ---------------------------------------------------------------------------
# 2. 多维度过滤器共振
# ---------------------------------------------------------------------------


class TestMultiFilterResonance:
    """§4.5 stub ②：缺任一过滤器 → 基础分归零。"""

    def test_full_resonance_gives_score(self):
        """三过滤器全共振（量 3×+实体+长下影）→ 正分。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        out = _run(d)
        assert out.iloc[60] > 0

    def test_missing_volume_surge_zeroed(self):
        """缺量能放大（量仅 1.5× 均量 <2.0×）→ 0。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        d["volume"][60] = 1.5e8
        out = _run(d)
        assert out.iloc[60] == 0.0

    def test_missing_body_zeroed(self):
        """缺实体力度（十字星：open≈close，实体<40%ATR）→ 0。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        d["open"][60] = 2864.0  # 实体 |2865-2864|=1，远小于 40%ATR
        d["high"][60] = 2870.0
        out = _run(d)
        assert out.iloc[60] == 0.0

    def test_missing_lower_wick_zeroed(self):
        """缺下影线（low≈close，下影占比<50%）→ 0。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        d["low"][60] = 2860.0  # 下影仅 5，占 range 3%
        out = _run(d)
        assert out.iloc[60] == 0.0

    def test_no_crash_no_score(self):
        """平盘日（量价基础条件不满足）→ 全 0。"""
        out = _run(_flat_ohlcv())
        assert (out.fillna(0.0) == 0.0).all()


# ---------------------------------------------------------------------------
# 3. 可选第 5/6 维（期权 put/call + 新低占比）
# ---------------------------------------------------------------------------


class TestOptionsFilter:
    """enable_options_filter=True 时第 5/6 维未达标归零（默认关）。"""

    def test_options_filter_blocks_when_put_call_low(self):
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        s = _series(d)
        vol_z = pd.Series(0.0, index=s["close"].index)
        vol_z.iloc[60] = 3.5
        pct = s["close"].pct_change().fillna(0.0)
        pc_low = pd.Series(1.0, index=s["close"].index)  # put/call 未达 1.4
        out = s2_capitulation_score(
            vol_z,
            pct,
            s["volume"],
            s["high"],
            s["low"],
            s["open"],
            s["close"],
            put_call_ratio=pc_low,
            enable_options_filter=True,
        )
        assert out.iloc[60] == 0.0

    def test_options_filter_passes_when_confirmed(self):
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        s = _series(d)
        vol_z = pd.Series(0.0, index=s["close"].index)
        vol_z.iloc[60] = 3.5
        pct = s["close"].pct_change().fillna(0.0)
        pc = pd.Series(1.5, index=s["close"].index)
        nl = pd.Series(0.95, index=s["close"].index)
        out = s2_capitulation_score(
            vol_z,
            pct,
            s["volume"],
            s["high"],
            s["low"],
            s["open"],
            s["close"],
            put_call_ratio=pc,
            new_low_ratio=nl,
            enable_options_filter=True,
        )
        assert out.iloc[60] > 0

    def test_options_filter_default_off(self):
        """默认关：put_call/new_low=None 不影响三过滤器结果。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        assert _run(d).iloc[60] > 0


# ---------------------------------------------------------------------------
# 4. 降级路径 + NaN 容错 + _atr
# ---------------------------------------------------------------------------


class TestFallbackAndRobustness:
    def test_legacy_two_param_fallback(self):
        """缺 OHLCV → 回退瞬时两维版：z>3 & 跌>4% → 当日 90（无衰减）。"""
        n = 10
        vol_z = pd.Series([0.0] * 9 + [3.5])
        pct = pd.Series([0.0] * 9 + [-0.045])
        out = s2_capitulation_score(vol_z, pct)
        assert out.iloc[-1] == 90
        assert out.iloc[0] == 0.0

    def test_legacy_thresholds_unchanged(self):
        """降级路径分档与 commit 93a25890 一致（50/70/90）。"""
        vol_z = pd.Series([1.5, 1.5, 3.5, 0.5])
        pct = pd.Series([-0.02, -0.035, -0.045, -0.05])
        out = s2_capitulation_score(vol_z, pct)
        assert out.tolist() == [50, 70, 90, 0]

    def test_nan_inputs_tolerated(self):
        """vol_z/pct_change 含 NaN → fillna(0) 不抛错。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        s = _series(d)
        vol_z = pd.Series(np.nan, index=s["close"].index)
        pct = s["close"].pct_change()  # 首值 NaN
        out = s2_capitulation_score(vol_z, pct, s["volume"], s["high"], s["low"], s["open"], s["close"])
        # vol_z 全 NaN → 基础分 0 → 输出非正（warmup NaN 或 0）
        assert (out.fillna(0.0) == 0.0).all()

    def test_atr_helper(self):
        """_atr：恒定 TR=10 序列 → ATR 收敛 10；Wilder 平滑单调。"""
        n = 30
        high = pd.Series(np.full(n, 105.0))
        low = pd.Series(np.full(n, 95.0))
        close = pd.Series(np.full(n, 100.0))
        atr = _atr(high, low, close, window=14)
        assert atr.iloc[-1] == pytest.approx(10.0, rel=1e-6)
        assert (atr.dropna() > 0).all()
