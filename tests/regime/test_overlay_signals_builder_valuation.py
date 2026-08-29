# [A_test] module_id: MOD-TEST-OVERLAY-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 Phase2b
# [MODULE] tests.regime.test_overlay_signals_builder_valuation
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.overlay_signals_builder; zephyr.regime.features.overlay_features; pandas; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] 本文件
# [A_module] module_id: MOD-TEST-OVERLAY-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""OverlaySignalsConstructor S2 valuation 路A 接线测试（2026-08-28 S2 治本方案 §5.4）。

覆盖：
- 路A 优先：index_valuation_daily 有 CAPE 分位时调 s2_valuation_score_fundamental
- 路B 降级：index_valuation_daily 缺失/CAPE 分位缺失时回退 s2_valuation_score(close)
- 路A 危机期低估场景：CAPE 分位<25% → valuation ≥ 60（confirm 门槛）
"""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor

from tests.regime.test_overlay_signals_builder import _make_dates, _make_features, _make_index_df, _MockFeatureBuilder


class TestS2ValuationPathA:
    """S2 valuation 路A（s2_valuation_score_fundamental）接线测试。"""

    def test_path_a_preferred_when_cape_available(self):
        """路A 优先：index_valuation_daily 有 CAPE 分位时走 fundamental 评分。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.linspace(3000, 3100, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))

        # mock index_valuation：CAPE 分位 0.15（<25% → 60 分）
        index_val = pd.DataFrame(
            {
                "cape_5y_pct": np.full(300, 0.15),
                "pb_pct": np.full(300, 0.20),
                "erp": np.full(300, 0.03),
                "erp_pct": np.full(300, 0.70),
            },
            index=dates,
        )
        fb = _MockFeatureBuilder(feat, idx_df, index_valuation=index_val)

        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        valuation = result["transitions"]["S2"]["valuation"]
        # CAPE 分位 0.15 < 0.25 → 60 分 + PB 分位<10%? 0.20 不满足 + ERP 分位>95%? 0.70 不满足 + ERP 绝对值>5%? 0.03 不满足
        # 预期：60 分
        assert valuation == 60.0, f"路A CAPE 分位 0.15 应得 60 分，实际 {valuation}"

    def test_path_b_fallback_when_no_index_valuation(self):
        """路B 降级：index_valuation_daily 缺失时回退 s2_valuation_score(close)。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.linspace(3000, 3100, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))

        fb = _MockFeatureBuilder(feat, idx_df)
        # index_valuation=None → get_index_valuation 返回 None（默认）

        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        valuation = result["transitions"]["S2"]["valuation"]
        # 路B：close 从 3000 涨到 3100，rolling_max=3100，pos=3100/3100=1.0 → 0 分
        assert valuation == 0.0, f"路B 降级 close 新高应得 0 分，实际 {valuation}"

    def test_path_b_fallback_when_cape_nan(self):
        """路B 降级：CAPE 分位全 NaN 时回退 s2_valuation_score(close)。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.linspace(3000, 3100, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))

        # mock index_valuation：CAPE 分位全 NaN
        index_val = pd.DataFrame(
            {
                "cape_5y_pct": np.full(300, np.nan),
                "pb_pct": np.full(300, 0.20),
                "erp": np.full(300, 0.03),
                "erp_pct": np.full(300, 0.70),
            },
            index=dates,
        )
        fb = _MockFeatureBuilder(feat, idx_df, index_valuation=index_val)

        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        valuation = result["transitions"]["S2"]["valuation"]
        # CAPE 分位全 NaN → 降级路B → close 新高 → 0 分
        assert valuation == 0.0, f"CAPE 分位全 NaN 应降级路B，实际 {valuation}"

    def test_path_a_crisis_undervaluation(self):
        """路A 危机期低估：CAPE 分位<10% → 80 分（极度低估）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.linspace(3000, 2500, 300)  # 下跌通道
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))

        # mock index_valuation：CAPE 分位 0.05（<10% → 80 分）+ PB 分位 0.08（<10% → +10）+ ERP 绝对值 0.065（>6% → +10）
        index_val = pd.DataFrame(
            {
                "cape_5y_pct": np.full(300, 0.05),
                "pb_pct": np.full(300, 0.08),
                "erp": np.full(300, 0.065),
                "erp_pct": np.full(300, 0.97),
            },
            index=dates,
        )
        fb = _MockFeatureBuilder(feat, idx_df, index_valuation=index_val)

        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        valuation = result["transitions"]["S2"]["valuation"]
        # CAPE 分位<10% → 80 + PB 分位<10% → +10 + ERP 绝对值>6% → +10（ERP 项封顶 10）= 100（封顶）
        assert valuation == 100.0, f"危机期低估应得 100 分，实际 {valuation}"
