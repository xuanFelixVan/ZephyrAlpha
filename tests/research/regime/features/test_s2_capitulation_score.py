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
  8. 参数化候选族（2026-08-28 S2 校准调查报告 §四预注册，Owner 裁定聚合=C1 主+C3 对照）：
     base_mode(pct250/precrisis_z) × wick_mode(none/close_pos) ×
     vol_filter_mode(pct250/calm_window) × agg_mode(decayed_max/cluster_count)；
     legacy 默认值行为（1-7 节全部断言）不变

依据: 14_regime_s2_diagnosis v0.4.5 §4.1 / §4.5；2026-08-28-s2-calibration-investigation §四/§六
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


# ---------------------------------------------------------------------------
# 5. agg_mode="decayed_max"（C1 衰减峰值，Owner 裁定主口径）
# ---------------------------------------------------------------------------


class TestDecayedMaxAgg:
    """C1：score_t = max_{i∈窗口} daily_i×e^(-(t-i)/τ)，τ=halflife/0.693（非归一化）。"""

    def test_single_day_90_full_score_on_event_day(self):
        """单日 90 → 当日即 90（直接过 trigger 60，解开 wavg 数学锁死）。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        out = _run(d, agg_mode="decayed_max")
        assert out.iloc[60] == pytest.approx(90.0, rel=1e-9)
        assert out.iloc[60] >= 60, "C1 下单日满分簇当日应可过 trigger"

    def test_decay_curve_and_window_slideout(self):
        """逐日 e^(-k/τ) 衰减；滑出 lookback=20 窗口后归零（不粘滞）。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        out = _run(d, agg_mode="decayed_max")
        tau = 10 / 0.693
        assert out.iloc[61] == pytest.approx(90 * np.exp(-1 / tau), rel=1e-6)
        assert out.iloc[75] == pytest.approx(90 * np.exp(-15 / tau), rel=1e-6)
        # 严格单调递减
        assert out.iloc[75] < out.iloc[61] < out.iloc[60]
        # 事件滑出 20 日窗口（iloc 80 起窗口为 61..80）→ 0
        assert out.iloc[79] == pytest.approx(90 * np.exp(-19 / tau), rel=1e-6)
        assert out.iloc[80] == pytest.approx(0.0, abs=1e-9)
        assert (out.iloc[80:] == 0.0).all()

    def test_cluster_takes_max_not_sum(self):
        """3 日 90 分簇 → 当日仍 90（取衰减峰值而非求和，不奖励重复计数）。"""
        d = _flat_ohlcv()
        prev = 3000.0
        for i in (58, 59, 60):  # 3 日级联暴跌（每日 -5%），三过滤器各自共振
            o, c = prev * 0.99, prev * 0.94
            d["open"][i] = o
            d["close"][i] = c
            d["high"][i] = prev * 1.001
            d["low"][i] = c * 0.92
            d["volume"][i] = 3e8
            prev = c
        out = _run(d, agg_mode="decayed_max")
        assert out.iloc[60] == pytest.approx(90.0, rel=1e-6)
        tau = 10 / 0.693
        assert out.iloc[61] == pytest.approx(90 * np.exp(-1 / tau), rel=1e-6)

    def test_halflife_controls_decay_speed(self):
        """halflife 越大衰减越慢：事件后第 15 日 halflife=30 残留 > halflife=10。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        fast = _run(d, lookback=40, halflife=10, agg_mode="decayed_max")
        slow = _run(d, lookback=40, halflife=30, agg_mode="decayed_max")
        assert fast.iloc[75] == pytest.approx(90 * np.exp(-15 / (10 / 0.693)), rel=1e-6)
        assert slow.iloc[75] == pytest.approx(90 * np.exp(-15 / (30 / 0.693)), rel=1e-6)
        assert slow.iloc[75] > fast.iloc[75]

    def test_warmup_nan(self):
        """rolling(lookback) 满窗前为 NaN（与 wavg 一致）。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        out = _run(d, agg_mode="decayed_max")
        assert pd.isna(out.iloc[0])
        assert pd.isna(out.iloc[18])


# ---------------------------------------------------------------------------
# 6. agg_mode="cluster_count"（C3 簇计数映射，Owner 裁定对照口径）
# ---------------------------------------------------------------------------


