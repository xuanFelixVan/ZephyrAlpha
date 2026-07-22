# [A_test] module_id: MOD-GOV_phase_check_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_phase_check_registry
# [INVARIANTS] _CHECK_MAP keys match PHASE_SEQUENCE gate_checks;all checks return GateResult
# [MODIFY-GUARD] src/zephyr/rollback/phase_check_registry.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateResult.YELLOW on unknown check;GateResult.RED on exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.governance.ops_governance.phase_check_registry import (
    _CHECK_MAP,
    GateResult,
    PhaseCheckRegistry,
    run_check,
)


class TestGateResultEnum:
    def test_enum_values(self):
        assert GateResult.GREEN.value == "GREEN"
        assert GateResult.YELLOW.value == "YELLOW"
        assert GateResult.RED.value == "RED"

    def test_enum_member_count(self):
        assert len(GateResult) == 3

    def test_enum_from_string(self):
        assert GateResult("GREEN") == GateResult.GREEN


class TestPhaseCheckRegistryInstantiation:
    def test_static_methods_accessible(self):
        assert callable(PhaseCheckRegistry.get)
        assert callable(PhaseCheckRegistry.registered_checks)
        assert callable(PhaseCheckRegistry.check_count)


class TestPhaseCheckRegistryGet:
    def test_get_known_check(self):
        func = PhaseCheckRegistry.get("gate_session_manager")
        assert func is not None
        assert callable(func)

    def test_get_unknown_check_returns_none(self):
        func = PhaseCheckRegistry.get("gate_nonexistent_check")
        assert func is None

    def test_get_empty_string_returns_none(self):
        func = PhaseCheckRegistry.get("")
        assert func is None


class TestPhaseCheckRegistryRegisteredChecks:
    def test_registered_checks_returns_list(self):
        checks = PhaseCheckRegistry.registered_checks()
        assert isinstance(checks, list)
        assert len(checks) > 0

    def test_all_checks_start_with_gate_prefix(self):
        checks = PhaseCheckRegistry.registered_checks()
        for check in checks:
            assert check.startswith("gate_") or check.startswith("g_trae_"), (
                f"Check '{check}' missing gate_/g_trae_ prefix"
            )

    def test_registered_checks_match_check_map(self):
        checks = PhaseCheckRegistry.registered_checks()
        assert set(checks) == set(_CHECK_MAP.keys())


class TestPhaseCheckRegistryCheckCount:
    def test_check_count_positive(self):
        count = PhaseCheckRegistry.check_count()
        assert count > 0

    def test_check_count_matches_registered(self):
        count = PhaseCheckRegistry.check_count()
        registered = PhaseCheckRegistry.registered_checks()
        assert count == len(registered)


class TestRunCheck:
    def test_run_check_known_returns_gate_result(self):
        result = run_check("gate_gate_engine_judge")
        assert isinstance(result, GateResult)

    def test_run_check_unknown_returns_yellow(self):
        result = run_check("gate_totally_unknown_check")
        assert result == GateResult.YELLOW

    def test_run_check_exception_returns_red(self):
        with patch.dict(_CHECK_MAP, {"gate_error_test": MagicMock(side_effect=RuntimeError("boom"))}):
            result = run_check("gate_error_test")
            assert result == GateResult.RED

    def test_run_check_empty_string_returns_yellow(self):
        result = run_check("")
        assert result == GateResult.YELLOW


class TestCheckMapConsistency:
    def test_all_check_functions_callable(self):
        for name, func in _CHECK_MAP.items():
            assert callable(func), f"Check '{name}' is not callable"

    def test_check_count_reasonable(self):
        count = PhaseCheckRegistry.check_count()
        assert 40 <= count <= 120, f"Expected 40-120 checks, got {count}"

    def test_no_duplicate_check_names(self):
        checks = PhaseCheckRegistry.registered_checks()
        assert len(checks) == len(set(checks))
