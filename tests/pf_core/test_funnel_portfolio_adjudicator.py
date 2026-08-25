# [TTL] permanent
# [TESTS] src/zephyr/pf_core/core/funnel_portfolio_adjudicator.py (MOD-PF-010)
"""MOD-PF-010 funnel_portfolio_adjudicator 单元测试（B10-01505 筛选漏斗第六层）。"""
from __future__ import annotations

import pytest

from zephyr.pf_core.core.funnel_portfolio_adjudicator import (
    FunnelAdjudicationError,
    FunnelAdjudicatorConfig,
    FunnelCandidate,
    FunnelPortfolioAdjudicator,
    FunnelPortfolioVerdict,
)


def _cand(symbol, score, industry=None, market_cap=1e11, vol=0.02, maxdd=0.10,
          style=None, crowding=0.0) -> FunnelCandidate:
    return FunnelCandidate(
        symbol=symbol, score=score, industry=industry or symbol, market_cap=market_cap,
        volatility=vol, max_drawdown=maxdd, style_loadings=style or {},
        crowding_score=crowding,
    )


def _corr(*pairs: tuple[str, str, float]) -> dict[tuple[str, str], float]:
    return {(a, b): v for a, b, v in pairs}


class TestSelection:
    def test_basic_top_n_equal_weight(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        caps = [5e11, 5e10, 5e9]  # 大/中/小市值轮转，规避 bucket_cap 干扰
        cands = [_cand(f"S{i:02d}", score=100 - i, market_cap=caps[i % 3]) for i in range(15)]
        v = adj.adjudicate(cands, correlations={})
        assert isinstance(v, FunnelPortfolioVerdict)
        assert len(v.picks) == 10  # N≤10
        assert all(abs(p.weight - 0.1) < 1e-9 for p in v.picks)
        assert v.picks[0].symbol == "S00"

    def test_fewer_candidates_than_n(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        v = adj.adjudicate([_cand("A", 1.0), _cand("B", 0.9)], correlations={})
        assert len(v.picks) == 2
        assert all(abs(p.weight - 0.5) < 1e-9 for p in v.picks)

    def test_crowding_derate_reorders(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        crowded = _cand("CROWD", score=1.0, crowding=0.95)
        clean = _cand("CLEAN", score=0.8, crowding=0.0)
        v = adj.adjudicate([crowded, clean], correlations={})
        assert v.picks[0].symbol == "CLEAN"  # 拥挤度降权后 CLEAN 反超
        assert v.picks[1].adjusted_score < v.picks[0].adjusted_score

    def test_corr_filter(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        cands = [_cand("A", 1.0), _cand("B", 0.99), _cand("C", 0.5)]
        corr = _corr(("A", "B", 0.85))  # ≥0.7 → B 被过滤
        v = adj.adjudicate(cands, correlations=corr)
        syms = [p.symbol for p in v.picks]
        assert syms == ["A", "C"]
        assert any(r.symbol == "B" and "corr" in r.reason for r in v.rejected)

    def test_industry_cap(self) -> None:
        cfg = FunnelAdjudicatorConfig(max_names=10, industry_abs_cap=0.30)
        adj = FunnelPortfolioAdjudicator(cfg)
        # 同行业 5 只全高分：等权 1/N 下第 4 只起行业权重 >0.30
        cands = [_cand(f"B{i}", score=10 - i, industry="银行") for i in range(5)]
        cands += [_cand(f"X{i}", score=1 - i * 0.1, industry="电子") for i in range(5)]
        v = adj.adjudicate(cands, correlations={})
        bank = [p for p in v.picks if p.industry == "银行"]
        assert len(bank) <= 3  # 30% 硬帽（等权 10%×3=30%）

    def test_benchmark_industry_band(self) -> None:
        cfg = FunnelAdjudicatorConfig(max_names=10, industry_abs_cap=0.30, industry_band=0.10)
        adj = FunnelPortfolioAdjudicator(cfg)
        cands = [_cand(f"B{i}", score=10 - i, industry="银行") for i in range(6)]
        cands += [_cand(f"X{i}", score=1 - i * 0.1, industry="电子") for i in range(6)]
        # 基准银行 5% → 带内上限 15%（等权 10% 下仅 1 只银行）
        v = adj.adjudicate(cands, correlations={}, benchmark_industry_weights={"银行": 0.05, "电子": 0.20})
        bank = [p for p in v.picks if p.industry == "银行"]
        assert len(bank) <= 1

    def test_market_cap_dispersion(self) -> None:
        cfg = FunnelAdjudicatorConfig(max_names=10, bucket_cap=0.6)
        adj = FunnelPortfolioAdjudicator(cfg)
        # 7 只大市值高分 + 3 只小市值低分；bucket_cap=0.6 → 大市值最多 6 只（等权 0.1×6=0.6）
        cands = [_cand(f"L{i}", score=10 - i, market_cap=5e11) for i in range(7)]
        cands += [_cand(f"S{i}", score=1 - i * 0.1, market_cap=5e9) for i in range(3)]
        v = adj.adjudicate(cands, correlations={})
        large = [p for p in v.picks if p.symbol.startswith("L")]
        assert len(large) <= 6
        assert len(v.picks) == 9  # 大市值第 7 只因桶占比被拒

    def test_volatility_budget(self) -> None:
        cfg = FunnelAdjudicatorConfig(max_names=10, vol_budget=0.02)
        adj = FunnelPortfolioAdjudicator(cfg)
        # 组合波动 √Σ(w·σ)² = 0.05/√N ≤0.02 → N ≥ 7（独立近似 corr=0）
        cands = [_cand(f"V{i}", score=10 - i, vol=0.05) for i in range(10)]
        v = adj.adjudicate(cands, correlations={})
        assert len(v.picks) >= 7
        assert v.portfolio_volatility <= 0.02 + 1e-12

    def test_maxdd_budget(self) -> None:
        cfg = FunnelAdjudicatorConfig(max_names=10, maxdd_budget=0.10)
        adj = FunnelPortfolioAdjudicator(cfg)
        good = [_cand(f"G{i}", score=10 - i, maxdd=0.05) for i in range(5)]
        bad = [_cand(f"B{i}", score=5 - i, maxdd=0.50) for i in range(5)]
        v = adj.adjudicate(good + bad, correlations={})
        assert v.portfolio_maxdd <= 0.10 + 1e-12

    def test_style_exposure_limit(self) -> None:
        cfg = FunnelAdjudicatorConfig(max_names=10, style_limit=0.3)
        adj = FunnelPortfolioAdjudicator(cfg)
        tilted = [_cand(f"T{i}", score=10 - i, style={"growth": 2.0}) for i in range(5)]
        neutral = [_cand(f"N{i}", score=5 - i, style={"growth": 0.0}) for i in range(5)]
        v = adj.adjudicate(tilted + neutral, correlations={})
        assert abs(v.style_exposures.get("growth", 0.0)) <= 0.3 + 1e-12

    def test_bearish_gross_reduction(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        cands = [_cand(f"S{i}", score=10 - i) for i in range(12)]
        v = adj.adjudicate(cands, correlations={}, bearish=True)
        gross = sum(p.weight for p in v.picks)
        assert abs(gross - 0.5) < 1e-9  # C-036 合力偏空整体降仓 50%
        assert v.gross_scale == 0.5

    def test_deterministic_tie_break(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        cands = [_cand("B", 1.0), _cand("A", 1.0)]
        v = adj.adjudicate(cands, correlations={})
        assert [p.symbol for p in v.picks] == ["A", "B"]  # 同分 symbol 升序


class TestFailClosed:
    def test_empty_candidates(self) -> None:
        with pytest.raises(FunnelAdjudicationError):
            FunnelPortfolioAdjudicator().adjudicate([], correlations={})

    def test_invalid_candidate_fields(self) -> None:
        with pytest.raises(FunnelAdjudicationError):
            _cand("X", score=float("nan"))
        with pytest.raises(FunnelAdjudicationError):
            _cand("X", score=1.0, crowding=1.5)
        with pytest.raises(FunnelAdjudicationError):
            _cand("X", score=1.0, market_cap=-1)
        with pytest.raises(FunnelAdjudicationError):
            _cand("", score=1.0)

    def test_invalid_config(self) -> None:
        with pytest.raises(FunnelAdjudicationError):
            FunnelAdjudicatorConfig(max_names=0)
        with pytest.raises(FunnelAdjudicationError):
            FunnelAdjudicatorConfig(corr_limit=1.5)

    def test_duplicate_symbol_rejected(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        with pytest.raises(FunnelAdjudicationError):
            adj.adjudicate([_cand("A", 1.0), _cand("A", 0.5)], correlations={})

    def test_missing_corr_disclosed(self) -> None:
        adj = FunnelPortfolioAdjudicator()
        v = adj.adjudicate([_cand("A", 1.0), _cand("B", 0.9)], correlations={})
        assert ("A", "B") in v.missing_corr_pairs or ("B", "A") in v.missing_corr_pairs
