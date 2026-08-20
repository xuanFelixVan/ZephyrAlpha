# [A_test] module_id: MOD-GOV_paper_live_transition | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_paper_live_transition
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] TransitionPhase order: PARALLEL→SHADOW→GRAY_RAMP;valid_transition only sequential
# [MODIFY-GUARD] src/zephyr/rollback/paper_live_transition.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError on invalid phase;IndexError on out-of-range
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=stable | safety=H | ai_autonomy=human_gated
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.governance.lifecycle_governance.paper_live_transition import (
    DEFAULT_GATE_THRESHOLDS,
    PHASE_ORDER,
    PHASE_SPECS,
    GateThresholds,
    PhaseSpec,
    TransitionPhase,
    TransitionState,
    create_transition_state,
    get_next_phase,
    get_phase_spec,
    valid_transition,
    validate_gate_thresholds,
)


class TestTransitionPhaseEnum:
    def test_enum_values(self):
        assert TransitionPhase.PARALLEL.value == "PARALLEL"
        assert TransitionPhase.SHADOW.value == "SHADOW"
        assert TransitionPhase.GRAY_RAMP.value == "GRAY_RAMP"

    def test_enum_member_count(self):
        assert len(TransitionPhase) == 3

    def test_enum_from_string(self):
        assert TransitionPhase("PARALLEL") == TransitionPhase.PARALLEL


class TestPhaseSpec:
    def test_phase_spec_creation(self):
        spec = PhaseSpec(
            phase=TransitionPhase.PARALLEL,
            name="test",
            duration_days=10,
            description="test desc",
            key_gates=["gate1"],
        )
        assert spec.phase == TransitionPhase.PARALLEL
        assert spec.name == "test"
        assert spec.duration_days == 10
        assert spec.key_gates == ["gate1"]

    def test_phase_spec_default_gates(self):
        spec = PhaseSpec(
            phase=TransitionPhase.SHADOW,
            name="test",
            duration_days=5,
            description="test",
        )
        assert spec.key_gates == []

    def test_phase_specs_all_defined(self):
        for phase in TransitionPhase:
            assert phase in PHASE_SPECS
            assert isinstance(PHASE_SPECS[phase], PhaseSpec)

    def test_phase_specs_positive_duration(self):
        for phase in TransitionPhase:
            assert PHASE_SPECS[phase].duration_days > 0


class TestGetPhaseSpec:
    def test_valid_phase(self):
        spec = get_phase_spec(TransitionPhase.PARALLEL)
        assert spec is not None
        assert spec.phase == TransitionPhase.PARALLEL

    def test_all_phases_return_spec(self):
        for phase in TransitionPhase:
            spec = get_phase_spec(phase)
            assert spec is not None

    def test_nonexistent_phase_returns_none(self):
        result = get_phase_spec("INVALID_PHASE")
        assert result is None


class TestValidTransition:
    def test_parallel_to_shadow(self):
        assert valid_transition(TransitionPhase.PARALLEL, TransitionPhase.SHADOW) is True

    def test_shadow_to_gray_ramp(self):
        assert valid_transition(TransitionPhase.SHADOW, TransitionPhase.GRAY_RAMP) is True

    def test_skip_transition_invalid(self):
        assert valid_transition(TransitionPhase.PARALLEL, TransitionPhase.GRAY_RAMP) is False

    def test_reverse_transition_invalid(self):
        assert valid_transition(TransitionPhase.SHADOW, TransitionPhase.PARALLEL) is False

    def test_same_phase_invalid(self):
        assert valid_transition(TransitionPhase.PARALLEL, TransitionPhase.PARALLEL) is False

    def test_gray_ramp_to_anything_invalid(self):
        assert valid_transition(TransitionPhase.GRAY_RAMP, TransitionPhase.PARALLEL) is False
        assert valid_transition(TransitionPhase.GRAY_RAMP, TransitionPhase.SHADOW) is False


class TestGetNextPhase:
    def test_parallel_next_is_shadow(self):
        assert get_next_phase(TransitionPhase.PARALLEL) == TransitionPhase.SHADOW

    def test_shadow_next_is_gray_ramp(self):
        assert get_next_phase(TransitionPhase.SHADOW) == TransitionPhase.GRAY_RAMP

    def test_gray_ramp_has_no_next(self):
        assert get_next_phase(TransitionPhase.GRAY_RAMP) is None


class TestTransitionState:
    def test_creation(self):
        state = TransitionState(
            current_phase=TransitionPhase.PARALLEL,
            started_at=datetime.now(UTC).isoformat(),
        )
        assert state.current_phase == TransitionPhase.PARALLEL
        assert state.ramping_percentage == 0.0
        assert state.completed_at is None

    def test_elapsed_days(self):
        past = (datetime.now(UTC) - timedelta(days=2)).isoformat()
        state = TransitionState(
            current_phase=TransitionPhase.PARALLEL,
            started_at=past,
        )
        assert state.elapsed_days >= 2.0

    def test_ramp_up_increments(self):
        state = TransitionState(
            current_phase=TransitionPhase.GRAY_RAMP,
            started_at=datetime.now(UTC).isoformat(),
            ramping_percentage=0.0,
        )
        result = state.ramp_up(20.0)
        assert result == 20.0
        assert state.ramping_percentage == 20.0

    def test_ramp_up_caps_at_100(self):
        state = TransitionState(
            current_phase=TransitionPhase.GRAY_RAMP,
            started_at=datetime.now(UTC).isoformat(),
            ramping_percentage=90.0,
        )
        result = state.ramp_up(20.0)
        assert result == 100.0
        assert state.ramping_percentage == 100.0

    def test_ramp_up_multiple_steps(self):
        state = TransitionState(
            current_phase=TransitionPhase.GRAY_RAMP,
            started_at=datetime.now(UTC).isoformat(),
            ramping_percentage=0.0,
        )
        state.ramp_up(20.0)
        state.ramp_up(30.0)
        assert state.ramping_percentage == 50.0


