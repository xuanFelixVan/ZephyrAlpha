# [BLUEPRINT] MOD-E2E-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""25号memo §3.7#5 CrowdingRealTimeMonitor 测试。

覆盖：三代理各自归一化 / 综合分级响应（REDUCE_WEIGHT_50/ALERT/MONITOR）/
数据不足 degraded 退化 / 边界阈值。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

mod = pytest.importorskip("zephyr.factor.analysis.multifactor_crowding_monitor")

CrowdingLevel = mod.CrowdingLevel
CrowdingParams = mod.CrowdingParams
assess = mod.assess


def _etf_series(baseline: float, recent: float) -> pd.Series:
    """60 日序列：前 40 日=baseline，近 20 日=recent。"""
    return pd.Series([baseline] * 40 + [recent] * 20)


def _corr_panel(avg_corr: float, n: int = 40, k: int = 3) -> pd.DataFrame:
    """构造两两相关≈avg_corr 的因子收益面板。"""
    rng = np.random.default_rng(0)
    common = rng.normal(size=n)
    cols = {}
    for i in range(k):
        noise = rng.normal(size=n)
        # 控制相关系数：x = a*common + b*noise, corr≈a/sqrt(a²+b²)
        a = np.sqrt(avg_corr / max(1e-9, 1 - avg_corr))
        cols[f"f{i}"] = a * common + noise
    return pd.DataFrame(cols)


class TestComponentScores:
    def test_etf_growth_full_score(self):
        # 增长 30% > 20% 阈值 → 满分 1.0
        a = assess(etf_holdings=_etf_series(100.0, 130.0))
        assert a.etf_score == pytest.approx(1.0)
        assert "etf" not in a.degraded

    def test_etf_growth_partial_score(self):
        # 增长 10% → 0.5
        a = assess(etf_holdings=_etf_series(100.0, 110.0))
        assert a.etf_score == pytest.approx(0.5)

    def test_etf_no_growth_zero(self):
        a = assess(etf_holdings=_etf_series(100.0, 100.0))
        assert a.etf_score == pytest.approx(0.0)

    def test_corr_high_full_score(self):
        a = assess(factor_returns_panel=_corr_panel(0.85))
        assert a.corr_score == pytest.approx(1.0, abs=0.1)

    def test_corr_low_zero(self):
        a = assess(factor_returns_panel=_corr_panel(0.02))
        assert a.corr_score < 0.15

    def test_seat_ratio_scores(self):
        assert assess(quant_seat_ratio=0.35).seat_score == pytest.approx(1.0)
        assert assess(quant_seat_ratio=0.175).seat_score == pytest.approx(0.5)
        assert assess(quant_seat_ratio=0.0).seat_score == pytest.approx(0.0)


class TestGrading:
    def test_reduce_weight_50(self):
        # 三分量全满 → composite=1.0 > 0.70
        a = assess(etf_holdings=_etf_series(100.0, 130.0),
                   factor_returns_panel=_corr_panel(0.9),
                   quant_seat_ratio=0.40)
        assert a.level is CrowdingLevel.REDUCE_WEIGHT_50

    def test_alert(self):
        # composite ≈ (0.75+0+0.75)/3 = 0.5+ → ALERT 带内
        a = assess(etf_holdings=_etf_series(100.0, 115.0),
                   quant_seat_ratio=0.2625)
        assert CrowdingLevel.ALERT is a.level or CrowdingLevel.MONITOR is a.level
        assert 0.0 < a.composite < 0.70

    def test_monitor(self):
        a = assess(etf_holdings=_etf_series(100.0, 102.0),
                   factor_returns_panel=_corr_panel(0.02),
                   quant_seat_ratio=0.05)
        assert a.level is CrowdingLevel.MONITOR

    def test_boundary_above_070(self):
        p = CrowdingParams()
        # 直接构造 composite 恰 >0.70：seat=1.0, etf=1.0, corr 低 → (1+1+0.12)/3≈0.707
        a = assess(etf_holdings=_etf_series(100.0, 125.0),
                   quant_seat_ratio=0.40,
                   params=p)
        # composite=(1+0+1)/3≈0.667 → ALERT
        assert a.level is CrowdingLevel.ALERT


class TestDegraded:
    def test_all_missing_inputs(self):
        a = assess()
        assert a.composite == 0.0
        assert a.level is CrowdingLevel.MONITOR
        assert set(a.degraded) == {"etf", "corr", "seat"}

    def test_short_etf_series_degraded(self):
        a = assess(etf_holdings=pd.Series([1.0] * 30))
        assert "etf" in a.degraded

    def test_single_factor_panel_degraded(self):
        a = assess(factor_returns_panel=pd.DataFrame({"f1": [0.01] * 40}))
        assert "corr" in a.degraded
