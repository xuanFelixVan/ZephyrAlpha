# [A_test] module_id: MOD-GOV_contract | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_contract
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] All exit codes 0-50 mapped; gate actions in PIPELINE_ACTIONS; resolve_exit_code returns 4 keys
# [MODIFY-GUARD] blueprint.md §4
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError on invariant violation
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.rollback.contract import (
    EXIT_CODE_TO_GATE_ACTION,
    PIPELINE_ACTIONS,
    RollbackExitCode,
    get_gate_action,
    get_pipeline_action,
    resolve_exit_code,
)


class TestRollbackExitCode:
    def test_is_int_enum(self):
        assert issubclass(RollbackExitCode, int)

    def test_success_value(self):
        assert RollbackExitCode.SUCCESS == 0

    def test_all_codes_unique(self):
        values = [e.value for e in RollbackExitCode]
        assert len(values) == len(set(values))

    def test_all_codes_non_negative(self):
        for code in RollbackExitCode:
            assert code.value >= 0

    def test_critical_codes_exist(self):
        assert RollbackExitCode.G6_SECRETS_LEAK == 22
        assert RollbackExitCode.SANDBOX_BREACH == 25
        assert RollbackExitCode.KILL_SWITCH_L3_GLOBAL == 29
        assert RollbackExitCode.CREDENTIAL_LEAK_DETECTED == 43

    def test_enum_member_count(self):
        assert len(RollbackExitCode) == 51

    def test_exit_code_alias(self):
        from zephyr.infrastructure.rollback.contract import ExitCode

        assert ExitCode is RollbackExitCode


class TestExitCodeToGateAction:
    def test_success_maps_to_pass(self):
        gate, desc = EXIT_CODE_TO_GATE_ACTION[0]
        assert gate == "PASS"

    def test_all_defined_codes_have_mapping(self):
        for code in RollbackExitCode:
            assert code.value in EXIT_CODE_TO_GATE_ACTION

    def test_mapping_structure(self):
        for code_val, (gate, desc) in EXIT_CODE_TO_GATE_ACTION.items():
            assert isinstance(gate, str)
            assert isinstance(desc, str)
            assert len(gate) > 0
            assert len(desc) > 0

    def test_l3_kill_codes(self):
        l3_codes = [22, 25, 39, 43]
        for code in l3_codes:
            gate, _ = EXIT_CODE_TO_GATE_ACTION[code]
            assert gate == "L3_KILL"


class TestPipelineActions:
    def test_all_gate_actions_have_pipeline_action(self):
        for code_val, (gate, _) in EXIT_CODE_TO_GATE_ACTION.items():
            if gate != "UNKNOWN":
                assert gate in PIPELINE_ACTIONS, f"gate={gate} missing from PIPELINE_ACTIONS"

    def test_pass_action(self):
        assert "Continue" in PIPELINE_ACTIONS["PASS"]

    def test_fail_action(self):
        assert "Stop" in PIPELINE_ACTIONS["FAIL"]

    def test_l3_kill_action(self):
        assert "L3 Global Kill" in PIPELINE_ACTIONS["L3_KILL"]


class TestGetGateAction:
    def test_known_code(self):
        gate, desc = get_gate_action(0)
        assert gate == "PASS"

    def test_unknown_code(self):
        gate, desc = get_gate_action(9999)
        assert gate == "UNKNOWN"
        assert "Unknown" in desc

    def test_negative_code(self):
        gate, desc = get_gate_action(-1)
        assert gate == "UNKNOWN"

    def test_all_rollabck_codes(self):
        for code in RollbackExitCode:
            gate, desc = get_gate_action(code.value)
            assert gate != "UNKNOWN"


class TestGetPipelineAction:
    def test_known_gate(self):
        action = get_pipeline_action("PASS")
        assert "Continue" in action

    def test_unknown_gate(self):
        action = get_pipeline_action("NONEXISTENT")
        assert "Unknown" in action

    def test_empty_string(self):
        action = get_pipeline_action("")
        assert "Unknown" in action


class TestResolveExitCode:
    def test_success(self):
        result = resolve_exit_code(0)
        assert result["exit_code"] == "0"
        assert result["gate_action"] == "PASS"
        assert "pipeline_action" in result
        assert "description" in result

    def test_returns_four_keys(self):
        result = resolve_exit_code(22)
        assert len(result) == 4
        assert "exit_code" in result
        assert "gate_action" in result
        assert "description" in result
        assert "pipeline_action" in result

    def test_unknown_code(self):
        result = resolve_exit_code(9999)
        assert result["gate_action"] == "UNKNOWN"

    def test_credential_leak(self):
        result = resolve_exit_code(43)
        assert result["gate_action"] == "L3_KILL"
        assert "Credential" in result["description"]

    def test_secrets_leak(self):
        result = resolve_exit_code(22)
        assert result["gate_action"] == "L3_KILL"

    def test_all_codes_resolve(self):
        for code in RollbackExitCode:
            result = resolve_exit_code(code.value)
            assert result["gate_action"] != "UNKNOWN"
