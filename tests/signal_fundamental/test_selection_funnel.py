# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [TTL] permanent
"""选股漏斗三层级（BM-SEL-16/17/18）单元测试——含边界与降级用例。"""

from __future__ import annotations

from zephyr.signal_fundamental.selection_funnel import (
    DEFAULT_TOP_N,
    FunnelSymbolRecord,
    filter_graded_indicators,
    run_selection_funnel,
    score_fine_selection,
    screen_preliminary,
)


def _rec(symbol: str, **kw) -> FunnelSymbolRecord:
    return FunnelSymbolRecord(symbol=symbol, **kw)


class TestGradedFilter:
    def test_physical_exclusions(self):
        recs = [
            _rec("A", is_limit_locked=True),
            _rec("B", is_suspended=True),
            _rec("C", is_st=True),
            _rec("D"),
        ]
        out = filter_graded_indicators(recs)
        assert out.kept == ("D",)
        assert out.excluded["A"] == "physical:limit_locked"
        assert out.excluded["B"] == "physical:suspended"
        assert out.excluded["C"] == "physical:st"
        assert out.degraded is False

    def test_gate_exclusion_boundary(self):
        recs = [_rec("NEW29", list_days=29), _rec("NEW30", list_days=30)]
        out = filter_graded_indicators(recs)
        assert "NEW29" in out.excluded  # <30 天绝对排除
        assert "NEW30" in out.kept  # =30 天放行（边界）

    def test_tier_and_prob_exclusions(self):
        recs = [
            _rec("LOWAMT", avg_daily_amount=4_999_999.0),
            _rec("LOWAUM", aum=1_000_000.0),  # ≤100 万剔除（边界含等号）
            _rec("ABANDON", dealer_abandon_prob=0.96),
            _rec("OK", avg_daily_amount=5_000_000.0, aum=2e6, dealer_abandon_prob=0.95),
        ]
        out = filter_graded_indicators(recs)
        assert out.excluded["LOWAMT"] == "tier:low_amount"
        assert out.excluded["LOWAUM"] == "tier:low_aum"
        assert out.excluded["ABANDON"] == "prob:dealer_abandon"
        assert "OK" in out.kept  # 阈值边界值均放行

    def test_degraded_only_excludes_limit_locked_and_suspended(self):
        recs = [
            _rec("A", is_limit_locked=True),
            _rec("B", is_suspended=True),
            _rec("C", is_st=True, list_days=1, avg_daily_amount=0.0, aum=0.0, dealer_abandon_prob=1.0),
        ]
        out = filter_graded_indicators(recs, degraded=True)
        assert out.degraded is True
        assert out.kept == ("C",)  # 降级：ST/次新/低流动性/弃庄全放行
        assert set(out.excluded) == {"A", "B"}

    def test_empty_input(self):
        out = filter_graded_indicators([])
        assert out.kept == () and out.excluded == {}


class TestPreliminaryScreen:
    def test_five_dim_gates(self):
        base = dict(volume_ratio=2.0, sector_strength_rank_pct=0.2)
        recs = [
            _rec("T", technical_pass=False, **base),
            _rec("V", volume_ratio=1.5, sector_strength_rank_pct=0.2),  # 边界：>1.5 严格
            _rec("S", sector_strength_rank_pct=0.31, volume_ratio=2.0),
            _rec("M", main_force_pass=False, **base),
            _rec("R", market_state_pass=False, **base),
            _rec("OK", **base),
        ]
        out = screen_preliminary(recs)
        assert out.kept == ("OK",)
        assert out.excluded["V"].startswith("dim:volume_ratio")
        assert out.excluded["S"] == "dim:sector_rank"
        assert out.excluded["M"] == "dim:main_force"
        assert out.excluded["R"] == "dim:market_state"

    def test_sector_rank_boundary_30pct(self):
        recs = [_rec("E", volume_ratio=2.0, sector_strength_rank_pct=0.30)]
        out = screen_preliminary(recs)
        assert out.kept == ("E",)  # =30% 放行（前 30% 含边界）

    def test_degraded_passes_all(self):
        recs = [_rec("A", technical_pass=False, volume_ratio=0.1, sector_strength_rank_pct=1.0)]
        out = screen_preliminary(recs, degraded=True)
        assert out.degraded is True and out.kept == ("A",)


class TestFineScoring:
    def _make(self, n: int) -> list[FunnelSymbolRecord]:
        # 动量分线性递增 → Z-score 排名确定性
        return [_rec(f"S{i:03d}", base_momentum_score=float(i)) for i in range(n)]

    def test_top_n_and_zscore_order(self):
        recs = self._make(10)
        out = score_fine_selection(recs, top_n=3)
        assert len(out.top) == 3
        assert [t.symbol for t in out.top] == ["S009", "S008", "S007"]
        assert out.top[0].rank == 1
        assert out.top[0].z_score > out.top[1].z_score > 0.0

    def test_regime_shift_clipped_to_10pct(self):
        hi = _rec("HI", base_momentum_score=100.0, regime_shift=0.5)  # 超界 clip 到 +0.10
        lo = _rec("LO", base_momentum_score=100.0, regime_shift=0.10)
        out = score_fine_selection([hi, lo], top_n=2)
        # clip 后两者 raw 相等 → z 相等，排名稳定不报错
        assert len(out.top) == 2
        assert abs(out.top[0].raw_score - out.top[1].raw_score) < 1e-9

    def test_density_and_crowding_deduct(self):
        clean = _rec("CLEAN", base_momentum_score=80.0)
        noisy = _rec(
            "NOISY",
            base_momentum_score=80.0,
            crowding_score=100.0,
            neg_skewness=1.0,
            excess_kurtosis=2.0,
            forward_var_pct=5.0,
        )
        out = score_fine_selection([clean, noisy], top_n=2)
        assert out.top[0].symbol == "CLEAN"
        assert out.top[0].raw_score > out.top[1].raw_score

    def test_all_same_score_zscore_zero(self):
        recs = [_rec("A"), _rec("B"), _rec("C")]
        out = score_fine_selection(recs, top_n=2)
        assert all(t.z_score == 0.0 for t in out.top)
        assert len(out.top) == 2

    def test_degraded_equal_weight(self):
        rec = _rec(
            "A",
            base_value_score=100.0,
            base_momentum_score=0.0,
            base_quality_score=0.0,
            base_sentiment_score=0.0,
            main_force_score=0.0,
        )
        out = score_fine_selection([rec], top_n=1, degraded=True)
        assert out.degraded is True
        assert out.top[0].raw_score == 20.0  # 等权 (100+0+0+0+0)/5

    def test_empty_and_zero_topn(self):
        assert score_fine_selection([], top_n=5).top == ()
        assert score_fine_selection([_rec("A")], top_n=0).top == ()
        assert score_fine_selection([_rec("A")], top_n=-1).top == ()


class TestFunnelChain:
    def test_monotonic_convergence(self):
        recs = [_rec(f"S{i:03d}", base_momentum_score=float(i % 37)) for i in range(100)]
        recs.append(_rec("BAD", is_st=True))
        out = run_selection_funnel(recs, top_n=10)
        assert "BAD" not in out.graded.kept
        assert len(out.scored.top) == 10
        assert len(out.scored.top) <= len(out.screened.kept) <= len(out.graded.kept)

    def test_default_top_n_constant(self):
        assert DEFAULT_TOP_N == 50
