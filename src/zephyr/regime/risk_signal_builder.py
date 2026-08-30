# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §5.3 Phase2a
# [MODULE] zephyr.regime.risk_signal_builder
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.regime.features.risk_features; zephyr.regime.regime_feature_builder
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder.build_shrinkage_schedule消费→risk_signal_inputs)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] params系数∈[0.30,1.00]; 无异常=1.0; PIT严格(build_for_date(dt)只用≤dt-1,预计算shift(1)); 数据缺失→参数=1.0降级
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —(数据缺失降级为1.0,不抛错)
# [TESTS] tests/regime/test_risk_signal_builder.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §5.3 #MOD-REGIME-002 #Phase2a #C1-shrinkage-comparator
"""
RiskSignalInputs 构造器（MOD-REGIME-002 Phase 2a）。

把原始特征转换成 RegimeDetector._compute_risk_signal 期望的 13 参数输入 dict：
    {"params": {1: coef, ..., 10: coef, 12: coef},  # 11 风险参数（#1-10,#12）
     "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0}}  # #11/#13 机会抵消

设计（Phase 2 计划 §架构决策）：
  - **预计算全序列 + 按 dt 切片**：__init__ 后首次 build_for_date 触发 _precompute，
    一次性向量化算出 11 系数 Series（已 shift(1)），后续 build_for_date(dt) 取
    loc[:dt].iloc[-1]（O(1)），walk-forward 2800+ 日 detect 不重复计算。
  - **复用 feature_builder**：接收 RegimeFeatureBuilder 引用，复用其 build_features()
    （HMM 6 特征）+ get_index_kline()（代理 OHLC），避免重复查 ClickHouse。
  - **降级友好**：任一参数数据缺失 → 该参数系数=1.0（保守不下调）+ log WARN，
    保证 risk_base 只因真实异常走低，不因数据空洞误杀。
  - **PIT 铁律**：_precompute 末尾对每个系数 Series shift(1)，build_for_date(dt)
    取 loc[:dt].iloc[-1] 即 ≤ dt-1 数据（与 RegimeFeatureBuilder.shift(1) 一致）。

Phase 2a MVP 参数范围（Phase 2 计划 §13参数数据来源）：
  有效（8）：#1 realized_vol / #2 volume_anomaly / #3 price_pattern / #5 space_position /
            #6 cross_asset_corr / #7 ad_ratio_extreme / #9 tech_divergence / #10 trend_slope_decay
  stub（3）：#4 time_incubation=1.0（主观无数据）/ #8 siphon=1.0（待接 sector+money_flow）/
            #12 chip_structure=1.0（chip 引擎按日成本高，Phase 2c 接）
  opportunity stub（2）：#11 news_ghost=0.0 / #13 bad_news_flat=0.0（待 NLP）

依据: 10_regime_detector_spec v1.3.1 §5.3.3 / Phase 2 计划 §Phase2a
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: backtest_start 参数
#   fields: 参数 backtest_start（无注解）
#   code: risk_signal_builder.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: backtest_end 参数
#   fields: 参数 backtest_end（无注解）
#   code: risk_signal_builder.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: data_load_start 参数
#   fields: 参数 data_load_start（无注解）
#   code: risk_signal_builder.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: feature_builder 参数
#   fields: 参数 feature_builder（无注解）
#   code: risk_signal_builder.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RiskSignalConstructor
#   name_en: RiskSignalConstructor
#   intro: 13 参数 RiskSignalInputs 构造器（MOD-REGIME-002 Phase 2a）。
#   desc: 13 参数 RiskSignalInputs 构造器（MOD-REGIME-002 Phase 2a）。 Usage（由 RegimeFeatureBuilder.build_s…；公共方法（定义序）: build_f…
#   inputs: backtest_start backtest_end data_load_start feature_builder market_pr…
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RiskSignalConstructor
#   downstream: MOD-REGIME-002(RegimeFeatureBuilder.build_shrinkage_schedule消费→risk_signal_inpu…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from zephyr.regime.features import risk_features

if TYPE_CHECKING:  # 避免循环 import
    from zephyr.regime.regime_feature_builder import RegimeFeatureBuilder

_logger = logging.getLogger(__name__)

# 11 个风险参数 id（#1-10, #12；#11/#13 属 opportunity）
_RISK_PARAM_IDS: list[int] = list(range(1, 11)) + [12]
# Phase 2a 有效计算的参数 id（其余 stub=1.0）
# Phase 2c：#8 siphon 从 stub 升级为有效（接 sector_kline）
_ACTIVE_PARAMS: set[int] = {1, 2, 3, 5, 6, 7, 8, 9, 10}


class RiskSignalConstructor:
    """13 参数 RiskSignalInputs 构造器（MOD-REGIME-002 Phase 2a）。

    Usage（由 RegimeFeatureBuilder.build_shrinkage_schedule 内部调用）::

        ctor = RiskSignalConstructor(
            backtest_start="2015-01-01", backtest_end="2026-06-30",
            data_load_start="2010-01-01",
            feature_builder=builder,  # 复用已加载的 HMM 6 特征 + index_df
        )
        risk_inputs = ctor.build_for_date(dt)  # → {"params": {...}, "opportunity": {...}}

    数据源（经 feature_builder 复用 / TableRegistry）:
      - feature_builder.build_features() → HMM 6 特征（#1/#2/#6/#7/#10 复用）
      - feature_builder.get_index_kline() → 代理 OHLC（#3/#5/#9 新算）
      - #8 siphon：Phase 2c 接 sector_kline（涨幅 HHI 集中度）
      - #9 多分时共振：Phase 2c 接 multi_tf_kline（60min/30min KDJ 背离）
      - #12 chip：stub=1.0（chip 引擎按日成本高，后续接）

    PIT: _precompute 末尾 shift(1)，build_for_date(dt) 取 loc[:dt].iloc[-1]（≤ dt-1）。
    降级: 任一数据源缺失 → 该参数系数=1.0（保守不下调），log WARN。
    """

    def __init__(
        self,
        backtest_start: str,
        backtest_end: str,
        data_load_start: str,
        feature_builder: RegimeFeatureBuilder | None = None,
        market_proxy: str = "000300",
    ) -> None:
        """初始化。

        Args:
            backtest_start: 回测起始日（含，限定系数序列范围）。
            backtest_end: 回测结束日（含）。
            data_load_start: 数据加载起始日（需早于 backtest_start，供 warmup）。
            feature_builder: RegimeFeatureBuilder 引用（复用 6 特征 + index_df）。
                None 时无法计算（所有参数降级 1.0）。
            market_proxy: 市场代理指数代码（OHLC 源）。
        """
        self.backtest_start = backtest_start
        self.backtest_end = backtest_end
        self.data_load_start = data_load_start
        self.market_proxy = market_proxy
        self._feature_builder = feature_builder
        self._cache: dict[int, pd.Series] | None = None  # {param_id: coef_series(已shift)}

    # ── 公共接口 ──────────────────────────────────────────────────────────

    def build_for_date(self, dt: pd.Timestamp) -> dict[str, Any]:
        """取 dt 时点的 13 参数快照（PIT：只用 ≤ dt-1）。

        Args:
            dt: 查询时点（pd.Timestamp）。

        Returns:
            {"params": {1: float, ..., 10: float, 12: float},
             "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0}}
            缺失数据参数=1.0，opportunity stub=0.0。
        """
        cache = self._precompute()
        params: dict[int, float] = {}
        for pid in _RISK_PARAM_IDS:
            series = cache.get(pid)
            if series is None or series.empty:
                params[pid] = 1.0
                continue
            sub = series.loc[:dt]
            if sub.empty:
                params[pid] = 1.0
                continue
            val = sub.iloc[-1]
            params[pid] = float(val) if not np.isnan(val) else 1.0
        # Phase 2a opportunity stub（#11/#13 待 NLP）
        opportunity = {"news_ghost": 0.0, "bad_news_flat": 0.0}
        return {"params": params, "opportunity": opportunity}

    # ── 预计算 ────────────────────────────────────────────────────────────

    def _precompute(self) -> dict[int, pd.Series]:
        """一次性加载特征 + 向量化计算 11 系数 Series（已 shift(1)）。

        Returns:
            {param_id: pd.Series}，每个 Series 已 shift(1)（PIT）。
            数据缺失的参数不放入 cache（build_for_date 走 1.0 降级）。
        """
        if self._cache is not None:
            return self._cache

        cache: dict[int, pd.Series] = {}

        # 无 feature_builder → 全降级 1.0
        if self._feature_builder is None:
            _logger.warning("RiskSignalConstructor 无 feature_builder，所有参数降级 1.0")
            self._cache = cache
            return cache

        # 1. 复用 HMM 6 特征
        try:
            features = self._feature_builder.build_features()
        except Exception as exc:  # noqa: BLE001 — 降级友好
            _logger.warning("build_features 失败，RiskSignal 全降级 1.0: %s", exc)
            self._cache = cache
            return cache

        # 2. 复用代理 OHLC（#2/#3/#5/#9 用）
        # C1 验证 2026-08-06 修正：close 与 high/low 分离加载，避免 high 缺失连累 close
        # （index_kline 表可能无 high/low 列，但 close 一定有——原代码 try 块在 proxy["high"]
        # 抛 KeyError 时连 proxy_close 一起置 None，致 #2/#3/#5 全部误降级 1.0）
        proxy_close = proxy_high = proxy_low = None
        try:
            index_df = self._feature_builder.get_index_kline()
            proxy = index_df.xs(self.market_proxy, level="symbol")
            proxy_close = proxy["close"].astype(float)
        except Exception as exc:  # noqa: BLE001
            _logger.warning("代理 close 加载失败，#2/#3/#5/#9 降级 1.0: %s", exc)
        if proxy_close is not None:
            try:
                proxy_high = proxy["high"].astype(float)
                proxy_low = proxy["low"].astype(float)
            except Exception as exc:  # noqa: BLE001
                _logger.warning("代理 high/low 缺失，#9 KDJ 降级 1.0（#3/#5 仅用 close 不受影响）: %s", exc)

        # 限定到 [data_load_start, backtest_end]
        feat = features.loc[self.data_load_start : self.backtest_end]

        # 3. 各参数系数（仅有效参数，stub 参数不放入 cache → build_for_date 给 1.0）
        # #1 realized_vol（vol_pct + slope 交集，复刻 Phase 1 危机地板）
        if {"realized_vol_pct", "kalman_slope"}.issubset(feat.columns):
            cache[1] = risk_features.realized_vol_coef(feat["realized_vol_pct"], feat["kalman_slope"])
        else:
            _logger.warning("参数 #1 数据缺失（realized_vol_pct/kalman_slope），降级 1.0")

        # #2 volume_anomaly（F5 z-score + 日涨跌幅）
        if "volume_anomaly" in feat.columns and proxy_close is not None:
            pct_change = proxy_close.reindex(feat.index).pct_change()
            cache[2] = risk_features.volume_anomaly_coef(feat["volume_anomaly"], pct_change)
        else:
            _logger.warning("参数 #2 数据缺失，降级 1.0")

        # #3 price_pattern（MA5/20/60 + 破前低）
        if proxy_close is not None:
            cache[3] = risk_features.price_pattern_coef(proxy_close.reindex(feat.index))
        else:
            _logger.warning("参数 #3 数据缺失，降级 1.0")

        # #5 space_position（close vs 250日高点）
        if proxy_close is not None:
            cache[5] = risk_features.space_position_coef(proxy_close.reindex(feat.index))
        else:
            _logger.warning("参数 #5 数据缺失，降级 1.0")

        # #6 cross_asset_corr（F3）
        if "cross_asset_corr" in feat.columns:
            cache[6] = risk_features.cross_asset_corr_coef(feat["cross_asset_corr"])
        else:
            _logger.warning("参数 #6 数据缺失，降级 1.0")

        # #7 ad_ratio_extreme（F4）
        if "ad_ratio" in feat.columns:
            cache[7] = risk_features.ad_ratio_extreme_coef(feat["ad_ratio"])
        else:
            _logger.warning("参数 #7 数据缺失，降级 1.0")

        # #9 tech_divergence（KDJ J 值顶背离 + Phase 2c 多分时共振）
        if proxy_high is not None and proxy_low is not None and proxy_close is not None:
            h = proxy_high.reindex(feat.index)
            l = proxy_low.reindex(feat.index)
            c = proxy_close.reindex(feat.index)
            _k, _d, j = risk_features.kdj(h, l, c)
            div = risk_features.detect_top_divergence(c, j)
            # Phase 2c：60min/30min 顶背离共振（数据缺失降级单分时 0.92）
            div_60, div_30 = self._compute_multi_tf_divergence(feat.index)
            cache[9] = risk_features.tech_divergence_coef(div, div_60, div_30)
        else:
            _logger.warning("参数 #9 数据缺失，降级 1.0")

        # #10 trend_slope_decay（F2b slope z-score + F2a hurst）
        if "kalman_slope" in feat.columns:
            hurst = feat.get("hurst_dfa")
            cache[10] = risk_features.trend_slope_decay_coef(feat["kalman_slope"], hurst)
        else:
            _logger.warning("参数 #10 数据缺失，降级 1.0")

        # #8 siphon（Phase 2c：板块涨幅 HHI 集中度 → 虹吸态系数）
        sector_hhi, fund_conc = self._compute_siphon_inputs(feat.index)
        if sector_hhi is not None:
            cache[8] = risk_features.siphon_coef(sector_hhi, fund_conc)
        else:
            _logger.warning("参数 #8 数据缺失（sector_kline），降级 1.0")

        # #4/#12：stub=1.0（不放入 cache，build_for_date 给 1.0）
        _logger.info(
            "RiskSignalConstructor._precompute: 有效参数 %s，stub(#4/#12)=1.0",
            sorted(k for k in cache.keys()),
        )

        # 4. PIT 平移：所有系数 Series shift(1)，保证 build_for_date(dt) 取 ≤ dt-1
        for pid in cache:
            cache[pid] = cache[pid].shift(1)

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

    def _compute_siphon_inputs(self, index: pd.Index) -> tuple[pd.Series | None, pd.Series | None]:
        """Phase 2c: #8 siphon 输入（板块涨幅 HHI + 资金集中度）。

        sector_hhi：从 kline_sector 算板块涨幅 HHI（集中度），越高越虹吸。
        fund_concentration：头部资金净流入占比（需 per-sector money_flow，
            当前 loader 仅全市场聚合 → 暂返回 None，siphon_coef 按仅 hhi 降级，
            OR 语义保证部分数据仍有效）。
        """
        sector_df = self._fb_call("get_sector_kline")
        if sector_df is None or sector_df.empty:
            return None, None
        try:
            close = sector_df["close"].unstack("code")
            pct = close.pct_change()
            abs_ret = pct.abs()
            total_abs = abs_ret.sum(axis=1).replace(0.0, np.nan)
            share = abs_ret.div(total_abs, axis=0)
            hhi = (share**2).sum(axis=1)
            return hhi.reindex(index), None  # fund_concentration 待 per-sector money_flow
        except Exception as exc:  # noqa: BLE001
            _logger.warning("siphon 输入计算失败，#8 降级 1.0: %s", exc)
            return None, None

    def _compute_multi_tf_divergence(self, index: pd.Index) -> tuple[pd.Series | None, pd.Series | None]:
        """Phase 2c: #9 多分时顶背离（60min + 30min）。

        对每个频率的 ETF K 线聚合到日线（每日 max high / min low / last close），
        算 KDJ J 值顶背离。数据缺失返回 (None, None) → tech_divergence_coef 降级单分时。
        """
        multi_tf = self._fb_call("get_multi_tf_kline")
        if multi_tf is None:
            return None, None
        div_60 = self._divergence_for_freq(multi_tf.get("60min"), index)
        div_30 = self._divergence_for_freq(multi_tf.get("30min"), index)
        return div_60, div_30

    def _divergence_for_freq(self, df: pd.DataFrame | None, index: pd.Index) -> pd.Series | None:
        """单频率 KDJ 顶背离（聚合到日线后计算）。"""
        if df is None or df.empty:
            return None
        try:
            # 聚合到日线（分钟级表可能一日多 bar，取每日 max high / min low / last close）
            daily = df.groupby(level=df.index.name).agg({"high": "max", "low": "min", "close": "last"})
            daily = daily.reindex(index)
            h, l, c = daily["high"], daily["low"], daily["close"]
            _k, _d, j = risk_features.kdj(h, l, c)
            return risk_features.detect_top_divergence(c, j)
        except Exception as exc:  # noqa: BLE001
            _logger.warning("多分时背离计算失败，降级单分时: %s", exc)
            return None


__all__ = ["RiskSignalConstructor"]
