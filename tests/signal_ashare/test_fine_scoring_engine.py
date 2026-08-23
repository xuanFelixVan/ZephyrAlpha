# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [TTL] permanent
"""选股漏斗第三层 精筛评分（BM-SEL-18，MOD-SIG-048）单元测试——含六要素/Z-score/密度要素/降级用例。"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from zephyr.signal_ashare.fine_scoring_engine import (
    FineScoreConfig,
    FineScoreRecord,
    compute_density_penalty,
    composite_raw_score,
    score_fine,
)


@dataclass(frozen=True)
class _DensityStub:
    """密度摘要鸭子类型桩（与 conditional_density_predictor 输出同形）。"""

    neg_skewness: float
    excess_kurtosis: float
    forward_var_pct: float


def _rec(symbol: str, **kw) -> FineScoreRecord:
    return FineScoreRecord(symbol=symbol, **kw)


class TestDensityPenalty:
    def test_none_density_zero_penalty(self):
        assert compute_density_penalty(None) == 0.0

    def test_penalty_formula(self):
        d = _DensityStub(neg_skewness=0.5, excess_kurtosis=2.0, forward_var_pct=3.0)
        # 0.5*10 + 2.0*5 + 3.0 = 18.0
        assert compute_density_penalty(d) == pytest.approx(18.0)


class TestCompositeRawScore:
    def test_base_weights_only_defaults(self):
        """默认记录（全 50 分、无偏移/拥挤/密度）：50 + 0.2*50 = 60。"""
        score = composite_raw_score(_rec("A"), cfg=FineScoreConfig(), degraded=False)
        assert score == pytest.approx(60.0)

    def test_regime_shift_clamped(self):
        cfg = FineScoreConfig()
        up = composite_raw_score(_rec("A", regime_shift=0.50), cfg=cfg, degraded=False)
        down = composite_raw_score(_rec("A", regime_shift=-0.50), cfg=cfg, degraded=False)
        # 截断 ±0.10：50*1.1 + 10 = 65；50*0.9 + 10 = 55
        assert up == pytest.approx(65.0)
        assert down == pytest.approx(55.0)

    def test_crowding_and_density_deduct(self):
        cfg = FineScoreConfig()
        d = _DensityStub(neg_skewness=1.0, excess_kurtosis=0.0, forward_var_pct=0.0)
        score = composite_raw_score(_rec("A", crowding_score=100.0, density=d), cfg=cfg, degraded=False)
        # 基础 50 + 主力 10 − 拥挤 0.10*100 − 密度 0.15*(1.0*10) = 50+10−10−1.5 = 48.5
        assert score == pytest.approx(48.5)

    def test_eight_state_weight_zero_by_default(self):
        """8 态修正暂缓置 0：eight_state_score 不影响合成。"""
        cfg = FineScoreConfig()
        s0 = composite_raw_score(_rec("A"), cfg=cfg, degraded=False)
        s1 = composite_raw_score(_rec("A", eight_state_score=100.0), cfg=cfg, degraded=False)
        assert s0 == pytest.approx(s1)

    def test_degraded_equal_weight(self):
        score = composite_raw_score(_rec("A"), cfg=FineScoreConfig(), degraded=True)
        assert score == pytest.approx(50.0)  # 五维全 50 等权


class TestScoreFine:
    def test_top_n_ordering_and_ranks(self):
        recs = [
            _rec("LOW", base_momentum_score=10.0),
            _rec("MID", base_momentum_score=50.0),
            _rec("HIGH", base_momentum_score=90.0),
        ]
        out = score_fine(recs, top_n=2)
        assert [e.symbol for e in out.top] == ["HIGH", "MID"]
        assert [e.rank for e in out.top] == [1, 2]
        assert out.top[0].z_score > out.top[1].z_score

    def test_zscore_zero_when_tie(self):
        """全体同分 → std≈0 → Z 置 0，按 raw+symbol 兜底确定性排名。"""
        out = score_fine([_rec("B"), _rec("A")], top_n=2)
        assert all(e.z_score == 0.0 for e in out.top)
        assert [e.symbol for e in out.top] == ["A", "B"]

    def test_top_n_larger_than_input(self):
        out = score_fine([_rec("A")], top_n=50)
        assert len(out.top) == 1

    def test_empty_and_nonpositive_topn(self):
        assert score_fine([], top_n=50).top == ()
        assert score_fine([_rec("A")], top_n=0).top == ()

    def test_degraded_flag_propagates(self):
        out = score_fine([_rec("A"), _rec("B")], top_n=2, degraded=True)
        assert out.degraded is True
        assert all(e.raw_score == pytest.approx(50.0) for e in out.top)
