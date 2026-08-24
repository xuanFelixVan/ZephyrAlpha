# [BLUEPRINT] MOD-SIG-086 | docs/03_modules/_domain_signal/selection_funnel_skeleton/blueprint.md
# [TTL] permanent
"""选股漏斗共享骨架（MOD-SIG-086，BM-SEL-16/17/18 层序/接口/数据流唯一真源）单元测试。

覆盖：三层引擎排除/放行语义、降级链路、extra_tier_checks 注入位、容量截断注入位、
密度鸭子类型注入位、精筛 tie-break 双口径、链式数据流。合成数据不触库。
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from zephyr.signal_ashare.selection_funnel_skeleton import (
    CapacityTruncation,
    FineScoreHooks,
    FineScoreWeights,
    FunnelChainResult,
    GradedExclusionHooks,
    GradedFilterThresholds,
    PreliminaryGateHooks,
    PreliminaryThresholds,
    density_penalty_from_summary,
    run_fine_scoring,
    run_funnel_chain,
    run_graded_exclusion,
    run_preliminary_gates,
    subset_by_kept,
)


@dataclass(frozen=True)
class _Rec:
    """骨架测试记录——字段平铺，经钩子闭包映射到各层语义。"""

    symbol: str
    # 第一层输入
    limit_locked: bool = False
    suspended: bool = False
    st: bool = False
    list_days: int = 9999
    amount: float = 1e12
    aum: float = 1e12
    abandon: float = 0.0
    # 第二层输入
    technical: bool = True
    vr: float = 999.0
    turnover: float = 999.0
    sector_rank: float = 0.0
    mf_pass: bool = True
    ms_pass: bool = True
    liquidity: float = 0.0
    # 第三层输入
    value: float = 50.0
    momentum: float = 50.0
    quality: float = 50.0
    sentiment: float = 50.0
    shift: float = 0.0
    mf_score: float = 50.0
    crowd: float = 0.0
    density: object = None
    eight: float = 0.0


def _sym(rec: _Rec) -> str:
    return rec.symbol


def _graded_hooks(**overrides) -> GradedExclusionHooks:
    base = {
        "is_limit_locked": lambda r: r.limit_locked,
        "is_suspended": lambda r: r.suspended,
        "is_st": lambda r: r.st,
        "list_days": lambda r: r.list_days,
        "avg_daily_amount": lambda r: r.amount,
        "dealer_abandon_prob": lambda r: r.abandon,
    }
    base.update(overrides)
    return GradedExclusionHooks(**base)


def _gate_hooks() -> PreliminaryGateHooks:
    return PreliminaryGateHooks(
        technical_pass=lambda r: r.technical,
        volume_ratio=lambda r: r.vr,
        turnover_rate_pct=lambda r: r.turnover,
        sector_strength_rank_pct=lambda r: r.sector_rank,
        main_force_pass=lambda r: r.mf_pass,
        market_state_pass=lambda r: r.ms_pass,
    )


def _score_hooks(**overrides) -> FineScoreHooks:
    base = {
        "base_value_score": lambda r: r.value,
        "base_momentum_score": lambda r: r.momentum,
        "base_quality_score": lambda r: r.quality,
        "base_sentiment_score": lambda r: r.sentiment,
        "regime_shift": lambda r: r.shift,
        "main_force_score": lambda r: r.mf_score,
        "crowding_score": lambda r: r.crowd,
        "density_penalty": lambda r: density_penalty_from_summary(r.density),
        "eight_state_score": lambda r: r.eight,
    }
    base.update(overrides)
    return FineScoreHooks(**base)


class TestGradedExclusion:
    def test_exclusion_order_and_reasons(self):
        recs = [
            _Rec("L", limit_locked=True),
            _Rec("S", suspended=True),
            _Rec("T", st=True),
            _Rec("N", list_days=29),
            _Rec("A", amount=4_999_999.0),
            _Rec("P", abandon=0.96),
            _Rec("OK"),
        ]
        out = run_graded_exclusion(recs, symbol_of=_sym, hooks=_graded_hooks(), thresholds=GradedFilterThresholds())
        assert out.kept == ("OK",)
        assert out.excluded["L"] == "physical:limit_locked"
        assert out.excluded["S"] == "physical:suspended"
        assert out.excluded["T"] == "physical:st"
        assert out.excluded["N"] == "gate:new_stock(29d<30d)"
        assert out.excluded["A"] == "tier:low_amount"
        assert out.excluded["P"] == "prob:dealer_abandon"

    def test_degraded_keeps_only_physical_exclusions(self):
        recs = [
            _Rec("L", limit_locked=True),
            _Rec("S", suspended=True),
            _Rec("BAD", st=True, list_days=1, amount=0.0, abandon=1.0),
        ]
        out = run_graded_exclusion(
            recs, symbol_of=_sym, hooks=_graded_hooks(), thresholds=GradedFilterThresholds(), degraded=True
        )
        assert out.kept == ("BAD",)
        assert set(out.excluded) == {"L", "S"}

    def test_extra_tier_checks_sit_between_amount_and_prob(self):
        hooks = _graded_hooks(
            extra_tier_checks=(lambda r: "tier:low_aum" if r.aum <= 1_000_000.0 else None,),
        )
        recs = [
            _Rec("AUM", aum=500_000.0, abandon=0.99),  # extra 先于 prob 命中
            _Rec("AMT", amount=1.0, aum=0.0),  # amount 先于 extra 命中
        ]
        out = run_graded_exclusion(recs, symbol_of=_sym, hooks=hooks, thresholds=GradedFilterThresholds())
        assert out.excluded["AUM"] == "tier:low_aum"
        assert out.excluded["AMT"] == "tier:low_amount"

    def test_empty_input(self):
        out = run_graded_exclusion([], symbol_of=_sym, hooks=_graded_hooks(), thresholds=GradedFilterThresholds())
        assert out.kept == () and out.excluded == {}


class TestPreliminaryGates:
    def test_five_gate_reasons(self):
        recs = [
            _Rec("T", technical=False, vr=2.0),
            _Rec("V", vr=1.5, sector_rank=0.2),  # 边界：>1.5 严格
            _Rec("S", vr=2.0, sector_rank=0.31),
            _Rec("M", vr=2.0, sector_rank=0.2, mf_pass=False),
            _Rec("R", vr=2.0, sector_rank=0.2, ms_pass=False),
            _Rec("OK", vr=2.0, sector_rank=0.2),
        ]
        out = run_preliminary_gates(recs, symbol_of=_sym, hooks=_gate_hooks(), thresholds=PreliminaryThresholds())
        assert out.kept == ("OK",)
        assert out.excluded["T"] == "dim:technical"
        assert out.excluded["V"] == "dim:volume_ratio(1.50<=1.5)"
        assert out.excluded["S"] == "dim:sector_rank"
        assert out.excluded["M"] == "dim:main_force"
        assert out.excluded["R"] == "dim:market_state"
        assert out.truncated is False

    def test_degraded_passes_all(self):
        recs = [_Rec("A", technical=False, vr=0.1, sector_rank=1.0)]
        out = run_preliminary_gates(
            recs, symbol_of=_sym, hooks=_gate_hooks(), thresholds=PreliminaryThresholds(), degraded=True
        )
        assert out.kept == ("A",) and out.excluded == {} and out.truncated is False

    def test_capacity_truncation_by_liquidity_desc(self):
        capacity = CapacityTruncation(target=2, liquidity_score_of=lambda r: r.liquidity)
        recs = [
            _Rec("K1", liquidity=10.0),
            _Rec("K2", liquidity=30.0),
            _Rec("K3", liquidity=30.0),  # 与 K2 同分 → symbol 字典序定先
            _Rec("K4", liquidity=20.0),
        ]
        out = run_preliminary_gates(
            recs, symbol_of=_sym, hooks=_gate_hooks(), thresholds=PreliminaryThresholds(), capacity=capacity
        )
        assert out.kept == ("K2", "K3")
        assert out.truncated is True
        assert "K1" not in out.excluded and "K4" not in out.excluded  # 截断非规则排除

    def test_capacity_target_non_positive_raises_even_degraded(self):
        capacity = CapacityTruncation(target=0, liquidity_score_of=lambda r: r.liquidity)
        with pytest.raises(ValueError):
            run_preliminary_gates(
                [_Rec("A")],
                symbol_of=_sym,
                hooks=_gate_hooks(),
                thresholds=PreliminaryThresholds(),
                capacity=capacity,
                degraded=True,
            )


class TestFineScoring:
    def _make(self, n: int) -> list[_Rec]:
        return [_Rec(f"S{i:03d}", value=0.0, momentum=float(i), quality=0.0, sentiment=0.0, mf_score=0.0) for i in range(n)]

    def test_composite_formula_default_weights(self):
        rec = _Rec("X", value=100.0, momentum=0.0, quality=0.0, sentiment=0.0, mf_score=0.0)
        top = run_fine_scoring([rec], symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=1)
        assert top[0].raw_score == pytest.approx(40.0)  # 0.40*100

    def test_regime_shift_clipped(self):
        hi = _Rec("HI", value=0.0, momentum=100.0, quality=0.0, sentiment=0.0, mf_score=0.0, shift=0.5)
        lo = _Rec("LO", value=0.0, momentum=100.0, quality=0.0, sentiment=0.0, mf_score=0.0, shift=0.10)
        top = run_fine_scoring([hi, lo], symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=2)
        assert abs(top[0].raw_score - top[1].raw_score) < 1e-9

    def test_density_penalty_hook_deducts(self):
        clean = _Rec("CLEAN", value=0.0, momentum=100.0, quality=0.0, sentiment=0.0, mf_score=0.0)
        noisy = _Rec("NOISY", value=0.0, momentum=100.0, quality=0.0, sentiment=0.0, mf_score=0.0)
        top = run_fine_scoring(
            [clean, noisy],
            symbol_of=_sym,
            hooks=_score_hooks(density_penalty=lambda r: 10.0 if r.symbol == "NOISY" else 0.0),
            weights=FineScoreWeights(),
            top_n=2,
        )
        assert top[0].symbol == "CLEAN"
        assert top[0].raw_score - top[1].raw_score == pytest.approx(1.5)  # 0.15*10

    def test_degraded_equal_weight(self):
        rec = _Rec("A", value=100.0, momentum=0.0, quality=0.0, sentiment=0.0, mf_score=0.0)
        top = run_fine_scoring(
            [rec], symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=1, degraded=True
        )
        assert top[0].raw_score == pytest.approx(20.0)

    def test_zscore_order_and_topn(self):
        top = run_fine_scoring(self._make(10), symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=3)
        assert [t.symbol for t in top] == ["S009", "S008", "S007"]
        assert top[0].rank == 1 and top[0].z_score > top[1].z_score > 0.0

    def test_all_same_score_z_zero(self):
        top = run_fine_scoring([_Rec("A"), _Rec("B"), _Rec("C")], symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=2)
        assert all(t.z_score == 0.0 for t in top) and len(top) == 2

    def test_empty_and_nonpositive_topn(self):
        assert run_fine_scoring([], symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=5) == ()
        assert run_fine_scoring([_Rec("A")], symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=0) == ()

    def test_tie_break_stable_keeps_input_order_symbol_breaks_by_name(self):
        recs = [_Rec("B"), _Rec("A")]  # 完全同分
        stable = run_fine_scoring(
            recs, symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=2, tie_break="stable"
        )
        by_symbol = run_fine_scoring(
            recs, symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=2, tie_break="symbol"
        )
        assert [t.symbol for t in stable] == ["B", "A"]
        assert [t.symbol for t in by_symbol] == ["A", "B"]

    def test_tie_break_unknown_raises(self):
        with pytest.raises(ValueError):
            run_fine_scoring(
                [_Rec("A")], symbol_of=_sym, hooks=_score_hooks(), weights=FineScoreWeights(), top_n=1, tie_break="bogus"
            )


class TestDensityPenaltyFromSummary:
    def test_none_returns_zero(self):
        assert density_penalty_from_summary(None) == 0.0

    def test_duck_typed_summary(self):
        density = SimpleNamespace(neg_skewness=1.0, excess_kurtosis=2.0, forward_var_pct=5.0)
        assert density_penalty_from_summary(density) == pytest.approx(25.0)  # 1*10 + 2*5 + 5


class TestFunnelChain:
    def test_chain_dataflow_and_layer_order(self):
        recs = [_Rec("X1"), _Rec("X2", suspended=True), _Rec("X3", technical=False)]
        thresholds1 = GradedFilterThresholds()
        thresholds2 = PreliminaryThresholds()
        weights = FineScoreWeights()
        chain = run_funnel_chain(
            recs,
            symbol_of=_sym,
            run_graded=lambda rs: run_graded_exclusion(rs, symbol_of=_sym, hooks=_graded_hooks(), thresholds=thresholds1),
            run_screen=lambda rs: run_preliminary_gates(rs, symbol_of=_sym, hooks=_gate_hooks(), thresholds=thresholds2),
            run_score=lambda rs: run_fine_scoring(rs, symbol_of=_sym, hooks=_score_hooks(), weights=weights, top_n=50),
        )
        assert isinstance(chain, FunnelChainResult)
        assert chain.graded.kept == ("X1", "X3")
        assert chain.screened.kept == ("X1",)
        assert [t.symbol for t in chain.scored] == ["X1"]

    def test_subset_by_kept_preserves_kept_order(self):
        recs = [_Rec("A"), _Rec("B"), _Rec("C")]
        assert [r.symbol for r in subset_by_kept(recs, symbol_of=_sym, kept=("C", "A"))] == ["C", "A"]