class TestClusterCountAgg:
    """C3：近 20 日 daily≥70 天数 n → 0/1/2/≥3 映射 0/40/60/80。"""

    def test_mapping_table(self):
        """映射表：n=0→0 / 1→40 / 2→60 / ≥3→80。"""
        # n=0
        assert (_run(_flat_ohlcv(), agg_mode="cluster_count") == 0.0).all()
        # n=1 → 40
        d1 = _flat_ohlcv()
        _set_capitulation_day(d1, 60)
        out1 = _run(d1, agg_mode="cluster_count")
        assert out1.iloc[60] == 40.0
        # n=2 → 60（事件日 60/65 均在窗口内）
        d2 = _flat_ohlcv()
        _set_capitulation_day(d2, 60)
        _set_capitulation_day(d2, 65)
        out2 = _run(d2, agg_mode="cluster_count")
        assert out2.iloc[64] == 40.0
        assert out2.iloc[65] == 60.0
        # n=3 → 80
        d3 = _flat_ohlcv()
        for i in (58, 60, 65):
            _set_capitulation_day(d3, i)
        assert _run(d3, agg_mode="cluster_count").iloc[65] == 80.0
        # n=4 → 仍 80（≥3 封顶）
        d4 = _flat_ohlcv()
        for i in (58, 60, 65, 70):
            _set_capitulation_day(d4, i)
        assert _run(d4, agg_mode="cluster_count").iloc[70] == 80.0

    def test_daily_50_not_counted(self):
        """daily=50（z>1∧跌>1.5% 低档）不计入簇（计数门槛 daily≥70）。"""
        d = _flat_ohlcv()
        d["open"][60] = 3000.0
        d["high"][60] = 3005.0
        d["low"][60] = 2850.0
        d["close"][60] = 2940.0  # -2%
        d["volume"][60] = 3e8
        s = _series(d)
        vol_z = pd.Series(0.0, index=s["close"].index)
        vol_z.iloc[60] = 1.5  # z>1∧pct<-1.5% → daily=50（过滤器全过：实体60/下影58%/量3×）
        pct = s["close"].pct_change().fillna(0.0)
        out = s2_capitulation_score(
            vol_z,
            pct,
            s["volume"],
            s["high"],
            s["low"],
            s["open"],
            s["close"],
            agg_mode="cluster_count",
        )
        assert out.iloc[60] == 0.0

    def test_window_slideout(self):
        """簇滑出 20 日窗口后计数归零（min_periods=1，warmup 期按已观测计数=0）。"""
        d = _flat_ohlcv()
        _set_capitulation_day(d, 60)
        out = _run(d, agg_mode="cluster_count")
        assert out.iloc[79] == 40.0  # 窗口 60..79 仍含事件日
        assert out.iloc[80] == 0.0  # 窗口 61..80 已滑出
        assert (out.iloc[:60] == 0.0).all()  # warmup/常态无信号


# ---------------------------------------------------------------------------
# 7. wick_mode="none"(B1) / "close_pos"(B2)（A 股光脚大阴线形态适配）
# ---------------------------------------------------------------------------


class TestWickModes:
    """B1/B2：下影线"卖盘吸收"语义属 spring/flush 域；capitulation 本土形态=光脚大阴线。"""

    def _barefoot_crash(self) -> dict[str, np.ndarray]:
        """光脚大阴线：-8%，close≈low（close_pos≈0.02<0.15，下影占比≈2%<<50%）。"""
        d = _flat_ohlcv()
        d["open"][60] = 3000.0
        d["high"][60] = 3010.0
        d["low"][60] = 2755.0
        d["close"][60] = 2760.0  # -8%
        d["volume"][60] = 3e8
        return d

    def test_legacy_wick_blocks_barefoot_candle(self):
        """legacy wick>50% 与光脚大阴线根本冲突（实证 §2.4：暴跌日 wick 中位 4.8%）→ 0。"""
        out = _run(self._barefoot_crash())
        assert out.iloc[60] == 0.0

    def test_wick_none_passes_barefoot_candle(self):
        """B1 删 wick：光脚大阴线 → 当日有分。"""
        out = _run(self._barefoot_crash(), wick_mode="none", agg_mode="decayed_max")
        assert out.iloc[60] == pytest.approx(90.0, rel=1e-9)

    def test_close_pos_passes_barefoot_candle(self):
        """B2 close_pos<0.15：收盘贴底（0.02）→ 当日 90。"""
        out = _run(self._barefoot_crash(), wick_mode="close_pos", agg_mode="decayed_max")
        assert out.iloc[60] == pytest.approx(90.0, rel=1e-9)

    def test_close_pos_boundary_blocked(self):
        """close_pos≥0.15（收盘未贴底，close 2800 → 45/255≈0.18）→ 0。"""
        d = self._barefoot_crash()
        d["close"][60] = 2800.0  # close_pos=(2800-2755)/(3010-2755)=0.176
        out = _run(d, wick_mode="close_pos", agg_mode="decayed_max")
        assert out.iloc[60] == 0.0


