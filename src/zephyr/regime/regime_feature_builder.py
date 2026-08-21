# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [MODULE] zephyr.regime.regime_feature_builder
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.regime.features.trend_features; zephyr.regime.features.market_features; zephyr.regime.core.regime_detector; zephyr.regime.cross_sectional_features
# [CONSUMERS] scripts/tests/run_c1_shrinkage_validation.py(real模式); BM-BT-03-E(回测验证)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] HMM 6特征X矩阵(T,6)列序钉死; PIT严格(detect(t)只用≤t-1数据); walk-forward季度重拟合训练/测试无重叠; ClickHouse不可用抛RegimeFeatureError
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegimeFeatureError(ZA-REGIME-0010)
# [TESTS] tests/regime/test_regime_feature_builder.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §3 #11_regime_backtest_validation_plan §4.5 #MOD-REGIME-001 #C1-shrinkage-comparator

"""MOD-REGIME-002 RegimeFeatureBuilder — Regime 特征管道编排器。

把 ClickHouse 多源数据转换成 RegimeDetector.detect() 的三参输入，是 regime 链的
"数据入口"（ClickHouse → 特征 → 检测器 → Shrinkage → budget）。

Phase 1 范围（11_regime_backtest_validation_plan §6）：
  - HMM 6 特征 + X 矩阵（本模块）→ 真实 HMM fit/detect
  - overlay_signals / risk_signal_inputs 暂用空 dict（regime_detector 降级为
    纯 HMM ConfidenceSignal 节流）—— 这是 C1 一票否决的核心假设验证
  - 后续 Phase 补 overlay（8转换评分）+ risk（13参数）→ 完整 Shrinkage

HMM 6 特征（blueprint §3，X 矩阵列序钉死）：
  F1 realized_vol_pct  — 20日HV的250日分位（market_features）
  F2a hurst_dfa        — DFA法Hurst指数（trend_features）
  F2b kalman_slope     — Kalman自适应斜率（trend_features）
  F3 cross_asset_corr  — 三大指数两两相关均值60日（market_features）
  F4 ad_ratio          — 全市场涨跌家数比tanh归一化（market_features，399106深证综指）
  F5 volume_anomaly    — 成交量z-score 20日（market_features）

walk-forward（blueprint §7）：季度重拟合，滚动5年训练，季度内同一 HMM 推断。
PIT 铁律（blueprint §6.1）：detect(t) 用 ≤ t-1 的特征（features.shift(1)），
禁止未来信息泄漏——C1 一票否决的前提。

ALG-01 横截面结构特征开关（2026-08 架构审查 P1，默认关）：
  enable_cross_sectional=True 时把 MOD-REGIME-007 的 4 列横截面结构特征
  （cross_dispersion/avg_pairwise_corr/vol_dispersion/momentum_breadth）并入
  特征 DataFrame **尾部**——既有 6 列列序零破坏（FEATURE_NAMES 不增不改），
  X 矩阵列序 = FEATURE_NAMES + 4 新列；默认 False 时输出与历史逐字节一致
  （A/B 对照纪律：开关即实验臂，先证增量再谈转正）。

依据: 10_regime_detector_spec v1.3.1 §3 / 11_regime_backtest_validation_plan v1.0.0 §4.5/§6
SSoT: depgraph MOD-REGIME-002
Version: 0.1.0
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.regime.cross_sectional_features import (
    CROSS_SECTIONAL_FEATURE_NAMES,
    compute_cross_sectional_features,
)
from zephyr.regime.features.market_features import (
    ad_ratio,
    cross_asset_corr,
    realized_vol_pct,
    volume_anomaly,
)
from zephyr.regime.features.regime_data_loader import parse_tsv, safe_float
from zephyr.regime.features.trend_features import hurst_dfa, kalman_slope

try:
    from sklearn.preprocessing import RobustScaler
except ImportError:  # pragma: no cover
    RobustScaler = None  # type: ignore[assignment,misc]

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class RegimeFeatureError(ZephyrBaseError):
    """ZA-REGIME-0010: Regime 特征管道错误（ClickHouse 不可用/数据缺失/特征异常）。"""

    error_code = "ZA-REGIME-0010"


# X 矩阵列序钉死（blueprint §3，detect 消费方按此序读 X）
FEATURE_NAMES: list[str] = [
    "realized_vol_pct",
    "hurst_dfa",
    "kalman_slope",
    "cross_asset_corr",
    "ad_ratio",
    "volume_anomaly",
]

# 市场代理指数（沪深300，F1/F2a/F2b/F5 的 close/volume 源）
MARKET_PROXY = "000300"
# 跨资产相关性指数（F3，沪深300/中证500/创业板指）
CROSS_ASSET_INDICES = ["000300", "000905", "399006"]
# 涨跌家数源（F4，深证综指 399106，advance_count/decline_count）
BREADTH_INDEX = "399106"


# ──────────────────────────────────────────────────────────────────────────────
# RegimeFeatureBuilder
# ──────────────────────────────────────────────────────────────────────────────


class RegimeFeatureBuilder:
    """Regime 特征管道编排器（MOD-REGIME-002）。

    Usage（C1 real 模式）:
        builder = RegimeFeatureBuilder(
            backtest_start="2015-01-01", backtest_end="2026-06-30"
        )
        features = builder.build_features()              # 6 特征 DataFrame
        detector = RegimeDetector(shrinkage_enabled=True)
        schedule = builder.build_shrinkage_schedule(detector)  # {date: shrinkage}
        provider = ScheduleShrinkageProvider(schedule)

    数据源（ClickHouse，经 TableRegistry 取表名）:
      - c1_market.kline_index（000300/000905/399006/399106）
      - F1/F2/F3/F5 用指数 close/volume；F4 用 399106 advance/decline_count

    PIT 铁律：build_shrinkage_schedule 用 features.shift(1) 推断，
    detect(t) 只见 ≤ t-1 数据（blueprint §6.1）。
    """

    def __init__(
        self,
        backtest_start: str = "2015-01-01",
        backtest_end: str = "2026-06-30",
        data_load_start: str = "2010-01-01",
        market_proxy: str = MARKET_PROXY,
        cross_asset_indices: list[str] | None = None,
        breadth_index: str = BREADTH_INDEX,
        shrinkage_ema_alpha: float | None = 0.15,
        standardize_features: bool = True,
        enable_full_risk: bool = False,
        enable_overlay: bool = False,
        enable_phase2c: bool = False,
        enable_cross_sectional: bool = False,
        cross_sectional_panel: pd.DataFrame | None = None,
        cross_sectional_top_n: int = 800,
        data_loader: Any = None,
    ) -> None:
        """初始化。

        Args:
            backtest_start: 回测/detect 起始日（含）。
            backtest_end: 回测/detect 结束日（含）。
            data_load_start: 数据加载起始日（需早于 backtest_start 至少 train_years+max_warmup，
                用于 walk-forward 训练历史 + 250日 warmup）。
            market_proxy: 市场代理指数代码（F1/F2/F5 源）。
            cross_asset_indices: 跨资产相关性指数列表（F3 源）。
            breadth_index: 涨跌家数指数代码（F4 源）。
            shrinkage_ema_alpha: Shrinkage 离线 EMA 平滑系数（None=不平滑）。
                α=0.15 半衰期约 4 天，抑制四档硬映射在阈值边界的跳变导致的 Turnover 激增。
                PIT 满足（只用 t 及之前数据），值仍∈[0,1]（凸组合），只减不增不变量保持。
            standardize_features: 是否对 HMM 输入特征做 RobustScaler 标准化。
                6 特征量纲差异巨大（vol_pct∈[0,1] vs kalman_slope~1e-3 vs volume_anomaly z-score），
                未标准化致高斯 HMM 协方差矩阵奇异、状态概率抖动。walk-forward 每季度用
                训练窗口 fit scaler，detect 时 transform（PIT：scaler 只见训练数据）。
            enable_full_risk: Phase 2a 开关。True=用 RiskSignalConstructor 产 13 参数
                risk_signal_inputs；False=回退 Phase 1 简化版 _build_feature_risk（1参数 #1）。
                默认 False（C1 回归保护）。生产推荐 True（#ARCH-REGIME-RISK-FULL-001 C1
                验证不退化，#1 门控保证非危机日 ≈ Phase 1）；C1 验证脚本已默认 full。
            enable_overlay: Phase 2b 开关。True=用 OverlaySignalsConstructor 产 8 转换
                overlay_signals；False=overlay_signals={}（纯 HMM）。默认 False。
            enable_phase2c: Phase 2c 开关。True=启用 4 T3 stub 维度 + #8 siphon + 合成VIX +
                多分时共振（需配合 data_loader）；False=Phase 2b 行为（stub=0/1.0）。默认 False。
            data_loader: RegimeDataLoader 实例（Phase 2c 新数据源加载层）。
                None 时 Phase 2c 新维度全降级（0.0/1.0），保持 Phase 2b 行为。
            enable_cross_sectional: ALG-01 横截面结构特征开关（默认 False，
                A/B 对照纪律）。True=把 MOD-REGIME-007 的 4 列横截面结构特征
                并入特征 DataFrame 尾部（既有 6 列列序零破坏，X=(T,10)）；
                False=输出与历史逐字节一致（X=(T,6)）。
            cross_sectional_panel: 预加载个股日 K 面板（长表 trade_date/symbol/
                close/volume/amount，测试/离线注入用）。None 且开关开时经
                _load_stock_panel 从 ClickHouse kline_daily 惰性加载。
            cross_sectional_top_n: 面板加载的每日流动性 top N（默认 800，
                控制 TSV 体积；横截面抽样在其内再分层抽 ~200）。
        """
        self.backtest_start = backtest_start
        self.backtest_end = backtest_end
        self.data_load_start = data_load_start
        self.market_proxy = market_proxy
        self.cross_asset_indices = cross_asset_indices or list(CROSS_ASSET_INDICES)
        self.breadth_index = breadth_index
        self.shrinkage_ema_alpha = shrinkage_ema_alpha
        self.standardize_features = standardize_features and RobustScaler is not None
        if standardize_features and RobustScaler is None:
            _logger.warning("sklearn 不可用，特征标准化关闭（HMM 拟合质量可能下降）")
        self.enable_full_risk = enable_full_risk
        self.enable_overlay = enable_overlay
        self.enable_phase2c = enable_phase2c
        self.enable_cross_sectional = enable_cross_sectional
        self._cs_panel = cross_sectional_panel  # 预注入个股面板（None=惰性 CH 加载）
        self._cs_top_n = cross_sectional_top_n
        self._cs_features_cache: pd.DataFrame | None = None  # 横截面 4 列缓存
        self._features_cache: pd.DataFrame | None = None
        self._index_df_cache: pd.DataFrame | None = None  # 代理 OHLC 缓存（供 risk/overlay 构造器复用）
        self._risk_ctor: Any = None  # RiskSignalConstructor（惰性构造）
        self._overlay_ctor: Any = None  # OverlaySignalsConstructor（惰性构造，Phase 2b）
        self._registry = get_registry()
        self._data_loader = data_loader  # Phase 2c 数据加载层（None 时新维度全降级）

    # ── 公共接口 ──────────────────────────────────────────────────────────

    def build_features(self) -> pd.DataFrame:
        """计算 HMM 6 特征，返回 DataFrame（index=trade_date, columns=FEATURE_NAMES）。

        Returns:
            pd.DataFrame，列序 = FEATURE_NAMES，index 为 pd.Timestamp（交易日）。
            warmup 期（前 ~250+200 日）含 NaN，由 walk-forward 训练时 dropna 处理。
            enable_cross_sectional=True 时列序 = FEATURE_NAMES + 横截面 4 列
            （尾部追加，既有 6 列列序零破坏）；默认 False 时输出与历史逐字节一致。
        """
        if self._features_cache is not None:
            return self._features_cache

        index_df = self.get_index_kline()

        # 市场代理 close/volume
        proxy = index_df.xs(self.market_proxy, level="symbol")
        proxy_close = proxy["close"].astype(float)
        proxy_volume = proxy["volume"].astype(float)

        # F1 实现波动率分位
        f1 = realized_vol_pct(proxy_close)
        # F5 量能异动
        f5 = volume_anomaly(proxy_volume)

        # F2a Hurst / F2b Kalman（滚动窗口，单值函数 → rolling apply）
        f2a = self._rolling_apply(proxy_close, hurst_dfa, window=200)
        f2b = self._rolling_apply(proxy_close, kalman_slope, window=200)

        # F3 跨资产相关性（多指数收益率）
        cross_close = self._unstack_close(index_df, self.cross_asset_indices)
        cross_returns = np.log(cross_close / cross_close.shift(1))
        f3 = cross_asset_corr(cross_returns, window=60)

        # F4 涨跌家数比（399106 adv/dec）
        adv, dec = self._load_breadth(index_df)
        f4 = ad_ratio(adv, dec)

        features = pd.DataFrame(
            {
                "realized_vol_pct": f1,
                "hurst_dfa": f2a,
                "kalman_slope": f2b,
                "cross_asset_corr": f3,
                "ad_ratio": f4,
                "volume_anomaly": f5,
            }
        )
        # 限定到 [data_load_start, backtest_end]
        features = features.loc[self.data_load_start : self.backtest_end]
        features = features.sort_index()
        # ALG-01 横截面结构特征（可选开关，默认关；尾部追加，6 列列序零破坏）
        if self.enable_cross_sectional:
            cs = self._build_cross_sectional_features()
            features = pd.concat([features, cs.reindex(features.index)], axis=1)
        self._features_cache = features
        _logger.info(
            "RegimeFeatureBuilder.build_features: %d 行 × %d 特征，区间 [%s, %s]",
            len(features),
            features.shape[1],
            features.index.min(),
            features.index.max(),
        )
        return features

    def active_feature_names(self) -> list[str]:
        """当前生效的 X 矩阵特征列序。

        开关关 = FEATURE_NAMES 原样（(T,6)，与历史一致）；开关开 =
        FEATURE_NAMES + 横截面 4 列（(T,10)，尾部追加）。
        """
        if self.enable_cross_sectional:
            return list(FEATURE_NAMES) + list(CROSS_SECTIONAL_FEATURE_NAMES)
        return list(FEATURE_NAMES)

    def get_index_kline(self) -> pd.DataFrame:
        """加载并缓存指数 K 线（市场代理 + 跨资产 + 广度指数）。

        供 build_features + RiskSignalConstructor/OverlaySignalsConstructor 复用，
        避免每个构造器重复查 ClickHouse。首次调用加载，后续返回缓存。

        Returns:
            MultiIndex(symbol, trade_date) DataFrame，含 close/volume/advance_count/decline_count。
        """
        if self._index_df_cache is not None:
            return self._index_df_cache
        idx_table = self._registry.table("market_index_kline")
        self._index_df_cache = self._load_index_kline(idx_table)
        return self._index_df_cache

    # ── Phase 2c 数据透传（委托 RegimeDataLoader，None 时降级）────────────

    def get_money_flow(self) -> pd.DataFrame | None:
        """Phase 2c: 全市场主力资金净流入（供 money_effect 维度）。None=降级。"""
        return self._data_loader.load_money_flow() if self._data_loader is not None else None

    def get_sector_kline(self) -> pd.DataFrame | None:
        """Phase 2c: 行业板块K线（供 mainline 维度 + #8 sector_hhi）。None=降级。"""
        return self._data_loader.load_sector_kline() if self._data_loader is not None else None

    def get_limit_up_down(self) -> pd.DataFrame | None:
        """Phase 2c: 涨跌停统计（供 leader/one_day_mainline 维度）。None=降级。"""
        return self._data_loader.load_limit_up_down() if self._data_loader is not None else None

    def get_hk_connect_flow(self) -> pd.DataFrame | None:
        """Phase 2c: 北向资金（供 money_effect 辅助）。None=降级。"""
        return self._data_loader.load_hk_connect_flow() if self._data_loader is not None else None

    def get_option_iv_surface(self) -> pd.DataFrame | None:
        """Phase 2c: 50ETF+300ETF 期权IV曲面（供合成VIX）。None=降级回退 vol_pct。"""
        return self._data_loader.load_option_iv_surface() if self._data_loader is not None else None

    def get_multi_tf_kline(self) -> dict[str, pd.DataFrame] | None:
        """Phase 2c: 多分时 ETF K线（供 #9 多分时共振）。None=降级单分时。"""
        return self._data_loader.load_multi_tf_kline() if self._data_loader is not None else None

    def get_news_sentiment(self) -> pd.DataFrame | None:
        """P1-E3: 新闻情感聚合（供 S2 policy/bad_news_flat 维度）。None=降级。"""
        return self._data_loader.load_news_sentiment() if self._data_loader is not None else None

    def build_train_matrix(self, start: str, end: str) -> dict[str, Any]:
        """构造 HMM 训练矩阵（walk-forward 季度重拟合用）。

        Args:
            start: 训练起始日（含）。
            end: 训练结束日（含）。

        Returns:
            {"X": np.ndarray (T, n_features), "lengths": None}，
            n_features = 6（开关关）/ 10（ALG-01 开关开，尾部追加横截面 4 列）。
            NaN 行 dropna（warmup 期），保证 HMM 拟合无 NaN。
        """
        features = self.build_features()
        sub = features.loc[start:end].dropna()
        if len(sub) < 100:
            raise RegimeFeatureError(f"训练矩阵样本不足: [{start}, {end}] 仅 {len(sub)} 行（需 ≥100）")
        X = sub[self.active_feature_names()].to_numpy(dtype=float)
        # 钳制 inf/NaN（防极端值破坏 HMM 拟合）
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        return {"X": X, "lengths": None}

    def build_shrinkage_schedule(
        self,
        detector: Any,
        refit_freq: str = "QE",
        train_years: int = 5,
        detect_window: int = 60,
    ) -> dict[datetime, float]:
        """walk-forward 季度重拟合 + 逐日 detect → Shrinkage schedule。

        流程（blueprint §7）:
          1. 生成季度边界日（QE），从 (data_load_start + train_years) 到 backtest_end
          2. 每个季度边界 q：fit HMM on [q - train_years, q]
          3. 季度内每个交易日 t：X_t = features.shift(1) 的 trailing detect_window 窗口
             （PIT：只用 ≤ t-1 特征），detect → schedule[t] = shrinkage.value

        Args:
            detector: RegimeDetector 实例（shrinkage_enabled=True）。
            refit_freq: 重拟合频率偏移字符串（"QE"=季末，pandas 锚点偏移）。
            train_years: 训练窗口年数（默认5）。
            detect_window: detect 时 trailing 特征窗口（默认60日，给 HMM 序列上下文）。

        Returns:
            {datetime: shrinkage_value∈[0,1]}，PIT as-of join 供 ScheduleShrinkageProvider。
        """
        features = self.build_features()
        # PIT 平移：detect(t) 只用 ≤ t-1 特征
        features_shifted = features.shift(1)

        # Phase 2a/2b：惰性构造 risk/overlay 构造器（复用 self 已加载的 6 特征 + index_df）
        if self.enable_full_risk and self._risk_ctor is None:
            from zephyr.regime.risk_signal_builder import RiskSignalConstructor

            self._risk_ctor = RiskSignalConstructor(
                backtest_start=self.backtest_start,
                backtest_end=self.backtest_end,
                data_load_start=self.data_load_start,
                feature_builder=self,
                market_proxy=self.market_proxy,
            )
            _logger.info("Phase 2a: 启用 RiskSignalConstructor（13 参数 risk_signal_inputs）")
        if self.enable_overlay and self._overlay_ctor is None:
            # Phase 2b：OverlaySignalsConstructor（尚未实现，import 失败时关闭并 WARN）
            try:
                from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor

                self._overlay_ctor = OverlaySignalsConstructor(
                    backtest_start=self.backtest_start,
                    backtest_end=self.backtest_end,
                    data_load_start=self.data_load_start,
                    feature_builder=self,
                    risk_constructor=self._risk_ctor,
                    market_proxy=self.market_proxy,
                )
                _logger.info("Phase 2b: 启用 OverlaySignalsConstructor（8 转换 overlay_signals）")
            except Exception as exc:  # noqa: BLE001 — Phase 2b 未实现时降级
                _logger.warning("OverlaySignalsConstructor 不可用，overlay_signals={} 降级: %s", exc)
                self._overlay_ctor = None

        schedule: dict[datetime, float] = {}
        quarter_ends = self._quarter_end_dates(
            pd.Timestamp(self.data_load_start) + pd.DateOffset(years=train_years),
            pd.Timestamp(self.backtest_end),
            freq=refit_freq,
        )
        if len(quarter_ends) == 0:
            raise RegimeFeatureError(
                f"walk-forward 无可用季度边界（data_load_start={self.data_load_start}, "
                f"train_years={train_years}, backtest_end={self.backtest_end}）"
            )

        _logger.info(
            "walk-forward: %d 个季度边界，train=%d年，detect_window=%d",
            len(quarter_ends),
            train_years,
            detect_window,
        )

        for i, q in enumerate(quarter_ends):
            train_start = (q - pd.DateOffset(years=train_years)).strftime("%Y-%m-%d")
            train_end = q.strftime("%Y-%m-%d")
            # 本季 scaler（PIT：只用训练窗口 fit；None=不标准化或 fit 失败时降级）
            scaler = None
            # fit HMM（失败降级为均匀分布，detector 内部处理）
            try:
                train_matrix = self.build_train_matrix(train_start, train_end)
                X_train = train_matrix["X"]
                if self.standardize_features:
                    scaler = RobustScaler().fit(X_train)
                    X_train = scaler.transform(X_train)
                detector.fit({"X": X_train, "lengths": train_matrix.get("lengths")})
                _logger.info("walk-forward fit Q%d [%s, %s] OK", i + 1, train_start, train_end)
            except Exception as exc:  # noqa: BLE001
                _logger.warning(
                    "walk-forward fit Q%d [%s, %s] 失败，本季降级均匀分布: %s",
                    i + 1,
                    train_start,
                    train_end,
                    exc,
                )

            # detect 季度内每个交易日：(q, next_q]
            next_q = quarter_ends[i + 1] if i + 1 < len(quarter_ends) else pd.Timestamp(self.backtest_end)
            # detect 区间 = (q, next_q]，限定到 backtest 区间
            detect_start = max(q + pd.Timedelta(days=1), pd.Timestamp(self.backtest_start))
            detect_end = min(next_q, pd.Timestamp(self.backtest_end))
            if detect_start > detect_end:
                continue

            period = features_shifted.loc[detect_start:detect_end]
            for dt, _row in period.iterrows():
                # trailing detect_window 窗口（含 dt，但已 shift 故数据 ≤ t-1）
                window = features_shifted.loc[:dt].iloc[-detect_window:]
                if len(window) < 10 or window.dropna().empty:
                    schedule[dt.to_pydatetime()] = 1.0  # warmup 期满部署
                    continue
                # risk_signal_inputs：Phase 2a 全量构造器 vs Phase 1 简化版
                # enable_full_risk=True → RiskSignalConstructor.build_for_date(dt)（13 参数）
                # False → _build_feature_risk（1 参数 #1，复刻 Phase 1 危机地板）
                if self._risk_ctor is not None:
                    risk_inputs = self._risk_ctor.build_for_date(dt)
                else:
                    last_row = window.iloc[-1]
                    risk_inputs = self._build_feature_risk(
                        vol_pct=safe_float(last_row.get("realized_vol_pct")),
                        slope=safe_float(last_row.get("kalman_slope")),
                        vol_anom=safe_float(last_row.get("volume_anomaly")),
                    )
                # overlay_signals：Phase 2b 构造器 vs 空覆盖层（纯 HMM）
                overlay_signals = self._overlay_ctor.build_for_date(dt) if self._overlay_ctor is not None else {}
                X = window[self.active_feature_names()].to_numpy(dtype=float)
                X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
                if scaler is not None:
                    X = scaler.transform(X)
                try:
                    _probs, shrinkage = detector.detect(
                        {"X": X},
                        overlay_signals=overlay_signals,
                        risk_signal_inputs=risk_inputs,
                    )
                    schedule[dt.to_pydatetime()] = float(shrinkage.value)
                except Exception as exc:  # noqa: BLE001
                    _logger.warning("detect 异常 (date=%s)，退化为 1.0: %s", dt, exc)
                    schedule[dt.to_pydatetime()] = 1.0

        # EMA 时序平滑：抑制四档硬映射在阈值边界的跳变（降 Turnover）
        # PIT 满足（只用 t 及之前数据），值仍∈[0,1]（凸组合），只减不增不变量保持
        if self.shrinkage_ema_alpha is not None and 0.0 < self.shrinkage_ema_alpha < 1.0 and len(schedule) > 1:
            schedule = self._ema_smooth_schedule(schedule, self.shrinkage_ema_alpha)
            _logger.info(
                "Shrinkage EMA 平滑: α=%.2f，平滑后均值=%.3f",
                self.shrinkage_ema_alpha,
                float(np.mean(list(schedule.values()))) if schedule else 1.0,
            )

        _logger.info(
            "walk-forward 完成: %d 日 Shrinkage，均值=%.3f，<1.0 占比=%.1f%%",
            len(schedule),
            float(np.mean(list(schedule.values()))) if schedule else 1.0,
            100.0 * sum(1 for v in schedule.values() if v < 1.0) / max(len(schedule), 1),
        )
        return schedule

    # ── 私有：数据加载 ────────────────────────────────────────────────────

    def _load_index_kline(self, table: str) -> pd.DataFrame:
        """从 ClickHouse 加载指数 K 线（市场代理 + 跨资产 + 广度指数）。

        Returns:
            MultiIndex(symbol, trade_date) DataFrame，含
            open/high/low/close/volume/advance_count/decline_count。
            high/low 供 #9 KDJ + S2 wyckoff 使用（P1-E4 激活，2026-08-08）。
        """
        symbols = sorted(set(self.cross_asset_indices + [self.market_proxy, self.breadth_index]))
        syms_str = ", ".join([f"'{s}'" for s in symbols])
        sql = (
            f"SELECT trade_date, symbol, open, high, low, close, volume, "
            f"advance_count, decline_count "
            f"FROM {table} FINAL "
            f"WHERE symbol IN ({syms_str}) "
            f"AND trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"ORDER BY symbol, trade_date"
        )
        tsv = self._safe_query(sql, context="index_kline")
        rows = parse_tsv(tsv, ncols=9)
        if not rows:
            raise RegimeFeatureError(
                f"index_kline 查询为空: symbols={symbols}, [{self.data_load_start}, {self.backtest_end}]"
            )
        cols = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "advance_count", "decline_count"]
        df = pd.DataFrame(rows, columns=cols)
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for c in ["open", "high", "low", "close"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
        df["advance_count"] = pd.to_numeric(df["advance_count"], errors="coerce").fillna(0)
        df["decline_count"] = pd.to_numeric(df["decline_count"], errors="coerce").fillna(0)
        return df.set_index(["symbol", "trade_date"]).sort_index()

    def _load_breadth(self, index_df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        """从 index_df 提取广度指数的涨跌家数（F4 源）。

        399106 深证综指 advance_count/decline_count（2015-2026-07 有数据，近期断更处填 0）。
        """
        try:
            br = index_df.xs(self.breadth_index, level="symbol")
        except KeyError as exc:
            raise RegimeFeatureError(f"广度指数 {self.breadth_index} 未在 index_kline 数据中") from exc
        # 对齐到市场代理日期
        proxy_dates = index_df.xs(self.market_proxy, level="symbol").index
        adv = br["advance_count"].reindex(proxy_dates).fillna(0.0)
        dec = br["decline_count"].reindex(proxy_dates).fillna(0.0)
        return adv, dec

    def _unstack_close(self, index_df: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
        """把多指数 close 展开成 date × symbol DataFrame（F3 用）。"""
        sub = index_df.loc[[s for s in symbols if s in index_df.index.get_level_values(0)]]
        return sub["close"].unstack("symbol")

    # ── 私有：ALG-01 横截面结构特征（可选开关，默认关）────────────────────

    def _build_cross_sectional_features(self) -> pd.DataFrame:
        """计算横截面 4 列特征（MOD-REGIME-007），index=trade_date，带缓存。"""
        if self._cs_features_cache is not None:
            return self._cs_features_cache
        panel = self._cs_panel if self._cs_panel is not None else self._load_stock_panel()
        self._cs_features_cache = compute_cross_sectional_features(panel)
        return self._cs_features_cache

    def _load_stock_panel(self) -> pd.DataFrame:
        """从 ClickHouse kline_daily 加载个股日 K 面板（ALG-01 开关开时调用）。

        每日按成交额取 top N（cross_sectional_top_n，控制 TSV 体积；横截面
        分层抽样在其内再抽 ~200 只），A_share + quality_flag=1。

        Returns:
            长表 DataFrame：trade_date / symbol / close / volume / amount。
        """
        table = self._registry.table("market_kline_daily")
        sql = (
            f"SELECT trade_date, symbol, close, volume, amount "
            f"FROM {table} FINAL "
            f"WHERE market_type = 'A_share' AND quality_flag = 1 "
            f"AND trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"AND (trade_date, symbol) IN ("
            f"SELECT trade_date, symbol FROM {table} FINAL "
            f"WHERE market_type = 'A_share' AND quality_flag = 1 "
            f"AND trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"ORDER BY amount DESC LIMIT {int(self._cs_top_n)} BY trade_date"
            f") ORDER BY trade_date, symbol"
        )
        tsv = self._safe_query(sql, context="stock_panel (cross_sectional)")
        rows = parse_tsv(tsv, ncols=5)
        if not rows:
            raise RegimeFeatureError(
                f"stock_panel 查询为空: [{self.data_load_start}, {self.backtest_end}] top_n={self._cs_top_n}"
            )
        df = pd.DataFrame(rows, columns=["trade_date", "symbol", "close", "volume", "amount"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for c in ["close", "volume", "amount"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        _logger.info(
            "stock_panel 加载: %d 行, %d 只, %s~%s",
            len(df),
            df["symbol"].nunique(),
            df["trade_date"].min(),
            df["trade_date"].max(),
        )
        return df

    # ── 私有：工具 ────────────────────────────────────────────────────────

    @staticmethod
    def _ema_smooth_schedule(schedule: dict[datetime, float], alpha: float) -> dict[datetime, float]:
        """对 Shrinkage schedule 做离线 EMA 平滑（降 Turnover）。

        smoothed_t = α * raw_t + (1-α) * smoothed_{t-1}，按日期升序递推。
        PIT 满足（只用 t 及之前数据）；值仍∈[0,1]（凸组合）；只减不增不变量保持（value≤1.0）。

        Args:
            schedule: {datetime: shrinkage∈[0,1]}（原始，可能跳变）。
            alpha: EMA 系数，越小越平滑（α=0.15 半衰期约4天）。

        Returns:
            {datetime: smoothed_shrinkage}，键同输入，按日期升序递推。
        """
        if not schedule or not (0.0 < alpha < 1.0):
            return schedule
        sorted_dt = sorted(schedule.keys())
        smoothed: dict[datetime, float] = {}
        prev = float(schedule[sorted_dt[0]])
        smoothed[sorted_dt[0]] = prev
        for dt in sorted_dt[1:]:
            prev = alpha * float(schedule[dt]) + (1.0 - alpha) * prev
            smoothed[dt] = prev
        return smoothed

    @staticmethod
    def _build_feature_risk(vol_pct: float, slope: float, vol_anom: float) -> dict[str, Any]:
        """基于 HMM 6 特征构造简化版 risk_signal_inputs（危机覆盖）。

        不依赖 HMM 状态语义（无监督 HMM 的 r1-r9 标签不可控），直接用特征
        风险含义计算单一综合风险系数 #1，传入 _compute_risk_signal。

        设计原则（C1 验证 2026-08-06 校准）：
          - **波动率主导**：realized_vol_pct 是 [0,1] 分位，阈值明确，作为主信号。
            平时（vol_pct<0.75）→ risk=1.0，HMM 主导，不干预（避免平时过度节流）。
          - **趋势辅助确认**：kalman_slope<0（下跌）配合高波动才触发危机收缩。
            单独下跌（低波阴跌）只轻度收缩，避免误判。
          - **交集而非并集**：只有"高波 AND 下跌"才强收缩，平时不触发。

        分级：
          vol_pct>0.90 + 下跌 → 0.30（危机：极端高波+暴跌）
          vol_pct>0.90        → 0.60（极端高波，可能赶顶/赶底）
          vol_pct>0.75 + 下跌 → 0.50（高波+下跌，偏危机）
          vol_pct>0.75        → 0.80（高波但未跌）
          else                → 1.00（正常，HMM 主导）

        只传 1 个参数 #1，risk_base=该值，不被其他参数 min 拉低。
        _compute_risk_signal: RiskSignal = risk_base × resonance(=1.0) + 0。
        Shrinkage = ConfidenceSignal × RiskSignal，危机时即使 HMM 满部署
        （ConfidenceSignal=1.0）也强制 Shrinkage=0.3。

        后续 Phase 补全 13 参数构造器后可替换。PIT：特征均来自 shift(1)。

        Args:
            vol_pct: realized_vol_pct（[0,1]，高=波动率处于历史高位）。
            slope: kalman_slope（负=下跌，正=上涨）。
            vol_anom: volume_anomaly（z-score，预留，当前未用）。

        Returns:
            {"params": {1: risk}, "opportunity": {}}。
        """
        down = slope < 0.0  # 下跌趋势确认
        if vol_pct > 0.90:
            risk = 0.30 if down else 0.60
        elif vol_pct > 0.75:
            risk = 0.50 if down else 0.80
        else:
            risk = 1.00
        return {"params": {1: risk}, "opportunity": {}}

    @staticmethod
    def _rolling_apply(series: pd.Series, func: Any, window: int) -> pd.Series:
        """对 series 做 trailing window 滚动应用单值函数（F2a/F2b 用）。

        Args:
            series: 输入序列（如 close）。
            func: 单值函数 func(np.ndarray) -> float（如 hurst_dfa）。
            window: trailing 窗口长度。

        Returns:
            pd.Series，每行 = func(series.iloc[i-window+1 : i+1])；前 window-1 行为 NaN。
        """
        vals = series.to_numpy(dtype=float)
        n = len(vals)
        out = np.full(n, np.nan)
        for i in range(window - 1, n):
            out[i] = func(vals[i - window + 1 : i + 1])
        return pd.Series(out, index=series.index)

    @staticmethod
    def _quarter_end_dates(start: pd.Timestamp, end: pd.Timestamp, freq: str = "QE") -> list[pd.Timestamp]:
        """生成 [start, end] 内的季度末日列表（pandas 锚点，QE=季末）。"""
        dates = pd.date_range(start=start, end=end, freq=freq)
        return [d for d in dates]

    def _safe_query(self, sql: str, context: str) -> str:
        """执行 ClickHouse 查询，失败抛 RegimeFeatureError。"""
        try:
            return ch_reader.query(sql)
        except Exception as exc:
            raise RegimeFeatureError(f"ClickHouse 查询失败 ({context}): {exc}") from exc


__all__ = [
    "RegimeFeatureBuilder",
    "RegimeFeatureError",
    "FEATURE_NAMES",
    "MARKET_PROXY",
    "CROSS_ASSET_INDICES",
    "BREADTH_INDEX",
]
