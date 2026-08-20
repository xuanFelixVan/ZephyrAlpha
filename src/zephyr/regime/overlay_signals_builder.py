# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 D-SIGNAL-68 Phase2b
# [MODULE] zephyr.regime.overlay_signals_builder
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.regime.features.overlay_features; zephyr.regime.regime_feature_builder
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder.build_shrinkage_schedule消费→overlay_signals)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] score维度∈[0,100]; flag维度∈{0,1}; 无信号=0(平时不干预→纯HMM不退化); PIT严格(build_for_date(dt)只用≤dt-1,预计算shift(1)); 数据缺失→维度=0.0降级
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] —(数据缺失降级为0.0,不抛错)
# [TESTS] tests/regime/test_overlay_signals_builder.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4 #D-SIGNAL-68 #MOD-REGIME-002 #Phase2b #C1-shrinkage-comparator
"""OverlaySignals 构造器（MOD-REGIME-002 Phase 2b）。

把原始特征转换成 RegimeDetector._run_overlay 期望的 8 转换 overlay_signals 输入 dict：
    {"transitions": {"S1": {"vix_panic": 85.0, "correlation": 70.0, ...}, ...}}

8 转换（对齐 TRANSITION_CONFIG）:
    S1 Any→CRISIS（VIX Panic + Correlation + Liquidity）
    S2 CRISIS→RECOVERY（八维度见底：capitulation/vix/wyckoff/valuation/fund/spring/three_yang/...）
    T1 Neutral→BREAKOUT（bqs/rcs/frs）
    T2 Bear-Low→RECOVERY（冰点反核，total 评分）
    T3 RECOVERY→BREAKOUT（volume_price/ma_trend/sentiment + 资金/板块/北向资金）
    T4 Bull-Med→Bull-High（疯狂赶顶，total 评分）
    T5 Bull-High→Bear-Med（逃顶退潮，leader_break/rebound_wrap）
    T6 Bear-Med→Bear-Low（退潮冰点，sudden_volume）

设计（Phase 2 计划 §架构决策，与 RiskSignalConstructor 一致）：
  - **预计算全序列 + 按 dt 切片**：__init__ 后首次 build_for_date 触发 _precompute，
    一次性向量化算出 25 可算维度 Series（已 shift(1)），后续 build_for_date(dt) 取
    loc[:dt].iloc[-1]（O(1)），walk-forward 2800+ 日 detect 不重复计算。
  - **复用 feature_builder**：接收 RegimeFeatureBuilder 引用，复用其 build_features()
    （HMM 6 特征：vol_pct/hurst/slope/corr/ad_ratio/vol_z）+ get_index_kline()
    （代理 OHLCV：close/volume），避免重复查 ClickHouse。
  - **无信号 = 0**：平时所有维度评分 0 → 无转换触发 → overlay 不干预（C1 不退化前提）。
    这是 Phase 2b 的核心保护——overlay 只在明确信号时触发，平时退化为纯 HMM。
  - **降级友好**：任一维度数据缺失 → 该维度=0.0（不触发）+ log WARN，保证 overlay
    只因真实信号触发，不因数据空洞误杀。全 feature_builder 缺失 → 所有维度=0.0（纯 HMM）。
  - **PIT 铁律**：_precompute 末尾对每个维度 Series shift(1)，build_for_date(dt) 取
    loc[:dt].iloc[-1] 即 ≤ dt-1 数据（与 RegimeFeatureBuilder.shift(1) 一致）。

32 个维度 key（对齐 TRANSITION_CONFIG 的 keys_gte/keys_or_gte，契约守护）:
  可算 32：vix_panic/correlation/liquidity/flash_recover（S1）
           capitulation/vix/wyckoff/valuation/fund/spring/three_yang/
           breadth_thrust/break_sc_low/vix_new_high/fund_outflow/policy/bad_news_flat（S2）
           bqs/rcs/frs（T1）, continue_decline（T2）
           volume_price/ma_trend/sentiment/money_effect/mainline/leader/
           one_day_mainline（T3）, shrink_flat（T4）
           leader_break/rebound_wrap（T5）, sudden_volume（T6）
  stub 0：全部已激活（P1-E3 关键词 NLP + P1-E4/E5 资金板块）

P1-E9 升级（14_regime_s2_diagnosis §4）：capitulation 衰减加权多过滤器（E9a）/
valuation 路 B 阈值校准（E9b，路 A CAPE 待 daily_valuation 管道）/
spring 深度分级+velocity+0.5×ATR 失效边距（E9c）/breadth_thrust V 反转析取通路（E9d，
数据源=广度指数 399106 advance_count/decline_count）/three_yang 6 维分级（E9e）。

Phase 2c 升级：money_effect/mainline/leader/one_day_mainline 从 stub→可算
（接入 money_flow/kline_sector/limit_up_down + hk_connect_flow 北向融合），T3 confirm/trigger/fail 解锁。
合成 VIX（vix_pct）优先注入 s1_vix_panic/s2_vix（回退 vol_pct）；
s2_wyckoff 委托 wyckoff_engine 6 阶段 FSM（需 high/low，P1-E4 已从 kline_index 激活）。
P1-E3 升级：policy/bad_news_flat 从 stub→可算（关键词字典 NLP 情感分析），
S2 confirm/trigger 全阶段解锁。8 转换全部可触发。

依据: 10_regime_detector_spec v1.3.1 §4 / Phase 2 计划 §Phase2b
Version: 0.1.0
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from zephyr.regime.features import overlay_features

if TYPE_CHECKING:  # 避免循环 import
    from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder
    from zephyr.regime.risk_signal_builder import RiskSignalConstructor

_logger = logging.getLogger(__name__)

# 8 转换 → 各转换的维度 key（对齐 TRANSITION_CONFIG 的 keys_gte，含 stub）
# breakdown 必须包含 stub key（=0.0），否则 keys_gte 的 .get(key, 0.0) 永远 0 →
# 需该 key 的阶段（如 S2 confirm 需 policy>=40）正确判定为不满足（而非跳过）
_TRANSITION_DIMS: dict[str, list[str]] = {
    "S1": ["vix_panic", "correlation", "liquidity", "flash_recover"],
    "S2": [
        "capitulation",
        "vix",
        "wyckoff",
        "valuation",
        "fund",
        "spring",
        "three_yang",
        "breadth_thrust",  # P1-E9d：V 反转通路（confirm 析取 keys_or_gte）
        "break_sc_low",
        "vix_new_high",
        "fund_outflow",
        "policy",
        "bad_news_flat",
    ],
    "T1": ["bqs", "rcs", "frs"],
    "T2": ["continue_decline"],
    "T3": [
        "volume_price",
        "ma_trend",
        "sentiment",
        "money_effect",
        "mainline",
        "leader",
        "one_day_mainline",  # Phase 2c 已激活（kline_sector）
    ],
    "T4": ["shrink_flat"],
    "T5": ["leader_break", "rebound_wrap"],
    "T6": ["sudden_volume"],
}

# stub 维度（不预计算，build_for_date 给 0.0）
# Phase 2c: policy/bad_news_flat 已从 stub 激活（P1-E3 MVP 关键词 NLP）
# T3 资金/板块 4 维度（money_effect/mainline/leader/one_day_mainline）已激活（P1-E4/E5）:
#   _compute_t3_inputs 接入 money_flow/kline_sector/limit_up_down/hk_connect_flow，
#   _precompute 调用 7 评分函数算出维度 Series 放入 cache。
#   数据缺失时对应输入 None → 维度=0.0 降级（C1 不退化）。
_STUB_DIMS: set[str] = set()  # P1-E3: policy/bad_news_flat 已激活


class OverlaySignalsConstructor:
    """8 转换 OverlaySignals 构造器（MOD-REGIME-002 Phase 2b）。

    Usage（由 RegimeFeatureBuilder.build_shrinkage_schedule 内部调用）::

        ctor = OverlaySignalsConstructor(
            backtest_start="2015-01-01", backtest_end="2026-06-30",
            data_load_start="2010-01-01",
            feature_builder=builder,  # 复用已加载的 HMM 6 特征 + index_df
        )
        overlay = ctor.build_for_date(dt)  # → {"transitions": {"S1": {...}, ...}}

    数据源（经 feature_builder 复用）:
      - feature_builder.build_features() → HMM 6 特征（vol_pct/hurst/slope/corr/ad_ratio/vol_z）
      - feature_builder.get_index_kline() → 代理 OHLCV（close/volume）
      - stub 维度（policy/bad_news_flat）：=0.0（待 P1-E3 NLP 管道）

    PIT: _precompute 末尾 shift(1)，build_for_date(dt) 取 loc[:dt].iloc[-1]（≤ dt-1）。
    降级: 任一数据源缺失 → 该维度=0.0（不触发），log WARN。
    """

    def __init__(
        self,
        backtest_start: str,
        backtest_end: str,
        data_load_start: str,
        feature_builder: RegimeFeatureBuilder | None = None,
        risk_constructor: RiskSignalConstructor | None = None,
        market_proxy: str = "000300",
    ) -> None:
        """初始化。

        Args:
            backtest_start: 回测起始日（含，限定维度序列范围）。
            backtest_end: 回测结束日（含）。
            data_load_start: 数据加载起始日（需早于 backtest_start，供 warmup）。
            feature_builder: RegimeFeatureBuilder 引用（复用 6 特征 + index_df）。
                None 时无法计算（所有维度=0.0，纯 HMM 降级）。
            risk_constructor: RiskSignalConstructor 引用（Phase 2b 暂未使用，预留
                未来 cross-reference risk 状态过滤 overlay 误触发）。默认 None。
            market_proxy: 市场代理指数代码（OHLCV 源）。
        """
        self.backtest_start = backtest_start
        self.backtest_end = backtest_end
        self.data_load_start = data_load_start
        self.market_proxy = market_proxy
        self._feature_builder = feature_builder
        self._risk_constructor = risk_constructor
        self._cache: dict[str, pd.Series] | None = None  # {dim_key: score_series(已shift)}

    # ── 公共接口 ──────────────────────────────────────────────────────────

    def build_for_date(self, dt: pd.Timestamp) -> dict[str, Any]:
        """取 dt 时点的 8 转换各维度评分快照（PIT：只用 ≤ dt-1）。

        Args:
            dt: 查询时点（pd.Timestamp）。

        Returns:
            {"transitions": {"S1": {"vix_panic": 85.0, ...}, "S2": {...}, ...}}
            缺失数据的维度=0.0，stub 维度=0.0。平时所有维度=0.0 → 无转换触发。
        """
        cache = self._precompute()
        transitions: dict[str, dict[str, float]] = {}
        for tid, dim_keys in _TRANSITION_DIMS.items():
            breakdown: dict[str, float] = {}
            for key in dim_keys:
                if key in _STUB_DIMS:
                    breakdown[key] = 0.0
                    continue
                series = cache.get(key)
                if series is None or series.empty:
                    breakdown[key] = 0.0
                    continue
                sub = series.loc[:dt]
                if sub.empty:
                    breakdown[key] = 0.0
                    continue
                val = sub.iloc[-1]
                breakdown[key] = float(val) if not np.isnan(val) else 0.0
            transitions[tid] = breakdown
        return {"transitions": transitions}

    # ── 预计算 ────────────────────────────────────────────────────────────

    def _precompute(self) -> dict[str, pd.Series]:
        """一次性加载特征 + 向量化计算 25 可算维度 Series（已 shift(1)）。

        Returns:
            {dim_key: pd.Series}，每个 Series 已 shift(1)（PIT）。
            数据缺失的维度不放入 cache（build_for_date 走 0.0 降级）。
        """
        if self._cache is not None:
            return self._cache

        cache: dict[str, pd.Series] = {}

        # 无 feature_builder → 全降级 0.0（纯 HMM）
        if self._feature_builder is None:
            _logger.warning("OverlaySignalsConstructor 无 feature_builder，所有维度=0.0（纯 HMM 降级）")
            self._cache = cache
            return cache

        # 1. 复用 HMM 6 特征
        try:
            features = self._feature_builder.build_features()
        except Exception as exc:  # noqa: BLE001 — 降级友好
            _logger.warning("build_features 失败，Overlay 全降级（维度=0.0）: %s", exc)
            self._cache = cache
            return cache

        # 2. 复用代理 OHLCV（close/volume + high/low + open）
        # Phase 2c：high/low 分离加载，避免 high 缺失连累 close（与 risk_signal_builder 一致）
        # P1-E9a：open 分离加载（capitulation 真实体 + 下影线过滤器的数据前置）
        proxy_close = proxy_volume = proxy_high = proxy_low = proxy_open = None
        proxy_adv = proxy_dec = None
        try:
            index_df = self._feature_builder.get_index_kline()
            proxy = index_df.xs(self.market_proxy, level="symbol")
            proxy_close = proxy["close"].astype(float)
            proxy_volume = proxy["volume"].astype(float)
        except Exception as exc:  # noqa: BLE001
            _logger.warning("代理 OHLCV 加载失败，需 close/volume 的维度降级 0.0: %s", exc)
        if proxy_close is not None:
            try:
                proxy_high = proxy["high"].astype(float)
                proxy_low = proxy["low"].astype(float)
            except Exception as exc:  # noqa: BLE001
                _logger.warning("代理 high/low 缺失，s2_wyckoff 回退 MVP 简化版: %s", exc)
            try:
                proxy_open = proxy["open"].astype(float)
            except Exception as exc:  # noqa: BLE001
                _logger.warning("代理 open 缺失，capitulation/three_yang 降级: %s", exc)
            # P1-E9d：广度指数涨跌家数（breadth_thrust 源，默认 399106 深证综指）
            try:
                breadth_sym = getattr(self._feature_builder, "breadth_index", "399106")
                br = index_df.xs(breadth_sym, level="symbol")
                proxy_adv = br["advance_count"].astype(float)
                proxy_dec = br["decline_count"].astype(float)
            except Exception as exc:  # noqa: BLE001
                _logger.warning("广度指数涨跌家数缺失，S2 breadth_thrust 降级 0.0: %s", exc)

        # 限定到 [data_load_start, backtest_end]
        feat = features.loc[self.data_load_start : self.backtest_end]

        # 派生序列（reindex 到 feat.index 保证对齐）
        vol_pct = feat.get("realized_vol_pct")
        hurst = feat.get("hurst_dfa")
        slope = feat.get("kalman_slope")
        corr = feat.get("cross_asset_corr")
        ad_ratio_series = feat.get("ad_ratio")
        vol_z = feat.get("volume_anomaly")
        close = proxy_close.reindex(feat.index) if proxy_close is not None else None
        volume = proxy_volume.reindex(feat.index) if proxy_volume is not None else None
        pct_change = close.pct_change() if close is not None else None
        high = proxy_high.reindex(feat.index) if proxy_high is not None else None
        low = proxy_low.reindex(feat.index) if proxy_low is not None else None
        open_ = proxy_open.reindex(feat.index) if proxy_open is not None else None
        # P1-E9d：涨跌家数 reindex 后缺日填 0（与 RegimeFeatureBuilder._load_breadth 一致）
        adv = proxy_adv.reindex(feat.index).fillna(0.0) if proxy_adv is not None else None
        dec = proxy_dec.reindex(feat.index).fillna(0.0) if proxy_dec is not None else None

        # ── Phase 2c: 合成 VIX（vix_pct，优先于 vol_pct 注入 S1/S2）──
        vix_pct = self._compute_vix_pct(feat.index)

        # ── Phase 2c: 4 T3 维度输入（money_flow/sector/limit_up_down）──
        t3_inputs = self._compute_t3_inputs(feat.index)

        # 3. 各维度评分（仅可算维度，stub 不放入 cache → build_for_date 给 0.0）

        # ── S1: Any → CRISIS ──
        if vol_pct is not None:
            cache["vix_panic"] = overlay_features.s1_vix_panic_score(vol_pct, vix_pct)
        else:
            _logger.warning("S1 vix_panic 数据缺失（realized_vol_pct），降级 0.0")
        if corr is not None:
            cache["correlation"] = overlay_features.s1_correlation_score(corr)
        else:
            _logger.warning("S1 correlation 数据缺失（cross_asset_corr），降级 0.0")
        if vol_z is not None:
            cache["liquidity"] = overlay_features.s1_liquidity_score(vol_z)
        else:
            _logger.warning("S1 liquidity 数据缺失（volume_anomaly），降级 0.0")
        if pct_change is not None and vol_pct is not None:
            cache["flash_recover"] = overlay_features.s1_flash_recover_flag(pct_change, vol_pct)
        else:
            _logger.warning("S1 flash_recover 数据缺失，降级 0.0")

        # ── S2: CRISIS → RECOVERY ──
        # P1-E9a：衰减加权多过滤器版（需 OHLCV+open）；缺 OHLCV 回退瞬时两维版（治标 z>1）
        if (
            vol_z is not None
            and pct_change is not None
            and close is not None
            and high is not None
            and low is not None
            and volume is not None
            and open_ is not None
        ):
            # 期权 put/call + 新低占比（第 5/6 维）：Step 0 ④ 勘探无数据管道，默认关闭
            cache["capitulation"] = overlay_features.s2_capitulation_score(
                vol_z, pct_change, volume, high, low, open_, close
            )
        elif vol_z is not None and pct_change is not None:
            _logger.warning("S2 capitulation 缺 OHLCV/open，降级瞬时两维版（治标 z>1）")
            cache["capitulation"] = overlay_features.s2_capitulation_score(vol_z, pct_change)
        else:
            _logger.warning("S2 capitulation 数据缺失，降级 0.0")
        if vol_pct is not None:
            cache["vix"] = overlay_features.s2_vix_score(vol_pct, vix_pct)
        else:
            _logger.warning("S2 vix 数据缺失，降级 0.0")
        if close is not None:
            # Phase 2c：s2_wyckoff 委托 wyckoff_engine（需 high/low/volume/pct/vol_z）
            cache["wyckoff"] = overlay_features.s2_wyckoff_score(close, high, low, volume, pct_change, vol_z)
            # P1-E9b 路 B：阈值校准版（路 A CAPE 分位待 daily_valuation 管道，Step 0 ①）
            cache["valuation"] = overlay_features.s2_valuation_score(close)
            # P1-E9c：spring 深度分级版（需 high/low；缺失时函数内回退 close 简化版）
            cache["spring"] = overlay_features.s2_spring_flag(close, high, low, volume)
            cache["break_sc_low"] = overlay_features.s2_break_sc_low_flag(close)
        else:
            _logger.warning("S2 wyckoff/valuation/spring/break_sc_low 数据缺失，降级 0.0")
        if volume is not None:
            cache["fund"] = overlay_features.s2_fund_score(volume)
        else:
            _logger.warning("S2 fund 数据缺失，降级 0.0")
        # P1-E9e：three_yang 6 维分级版（需 OHLCV 五序列；缺失降级 0.0，不回退旧宽松版）
        if open_ is not None and high is not None and low is not None and close is not None and volume is not None:
            cache["three_yang"] = overlay_features.s2_three_yang_flag(open_, high, low, close, volume)
        else:
            _logger.warning("S2 three_yang 数据缺失（需 OHLCV），降级 0.0")
        # P1-E9d：breadth_thrust V 反转通路（需广度指数涨跌家数，confirm 析取维度）
        if adv is not None and dec is not None:
            cache["breadth_thrust"] = overlay_features.s2_breadth_thrust_score(adv, dec)
        else:
            _logger.warning("S2 breadth_thrust 涨跌家数数据缺失，降级 0.0")
        if vol_pct is not None:
            cache["vix_new_high"] = overlay_features.s2_vix_new_high_flag(vol_pct)
        else:
            _logger.warning("S2 vix_new_high 数据缺失，降级 0.0")
        if volume is not None and pct_change is not None:
            cache["fund_outflow"] = overlay_features.s2_fund_outflow_flag(volume, pct_change)
        else:
            _logger.warning("S2 fund_outflow 数据缺失，降级 0.0")
        # policy / bad_news_flat: P1-E3 MVP 关键词 NLP 情感分析
        news_sent = self._fb_call("get_news_sentiment")
        if news_sent is not None and not news_sent.empty:
            pol_count = news_sent["policy_count"].reindex(feat.index).fillna(0)
            pos_count = news_sent["positive_count"].reindex(feat.index).fillna(0)
            neg_count = news_sent["negative_count"].reindex(feat.index).fillna(0)
            cache["policy"] = overlay_features.s2_policy_score(pol_count, pos_count, neg_count)
            if pct_change is not None:
                cache["bad_news_flat"] = overlay_features.s2_bad_news_flat_score(neg_count, pct_change)
            else:
                _logger.warning("S2 bad_news_flat 数据缺失（pct_change），降级 0.0")
        else:
            _logger.warning("S2 policy/bad_news_flat 数据缺失（news_sentiment），降级 0.0")

        # ── T1: Neutral → BREAKOUT ──
        if close is not None and volume is not None:
            cache["bqs"] = overlay_features.t1_bqs_score(close, volume)
        else:
            _logger.warning("T1 bqs 数据缺失，降级 0.0")
        if slope is not None and hurst is not None:
            cache["rcs"] = overlay_features.t1_rcs_score(slope, hurst)
        else:
            _logger.warning("T1 rcs 数据缺失，降级 0.0")
        if vol_pct is not None and slope is not None:
            cache["frs"] = overlay_features.t1_frs_score(vol_pct, slope)
        else:
            _logger.warning("T1 frs 数据缺失，降级 0.0")

        # ── T2: Bear-Low → RECOVERY ──
        if slope is not None and vol_pct is not None:
            cache["continue_decline"] = overlay_features.t2_continue_decline_flag(slope, vol_pct)
        else:
            _logger.warning("T2 continue_decline 数据缺失，降级 0.0")

        # ── T3: RECOVERY → BREAKOUT ──
        if pct_change is not None and vol_z is not None:
            cache["volume_price"] = overlay_features.t3_volume_price_score(pct_change, vol_z)
        else:
            _logger.warning("T3 volume_price 数据缺失，降级 0.0")
        if close is not None:
            cache["ma_trend"] = overlay_features.t3_ma_trend_score(close)
        else:
            _logger.warning("T3 ma_trend 数据缺失，降级 0.0")
        if ad_ratio_series is not None:
            cache["sentiment"] = overlay_features.t3_sentiment_score(ad_ratio_series)
        else:
            _logger.warning("T3 sentiment 数据缺失，降级 0.0")

        # ── Phase 2c: 4 T3 资金/板块维度（原 stub，现接真实数据）──
        inflow_pct = t3_inputs.get("inflow_pct")
        lu_count = t3_inputs.get("limit_up_count")
        if inflow_pct is not None and lu_count is not None:
            cache["money_effect"] = overlay_features.t3_money_effect_score(inflow_pct, lu_count)
        else:
            _logger.warning("T3 money_effect 数据缺失（money_flow/limit_up_down），降级 0.0")
        sector_hhi = t3_inputs.get("sector_hhi")
        top_sector_pct = t3_inputs.get("top_sector_pct")
        if sector_hhi is not None and top_sector_pct is not None:
            cache["mainline"] = overlay_features.t3_mainline_score(sector_hhi, top_sector_pct)
        else:
            _logger.warning("T3 mainline 数据缺失（kline_sector），降级 0.0")
        max_consec = t3_inputs.get("max_consec_limit")
        promotion = t3_inputs.get("promotion_rate")
        if max_consec is not None and promotion is not None:
            cache["leader"] = overlay_features.t3_leader_score(max_consec, promotion)
        else:
            _logger.warning("T3 leader 数据缺失（limit_up_down），降级 0.0")
        prev_top3_max = t3_inputs.get("prev_top3_max_today_pct")
        if prev_top3_max is not None:
            cache["one_day_mainline"] = overlay_features.t3_one_day_mainline_flag(prev_top3_max)
        else:
            _logger.warning("T3 one_day_mainline 数据缺失（kline_sector），降级 0.0")

        # ── T4: Bull-Med → Bull-High ──
        if vol_pct is not None:
            cache["shrink_flat"] = overlay_features.t4_shrink_flat_flag(vol_pct)
        else:
            _logger.warning("T4 shrink_flat 数据缺失，降级 0.0")

        # ── T5: Bull-High → Bear-Med ──
        if close is not None and volume is not None:
            cache["leader_break"] = overlay_features.t5_leader_break_score(close, volume)
        else:
            _logger.warning("T5 leader_break 数据缺失，降级 0.0")
        if close is not None:
            cache["rebound_wrap"] = overlay_features.t5_rebound_wrap_flag(close)
        else:
            _logger.warning("T5 rebound_wrap 数据缺失，降级 0.0")

        # ── T6: Bear-Med → Bear-Low ──
        if vol_z is not None and pct_change is not None:
            cache["sudden_volume"] = overlay_features.t6_sudden_volume_flag(vol_z, pct_change)
        else:
            _logger.warning("T6 sudden_volume 数据缺失，降级 0.0")

        _logger.info(
            "OverlaySignalsConstructor._precompute: 可算维度 %d，policy/bad_news_flat=%s，vix_pct=%s，wyckoff=%s",
            len(cache),
            "NLP" if "policy" in cache else "stub(降级)",
            "synth" if vix_pct is not None else "vol_pct代理",
            "engine" if (high is not None and low is not None) else "MVP",
        )

        # 4. PIT 平移：所有维度 Series shift(1)，保证 build_for_date(dt) 取 ≤ dt-1
        for key in cache:
            cache[key] = cache[key].shift(1)

        self._cache = cache
        return cache

    # ── Phase 2c 数据加载辅助 ─────────────────────────────────────────────

    def _fb_call(self, method_name: str) -> Any:
        """安全调用 feature_builder 的数据透传方法，缺失/失败返回 None。

        兼容旧 mock（无新透传方法时 getattr 返回 None → 降级），保证测试隔离。
        """
        fn = getattr(self._feature_builder, method_name, None)
        if fn is None:
            return None
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — 降级友好
            _logger.warning("%s 调用失败，降级 None: %s", method_name, exc)
            return None

    def _compute_vix_pct(self, index: pd.DatetimeIndex) -> pd.Series | None:
        """Phase 2c: VIX 历史分位（vix_pct）—— 期权 IV 优先，合成 VIX 后备。

        优先路径：50ETF+300ETF 期权 IV 曲面 → CBOE 简化 VIX → 250 日分位。
        后备路径（P0）：期权数据缺失时，用**下行半偏差分位**（synthetic_vix_pct）
        作为 A 股恐慌代理——只计负收益的年化下行波动率，危机特异性强于总波动率。

        两路径均失败 → 返回 None → s1_vix_panic/s2_vix 回退 vol_pct（C1 不退化）。
        """
        # ── 优先路径：期权 IV 曲面 ──
        option_iv = self._fb_call("get_option_iv_surface")
        if option_iv is not None and not getattr(option_iv, "empty", True):
            try:
                from zephyr.regime.features.synthetic_vix import (
                    compute_synthetic_vix,
                    vix_pct_from_vix,
                )

                vix = compute_synthetic_vix(option_iv)
                vix_pct = vix_pct_from_vix(vix)
                if vix_pct is not None and not vix_pct.empty:
                    return vix_pct.reindex(index)
                _logger.warning("期权 IV → VIX 计算得空序列，回退合成 VIX")
            except Exception as exc:  # noqa: BLE001
                _logger.warning("期权 IV → VIX 计算失败，回退合成 VIX: %s", exc)

        # ── 后备路径：合成 VIX（下行半偏差分位，只依赖 close）──
        if self._feature_builder is None:
            _logger.debug("_compute_vix_pct: 无 feature_builder，返回 None")
            return None
        try:
            index_df = self._feature_builder.get_index_kline()
            proxy = index_df.xs(self.market_proxy, level="symbol")
            close = proxy["close"].astype(float)
            from zephyr.regime.features.synthetic_vix import synthetic_vix_pct

            vix = synthetic_vix_pct(close)
            non_na = int(vix.notna().sum())
            if non_na == 0:
                _logger.warning("合成 VIX 全 NaN（close 数据不足），返回 None")
                return None
            _logger.info(
                "Phase 2c: 合成 VIX (downside semi-dev pct) 已计算, %d 非 NaN",
                non_na,
            )
            return vix.reindex(index)
        except Exception as exc:  # noqa: BLE001 — 降级友好
            _logger.warning("合成 VIX 计算失败，回退 None（s1/s2 vix 用 vol_pct 代理）: %s", exc)
            return None

    def _compute_t3_inputs(self, index: pd.DatetimeIndex) -> dict[str, pd.Series | None]:
        """Phase 2c: 加载 money_flow/sector/limit_up_down/hk_connect_flow，算 4 T3 维度的 7 输入。

        北向资金（hk_connect_flow）作为主力净流入的辅助确认信号：
        z-score > 1 时加成 inflow_pct，z-score < -1 时削弱（P1-E5 融合）。
        任一数据源缺失 → 对应输入 None（维度降级 0.0，C1 不退化）。
        """
        inputs: dict[str, pd.Series | None] = {
            "inflow_pct": None,
            "limit_up_count": None,
            "sector_hhi": None,
            "top_sector_pct": None,
            "max_consec_limit": None,
            "promotion_rate": None,
            "prev_top3_max_today_pct": None,
        }
        # money_effect: 全市场主力净流入占比
        money_flow = self._fb_call("get_money_flow")
        if money_flow is not None and not money_flow.empty and "avg_main_net_inflow_pct" in money_flow:
            inputs["inflow_pct"] = money_flow["avg_main_net_inflow_pct"].reindex(index)
        # hk_connect_flow: 北向资金辅助（P1-E5 融合到 inflow_pct）
        hk_flow = self._fb_call("get_hk_connect_flow")
        if hk_flow is not None and not hk_flow.empty and "net_buy_amount" in hk_flow:
            hk_net = hk_flow["net_buy_amount"].reindex(index)
            # 20 日滚动 z-score（北向资金相对于自身近期的异常程度）
            hk_mean = hk_net.rolling(20, min_periods=5).mean()
            hk_std = hk_net.rolling(20, min_periods=5).std()
            hk_z = (hk_net - hk_mean) / hk_std.replace(0.0, np.nan)
            # z-score → 百分比调整：z=1 → +0.5pp，z=2 → +1.0pp，z=-1 → -0.5pp
            hk_adj = (hk_z.clip(-3, 3) * 0.5).fillna(0.0)
            if inputs["inflow_pct"] is not None:
                inputs["inflow_pct"] = inputs["inflow_pct"] + hk_adj
            else:
                # 主力资金缺失时，北向 z-score 单独作为弱代理
                inputs["inflow_pct"] = hk_adj
        # sector: mainline(HHI+top) + one_day_mainline(prev_top3)
        sector_df = self._fb_call("get_sector_kline")
        if sector_df is not None and not sector_df.empty:
            sector_inputs = self._compute_sector_metrics(sector_df, index)
            inputs["sector_hhi"] = sector_inputs.get("sector_hhi")
            inputs["top_sector_pct"] = sector_inputs.get("top_sector_pct")
            inputs["prev_top3_max_today_pct"] = sector_inputs.get("prev_top3_max_today_pct")
        # limit_up_down: leader(max_consec+promotion) + limit_up_count
        limit_df = self._fb_call("get_limit_up_down")
        if limit_df is not None and not limit_df.empty:
            lu_inputs = self._compute_limit_up_metrics(limit_df, index)
            inputs["max_consec_limit"] = lu_inputs.get("max_consec_limit")
            inputs["promotion_rate"] = lu_inputs.get("promotion_rate")
            inputs["limit_up_count"] = lu_inputs.get("limit_up_count")
        return inputs

    def _compute_sector_metrics(self, sector_df: pd.DataFrame, index: pd.Index) -> dict[str, pd.Series]:
        """从板块K线算 HHI / top_sector_pct / prev_top3_max_today_pct。

        HHI = Σ(share_i²)，share_i = |ret_i| / Σ|ret_j|（涨幅集中度）。
        top_sector_pct = 当日涨幅最高板块的涨幅（%）。
        prev_top3_max_today_pct = 昨日 Top3 板块今日最佳涨幅（%，全跌<-2 则证伪）。
        """
        try:
            close = sector_df["close"].unstack("code")
            pct = close.pct_change()
            abs_ret = pct.abs()
            total_abs = abs_ret.sum(axis=1).replace(0.0, np.nan)
            share = abs_ret.div(total_abs, axis=0)
            hhi = (share**2).sum(axis=1)
            top_pct = pct.max(axis=1) * 100  # 转百分数
            # 昨日 Top3 板块今日最佳表现（max < -2 ⟺ 三者全跌 >2%）
            ranks = pct.rank(axis=1, ascending=False, method="first")
            top3_mask = ranks <= 3
            prev_top3 = top3_mask.shift(1)
            masked = pct.where(prev_top3)
            prev_top3_max_today = masked.max(axis=1) * 100
            return {
                "sector_hhi": hhi.reindex(index),
                "top_sector_pct": top_pct.reindex(index),
                "prev_top3_max_today_pct": prev_top3_max_today.reindex(index),
            }
        except Exception as exc:  # noqa: BLE001
            _logger.warning("板块指标计算失败，降级 None: %s", exc)
            return {}

    def _compute_limit_up_metrics(self, limit_df: pd.DataFrame, index: pd.Index) -> dict[str, pd.Series]:
        """从涨跌停统计算 max_consec_limit / promotion_rate / limit_up_count。

        max_consec_limit = 全市场最高连板数（按 symbol 分组，非涨停重置 cumsum）。
        promotion_rate = 昨日涨停今日继续涨停比例（晋级率）。
        limit_up_count = 每日涨停家数。
        """
        try:
            df = limit_df.reset_index().copy()
            df["is_up"] = df["limit_type"].astype(str).str.contains("涨停").astype(int)
            df = df.sort_values(["symbol", "trade_date"])
            # 连板数：按 symbol 分组，遇到非涨停重置 run_group
            df["run_group"] = df.groupby("symbol")["is_up"].transform(lambda x: (x == 0).cumsum())
            df["consec"] = df.groupby(["symbol", "run_group"])["is_up"].cumsum()
            max_consec = df.groupby("trade_date")["consec"].max()
            lu_count = df.groupby("trade_date")["is_up"].sum()
            # 晋级率：昨日涨停今日继续涨停比例
            pivot = df.pivot(index="trade_date", columns="symbol", values="is_up").fillna(0)
            yesterday_up = pivot.shift(1)
            continued = (pivot == 1) & (yesterday_up == 1)
            yest_count = yesterday_up.sum(axis=1).replace(0, np.nan)
            promotion = (continued.sum(axis=1) / yest_count).fillna(0.0)
            return {
                "max_consec_limit": max_consec.reindex(index),
                "promotion_rate": promotion.reindex(index),
                "limit_up_count": lu_count.reindex(index),
            }
        except Exception as exc:  # noqa: BLE001
            _logger.warning("涨跌停指标计算失败，降级 None: %s", exc)
            return {}


__all__ = ["OverlaySignalsConstructor"]