# ---------------------------------------------------------------------------
# 8. base_mode="pct250"（A1 长期分位基准）+ vol_filter_mode="pct250"（B3）
# ---------------------------------------------------------------------------


class TestPct250Modes:
    """A1：vol_pct250=volume.rolling(250).rank(pct=True)；分档锚定跌幅主导。"""

    def _pct250_scene(self, n: int = 300) -> dict[str, np.ndarray]:
        """量能长期斜坡 0.5e8→1.2e8（300 日线性）；暴跌日量 3e8 → vol_pct250=1.0。"""
        return {
            "open": np.full(n, 3000.0),
            "high": np.full(n, 3005.0),
            "low": np.full(n, 2995.0),
            "close": np.full(n, 3000.0),
            "volume": np.linspace(0.5e8, 1.2e8, n),
        }

    def _set_pct250_crash(self, d: dict[str, np.ndarray], i: int, pct_drop: float, vol: float = 3e8) -> None:
        """第 i 日暴跌 pct_drop（光脚形态 close_pos<0.15，实体>>40%ATR）。"""
        close = 3000.0 * (1 + pct_drop)
        d["open"][i] = 3000.0
        d["high"][i] = 3005.0
        d["low"][i] = close - 5.0  # close_pos=5/(3005-close+5)<0.15
        d["close"][i] = close
        d["volume"][i] = vol

    def _run_pct250(self, d: dict[str, np.ndarray]) -> pd.Series:
        """A1+B2+B3 组合：pct250 基础分档 + close_pos 形态 + pct250 量能过滤。"""
        return _run(
            d,
            base_mode="pct250",
            wick_mode="close_pos",
            vol_filter_mode="pct250",
            agg_mode="decayed_max",
        )

    def test_pct250_tiers(self):
        """分档：跌≥3%∧分位>0.6→50 / 跌≥5%∧分位>0.5→70 / 跌≥7%→90（分位=1.0）。"""
        for pct_drop, expected in ((-0.035, 50.0), (-0.055, 70.0), (-0.075, 90.0)):
            d = self._pct250_scene()
            self._set_pct250_crash(d, 280, pct_drop)
            out = self._run_pct250(d)
            assert out.iloc[280] == pytest.approx(expected, rel=1e-9), (
                f"pct={pct_drop} 应得 {expected}，实际 {out.iloc[280]}"
            )

    def test_pct250_low_volume_percentile_blocks(self):
        """跌 3.5% 但 vol_pct250≈0.05（<0.6，量能佐证缺失）→ 0（同日量能过滤亦不满足）。"""
        d = self._pct250_scene()
        self._set_pct250_crash(d, 280, -0.035, vol=0.6e8)  # 斜坡上 0.6e8 为低分位
        assert self._run_pct250(d).iloc[280] == 0.0

    def test_pct250_shallow_drop_no_score(self):
        """跌 2.5%（未达 -3% 最低档）即使分位 1.0 → 0。"""
        d = self._pct250_scene()
        self._set_pct250_crash(d, 280, -0.025)
        assert self._run_pct250(d).iloc[280] == 0.0

    def test_pct250_90_tier_has_no_volume_condition(self):
        """90 档无量能条件：warmup 期（<250 日，分位 NaN）跌 8% 仍 → 90。"""
        d = _flat_ohlcv()  # n=85，rolling(250).rank 全程 NaN
        d["open"][60] = 3000.0
        d["high"][60] = 3005.0
        d["low"][60] = 2755.0
        d["close"][60] = 2760.0  # -8%
        d["volume"][60] = 3e8
        out = _run(
            d,
            base_mode="pct250",
            wick_mode="close_pos",
            vol_filter_mode="mult",  # 3e8>2×1e8 ✓（隔离基础分语义）
            agg_mode="decayed_max",
        )
        assert out.iloc[60] == pytest.approx(90.0, rel=1e-9)


# ---------------------------------------------------------------------------
# 9. base_mode="precrisis_z"（A2 危机前基准 z）+ vol_filter_mode="calm_window"（B3）
# ---------------------------------------------------------------------------


