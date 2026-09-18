# [BLUEPRINT] MOD-POS-027 | (auto-injected by S4 reconciler，gw-tdm-20260909 修正为模块级 ID) | §
# [TTL] permanent
# [DOMAIN] D_POSITION
"""MOD-POS-027 pyramiding_rules 单元测试（红蓝对抗：红-边界/红-竞态语义/红-契约）。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.position.core.defensive_asset_whitelist import CircuitLevel
from zephyr.position.core.pyramiding_rules import (
    GateCode,
    PyramidingConfig,
    PyramidingError,
    PyramidingGateRequest,
    PyramidPlanRequest,
    PyramidingPhase,
    check_pyramiding_eligibility,
    get_default_config,
    plan_pyramid_addition,
)


def _ok_gate(**kw) -> PyramidingGateRequest:
    base = dict(
        current_price=Decimal("11.00"),
        cost_price=Decimal("10.00"),
        sentiment_phase=PyramidingPhase.EXPANSION,
        strategy_affinity=0.5,
        circuit_level=CircuitLevel.L0,
    )
    base.update(kw)
    return PyramidingGateRequest(**base)


def _ok_plan(**kw) -> PyramidPlanRequest:
    base = dict(
        current_price=Decimal("11.00"),
        last_add_price=None,
        last_add_price_below=False,
        tranches_done=0,
        remaining_budget=Decimal("30000"),
        confirm_entry_ok=True,
    )
    base.update(kw)
    return PyramidingGateRequest, base


class TestEligibilityGates:
    """P3-01 四重门逐门验证。"""

    def test_all_pass(self):
        ok, code = check_pyramiding_eligibility(_ok_gate())
        assert ok and code is GateCode.ALLOWED

    def test_no_averaging_down_on_losses_redline(self):
        # 平价也拒（现价≤成本恒拒——红线）
        ok, code = check_pyramiding_eligibility(_ok_gate(current_price=Decimal("10.00")))
        assert not ok and code is GateCode.NOT_PROFITABLE
        ok2, code2 = check_pyramiding_eligibility(_ok_gate(current_price=Decimal("9.00")))
        assert not ok2 and code2 is GateCode.NOT_PROFITABLE

    @pytest.mark.parametrize("phase", [
        PyramidingPhase.ICE, PyramidingPhase.EXCITEMENT, PyramidingPhase.EBB,
    ])
    def test_closed_phases(self, phase):
        ok, code = check_pyramiding_eligibility(_ok_gate(sentiment_phase=phase))
        assert not ok and code is GateCode.PHASE_CLOSED

    @pytest.mark.parametrize("phase", [PyramidingPhase.IGNITION, PyramidingPhase.EXPANSION])
    def test_open_phases(self, phase):
        ok, _ = check_pyramiding_eligibility(_ok_gate(sentiment_phase=phase))
        assert ok

    def test_zero_affinity_rejected(self):
        ok, code = check_pyramiding_eligibility(_ok_gate(strategy_affinity=0.0))
        assert not ok and code is GateCode.AFFINITY_NOT_POSITIVE

    def test_negative_affinity_rejected(self):
        ok, code = check_pyramiding_eligibility(_ok_gate(strategy_affinity=-0.2))
        assert not ok and code is GateCode.AFFINITY_NOT_POSITIVE

    @pytest.mark.parametrize("level", [CircuitLevel.L2, CircuitLevel.L3, CircuitLevel.L4])
    def test_circuit_ban(self, level):
        ok, code = check_pyramiding_eligibility(_ok_gate(circuit_level=level))
        assert not ok and code is GateCode.CIRCUIT_BAN

    @pytest.mark.parametrize("level", [CircuitLevel.L0, CircuitLevel.L1])
    def test_circuit_ok(self, level):
        ok, _ = check_pyramiding_eligibility(_ok_gate(circuit_level=level))
        assert ok


class TestPyramidPlan:
    """P3-02 三规则：递减/阶梯/限次。"""

    def test_first_tranche_half_budget(self):
        ok, code, plan = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("11.00"),
                last_add_price=None,
                last_add_price_below=False,
                tranches_done=0,
                remaining_budget=Decimal("30000"),
                confirm_entry_ok=True,
            )
        )
        assert ok and code is GateCode.ALLOWED
        assert plan.amount == Decimal("15000.00")
        assert plan.tranche_no == 1

    def test_decreasing_halves(self):
        def _plan(done: int, budget: str):
            return plan_pyramid_addition(
                PyramidPlanRequest(
                    current_price=Decimal("12.00"),
                    last_add_price=Decimal("10.00"),
                    last_add_price_below=False,
                    tranches_done=done,
                    remaining_budget=Decimal(budget),
                    confirm_entry_ok=True,
                )
            )
        _, _, p1 = _plan(1, "15000")
        assert p1.amount == Decimal("7500.00")  # 剩余减半
        _, _, p2 = _plan(2, "7500")
        assert p2.amount == Decimal("3750.00")  # 再减半

    def test_max_three_tranches(self):
        ok, code, plan = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("12.00"),
                last_add_price=Decimal("10.00"),
                last_add_price_below=False,
                tranches_done=3,
                remaining_budget=Decimal("10000"),
                confirm_entry_ok=True,
            )
        )
        assert not ok and code is GateCode.MAX_TRANCHE and plan is None

    def test_ladder_min_not_met(self):
        ok, code, _ = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("10.24"),  # 恰好 2.4% < 2.5%
                last_add_price=Decimal("10.00"),
                last_add_price_below=False,
                tranches_done=1,
                remaining_budget=Decimal("10000"),
                confirm_entry_ok=True,
            )
        )
        assert not ok and code is GateCode.LADDER_NOT_MET

    def test_ladder_exact_boundary_passes(self):
        ok, code, _ = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("10.25"),  # 恰好 2.5%
                last_add_price=Decimal("10.00"),
                last_add_price_below=False,
                tranches_done=1,
                remaining_budget=Decimal("10000"),
                confirm_entry_ok=True,
            )
        )
        assert ok and code is GateCode.ALLOWED

    def test_below_last_add_stops_plan(self):
        ok, code, _ = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("9.50"),
                last_add_price=Decimal("10.00"),
                last_add_price_below=True,
                tranches_done=1,
                remaining_budget=Decimal("10000"),
                confirm_entry_ok=True,
            )
        )
        assert not ok and code is GateCode.BELOW_LAST_ADD

    def test_entry_reconfirmation_required(self):
        ok, code, _ = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("12.00"),
                last_add_price=Decimal("10.00"),
                last_add_price_below=False,
                tranches_done=1,
                remaining_budget=Decimal("10000"),
                confirm_entry_ok=False,
            )
        )
        assert not ok and code is GateCode.ENTRY_NOT_RECONFIRMED

    def test_budget_exhausted(self):
        ok, code, _ = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("12.00"),
                last_add_price=Decimal("10.00"),
                last_add_price_below=False,
                tranches_done=1,
                remaining_budget=Decimal("0"),
                confirm_entry_ok=True,
            )
        )
        assert not ok and code is GateCode.BUDGET_EXHAUSTED


class TestFailClosed:
    """红-契约 + 红-故障。"""

    def test_float_price_rejected(self):
        with pytest.raises(PyramidingError):
            check_pyramiding_eligibility(
                PyramidingGateRequest(
                    current_price=11.0,  # type: ignore[arg-type]
                    cost_price=Decimal("10.00"),
                    sentiment_phase=PyramidingPhase.IGNITION,
                    strategy_affinity=0.5,
                    circuit_level=CircuitLevel.L0,
                )
            )

    def test_negative_budget_rejected(self):
        with pytest.raises(PyramidingError):
            plan_pyramid_addition(
                PyramidPlanRequest(
                    current_price=Decimal("12.00"),
                    last_add_price=None,
                    last_add_price_below=False,
                    tranches_done=0,
                    remaining_budget=Decimal("-1"),
                    confirm_entry_ok=True,
                )
            )

    def test_unknown_phase_and_circuit(self):
        with pytest.raises(PyramidingError):
            check_pyramiding_eligibility(_ok_gate(sentiment_phase="MANIA"))
        with pytest.raises(PyramidingError):
            check_pyramiding_eligibility(_ok_gate(circuit_level="L9"))

    def test_custom_config_validation(self):
        with pytest.raises(PyramidingError):
            PyramidingConfig(max_tranches=0)
        with pytest.raises(PyramidingError):
            PyramidingConfig(ladder_min_pct=1.5)

    def test_tiny_budget_rounds_to_reject(self):
        ok, code, _ = plan_pyramid_addition(
            PyramidPlanRequest(
                current_price=Decimal("12.00"),
                last_add_price=Decimal("10.00"),
                last_add_price_below=False,
                tranches_done=1,
                remaining_budget=Decimal("0.001"),
                confirm_entry_ok=True,
            )
        )
        assert not ok and code is GateCode.BUDGET_EXHAUSTED

    def test_determinism(self):
        req = PyramidPlanRequest(
            current_price=Decimal("11.00"),
            last_add_price=None,
            last_add_price_below=False,
            tranches_done=0,
            remaining_budget=Decimal("30000"),
            confirm_entry_ok=True,
        )
        assert plan_pyramid_addition(req) == plan_pyramid_addition(req)
