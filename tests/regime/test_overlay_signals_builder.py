# [A_test] module_id: MOD-TEST-OVERLAY-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 Phase2b
# [MODULE] tests.regime.test_overlay_signals_builder
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.overlay_signals_builder; zephyr.regime.core.regime_detector; pandas; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_overlay_signals_builder.py
# [A_module] module_id: MOD-TEST-OVERLAY-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #10_regime_detector_spec §4 #Phase2b
"""test_overlay_signals_builder.py — OverlaySignalsConstructor (Phase 2b) 单元测试。

覆盖：
  - 结构契约：8 转换 key 齐全 + 31 维度 key 齐全（对齐 TRANSITION_CONFIG）
  - 平时不干预：常态数据所有维度=0 → 无转换触发（C1 不退化前提）
  - S1 触发场景：高 vol_pct + 高 corr → vix_panic/correlation/liquidity > 0
  - S2 触发场景：暴跌 + 放量 → capitulation > 0
  - T1 触发场景：突破 + 放量 → bqs > 0
  - PIT：build_for_date(dt) 只用 ≤ dt-1（shift(1) 生效）
  - 降级：feature_builder=None → 全维度=0.0（纯 HMM）
  - 端到端：overlay_signals 喂 RegimeDetector._run_overlay 不报错

依据: 10_regime_detector_spec v1.3.1 §4 / Phase 2 计划 §Phase2b
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.core.regime_detector import (
    TRANSITION_CONFIG,
    TRANSITIONS,
    RegimeDetector,
)
from zephyr.regime.overlay_signals_builder import (
    _STUB_DIMS,
    _TRANSITION_DIMS,
    OverlaySignalsConstructor,
)

# ---------------------------------------------------------------------------
# Mock feature_builder
# ---------------------------------------------------------------------------


class _MockFeatureBuilder:
    """最小化 mock，模拟 RegimeFeatureBuilder 的 build_features + get_index_kline。

    Phase 2c：新增 6 个数据透传方法（money_flow/sector/limit_up_down/hk_connect/
    option_iv/multi_tf_kline），默认 None（降级 0.0），测试可通过 kwargs 注入。
    """

    def __init__(
        self,
        features: pd.DataFrame,
        index_df: pd.DataFrame,
        *,
        money_flow: pd.DataFrame | None = None,
        sector_kline: pd.DataFrame | None = None,
        limit_up_down: pd.DataFrame | None = None,
        hk_connect_flow: pd.DataFrame | None = None,
        option_iv_surface: pd.DataFrame | None = None,
        multi_tf_kline: dict[str, pd.DataFrame] | None = None,
    ) -> None:
        self._features = features
        self._index_df = index_df
        self._money_flow = money_flow
        self._sector_kline = sector_kline
        self._limit_up_down = limit_up_down
        self._hk_connect_flow = hk_connect_flow
        self._option_iv_surface = option_iv_surface
        self._multi_tf_kline = multi_tf_kline

    def build_features(self) -> pd.DataFrame:
        return self._features

    def get_index_kline(self) -> pd.DataFrame:
        return self._index_df

    # ── Phase 2c 数据透传（None → _fb_call 降级 0.0）──
    def get_money_flow(self) -> pd.DataFrame | None:
        return self._money_flow

    def get_sector_kline(self) -> pd.DataFrame | None:
        return self._sector_kline

    def get_limit_up_down(self) -> pd.DataFrame | None:
        return self._limit_up_down

    def get_hk_connect_flow(self) -> pd.DataFrame | None:
        return self._hk_connect_flow

    def get_option_iv_surface(self) -> pd.DataFrame | None:
        return self._option_iv_surface

    def get_multi_tf_kline(self) -> dict[str, pd.DataFrame] | None:
        return self._multi_tf_kline


def _make_features(
    dates: pd.DatetimeIndex,
    vol_pct: float = 0.3,
    hurst: float = 0.5,
    slope: float = 0.0,
    corr: float = 0.5,
    ad_ratio: float = 0.0,
    vol_anom: float = 0.0,
) -> pd.DataFrame:
    """构造 HMM 6 特征 DataFrame（常量填充，用于受控测试）。"""
    n = len(dates)
    return pd.DataFrame(
        {
            "realized_vol_pct": np.full(n, vol_pct),
            "hurst_dfa": np.full(n, hurst),
            "kalman_slope": np.full(n, slope),
            "cross_asset_corr": np.full(n, corr),
            "ad_ratio": np.full(n, ad_ratio),
            "volume_anomaly": np.full(n, vol_anom),
        },
        index=dates,
    )


def _make_index_df(
    dates: pd.DatetimeIndex,
    close_arr: np.ndarray,
    volume_arr: np.ndarray,
    symbol: str = "000300",
    high_arr: np.ndarray | None = None,
    low_arr: np.ndarray | None = None,
) -> pd.DataFrame:
    """构造 MultiIndex(symbol, trade_date) index_df。

    Phase 2c：新增可选 high/low（wyckoff_engine 需要，缺失时降级 MVP 简化版）。
    """
    idx = pd.MultiIndex.from_product([[symbol], dates], names=["symbol", "trade_date"])
    data: dict[str, np.ndarray] = {
        "close": close_arr,
        "volume": volume_arr,
        "advance_count": np.full(len(dates), 2000.0),
        "decline_count": np.full(len(dates), 2000.0),
    }
    if high_arr is not None:
        data["high"] = high_arr
    if low_arr is not None:
        data["low"] = low_arr
    return pd.DataFrame(data, index=idx)


def _make_dates(n: int = 300, start: str = "2020-01-01") -> pd.DatetimeIndex:
    return pd.bdate_range(start=start, periods=n)


# ---------------------------------------------------------------------------
# Phase 2c 新数据源 mock 构造器
# ---------------------------------------------------------------------------


def _make_money_flow(dates: pd.DatetimeIndex, inflow_pct: float = 0.0) -> pd.DataFrame:
    """全市场主力净流入占比 DataFrame（index=trade_date, col=avg_main_net_inflow_pct）。"""
    return pd.DataFrame(
        {"avg_main_net_inflow_pct": np.full(len(dates), inflow_pct)},
        index=dates,
    )


def _make_sector_kline(
    dates: pd.DatetimeIndex,
    n_sectors: int = 5,
    leader_pct: float = 0.0,
    others_pct: float = 0.0,
) -> pd.DataFrame:
    """行业板块K线 MultiIndex(code, trade_date) DataFrame。

    leader_pct: 头部板块每日涨幅（其余板块 = others_pct，负值=下跌）。
    close 按日几何增长 → pct_change() 复现指定日涨幅。
    用于构造 HHI 集中度（leader 独涨 → HHI 高）+ top_sector_pct。
    """
    codes = [f"S{i:02d}" for i in range(n_sectors)]
    rows = []
    for code in codes:
        pct = leader_pct if code == codes[0] else others_pct
        base = 1000.0
        for i, d in enumerate(dates):
            close = base * ((1 + pct) ** i)
            rows.append((code, d, close, 1e6, 1e8))
    df = pd.DataFrame(rows, columns=["code", "trade_date", "close", "volume", "amount"])
    return df.set_index(["code", "trade_date"]).sort_index()


def _make_limit_up_down(
    dates: pd.DatetimeIndex,
    limit_up_per_day: int = 0,
    consec_symbol: str | None = None,
    consec_days: int = 0,
    consec_start_idx: int = 100,
) -> pd.DataFrame:
    """涨跌停统计 MultiIndex(trade_date, symbol) DataFrame。

    limit_up_per_day: 每日涨停家数（普通涨停，次日不续）。
    consec_symbol + consec_days: 构造连板（同一 symbol 连续 consec_days 日涨停）。
    consec_start_idx: 连板起始日索引（默认 100；测试末期场景设靠近查询日）。
    """
    rows = []
    # 连板 symbol（连续 consec_days 日涨停）
    if consec_symbol is not None and consec_days > 0:
        for i in range(consec_days):
            idx = consec_start_idx + i
            if 0 <= idx < len(dates):
                rows.append((dates[idx], consec_symbol, "涨停", 0.1, 1e8))
    # 每日普通涨停（不连板，分散在不同 symbol）
    for di, d in enumerate(dates):
        for k in range(limit_up_per_day):
            sym = f"LU{di:04d}_{k:02d}"
            rows.append((d, sym, "涨停", 0.1, 1e8))
    if not rows:
        # 空表也要有正确结构（return None 由调用方处理）
        return pd.DataFrame(columns=["symbol", "limit_type", "pct_change", "amount"]).set_index(
            [pd.DatetimeIndex([], name="trade_date"), "symbol"]
        )
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "limit_type", "pct_change", "amount"])
    return df.set_index(["trade_date", "symbol"]).sort_index()


# ---------------------------------------------------------------------------
# 结构契约测试
# ---------------------------------------------------------------------------


class TestStructureContract:
    """8 转换 key + 32 维度 key 对齐 TRANSITION_CONFIG（P1-E9d 后含 breadth_thrust）。"""

    def test_8_transitions_present(self):
        """_TRANSITION_DIMS 包含全部 8 转换（T1-T6/S1/S2）。"""
        assert set(_TRANSITION_DIMS.keys()) == set(TRANSITIONS)

    def test_dims_align_config(self):
        """每个转换的维度 key 与 TRANSITION_CONFIG 的 keys_gte/keys_or_gte 完全对齐。

        P1-E9d：S2 confirm 新增 keys_or_gte 析取字段（wyckoff/breadth_thrust），
        契约对齐须同时收集析取 key。
        """
        for tid in TRANSITIONS:
            cfg = TRANSITION_CONFIG[tid]
            config_keys: set[str] = set()
            for stage in cfg["stages"].values():
                config_keys.update((stage.get("keys_gte") or {}).keys())
                config_keys.update((stage.get("keys_or_gte") or {}).keys())
            builder_keys = set(_TRANSITION_DIMS[tid])
            assert builder_keys == config_keys, f"{tid} 维度不匹配: builder={builder_keys} vs config={config_keys}"

    def test_31_unique_keys(self):
        """全转换并集 = 32 个维度 key（32 可算 + 0 stub）。

        Phase 2c: T3 资金/板块 4 维度从 stub 升级为可算，stub 6→2。
        P1-E3: policy/bad_news_flat 从 stub 升级为可算（关键词 NLP），stub 2→0。
        P1-E9d: S2 新增 breadth_thrust 维度（V 反转析取通路），31→32。
        """
        all_keys: set[str] = set()
        for keys in _TRANSITION_DIMS.values():
            all_keys.update(keys)
        assert len(all_keys) == 32, f"期望 32 维度，实际 {len(all_keys)}"
        assert set() == _STUB_DIMS, f"期望 0 stub（全部已激活），实际 {_STUB_DIMS}"

    def test_build_for_date_has_all_transitions_and_dims(self):
        """build_for_date 返回结构包含 8 转换 + 各转换全部维度 key。"""
        dates = _make_dates(300)
        feat = _make_features(dates)
        idx_df = _make_index_df(dates, np.linspace(3000, 3500, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        assert "transitions" in result
        trans = result["transitions"]
        assert set(trans.keys()) == set(TRANSITIONS)
        for tid in TRANSITIONS:
            assert set(trans[tid].keys()) == set(_TRANSITION_DIMS[tid])


# ---------------------------------------------------------------------------
# 平时不干预测试（C1 不退化前提）
# ---------------------------------------------------------------------------


class TestNoSignalInNormalMarket:
    """常态数据所有维度=0 → 无转换触发（平时退化为纯 HMM）。"""

    def test_normal_market_all_zero(self):
        """低波/低相关/宽幅震荡 → 无转换 stage 触发（C1 不退化前提）。

        注：个别弱维度（如 wyckoff=25 在窄幅日）可能非零，但单维度无法触发
        stage（S2 confirm 需 wyckoff>=60 + policy stub=0 → 永不满足）。
        真正的不退化保证 = 无 stage 触发 → overlay_probs 全 0 → 纯 HMM。
        """
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5, vol_anom=0.0)
        rng = np.random.default_rng(42)
        close = 3000 + 200 * np.sin(np.linspace(0, 8 * np.pi, 300)) + rng.normal(0, 5, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        # 核心保证：无 stage 触发 → overlay 不干预（纯 HMM）
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(result)
        assert all(v == 0.0 for v in overlay_probs.values()), (
            f"常态不应触发 overlay，实际 overlay_probs={overlay_probs}"
        )

    def test_normal_market_no_overlay_effect(self):
        """常态 overlay_signals 喂检测器 → 无 overlay 概率（纯 HMM）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.linspace(3000, 3100, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        overlay = ctor.build_for_date(dates[250])
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(overlay)
        # 无转换触发 → overlay 概率全 0
        assert all(v == 0.0 for v in overlay_probs.values())


# ---------------------------------------------------------------------------
# 触发场景测试
# ---------------------------------------------------------------------------


class TestTriggerScenarios:
    """危机/突破/见底场景下对应维度 > 0。"""

    def test_s1_crisis_trigger(self):
        """高 vol_pct(>0.90) + 高 corr(>0.95) + 暴跌 close → vix_panic/correlation > 0。

        Phase 2c：vix_panic 优先用合成 VIX（基于 close 下行半偏差），需构造暴跌
        close 让 vix_pct 飙升；corr 常量 0.96 → corr_scr=90（P1 校准后过门槛）。
        """
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, corr=0.96, vol_anom=2.5)
        # 前 270 日平稳（warmup），后 30 日持续大跌 → 合成 VIX 飙升
        rng = np.random.default_rng(0)
        returns = np.concatenate(
            [
                rng.normal(0.0, 0.003, 270),  # 平稳期
                rng.normal(-0.03, 0.015, 30),  # 暴跌期（下行半偏差飙升）
            ]
        )
        close = 3000.0 * np.exp(np.cumsum(returns))
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        # dates[280]：warmup（270 日）后的暴跌段，合成 VIX 应飙升
        result = ctor.build_for_date(dates[280])
        s1 = result["transitions"]["S1"]
        assert s1["vix_panic"] >= 60, f"S1 vix_panic={s1['vix_panic']} 应过触发门槛"
        assert s1["correlation"] >= 60, f"S1 correlation={s1['correlation']} 应过触发门槛"
        # S1 trigger 条件：vix_panic>=60 AND correlation>=60
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(result)
        assert overlay_probs["r10"] > 0, "S1 触发应产出 CRISIS(r10) 概率"

    def test_s2_capitulation_signal(self):
        """暴跌(>4%) + 放量(z>3) → capitulation > 0。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, vol_anom=3.5)
        close = np.full(300, 3000.0)
        close[249] = 3000 * (1 - 0.05)  # 暴跌 5%
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        s2 = result["transitions"]["S2"]
        # capitulation 在暴跌次日（shift(1) PIT）应 > 0
        assert s2["capitulation"] > 0, f"S2 capitulation={s2['capitulation']} 应 > 0"

    def test_t1_breakout_signal(self):
        """价格破 60 日新高 + 放量 → bqs > 0。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.4, slope=0.001, hurst=0.55)
        close = np.linspace(3000, 3100, 300)
        close[250] = 3300  # 突破前高
        volume = np.full(300, 1e8)
        volume[250] = 3e8  # 放量
        idx_df = _make_index_df(dates, close, volume)
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[251])
        t1 = result["transitions"]["T1"]
        assert t1["bqs"] > 0, f"T1 bqs={t1['bqs']} 应 > 0"


