# [A_test] module_id: MOD-GOV_governance_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-510 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.governance.test_governance_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: governance core (PhaseCheckRegistry + architecture_contracts)"""

import pytest

from zephyr.governance.architecture_governance.architecture_contracts import (
    ARCH_BASE_CONTRACTS,
    CircuitBreaker,
    CircuitBreakerState,
    Contract,
    generate_client_order_id,
)
from zephyr.governance.ops_governance.phase_check_registry import (
    _CHECK_MAP,
    GateResult,
    PhaseCheckRegistry,
    run_check,
)

# ---------------------------------------------------------------------------
# PhaseCheckRegistry
# ---------------------------------------------------------------------------


class TestGateResult:
    def test_values(self):
        assert GateResult.GREEN.value == "GREEN"
        assert GateResult.YELLOW.value == "YELLOW"
        assert GateResult.RED.value == "RED"

    def test_is_str_enum(self):
        assert isinstance(GateResult.GREEN, str)
        assert GateResult.GREEN == "GREEN"


class TestPhaseCheckRegistry:
    def test_check_count_matches_map(self):
        assert PhaseCheckRegistry.check_count() == len(_CHECK_MAP)

    def test_registered_checks_returns_list(self):
        checks = PhaseCheckRegistry.registered_checks()
        assert isinstance(checks, list)
        assert len(checks) > 0

    def test_get_known_check(self):
        func = PhaseCheckRegistry.get("gate_session_manager")
        assert func is not None
        assert callable(func)

    def test_get_unknown_check_returns_none(self):
        assert PhaseCheckRegistry.get("gate_nonexistent_xyz") is None

    def test_all_registered_checks_are_callable(self):
        for name in PhaseCheckRegistry.registered_checks():
            func = PhaseCheckRegistry.get(name)
            assert callable(func), f"Check '{name}' is not callable"

    def test_phase0_checks_exist(self):
        phase0_names = [
            "gate_session_manager",
            "gate_session_continuity",
            "gate_lock_protocol",
            "gate_blueprint_mandatory",
            "gate_path_resolver",
            "gate_script_manifest",
            "gate_env_vars",
        ]
        for name in phase0_names:
            assert PhaseCheckRegistry.get(name) is not None, f"Phase 0 check '{name}' missing"

    def test_phase1_checks_exist(self):
        phase1_names = [
            "gate_data_vendor_integration",
            "gate_factor_factory",
            "gate_feedback_loop",
            "gate_db_integrity",
        ]
        for name in phase1_names:
            assert PhaseCheckRegistry.get(name) is not None, f"Phase 1 check '{name}' missing"

    def test_phase2_checks_exist(self):
        phase2_names = [
            "gate_strategy_pipeline",
            "gate_kill_switch",
            "gate_drift_detection",
        ]
        for name in phase2_names:
            assert PhaseCheckRegistry.get(name) is not None, f"Phase 2 check '{name}' missing"


class TestRunCheck:
    def test_unknown_check_returns_yellow(self):
        result = run_check("gate_nonexistent_xyz")
        assert result == GateResult.YELLOW

    def test_known_check_returns_gate_result(self):
        result = run_check("gate_env_vars")
        assert isinstance(result, GateResult)

    def test_blueprint_mandatory_returns_green_or_red(self):
        result = run_check("gate_blueprint_mandatory")
        assert result in (GateResult.GREEN, GateResult.RED)

    def test_feedback_loop_check(self):
        result = run_check("gate_feedback_loop")
        assert isinstance(result, GateResult)
        assert result in (GateResult.GREEN, GateResult.YELLOW)


# ---------------------------------------------------------------------------
# Architecture Contracts
# ---------------------------------------------------------------------------


class TestContract:
    def test_contract_creation(self):
        c = Contract(name="test", description="desc", status="active")
        assert c.name == "test"
        assert c.description == "desc"
        assert c.status == "active"

    def test_contract_default_status(self):
        c = Contract(name="test", description="desc")
        assert c.status == "active"


class TestArchBaseContracts:
    def test_five_base_contracts(self):
        assert len(ARCH_BASE_CONTRACTS) == 5

    def test_c1_communication_exists(self):
        assert "C1_COMMUNICATION" in ARCH_BASE_CONTRACTS

    def test_c4_circuit_breaker_exists(self):
        assert "C4_CIRCUIT_BREAKER" in ARCH_BASE_CONTRACTS

    def test_all_contracts_have_name_and_description(self):
        for key, contract in ARCH_BASE_CONTRACTS.items():
            assert contract.name, f"Contract {key} missing name"
            assert contract.description, f"Contract {key} missing description"


class TestCircuitBreaker:
    @pytest.fixture
    def breaker(self):
        return CircuitBreaker()

    def test_initial_state_closed(self, breaker):
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_record_failure_increments(self, breaker):
        breaker.record_failure()
        assert breaker._failure_count == 1
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_opens_after_threshold(self, breaker):
        for _ in range(5):
            breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN

    def test_attempt_reset_from_open(self, breaker):
        for _ in range(5):
            breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        breaker.attempt_reset()
        assert breaker.state == CircuitBreakerState.HALF_OPEN

    def test_success_in_half_open_closes(self, breaker):
        for _ in range(5):
            breaker.record_failure()
        breaker.attempt_reset()
        assert breaker.state == CircuitBreakerState.HALF_OPEN
        breaker.record_success()
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker._failure_count == 0

    def test_success_in_closed_does_nothing(self, breaker):
        breaker.record_success()
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_attempt_reset_in_closed_does_nothing(self, breaker):
        breaker.attempt_reset()
        assert breaker.state == CircuitBreakerState.CLOSED


class TestCircuitBreakerState:
    def test_values(self):
        assert CircuitBreakerState.CLOSED.value == "CLOSED"
        assert CircuitBreakerState.OPEN.value == "OPEN"
        assert CircuitBreakerState.HALF_OPEN.value == "HALF_OPEN"


class TestGenerateClientOrderId:
    def test_returns_string(self):
        oid = generate_client_order_id()
        assert isinstance(oid, str)
        assert len(oid) > 0

    def test_format_contains_dash(self):
        oid = generate_client_order_id()
        assert "-" in oid

    def test_unique_per_call(self):
        ids = {generate_client_order_id() for _ in range(20)}
        assert len(ids) == 20
