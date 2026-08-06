# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 D-SIGNAL-68 Phase2b
# [MODULE] zephyr.regime.overlay_signals_builder
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.regime.features.overlay_features; zephyr.regime.regime_feature_builder
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder.build_shrinkage_schedule消费→overlay_signals)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] score维度∈[0,100]; flag维度∈{0,1}; 无信号=0(平时不干预→纯HMM不退化); PIT严格(build_for_date(dt)只用≤dt-1,预计算shift(1)); 数据缺失→维度=0.0降级
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] —(数据缺失降级为0.0,不抛错)
# [TESTS] tests/regime/test_overlay_signals_builder.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #discussion_001 §4 #D-SIGNAL-68 #MOD-REGIME-002 #Phase2b #C1-shrinkage-comparator
"""OverlaySignals 构造器（MOD-REGIME-002 Phase 2b）。

把原始特征转换成 RegimeDetector._run_overlay 期望的 8 转换 overlay_signals 输入 dict：
    {"transitions": {"S1": {"vix_panic": 85.0, "correlation": 70.0, ...}, ...}}

8 转换（对齐 TRANSITION_CONFIG）:
    S1 Any→CRISIS（VIX Panic + Correlation + Liquidity）
    S2 CRISIS→RECOVERY（八维度见底：capitulation/vix/wyckoff/valuation/fund/spring/three_yang/...）
    T1 Neutral→BREAKOUT（bqs/rcs/frs）
    T2 Bear-Low→RECOVERY（冰点反核，total 评分）
    T3 RECOVERY→BREAKOUT（volume_price/ma_trend/sentiment + 资金/板块 stub）
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

31 个维度 key（对齐 TRANSITION_CONFIG 的 keys_gte，契约守护）:
  可算 25：vix_panic/correlation/liquidity/flash_recover（S1）
           capitulation/vix/wyckoff/valuation/fund/spring/three_yang/
           break_sc_low/vix_new_high/fund_outflow（S2）
           bqs/rcs/frs（T1）, continue_decline（T2）
           volume_price/ma_trend/sentiment（T3）, shrink_flat（T4）
           leader_break/rebound_wrap（T5）, sudden_volume（T6）
  stub 6（=0.0）：policy/bad_news_flat（S2, NLP）,
                  money_effect/mainline/leader/one_day_mainline（T3, 资金/板块）

stub 影响：S2 confirm/trigger（需 policy/bad_news_flat）+ T3 confirm/trigger/fail
（需 money_effect/mainline/leader/one_day_mainline）在 Phase 2b MVP 无法触发，
仅 S2 strong_confirm/fail + T3 strong_confirm 可触发——这是 MVP 预期范围，
S1/T1/T2/T4/T5/T6 全阶段可触发（覆盖 CRISIS/BREAKOUT/RECOVERY 三特殊态）。

依据: discussion_001 v1.3.1 §4 / Phase 2 计划 §Phase2b
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
        "capitulation", "vix", "wyckoff", "valuation", "fund",
        "spring", "three_yang", "break_sc_low", "vix_new_high", "fund_outflow",
        "policy", "bad_news_flat",  # stub（NLP）
    ],
    "T1": ["bqs", "rcs", "frs"],
    "T2": ["continue_decline"],
    "T3": [
        "volume_price", "ma_trend", "sentiment",
        "money_effect", "mainline", "leader", "one_day_mainline",  # stub（资金/板块）
    ],
    "T4": ["shrink_flat"],
    "T5": ["leader_break", "rebound_wrap"],
    "T6": ["sudden_volume"],
}

# stub 维度（不预计算，build_for_date 给 0.0）
_STUB_DIMS: set[str] = {
    "policy", "bad_news_flat",  # S2 NLP
    "money_effect", "mainline", "leader", "one_day_mainline",  # T3 资金/板块
}


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
      - stub 维度（policy/bad_news_flat/money_effect/...）：=0.0（待 NLP/资金管道）

    PIT: _precompute 末尾 shift(1)，build_for_date(dt) 取 loc[:dt].iloc[-1]（≤ dt-1）。
    降级: 任一数据源缺失 → 该维度=0.0（不触发），log WARN。
    """

    def __init__(
        self,
        backtest_start: str,
        backtest_end: str,
        data_load_start: str,
        feature_builder: "RegimeFeatureBuilder | None" = None,
        risk_constructor: "RiskSignalConstructor | None" = None,
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
            _logger.warning(
                "OverlaySignalsConstructor 无 feature_builder，所有维度=0.0（纯 HMM 降级）"
            )
            self._cache = cache
            return cache

        # 1. 复用 HMM 6 特征
        try:
            features = self._feature_builder.build_features()
        except Exception as exc:  # noqa: BLE001 — 降级友好
            _logger.warning("build_features 失败，Overlay 全降级（维度=0.0）: %s", exc)
            self._cache = cache
            return cache

        # 2. 复用代理 OHLCV（close/volume）
        proxy_close = proxy_volume = None
        try:
            index_df = self._feature_builder.get_index_kline()
            proxy = index_df.xs(self.market_proxy, level="symbol")
            proxy_close = proxy["close"].astype(float)
            proxy_volume = proxy["volume"].astype(float)
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "代理 OHLCV 加载失败，需 close/volume 的维度降级 0.0: %s", exc
            )

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

        # 3. 各维度评分（仅可算维度，stub 不放入 cache → build_for_date 给 0.0）

        # ── S1: Any → CRISIS ──
        if vol_pct is not None:
            cache["vix_panic"] = overlay_features.s1_vix_panic_score(vol_pct)
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
            cache["flash_recover"] = overlay_features.s1_flash_recover_flag(
                pct_change, vol_pct
            )
        else:
            _logger.warning("S1 flash_recover 数据缺失，降级 0.0")

        # ── S2: CRISIS → RECOVERY ──
        if vol_z is not None and pct_change is not None:
            cache["capitulation"] = overlay_features.s2_capitulation_score(
                vol_z, pct_change
            )
        else:
            _logger.warning("S2 capitulation 数据缺失，降级 0.0")
        if vol_pct is not None:
            cache["vix"] = overlay_features.s2_vix_score(vol_pct)
        else:
            _logger.warning("S2 vix 数据缺失，降级 0.0")
        if close is not None:
            cache["wyckoff"] = overlay_features.s2_wyckoff_score(close)
            cache["valuation"] = overlay_features.s2_valuation_score(close)
            cache["spring"] = overlay_features.s2_spring_flag(close)
            cache["break_sc_low"] = overlay_features.s2_break_sc_low_flag(close)
        else:
            _logger.warning("S2 wyckoff/valuation/spring/break_sc_low 数据缺失，降级 0.0")
        if volume is not None:
            cache["fund"] = overlay_features.s2_fund_score(volume)
        else:
            _logger.warning("S2 fund 数据缺失，降级 0.0")
        if pct_change is not None:
            cache["three_yang"] = overlay_features.s2_three_yang_flag(pct_change)
        else:
            _logger.warning("S2 three_yang 数据缺失，降级 0.0")
        if vol_pct is not None:
            cache["vix_new_high"] = overlay_features.s2_vix_new_high_flag(vol_pct)
        else:
            _logger.warning("S2 vix_new_high 数据缺失，降级 0.0")
        if volume is not None and pct_change is not None:
            cache["fund_outflow"] = overlay_features.s2_fund_outflow_flag(
                volume, pct_change
            )
        else:
            _logger.warning("S2 fund_outflow 数据缺失，降级 0.0")
        # policy / bad_news_flat: stub 0.0（NLP）

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
            cache["continue_decline"] = overlay_features.t2_continue_decline_flag(
                slope, vol_pct
            )
        else:
            _logger.warning("T2 continue_decline 数据缺失，降级 0.0")

        # ── T3: RECOVERY → BREAKOUT ──
        if pct_change is not None and vol_z is not None:
            cache["volume_price"] = overlay_features.t3_volume_price_score(
                pct_change, vol_z
            )
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
        # money_effect / mainline / leader / one_day_mainline: stub 0.0（资金/板块）

        # ── T4: Bull-Med → Bull-High ──
        if vol_pct is not None:
            cache["shrink_flat"] = overlay_features.t4_shrink_flat_flag(vol_pct)
        else:
            _logger.warning("T4 shrink_flat 数据缺失，降级 0.0")

        # ── T5: Bull-High → Bear-Med ──
        if close is not None and volume is not None:
            cache["leader_break"] = overlay_features.t5_leader_break_score(
                close, volume
            )
        else:
            _logger.warning("T5 leader_break 数据缺失，降级 0.0")
        if close is not None:
            cache["rebound_wrap"] = overlay_features.t5_rebound_wrap_flag(close)
        else:
            _logger.warning("T5 rebound_wrap 数据缺失，降级 0.0")

        # ── T6: Bear-Med → Bear-Low ──
        if vol_z is not None and pct_change is not None:
            cache["sudden_volume"] = overlay_features.t6_sudden_volume_flag(
                vol_z, pct_change
            )
        else:
            _logger.warning("T6 sudden_volume 数据缺失，降级 0.0")

        _logger.info(
            "OverlaySignalsConstructor._precompute: 可算维度 %d，"
            "stub(policy/bad_news_flat/money_effect/mainline/leader/one_day_mainline)=0.0",
            len(cache),
        )

        # 4. PIT 平移：所有维度 Series shift(1)，保证 build_for_date(dt) 取 ≤ dt-1
        for key in cache:
            cache[key] = cache[key].shift(1)

        self._cache = cache
        return cache


__all__ = ["OverlaySignalsConstructor"]
