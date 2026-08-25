# [BLUEPRINT] MOD-POS-025 | docs/03_modules/_domain_position/core_satellite_allocator/blueprint.md | §D-POSITION §8模块24
# [TTL] permanent
# [A_test] module_id: MOD-POS-025 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.position.test_core_satellite_allocator
# [TESTS] src/zephyr/position/core/core_satellite_allocator.py
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""CoreSatelliteAllocator (MOD-POS-025) 测试套件。

覆盖: 核心-卫星分组与30%帽截断/half-Kelly口径/止损k分轨/做T三态信号/RS换仓触发/空输入/输入校验。
"""

from __future__ import annotations

import pytest

from zephyr.position.core.core_satellite_allocator import (
    AllocationLeg,
    CandidateAsset,
    CoreSatelliteAllocator,
    CoreSatelliteConfig,
    CoreSatelliteError,
    CoreSatellitePlan,
    Sleeve,
    SwapTrigger,
    TTradeSignal,
)


def _cand(symbol: str, kelly: float = 0.5, rs_pct: float = 0.5, price: float = 10.0, vwap: float = 10.0, atr: float = 0.2) -> CandidateAsset:
    return CandidateAsset(symbol, kelly, rs_pct, price, vwap, atr)


# ── 分组与 30% 帽 ─────────────────────────────────────────────────────────────


class TestAllocate:
    def test_core_only_when_few_candidates(self):
        allocator = CoreSatelliteAllocator()
        candidates = [_cand("A", kelly=0.4), _cand("B", kelly=0.2)]
        plan = allocator.allocate(candidates)
        assert isinstance(plan, CoreSatellitePlan)
        core_syms = {leg.symbol for leg in plan.legs if leg.sleeve is Sleeve.CORE}
        assert core_syms == {"A", "B"}
        assert plan.satellite_weight == pytest.approx(0.0)

    def test_satellite_cap_truncation(self):
        allocator = CoreSatelliteAllocator()
        # 大量候选让卫星仓超出 0.30 帽
        candidates = [_cand(f"S{i:03d}", kelly=0.6, rs_pct=0.9 - i * 0.01) for i in range(10)]
        plan = allocator.allocate(candidates)
        assert plan.satellite_weight <= 0.30 + 1e-9
        satellite_legs = [leg for leg in plan.legs if leg.sleeve is Sleeve.SATELLITE]
        assert any(leg.truncated for leg in satellite_legs)

    def test_half_kelly_weight(self):
        allocator = CoreSatelliteAllocator()
        cfg = CoreSatelliteConfig(single_name_cap=1.0)  # 不设单票帽, 纯 half-Kelly
        candidates = [_cand("A", kelly=0.6)]
        plan = allocator.allocate(candidates, cfg)
        leg = plan.legs[0]
        assert leg.target_weight == pytest.approx(0.3)  # half-Kelly

    def test_stop_k_by_sleeve(self):
        allocator = CoreSatelliteAllocator()
        cfg = CoreSatelliteConfig(core_atr_k=3.5, satellite_atr_k=1.75, single_name_cap=1.0)
        # kelly=0.6 → weight=0.3 > core_budget(0.7)? 0.3≤0.7 入核心
        # kelly=0.4 → weight=0.2, 核心 0.3+0.2=0.5≤0.7 仍入核心
        # 再塞 kelly=0.4 的 C → 核心 0.5+0.2=0.7 恰好满, 再 D 入卫星
        a = _cand("A", kelly=0.6)
        b = _cand("B", kelly=0.4)
        c = _cand("C", kelly=0.4)
        d = _cand("D", kelly=0.4)
        plan = allocator.allocate([a, b, c, d], cfg)
        leg_a = next(leg for leg in plan.legs if leg.symbol == "A")
        leg_d = next(leg for leg in plan.legs if leg.symbol == "D")
        assert leg_a.stop_atr_k == pytest.approx(3.5)
        assert leg_d.stop_atr_k == pytest.approx(1.75)

    def test_empty_candidates_returns_notes(self):
        allocator = CoreSatelliteAllocator()
        plan = allocator.allocate([])
        assert plan.legs == ()
        assert plan.satellite_weight == 0.0
        assert plan.notes == ("empty_candidates",)


# ── 做T信号 ────────────────────────────────────────────────────────────────────


class TestTTradeSignals:
    def test_satellite_sell_above_band(self):
        allocator = CoreSatelliteAllocator()
        # price > vwap + band*atr
        candidates = [_cand("A", price=11.0, vwap=10.0, atr=0.5)]  # deviation=2.0
        legs = [AllocationLeg("A", Sleeve.SATELLITE, 0.1, 1.75)]
        signals = allocator.satellite_t_signals(legs, candidates)
        assert len(signals) == 1
        assert signals[0].action == "SELL_PART"

    def test_satellite_buy_below_band(self):
        allocator = CoreSatelliteAllocator()
        candidates = [_cand("A", price=9.0, vwap=10.0, atr=0.5)]  # deviation=-2.0
        legs = [AllocationLeg("A", Sleeve.SATELLITE, 0.1, 1.75)]
        signals = allocator.satellite_t_signals(legs, candidates)
        assert len(signals) == 1
        assert signals[0].action == "BUY_BACK"

    def test_core_no_t_signals(self):
        allocator = CoreSatelliteAllocator()
        candidates = [_cand("A", price=11.0, vwap=10.0, atr=0.5)]
        legs = [AllocationLeg("A", Sleeve.CORE, 0.1, 3.5)]
        signals = allocator.satellite_t_signals(legs, candidates)
        assert len(signals) == 0

    def test_within_band_no_signal(self):
        allocator = CoreSatelliteAllocator()
        candidates = [_cand("A", price=10.1, vwap=10.0, atr=0.5)]  # deviation=0.2 < 1.0
        legs = [AllocationLeg("A", Sleeve.SATELLITE, 0.1, 1.75)]
        signals = allocator.satellite_t_signals(legs, candidates)
        assert len(signals) == 0


# ── RS 换仓 ────────────────────────────────────────────────────────────────────


class TestRSSwap:
    def test_satellite_falls_out_triggers_swap(self):
        allocator = CoreSatelliteAllocator()
        # 卫星 A rs_pct=0.20 (<0.30 阈值), 挑战者 B rs_pct=0.80
        candidates = [_cand("A", kelly=0.4, rs_pct=0.20), _cand("B", kelly=0.4, rs_pct=0.80)]
        legs = [
            AllocationLeg("A", Sleeve.SATELLITE, 0.1, 1.75),
        ]
        triggers = allocator.rs_swap_check(legs, candidates)
        assert len(triggers) == 1
        assert triggers[0].out_symbol == "A"
        assert triggers[0].in_symbol == "B"

    def test_core_no_swap(self):
        allocator = CoreSatelliteAllocator()
        candidates = [_cand("A", rs_pct=0.20), _cand("B", rs_pct=0.80)]
        legs = [AllocationLeg("A", Sleeve.CORE, 0.1, 3.5)]
        triggers = allocator.rs_swap_check(legs, candidates)
        assert len(triggers) == 0

    def test_no_challenger_no_swap(self):
        allocator = CoreSatelliteAllocator()
        candidates = [_cand("A", rs_pct=0.20)]
        legs = [AllocationLeg("A", Sleeve.SATELLITE, 0.1, 1.75)]
        triggers = allocator.rs_swap_check(legs, candidates)
        assert len(triggers) == 0


# ── 输入校验 ──────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_negative_price(self):
        with pytest.raises(CoreSatelliteError, match="price must be > 0"):
            _cand("A", price=-1.0)

    def test_kelly_out_of_range(self):
        with pytest.raises(CoreSatelliteError, match="kelly_fraction must be in"):
            _cand("A", kelly=1.5)

    def test_empty_symbol(self):
        with pytest.raises(CoreSatelliteError, match="symbol must be non-empty"):
            _cand("", kelly=0.5)

    def test_config_satellite_cap_too_high(self):
        with pytest.raises(CoreSatelliteError, match="satellite_cap must be in"):
            CoreSatelliteConfig(satellite_cap=1.5)
