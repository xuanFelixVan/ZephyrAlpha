# [A_test] module_id: SRC-TST-0832 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_en_002_enforcement_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit code reflects pass/fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

from zephyr.gov_enforcement.rule_enforcement.invariants.en_002_enforcement_validator import (
    VALID_ENFORCEMENT_MODES,
    EnforcementResult,
    _load_contracts,
    check,
    run_check,
)


class TestValidEnforcementModes:
    def test_is_set(self):
        assert isinstance(VALID_ENFORCEMENT_MODES, set)

    def test_contains_block(self):
        assert "block" in VALID_ENFORCEMENT_MODES

    def test_contains_warn(self):
        assert "warn" in VALID_ENFORCEMENT_MODES

    def test_contains_log(self):
        assert "log" in VALID_ENFORCEMENT_MODES

    def test_contains_shadow(self):
        assert "shadow" in VALID_ENFORCEMENT_MODES

    def test_contains_strict(self):
        assert "strict" in VALID_ENFORCEMENT_MODES

    def test_exactly_five_modes(self):
        assert len(VALID_ENFORCEMENT_MODES) == 5

    def test_all_lowercase(self):
        for mode in VALID_ENFORCEMENT_MODES:
            assert mode == mode.lower()


class TestEnforcementResult:
    def test_passed_summary(self):
        er = EnforcementResult(passed=True, total_contracts=5)
        assert er.summary() == "[PASS] EN-002: All 5 P0 contracts have enforcement declared"

    def test_failed_summary(self):
        er = EnforcementResult(
            passed=False,
            total_contracts=3,
            violations=["CTR-001: invalid enforcement_mode 'unknown'"],
        )
        summary = er.summary()
        assert "[FAIL] EN-002:" in summary
        assert "1 violation(s)" in summary
        assert "CTR-001" in summary

    def test_failed_summary_multiple_violations(self):
        er = EnforcementResult(
            passed=False,
            total_contracts=3,
            violations=["v1", "v2"],
        )
        summary = er.summary()
        assert "2 violation(s)" in summary

    def test_default_values(self):
        er = EnforcementResult(passed=True)
        assert er.total_contracts == 0
        assert er.violations == []
        assert er.warnings == []

    def test_passed_true_with_warnings(self):
        er = EnforcementResult(passed=True, total_contracts=2, warnings=["w1"])
        assert er.passed is True
        assert len(er.warnings) == 1


class TestLoadContracts:
    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator.CONTRACTS_PATH")
    def test_loads_yaml(self, mock_path, tmp_path):
        contract_file = tmp_path / "contracts.yaml"
        contract_file.write_text(
            "contracts:\n  - id: CTR-001\n    priority: P0\n",
            encoding="utf-8",
        )
        mock_path.__str__ = lambda s: str(contract_file)
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__ = lambda s: s
            mock_open.return_value.__exit__ = lambda s, *a: None
            mock_open.return_value.read.return_value = contract_file.read_text(encoding="utf-8")

    def test_load_contracts_returns_dict(self):
        result = _load_contracts()
        assert isinstance(result, dict)


class TestRunCheck:
    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_empty_contracts_passes(self, mock_load):
        mock_load.return_value = {"contracts": []}
        result = run_check()
        assert result.passed is True
        assert result.total_contracts == 0

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_p0_with_valid_enforcement_mode(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-001", "priority": "P0", "enforcement_mode": "block"},
            ]
        }
        result = run_check()
        assert result.passed is True
        assert result.total_contracts == 1

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_p0_with_invalid_enforcement_mode(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-002", "priority": "P0", "enforcement_mode": "unknown"},
            ]
        }
        result = run_check()
        assert result.passed is False
        assert len(result.violations) == 1
        assert "invalid enforcement_mode" in result.violations[0]

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_p0_missing_enforcement_mode_warns(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-003", "priority": "P0"},
            ]
        }
        result = run_check()
        assert result.passed is True
        assert len(result.warnings) >= 1
        assert "missing enforcement_mode" in result.warnings[0]

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_enforcement_action_as_fallback(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-004", "priority": "P0", "enforcement_action": "warn"},
            ]
        }
        result = run_check()
        assert result.passed is True

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_enforcement_action_invalid(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-005", "priority": "P0", "enforcement_action": "invalid"},
            ]
        }
        result = run_check()
        assert result.passed is False
        assert len(result.violations) == 1

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_non_p0_no_enforcement_ok(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-006", "priority": "P2"},
            ]
        }
        result = run_check()
        assert result.passed is True
        assert result.total_contracts == 0

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_all_valid_modes_accepted(self, mock_load):
        contracts = [
            {"id": f"CTR-{i}", "priority": "P0", "enforcement_mode": mode}
            for i, mode in enumerate(VALID_ENFORCEMENT_MODES)
        ]
        mock_load.return_value = {"contracts": contracts}
        result = run_check()
        assert result.passed is True
        assert result.total_contracts == 5

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_no_contracts_key(self, mock_load):
        mock_load.return_value = {}
        result = run_check()
        assert result.passed is True
        assert result.total_contracts == 0

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator._load_contracts")
    def test_mixed_valid_and_invalid(self, mock_load):
        mock_load.return_value = {
            "contracts": [
                {"id": "CTR-GOOD", "priority": "P0", "enforcement_mode": "block"},
                {"id": "CTR-BAD", "priority": "P0", "enforcement_mode": "nonsense"},
            ]
        }
        result = run_check()
        assert result.passed is False
        assert result.total_contracts == 2
        assert len(result.violations) == 1


class TestCheck:
    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator.run_check")
    def test_returns_tuple(self, mock_run):
        mock_run.return_value = EnforcementResult(passed=True, total_contracts=3)
        passed, msg = check()
        assert isinstance(passed, bool)
        assert isinstance(msg, str)

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator.run_check")
    def test_pass(self, mock_run):
        mock_run.return_value = EnforcementResult(passed=True, total_contracts=5)
        passed, msg = check()
        assert passed is True
        assert "[PASS]" in msg

    @patch("zephyr.governance.rule_enforcement.invariants.en_002_enforcement_validator.run_check")
    def test_fail(self, mock_run):
        mock_run.return_value = EnforcementResult(passed=False, total_contracts=1, violations=["v1"])
        passed, msg = check()
        assert passed is False
        assert "[FAIL]" in msg