# ---------------------------------------------------------------------------
# PIT 测试
# ---------------------------------------------------------------------------


class TestPIT:
    """build_for_date(dt) 只用 ≤ dt-1 数据（shift(1) 生效）。"""

    def test_shift_prevents_lookahead(self):
        """dt 日的新数据不影响 build_for_date(dt)（shift(1) 隔离）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.full(300, 3000.0)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        dt = dates[250]
        result_before = ctor.build_for_date(dt)

        # 篡改 dt 当日的特征为极端危机值
        feat.loc[dt, "realized_vol_pct"] = 0.99
        feat.loc[dt, "cross_asset_corr"] = 0.99
        # 重新构造（清缓存）
        ctor2 = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=_MockFeatureBuilder(feat, idx_df),
        )
        result_after = ctor2.build_for_date(dt)
        # dt 当日的极端值因 shift(1) 不影响 build_for_date(dt)
        assert result_before["transitions"]["S1"]["vix_panic"] == result_after["transitions"]["S1"]["vix_panic"], (
            "PIT 违规：dt 当日数据泄漏到 build_for_date(dt)"
        )


# ---------------------------------------------------------------------------
# 降级测试
# ---------------------------------------------------------------------------


class TestDegradation:
    """数据缺失时降级为 0.0（不触发）。"""

    def test_none_feature_builder(self):
        """feature_builder=None → 全维度=0.0。"""
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=None,
        )
        result = ctor.build_for_date(pd.Timestamp("2020-06-01"))
        trans = result["transitions"]
        assert set(trans.keys()) == set(TRANSITIONS)
        for tid, breakdown in trans.items():
            assert all(v == 0.0 for v in breakdown.values())

    def test_stub_dims_always_zero(self):
        """stub 维度（policy/bad_news_flat）恒为 0.0（NLP 未接入）。

        Phase 2c: T3 资金/板块 4 维度已从 stub 升级为可算，不再是 stub。
        """
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, corr=0.96, vol_anom=3.0)
        close = np.linspace(3000, 2900, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        trans = result["transitions"]
        for tid, breakdown in trans.items():
            for key in breakdown:
                if key in _STUB_DIMS:
                    assert breakdown[key] == 0.0, f"stub {tid}.{key} 应恒 0.0"


# ---------------------------------------------------------------------------
# P1-E9: S2 五子项调用链集成（OHLCV+广度指数全数据 mock）
# ---------------------------------------------------------------------------


class TestP1E9S2Integration:
    """P1-E9a~e 调用链迁移集成验证（14_regime_s2_diagnosis §4）。

    既有 mock 仅 close/volume（走降级路径）；本类构造含 open/high/low + 广度指数
    399106 涨跌家数的全数据 mock，验证新调用链真实生效：
      capitulation 衰减加权簇集 > 0 / breadth_thrust 完整 thrust = 80 /
      spring 深度分级 / three_yang 6 维分级。
    """

    def _make_full_index_df(self, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """双符号 index_df：000300 完整 OHLCV + 399106 涨跌家数（breadth thrust）。"""
        n = len(dates)
        # 000300：常态平盘 3000；250-252 日 3 日 capitulation 级联暴跌（-6%/日，
        # 3×量 + 长下影 + 大实体，三过滤器全共振）
        open_a = np.full(n, 3000.0)
        high = np.full(n, 3005.0)
        low = np.full(n, 2995.0)
        close = np.full(n, 3000.0)
        volume = np.full(n, 1e8)
        prev = 3000.0
        for i in (250, 251, 252):
            o, c = prev * 0.99, prev * 0.94
            open_a[i], close[i] = o, c
            high[i] = prev * 1.001
            low[i] = c * 0.92  # 下影占比 ~57%>50%
            volume[i] = 3e8
            prev = c
        proxy_idx = pd.MultiIndex.from_product([["000300"], dates], names=["symbol", "trade_date"])
        proxy_df = pd.DataFrame(
            {"open": open_a, "high": high, "low": low, "close": close, "volume": volume},
            index=proxy_idx,
        )
        # 399106：230-244 日 washout（涨 30%）→ 245 日起普涨（涨 80%）→ 完整 thrust
        ratio = np.full(n, 0.50)
        ratio[230:245] = 0.30
        ratio[245:] = 0.80
        br_idx = pd.MultiIndex.from_product([["399106"], dates], names=["symbol", "trade_date"])
        br_df = pd.DataFrame(
            {
                "open": np.full(n, 1000.0),
                "high": np.full(n, 1001.0),
                "low": np.full(n, 999.0),
                "close": np.full(n, 1000.0),
                "volume": np.full(n, 1e8),
                "advance_count": ratio * 5000.0,
                "decline_count": (1.0 - ratio) * 5000.0,
            },
            index=br_idx,
        )
        return pd.concat([proxy_df, br_df]).sort_index()

    def test_p1e9_s2_dims_via_full_chain(self):
        """全数据 mock：capitulation 簇集>0 + breadth_thrust=80（shift(1) PIT 后）。"""
        dates = _make_dates(300)
        vol_anom = np.zeros(300)
        vol_anom[250:253] = 3.5  # capitulation 日 z>3（90 分档）
        feat = _make_features(dates, vol_pct=0.3, corr=0.5, vol_anom=0.0)
        feat["volume_anomaly"] = vol_anom
        idx_df = self._make_full_index_df(dates)
        fb = _MockFeatureBuilder(feat, idx_df)
        fb.breadth_index = "399106"  # 与生产 RegimeFeatureBuilder 属性同名
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        # 查 dates[253] → shift(1) 取 252（第 3 个 capitulation 日 / thrust 第 8 日）
        s2 = ctor.build_for_date(dates[253])["transitions"]["S2"]
        assert s2["capitulation"] > 0, (
            f"P1-E9a 衰减加权簇集应 >0（3 日 90 分簇集），实际 {s2['capitulation']}"
        )
        assert s2["breadth_thrust"] == 80, (
            f"P1-E9d 完整 thrust（washout→普涨）应=80，实际 {s2['breadth_thrust']}"
        )
        # 新维度已注册进 S2 breakdown
        assert "breadth_thrust" in s2

    def test_p1e9_degrade_without_ohlc_and_breadth(self):
        """缺 open/399106（旧 mock 形态）→ capitulation 降级瞬时版 + breadth_thrust=0。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, vol_anom=3.5)
        close = np.full(300, 3000.0)
        close[249] = 3000 * (1 - 0.05)  # 单日暴跌 5%
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))  # 无 open，仅 000300
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        s2 = ctor.build_for_date(dates[250])["transitions"]["S2"]
        # 降级瞬时两维版：z>3 & 跌>4% → 90（无衰减）
        assert s2["capitulation"] == 90
        assert s2["breadth_thrust"] == 0.0



