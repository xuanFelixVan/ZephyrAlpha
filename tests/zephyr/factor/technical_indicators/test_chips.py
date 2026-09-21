# [BLUEPRINT] MOD-L02-031 | (batch10 chips indicators) | §
# [TTL] permanent
"""筹码族技术指标测试（3 个，批10 施工 2026-09-21）。

测试内容：
- 3 个筹码指标（cyq/scr/cyc）注册到 Registry，category=="chips"
- meta 契约：output_columns/params 与 catalog §6.10 一致
- CYQ 数值正确性（手工可验场景）+ 边界（停牌/新股/一字涨跌停/换手极端值）
- CYQ PIT 无前视不变量：前缀序列输出 == 全序列前缀
- SCR 与 CYQ 分位同源自洽
- CYC 成本均线滚动口径 + cyc_inf DMA 递推 + 换手率缺失降级
- 换手率软输入契约：缺列→CYQ/SCR 空输出（不抛），CYC cyc_inf=NaN

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §6.10
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import chips  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.chips import CYC, CYQ, SCR
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# 期望契约（catalog §6.10）：indicator_id → (name_zh, output_columns)
EXPECTED = {
    "cyq": ("筹码分布", ["chips_winner", "chips_avg_cost", "chips_cost_5", "chips_cost_95"]),
    "scr": ("筹码集中度", ["scr"]),
    "cyc": ("成本均线", ["cyc_5", "cyc_13", "cyc_34", "cyc_inf"]),
}


def _two_day_df() -> pd.DataFrame:
    """手工可验两日场景：
    day1 [10,12] close 11 vol100 tr0%   → 初始分布 100 股均匀铺 [10,12]
    day2 [11,13] close 12 vol100 tr10%  → 旧分布×0.9 + 新增 100 均匀铺 [11,13]
    手算（连续均匀近似）：
      day2 总质量=190；winner=45+50 +50×0 /... = (90×1 + 100×0.5)/190 = 140/190 ≈ 0.7368
      avg=(90×11+100×12)/190 = 2190/190 ≈ 11.5263
      q05 = 10 + (0.05×190)/45 ≈ 10.2111；q95 = 12 + (0.95×190−140)/50 = 12.81
    """
    return pd.DataFrame(
        {
            "high": [12.0, 13.0],
            "low": [10.0, 11.0],
            "close": [11.0, 12.0],
            "volume": [100.0, 100.0],
            "amount": [1100.0, 1200.0],
            "turnover_rate": [0.0, 10.0],
        }
    )


_RNG = np.random.default_rng(20260921)


def _make_chips_ohlcv(n: int = 60) -> pd.DataFrame:
    """生成带趋势的 OHLCV+换手率测试数据（价格恒正）。"""
    close = 100 + _RNG.standard_normal(n).cumsum() * 0.3
    high = close + _RNG.uniform(0.1, 0.8, n)
    low = close - _RNG.uniform(0.1, 0.8, n)
    volume = _RNG.uniform(800, 1200, n)
    amount = close * volume
    turnover = _RNG.uniform(0.3, 5.0, n)
    return pd.DataFrame(
        {
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "amount": amount,
            "turnover_rate": turnover,
        }
    )


# ============== 注册与 meta 契约 ==============


class TestChipsRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("chips")}
        for iid in EXPECTED:
            assert iid in metas, f"筹码指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("chips")) == len(EXPECTED) == 3

    @pytest.mark.parametrize("iid", list(EXPECTED))
    def test_meta_contract(self, iid):
        name, cols = EXPECTED[iid]
        meta = TechnicalIndicatorRegistry.get(iid).meta
        assert meta.name == name
        assert meta.category == "chips"
        assert meta.output_columns == cols
        assert meta.version == "1.0.0"

    def test_inputs_declare_turnover(self):
        """批10 契约扩张：筹码族输入首次引入换手率（meta 声明钉死）。"""
        for iid in ["cyq", "scr", "cyc"]:
            assert "turnover_rate" in TechnicalIndicatorRegistry.get(iid).meta.input_columns


# ============== CYQ 数值正确性 ==============


class TestCYQNumeric:
    def test_single_day_uniform(self):
        """新股单日：均匀铺 [10,12]，close=11 → winner=0.5、avg=11。"""
        df = pd.DataFrame(
            {
                "high": [12.0],
                "low": [10.0],
                "close": [11.0],
                "volume": [100.0],
                "turnover_rate": [1.0],
            }
        )
        r = CYQ().compute(df)
        assert abs(r["chips_winner"].iloc[0] - 0.5) < 0.01
        assert abs(r["chips_avg_cost"].iloc[0] - 11.0) < 1e-6
        assert abs(r["chips_cost_5"].iloc[0] - 10.1) < 0.05
        assert abs(r["chips_cost_95"].iloc[0] - 11.9) < 0.05

    def test_two_day_hand_math(self):
        r = CYQ().compute(_two_day_df())
        assert abs(r["chips_winner"].iloc[1] - 140.0 / 190.0) < 0.01
        assert abs(r["chips_avg_cost"].iloc[1] - 2190.0 / 190.0) < 0.01
        assert abs(r["chips_cost_5"].iloc[1] - 10.2111) < 0.05
        assert abs(r["chips_cost_95"].iloc[1] - 12.81) < 0.05

    def test_full_turnover_resets_distribution(self):
        """换手率 100%（极端值）：旧筹码全换手，分布=当日新增。"""
        df = pd.DataFrame(
            {
                "high": [12.0, 13.0],
                "low": [10.0, 11.0],
                "close": [11.0, 12.0],
                "volume": [100.0, 100.0],
                "turnover_rate": [0.0, 100.0],
            }
        )
        r = CYQ().compute(df)
        # 分布仅剩 day2 的 [11,13] 均匀 → winner≈(12-11)/2=0.5、avg≈12
        assert abs(r["chips_winner"].iloc[1] - 0.5) < 0.02
        assert abs(r["chips_avg_cost"].iloc[1] - 12.0) < 0.02

    def test_turnover_above_100_clipped(self):
        """换手率 >100% 截断为 100%（与 tr=100 等价）。"""
        base = pd.DataFrame(
            {
                "high": [12.0, 13.0],
                "low": [10.0, 11.0],
                "close": [11.0, 12.0],
                "volume": [100.0, 100.0],
                "turnover_rate": [0.0, 100.0],
            }
        )
        extreme = base.copy()
        extreme["turnover_rate"] = [0.0, 250.0]
        r1 = CYQ().compute(base)
        r2 = CYQ().compute(extreme)
        pd.testing.assert_series_equal(r1["chips_winner"], r2["chips_winner"])

    def test_limit_up_one_price_board(self):
        """一字涨停：high==low 全部筹码落同一价位；close==价位 → winner=1。"""
        df = pd.DataFrame(
            {
                "high": [10.0, 11.0, 12.0, 12.0],
                "low": [10.0, 11.0, 12.0, 12.0],
                "close": [10.0, 11.0, 12.0, 12.0],
                "volume": [100.0, 50.0, 30.0, 20.0],
                "turnover_rate": [1.0, 0.5, 0.3, 0.2],
            }
        )
        r = CYQ().compute(df)
        assert r["chips_winner"].iloc[2] == pytest.approx(1.0)
        # 低换手下一字板上移：旧筹码（10/11）仍留存拉低均价——手算 ≈10.75（非 12）
        assert r["chips_avg_cost"].iloc[3] == pytest.approx(10.753, abs=0.01)
        assert r["chips_avg_cost"].iloc[3] < 12.0
        # 末日暴跌 close=9 → 获利盘=0（所有成本高于现价）
        df_crash = df.copy()
        df_crash.loc[3, "close"] = 9.0
        r2 = CYQ().compute(df_crash)
        assert r2["chips_winner"].iloc[3] == pytest.approx(0.0, abs=1e-9)

    def test_suspension_volume_zero(self):
        """停牌日（volume=0 且 tr=0）：分布冻结，指标与前一日一致（close 不变时）。"""
        n = 10
        rng = np.random.default_rng(5)
        df = pd.DataFrame(
            {
                "high": 20 + np.abs(rng.standard_normal(n)),
                "low": 20 - np.abs(rng.standard_normal(n)),
                "close": 20.0,
                "volume": rng.uniform(90, 110, n),
                "turnover_rate": rng.uniform(0.5, 2.0, n),
            }
        )
        df.loc[8] = [df.loc[7, "high"], df.loc[7, "low"], 20.0, 0.0, 0.0]  # 停牌日
        r = CYQ().compute(df)
        for col in ["chips_winner", "chips_avg_cost", "chips_cost_5", "chips_cost_95"]:
            assert r[col].iloc[8] == pytest.approx(r[col].iloc[7], rel=1e-9), col

    def test_nan_turnover_no_decay(self):
        """换手率 NaN（缺数日）：该日不衰减，与 tr=0 完全一致。"""
        n = 12
        rng = np.random.default_rng(6)
        base = pd.DataFrame(
            {
                "high": 30 + np.abs(rng.standard_normal(n)),
                "low": 30 - np.abs(rng.standard_normal(n)),
                "close": 30 + rng.standard_normal(n).cumsum() * 0.1,
                "volume": rng.uniform(90, 110, n),
                "turnover_rate": rng.uniform(0.5, 2.0, n),
            }
        )
        zero = base.copy()
        zero.loc[5, "turnover_rate"] = 0.0
        nan = base.copy()
        nan.loc[5, "turnover_rate"] = np.nan
        r0 = CYQ().compute(zero)
        rn = CYQ().compute(nan)
        pd.testing.assert_series_equal(r0["chips_avg_cost"], rn["chips_avg_cost"])

    def test_price_expansion_beyond_initial_grid(self):
        """新股后价格创极端新高：网格扩张重铺，指标仍有限且 winner∈[0,1]。"""
        df = pd.DataFrame(
            {
                "high": [10.0, 10.5, 50.0],
                "low": [9.0, 9.8, 48.0],
                "close": [9.5, 10.2, 49.0],
                "volume": [100.0, 100.0, 100.0],
                "turnover_rate": [1.0, 1.0, 2.0],
            }
        )
        r = CYQ().compute(df)
        # 手算：旧筹码(~194)全部获利 + 新增 [48,50] 中 <=49 的一半(50)，winner≈0.83
        assert 0.78 < r["chips_winner"].iloc[2] < 0.88
        assert r["chips_cost_95"].iloc[2] <= 50.0
        assert r["chips_avg_cost"].iloc[2] > 9.0

    def test_pit_prefix_invariance(self):
        """PIT 无前视：任一前缀序列的输出 == 全序列输出的对应前缀（网格重建只用过去）。"""
        n = 80
        df = _make_chips_ohlcv(n).reset_index(drop=True)
        full = CYQ().compute(df)
        cut = 55
        part = CYQ().compute(df.iloc[:cut].reset_index(drop=True))
        for col in ["chips_winner", "chips_avg_cost", "chips_cost_5", "chips_cost_95"]:
            np.testing.assert_allclose(part[col].to_numpy(), full[col].to_numpy()[:cut], rtol=1e-12, atol=1e-12)

    def test_warmup_all_zero_volume_nan(self):
        """全历史成交量为 0（极端停牌序列）→ NaN 不前填不抛。"""
        df = pd.DataFrame(
            {
                "high": [10.0, 10.2],
                "low": [9.0, 9.5],
                "close": [9.5, 10.0],
                "volume": [0.0, 0.0],
                "turnover_rate": [0.0, 0.0],
            }
        )
        r = CYQ().compute(df)
        assert r["chips_winner"].isna().all()


# ============== SCR ==============


class TestSCR:
    def test_consistent_with_cost_quantiles(self):
        """SCR 与 CYQ 成本分位同源自洽：scr==100×(q95−q05)/(q95+q05)。"""
        df = _make_chips_ohlcv(60)
        m = CYQ().compute(df)
        s = SCR().compute(df)
        q05 = m["chips_cost_5"].to_numpy()
        q95 = m["chips_cost_95"].to_numpy()
        expect = 100.0 * (q95 - q05) / (q95 + q05)
        np.testing.assert_allclose(s["scr"].to_numpy(), expect, rtol=1e-12, atol=1e-12)

    def test_range(self):
        df = _make_chips_ohlcv(60)
        s = SCR().compute(df)
        valid = s["scr"].dropna()
        assert ((valid >= 0) & (valid <= 100)).all()

    def test_missing_turnover_empty(self):
        df = _make_chips_ohlcv(30).drop(columns=["turnover_rate"])
        s = SCR().compute(df)
        assert len(s) == 0 and list(s.columns) == ["scr"]


# ============== CYC ==============


class TestCYC:
    def test_rolling_cost_moving_average(self):
        """cyc_N == Σ(amount,N)/(Σ(volume,N)×100)（存量 volume=手，通达信原式÷100）。"""
        df = _make_chips_ohlcv(60)
        r = CYC().compute(df)
        for n in [5, 13, 34]:
            manual = df["amount"].rolling(n).sum() / (df["volume"].rolling(n).sum() * 100.0)
            np.testing.assert_allclose(r[f"cyc_{n}"].to_numpy(), manual.to_numpy(), rtol=1e-12)
            assert r[f"cyc_{n}"].iloc[: n - 1].isna().all()  # 预热期 NaN

    def test_cyc_cost_near_price_scale(self):
        """量纲回归：cyc_5 应贴近价位量级（amount/(volume×100)），防手/股口径回归。"""
        df = _make_chips_ohlcv(60)
        r = CYC().compute(df)
        avg_price = df["amount"].iloc[10:].sum() / (df["volume"].iloc[10:].sum() * 100.0)
        assert abs(r["cyc_5"].iloc[-1] / avg_price - 1.0) < 0.5

    def test_cyc_inf_dma_recursion(self):
        """cyc_inf == DMA(close, tr/100) 逐日递推，种子=首日收盘。"""
        df = _make_chips_ohlcv(40)
        r = CYC().compute(df)
        c = df["close"].to_numpy()
        tr = df["turnover_rate"].to_numpy()
        manual = np.empty(40)
        manual[0] = c[0]
        for i in range(1, 40):
            manual[i] = manual[i - 1] + (c[i] - manual[i - 1]) * min(max(tr[i], 0.0), 100.0) / 100.0
        np.testing.assert_allclose(r["cyc_inf"].to_numpy(), manual, rtol=1e-12)

    def test_cyc_inf_rising_close_lags(self):
        """单向上涨中 cyc_inf 应滞后于 close（成本均线语义）。"""
        n = 30
        df = pd.DataFrame(
            {
                "high": np.arange(n) + 1.0 + 0.5,
                "low": np.arange(n) + 1.0 - 0.5,
                "close": np.arange(n) + 1.0,
                "volume": np.full(n, 1000.0),
                "amount": (np.arange(n) + 1.0) * 1000.0,
                "turnover_rate": np.full(n, 2.0),
            }
        )
        r = CYC().compute(df)
        lagging = r["cyc_inf"].to_numpy()[1:] < df["close"].to_numpy()[1:]  # 首日=种子==close 除外
        assert lagging.all()

    def test_missing_turnover_cyc_inf_nan_others_ok(self):
        df = _make_chips_ohlcv(40).drop(columns=["turnover_rate"])
        r = CYC().compute(df)
        assert r["cyc_inf"].isna().all()
        assert r["cyc_5"].notna().sum() > 0  # cyc_N 不依赖换手率，照常计算

    def test_missing_amount_raises(self):
        df = _make_chips_ohlcv(40).drop(columns=["amount"])
        with pytest.raises(ValueError):
            CYC().compute(df)


# ============== 软降级与空输入契约 ==============


class TestDegradation:
    @pytest.mark.parametrize("iid", ["cyq", "scr", "cyc"])
    def test_empty_input_empty_output(self, iid):
        cls = TechnicalIndicatorRegistry.get(iid)
        r = cls().compute(pd.DataFrame(columns=["high", "low", "close", "volume", "amount", "turnover_rate"]))
        assert len(r) == 0

    def test_missing_turnover_no_raise(self):
        """缺换手率列必须软降级（禁 ValueError——provider 逐标的异常会跳过整标的）。"""
        df = _make_chips_ohlcv(30).drop(columns=["turnover_rate"])
        assert len(CYQ().compute(df)) == 0
        assert len(SCR().compute(df)) == 0
        r = CYC().compute(df)  # CYC 部分降级
        assert "cyc_inf" in r.columns and r["cyc_inf"].isna().all()

    def test_partial_nan_turnover_still_computes(self):
        """部分 NaN 换手率：照常计算（NaN 日不衰减），不空降级。"""
        df = _make_chips_ohlcv(30)
        df.loc[df.index[:5], "turnover_rate"] = np.nan
        r = CYQ().compute(df)
        assert len(r) == 30 and r["chips_winner"].notna().sum() > 20
