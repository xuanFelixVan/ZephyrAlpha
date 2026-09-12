# [BLUEPRINT] MOD-SIG-038 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [DOMAIN] D_ASHARE_SIGNAL
# [TTL] permanent
"""MOD-SIG-136 sector_conduction 单元测试（红蓝对抗：红-边界/红-契约）。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.core.sector_conduction import (
    ConductionResult,
    SectorConductionError,
    apply_strength_conduction,
    strength_conduction_bonus,
)


class TestAnchorPoints:
    """节点三锚点：10 分=+15%、6 分=+5%、<6 分=-10%。"""

    def test_strength_ten_full_bonus(self):
        assert strength_conduction_bonus(10.0) == pytest.approx(0.15)

    def test_strength_six_mid_bonus(self):
        assert strength_conduction_bonus(6.0) == pytest.approx(0.05)

    def test_strength_below_six_flat_discount(self):
        for s in (5.99, 3.0, 0.0):
            assert strength_conduction_bonus(s) == pytest.approx(-0.10)

    def test_linear_interpolation_midpoint(self):
        # 8 分 = 6→10 中点 → (0.05+0.15)/2 = 0.10
        assert strength_conduction_bonus(8.0) == pytest.approx(0.10)
        assert strength_conduction_bonus(7.0) == pytest.approx(0.075)


class TestApplication:
    """乘法传导：强板块弱票加分、弱板块强票打折。"""

    def test_strong_sector_boosts_weak_stock(self):
        r = apply_strength_conduction(stock_score=0.50, sector_strength=10.0)
        assert r.adjusted_score == pytest.approx(0.50 * 1.15)
        assert r.multiplier == pytest.approx(1.15)

    def test_weak_sector_discounts_strong_stock(self):
        r = apply_strength_conduction(stock_score=0.95, sector_strength=3.0)
        assert r.adjusted_score == pytest.approx(0.95 * 0.90)
        assert r.multiplier == pytest.approx(0.90)

    def test_order_preserved_within_sector(self):
        # 保序不重排名：同板块内两票的相对高低不变
        a = apply_strength_conduction(0.80, 9.0)
        b = apply_strength_conduction(0.60, 9.0)
        assert a.adjusted_score > b.adjusted_score


class TestBoundaries:
    """红-边界：越界 fail-closed、零分票。"""

    @pytest.mark.parametrize("bad_strength", [-0.1, 10.1, float("nan")])
    def test_strength_out_of_range_rejected(self, bad_strength):
        with pytest.raises(SectorConductionError):
            strength_conduction_bonus(bad_strength)

    @pytest.mark.parametrize("bad_score", [-0.01, float("nan")])
    def test_score_invalid_rejected(self, bad_score):
        with pytest.raises(SectorConductionError):
            apply_strength_conduction(bad_score, 8.0)

    def test_zero_score_passes_through(self):
        r = apply_strength_conduction(0.0, 10.0)
        assert r.adjusted_score == 0.0

    def test_multiplier_clamped(self):
        assert 0.90 <= apply_strength_conduction(1.0, 0.0).multiplier <= 1.15
        assert 0.90 <= apply_strength_conduction(1.0, 10.0).multiplier <= 1.15

    def test_determinism_and_frozen(self):
        r1 = apply_strength_conduction(0.5, 7.0)
        r2 = apply_strength_conduction(0.5, 7.0)
        assert r1 == r2
        assert isinstance(r1, ConductionResult)
        with pytest.raises(Exception):
            r1.multiplier = 2.0