class TestCreateTransitionState:
    def test_returns_transition_state(self):
        state = create_transition_state()
        assert isinstance(state, TransitionState)
        assert state.current_phase == TransitionPhase.PARALLEL
        assert state.ramping_percentage == 0.0
        assert state.completed_at is None

    def test_started_at_is_valid_isoformat(self):
        state = create_transition_state()
        parsed = datetime.fromisoformat(state.started_at)
        assert parsed is not None


class TestPhaseOrder:
    def test_phase_order_sequential(self):
        assert PHASE_ORDER[TransitionPhase.PARALLEL] == 0
        assert PHASE_ORDER[TransitionPhase.SHADOW] == 1
        assert PHASE_ORDER[TransitionPhase.GRAY_RAMP] == 2

    def test_phase_order_covers_all_phases(self):
        for phase in TransitionPhase:
            assert phase in PHASE_ORDER


# ============== 门禁阈值配置化(53号 §6 校准配置化) ==============


class TestGateThresholds:
    def test_defaults_unchanged(self):
        """默认值与机制初始值逐字一致(53号§3.3/§3.5)"""
        t = GateThresholds()
        assert t.parallel_min_days == 30
        assert t.shadow_min_days == 14
        assert t.gray_ramp_min_days == 30
        assert t.signal_match_min == 0.999
        assert t.slippage_diff_max_bp == 1.0
        assert t.fill_rate_min == 0.99
        assert t.shadow_pnl_correlation_min == 0.95
        assert t.settlement_match_min == 1.0
        assert t.latency_max_ms == 100.0
        assert t.ramp_drawdown_max == 0.01
        assert t.ramp_daily_loss_max == 0.03
        assert t.ramp_steps == (1.0, 5.0, 20.0, 50.0, 100.0)
        assert t.observation_min_months == 6
        assert t.min_trades_floor == 30

    def test_phase_specs_derived_from_thresholds(self):
        """PHASE_SPECS duration_days/key_gates 由默认阈值派生且与既有字面量一致"""
        assert PHASE_SPECS[TransitionPhase.PARALLEL].duration_days == 30
        assert PHASE_SPECS[TransitionPhase.SHADOW].duration_days == 14
        assert PHASE_SPECS[TransitionPhase.GRAY_RAMP].duration_days == 30
        assert PHASE_SPECS[TransitionPhase.PARALLEL].key_gates == [
            "paper_live_signal_match >= 99.9%", "slippage_diff < 1bp", "fill_rate >= 99%",
        ]
        assert PHASE_SPECS[TransitionPhase.SHADOW].key_gates == [
            "shadow_pnl_correlation >= 0.95", "settlement_match 100%", "latency < 100ms",
        ]
        assert PHASE_SPECS[TransitionPhase.GRAY_RAMP].key_gates == [
            "drawdown < 1% per ramp step", "no circuit_breaker triggers", "daily_loss < 3%",
        ]

    def test_default_singleton(self):
        assert isinstance(DEFAULT_GATE_THRESHOLDS, GateThresholds)

    def test_frozen(self):
        t = GateThresholds()
        with pytest.raises(Exception):
            t.latency_max_ms = 200.0  # type: ignore[misc]

    def test_invalid_days(self):
        with pytest.raises(ValueError):
            GateThresholds(parallel_min_days=0)

    def test_invalid_ratios(self):
        with pytest.raises(ValueError):
            GateThresholds(signal_match_min=1.5)
        with pytest.raises(ValueError):
            GateThresholds(fill_rate_min=0.0)
        with pytest.raises(ValueError):
            GateThresholds(shadow_pnl_correlation_min=-0.1)
        with pytest.raises(ValueError):
            GateThresholds(settlement_match_min=2.0)

    def test_invalid_ramp_gates(self):
        with pytest.raises(ValueError):
            GateThresholds(ramp_drawdown_max=0.0)
        with pytest.raises(ValueError):
            GateThresholds(ramp_daily_loss_max=1.0)

    def test_ramp_steps_must_strictly_increase(self):
        with pytest.raises(ValueError):
            GateThresholds(ramp_steps=(1.0, 5.0, 5.0, 100.0))
        with pytest.raises(ValueError):
            GateThresholds(ramp_steps=(100.0, 50.0))

    def test_ramp_steps_must_end_at_100(self):
        with pytest.raises(ValueError):
            GateThresholds(ramp_steps=(1.0, 5.0, 50.0))

    def test_ramp_steps_empty_or_nonpositive(self):
        with pytest.raises(ValueError):
            GateThresholds(ramp_steps=())
        with pytest.raises(ValueError):
            GateThresholds(ramp_steps=(0.0, 100.0))

    def test_invalid_observation_floor(self):
        with pytest.raises(ValueError):
            GateThresholds(observation_min_months=0)
        with pytest.raises(ValueError):
            GateThresholds(min_trades_floor=-1)

    def test_custom_thresholds_accepted(self):
        t = GateThresholds(latency_max_ms=200.0, min_trades_floor=50)
        assert t.latency_max_ms == 200.0
        assert t.min_trades_floor == 50

    def test_validate_gate_thresholds(self):
        t = GateThresholds()
        assert validate_gate_thresholds(t) is t
        with pytest.raises(TypeError):
            validate_gate_thresholds({"latency_max_ms": 100})