class TestPrecrisisZMode:
    """A2：z 改用平静窗 volume.shift(20).rolling(40) 均值/方差（危机簇内不失真）。"""

    def _precrisis_scene(self, n: int = 300) -> dict[str, np.ndarray]:
        """平静期(0-259)量 0.95/1.05e8 交替 → 危机簇(260-279)量 3e8 → 280 日光脚暴跌 -8%。

        平静窗（shift(20).rolling(40)）在 280 日覆盖 221-260 日（基本全平静期）
        → 内部 z≈7>3；而 legacy 20 日滚窗均量已被簇内高量抬至 ≈3e8（z 失真+mult 失效）。
        """
        vol = np.where(np.arange(n) % 2 == 0, 0.95e8, 1.05e8)
        vol[260:280] = 3e8
        d = {
            "open": np.full(n, 3000.0),
            "high": np.full(n, 3005.0),
            "low": np.full(n, 2995.0),
            "close": np.full(n, 3000.0),
            "volume": vol,
        }
        d["open"][280] = 3000.0
        d["high"][280] = 3010.0
        d["low"][280] = 2755.0
        d["close"][280] = 2760.0  # -8%
        d["volume"][280] = 3.3e8
        return d

    def test_precrisis_z_recovers_crisis_cluster_day(self):
        """簇内暴跌日：legacy zscore（外部 z=0.5 失真）→ 0；A2 内部重算 z>3 → 90。"""
        d = self._precrisis_scene()
        # legacy 对照：外部 vol_z=0.5（危机簇内 20 日滚窗失真后的典型低 z）→ 基础分 0
        legacy = _run(d, vol_z_val=0.5, wick_mode="close_pos", vol_filter_mode="calm_window", agg_mode="decayed_max")
        assert legacy.iloc[280] == 0.0
        # A2：忽略外部 vol_z，用平静窗重算 z（≈7>3）∧ pct=-8% → 90
        out = _run(
            d,
            vol_z_val=0.5,
            base_mode="precrisis_z",
            wick_mode="close_pos",
            vol_filter_mode="calm_window",
            agg_mode="decayed_max",
        )
        assert out.iloc[280] == pytest.approx(90.0, rel=1e-9)

    def test_calm_window_vol_filter_blocks_quiet_day(self):
        """calm_window 过滤器：平静期内量未超平静窗均量 1.5× → 不产生信号。"""
        d = self._precrisis_scene()
        # 平静期普通日（如第 100 日）：pct=0 → 基础分 0；且量 1e8 < 1.5×平静窗均量 → 过滤亦不满足
        out = _run(
            d, base_mode="precrisis_z", wick_mode="close_pos", vol_filter_mode="calm_window", agg_mode="decayed_max"
        )
        assert out.iloc[100] == 0.0
        # 暴跌日（280）之前全序列无信号（280 之后为 decayed_max 正常衰减尾巴，属预期）
        assert (out.iloc[:280].fillna(0.0) == 0.0).all()

    def test_legacy_mult_filter_fails_in_cluster(self):
        """对照：簇内 legacy vol_filter_mode="mult"（2×20 日均量≈6e8）卡死 3.3e8 暴跌日。"""
        d = self._precrisis_scene()
        out = _run(
            d, base_mode="precrisis_z", wick_mode="close_pos", vol_filter_mode="mult", agg_mode="decayed_max"
        )  # mult=legacy 2.0×
        assert out.iloc[280] == 0.0


# ---------------------------------------------------------------------------
# 10. 参数校验
# ---------------------------------------------------------------------------


class TestModeValidation:
    def test_invalid_agg_mode_raises(self):
        d = _flat_ohlcv()
        with pytest.raises(ValueError, match="agg_mode"):
            _run(d, agg_mode="bogus")

    def test_invalid_base_mode_raises(self):
        d = _flat_ohlcv()
        with pytest.raises(ValueError, match="base_mode"):
            _run(d, base_mode="bogus")

    def test_invalid_wick_mode_raises(self):
        d = _flat_ohlcv()
        with pytest.raises(ValueError, match="wick_mode"):
            _run(d, wick_mode="bogus")

    def test_invalid_vol_filter_mode_raises(self):
        d = _flat_ohlcv()
        with pytest.raises(ValueError, match="vol_filter_mode"):
            _run(d, vol_filter_mode="bogus")