# ---------------------------------------------------------------------------
# Phase 2c: T3 资金/板块维度（从 stub 升级为可算）
# ---------------------------------------------------------------------------


class TestPhase2cT3Dims:
    """4 个 T3 维度（money_effect/mainline/leader/one_day_mainline）接入真实数据。

    Phase 2c 升级：原 stub=0.0，现接 money_flow/kline_sector/limit_up_down。
    验证：数据注入 → 维度 > 0；数据缺失 → 维度 = 0.0（降级）；常态不误触发。
    """

    def test_t3_dims_zero_without_data(self):
        """无 money_flow/sector/limit_up_down → 4 T3 维度全 0.0（降级）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)  # 无 T3 数据 kwargs
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        t3 = result["transitions"]["T3"]
        for key in ("money_effect", "mainline", "leader", "one_day_mainline"):
            assert t3[key] == 0.0, f"T3.{key} 无数据应降级 0.0，实际 {t3[key]}"

    def test_t3_money_effect_computed(self):
        """主力净流入 4% + 涨停 60 家 → money_effect=65（过 trigger 门槛）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        money_flow = _make_money_flow(dates, inflow_pct=4.0)  # >3
        limit_df = _make_limit_up_down(dates, limit_up_per_day=60)  # >50
        fb = _MockFeatureBuilder(feat, idx_df, money_flow=money_flow, limit_up_down=limit_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        me = result["transitions"]["T3"]["money_effect"]
        # inflow=4>3 & lu=60>50 → 65（shift(1) 后取 dates[249]，数据恒定仍 65）
        assert me == 65.0, f"money_effect 应=65（inflow>3 & lu>50），实际 {me}"

    def test_t3_mainline_computed(self):
        """头部板块独涨 4%（其余平）→ HHI=1.0 + top=4 → mainline=80。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        # leader 独涨 4%，其余 4 个板块 0% → HHI=1.0, top_sector_pct=4
        sector_df = _make_sector_kline(dates, n_sectors=5, leader_pct=0.04, others_pct=0.0)
        fb = _MockFeatureBuilder(feat, idx_df, sector_kline=sector_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        ml = result["transitions"]["T3"]["mainline"]
        # HHI=1.0>0.15 & top=4>3 → 80
        assert ml == 80.0, f"mainline 应=80（HHI>0.15 & top>3），实际 {ml}"

    def test_t3_leader_computed(self):
        """5 连板 + 晋级率 1.0 → leader=80（过 trigger 门槛）。

        连板从 dates[244] 起 5 日（覆盖 dates[244..248]），build_for_date(dates[250])
        shift(1) 取 dates[249]；为稳取连板峰值，连板延至 dates[249]。
        """
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        # 5 连板覆盖 dates[245..249]，build_for_date(dates[250]) 取 dates[249] 的 max_consec=5
        limit_df = _make_limit_up_down(dates, consec_symbol="LEADER", consec_days=5, consec_start_idx=245)
        fb = _MockFeatureBuilder(feat, idx_df, limit_up_down=limit_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        ld = result["transitions"]["T3"]["leader"]
        # max_consec=5>=5 & promotion=1.0>0.5 → 80
        assert ld == 80.0, f"leader 应=80（连板≥5 & 晋级>0.5），实际 {ld}"

    def test_normal_market_t3_no_false_trigger(self):
        """常态（低波/低相关）+ 弱 T3 数据 → overlay_probs 全 0（C1 不退化）。

        T3 弱信号（money_effect=25/mainline=0/leader=0）不足以触发 T3 任一 stage
        （confirm 需 volume_price+ma_trend+sentiment+money_effect>=50 等），
        叠加常态 S1/S2 不触发 → overlay 全 0 → 纯 HMM 不退化。
        """
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)  # 常态
        close = np.linspace(3000, 3100, 300)  # 温和上行
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        # 弱 T3 数据：inflow=1（>0 但 <2）→ money_effect=25（未达 50 门槛）
        money_flow = _make_money_flow(dates, inflow_pct=1.0)
        limit_df = _make_limit_up_down(dates, limit_up_per_day=5)
        fb = _MockFeatureBuilder(feat, idx_df, money_flow=money_flow, limit_up_down=limit_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(result)
        assert all(v == 0.0 for v in overlay_probs.values()), (
            f"常态弱 T3 信号不应触发 overlay，实际 overlay_probs={overlay_probs}"
        )

    def test_t3_trigger_fires(self):
        """T3 trigger 阶段触发 → _run_overlay 给 r12 BREAKOUT 非零概率。

        _STAGE_ORDER = (strong_confirm, confirm, trigger, fail)，首个匹配生效。
        trigger 的 p_overlay={r12:0.55} 只有在 strong_confirm/confirm 都不匹配时才命中。
        故构造：trigger 维度过门槛 + confirm 维度不过门槛 + total<200。

          trigger:  sentiment>=60, mainline>=60, leader>=60 → p_overlay r12=0.55
          confirm:  volume_price<60（不满足）→ confirm 不匹配
          strong_confirm: total=195<200 → 不匹配
          fail:     one_day_mainline=0（不触发）
        """
        overlay_signals = {
            "transitions": {
                "T3": {
                    "volume_price": 0.0,  # < 60 → confirm 不匹配
                    "ma_trend": 0.0,  # < 50 → confirm 不匹配
                    "sentiment": 65.0,  # >= 60 (trigger)
                    "money_effect": 0.0,  # < 50 → confirm 不匹配
                    "mainline": 65.0,  # >= 60 (trigger)
                    "leader": 65.0,  # >= 60 (trigger)
                    "one_day_mainline": 0.0,  # < 1 (no fail)
                },
                "S1": {k: 0.0 for k in _TRANSITION_DIMS["S1"]},
                "S2": {k: 0.0 for k in _TRANSITION_DIMS["S2"]},
                "T1": {k: 0.0 for k in _TRANSITION_DIMS["T1"]},
                "T2": {k: 0.0 for k in _TRANSITION_DIMS["T2"]},
                "T4": {k: 0.0 for k in _TRANSITION_DIMS["T4"]},
                "T5": {k: 0.0 for k in _TRANSITION_DIMS["T5"]},
                "T6": {k: 0.0 for k in _TRANSITION_DIMS["T6"]},
            }
        }
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(overlay_signals)
        # T3 trigger → r12 (BREAKOUT) 获得非零概率
        assert overlay_probs.get("r12", 0.0) > 0, f"T3 触发应给 r12 非零概率，实际 overlay_probs={overlay_probs}"

    def test_t3_fail_when_one_day_mainline(self):
        """one_day_mainline=1 且 trigger/confirm 不匹配 → T3 fail 触发（r11 > 0）。

        _STAGE_ORDER 中 fail 排最后，只有 strong_confirm/confirm/trigger 都不匹配时
        才评估 fail。故构造全 0 维度 + one_day_mainline=1。
        """
        overlay_signals = {
            "transitions": {
                "T3": {
                    "volume_price": 0.0,
                    "ma_trend": 0.0,
                    "sentiment": 0.0,  # < 60 → trigger 不匹配
                    "money_effect": 0.0,
                    "mainline": 0.0,  # < 60 → trigger 不匹配
                    "leader": 0.0,  # < 60 → trigger 不匹配
                    "one_day_mainline": 1.0,  # >= 1 → fail 匹配
                },
                "S1": {k: 0.0 for k in _TRANSITION_DIMS["S1"]},
                "S2": {k: 0.0 for k in _TRANSITION_DIMS["S2"]},
                "T1": {k: 0.0 for k in _TRANSITION_DIMS["T1"]},
                "T2": {k: 0.0 for k in _TRANSITION_DIMS["T2"]},
                "T4": {k: 0.0 for k in _TRANSITION_DIMS["T4"]},
                "T5": {k: 0.0 for k in _TRANSITION_DIMS["T5"]},
                "T6": {k: 0.0 for k in _TRANSITION_DIMS["T6"]},
            }
        }
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(overlay_signals)
        # T3 fail → r11 (RECOVERY) 获得非零概率
        assert overlay_probs.get("r11", 0.0) > 0, f"T3 fail 应给 r11 非零概率，实际 overlay_probs={overlay_probs}"


# ---------------------------------------------------------------------------
# 端到端：overlay_signals 喂 RegimeDetector.detect 不报错
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """overlay_signals 喂 RegimeDetector.detect 全流程不报错。"""

    def test_detect_with_overlay_no_error(self):
        """危机场景 overlay + 风险输入 → detect 产出有效 Shrinkage。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, corr=0.96, vol_anom=2.5, slope=-0.001)
        close = np.linspace(3000, 2800, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        dt = dates[250]
        overlay = ctor.build_for_date(dt)
        # 构造 risk_inputs（#1 已触发危机）
        risk_inputs = {
            "params": {1: 0.30, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 12: 1.0},
            "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
        }
        detector = RegimeDetector(shrinkage_enabled=True)
        # HMM 未 fit → 降级均匀分布；overlay + risk 仍可算
        regime_features = {"X": np.zeros((60, 6))}
        probs, shrinkage = detector.detect(regime_features, overlay_signals=overlay, risk_signal_inputs=risk_inputs)
        assert 0.0 < shrinkage.value <= 1.0
        assert len(probs.probabilities) == 7  # 4 HMM 态(r1-r4) + 3 overlay 态(r10-r12)
