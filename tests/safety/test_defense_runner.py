# [A_test] module_id: SRC-TST-2133 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §16
# [MODULE] zephyr.security.adversarial_validation.defense_runner
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_defense_runner.py
# [TTL] task_bound

import hashlib
from unittest.mock import MagicMock, patch

import pytest

defense_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.defense_runner",
    reason="defense_runner not available",
)
DefenseRunner = defense_mod.DefenseRunner
GateEvaluationError = defense_mod.GateEvaluationError
GATE_MAP = defense_mod.GATE_MAP

validator_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.validator",
    reason="validator not available",
)
RedBlueValidator = validator_mod.RedBlueValidator
SessionError = validator_mod.SessionError

cli_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.cli",
    reason="cli not available",
)

models_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.models",
    reason="models not available",
)
AttackScenario = models_mod.AttackScenario
AttackTier = models_mod.AttackTier
BlastRadiusLevel = models_mod.BlastRadiusLevel
DefenseResult = models_mod.DefenseResult
DefenseSpec = models_mod.DefenseSpec
InjectionSpec = models_mod.InjectionSpec
RedBlueReport = models_mod.RedBlueReport
ResultClass = models_mod.ResultClass
ScenarioResult = models_mod.ScenarioResult
Severity = models_mod.Severity


def make_scenario(
    scenario_id: str = "TEST-001",
    name: str = "test scenario",
    tier: AttackTier = AttackTier.TIER_1,
    severity: Severity = Severity.MEDIUM,
    vector: str = "test_vector",
    gate_id: str = "prompt_injection_filter",
    target_module: str = "test_module",
    payload: str = "test_payload",
    status: str = "active",
) -> AttackScenario:
    return AttackScenario(
        scenario_id=scenario_id,
        name=name,
        tier=tier,
        severity=severity,
        injection=InjectionSpec(vector=vector, target_module=target_module, payload=payload),
        expected_defense=DefenseSpec(gate_id=gate_id, expected="blocked"),
        status=status,
    )


# ===========================================================================
# DefenseRunner — GATE_MAP
# ===========================================================================
class TestGateMap:
    def test_gate_map_is_dict(self):
        assert isinstance(GATE_MAP, dict)

    def test_gate_map_has_entries(self):
        assert len(GATE_MAP) >= 10

    def test_prompt_injection_filter_maps_to_g1(self):
        assert GATE_MAP["prompt_injection_filter"] == "G1"

    def test_immutable_core_verify_maps_to_g1(self):
        assert GATE_MAP["immutable_core.verify"] == "G1"

    def test_circuit_breaker_hard_check_maps_to_g1(self):
        assert GATE_MAP["circuit_breaker.hard_check"] == "G1"

    def test_drift_engine_reconcile_maps_to_g2(self):
        assert GATE_MAP["drift_engine.reconcile"] == "G2"

    def test_schema_registry_validate_maps_to_g2(self):
        assert GATE_MAP["schema_registry.validate"] == "G2"

    def test_audit_integrity_check_maps_to_g2(self):
        assert GATE_MAP["audit_integrity_check"] == "G2"

    def test_gates_registry_verify_maps_to_g1(self):
        assert GATE_MAP["gates_registry.verify"] == "G1"

    def test_event_schemas_validate_maps_to_g3(self):
        assert GATE_MAP["event_schemas.validate"] == "G3"

    def test_kb_verify_integrity_maps_to_g3(self):
        assert GATE_MAP["kb.verify_integrity"] == "G3"

    def test_budget_engine_pre_flight_maps_to_g3(self):
        assert GATE_MAP["budget_engine.pre_flight"] == "G3"

    def test_burn_rate_monitor_maps_to_g3(self):
        assert GATE_MAP["burn_rate_monitor"] == "G3"

    def test_mcp_auth_verify_maps_to_g1(self):
        assert GATE_MAP["mcp_auth.verify"] == "G1"

    def test_all_values_are_gate_ids(self):
        for v in GATE_MAP.values():
            assert isinstance(v, str)
            assert v.startswith("G")


# ===========================================================================
# DefenseRunner — 导入与实例化
# ===========================================================================
class TestDefenseRunnerImport:
    def test_import_success(self):
        assert DefenseRunner is not None

    def test_instantiation(self):
        runner = DefenseRunner()
        assert runner is not None

    def test_has_run_defense(self):
        runner = DefenseRunner()
        assert hasattr(runner, "run_defense")

    def test_has_evaluate_gate(self):
        runner = DefenseRunner()
        assert hasattr(runner, "_evaluate_gate")

    def test_has_try_real_gate(self):
        runner = DefenseRunner()
        assert hasattr(runner, "_try_real_gate")

    def test_has_simulate_gate(self):
        runner = DefenseRunner()
        assert hasattr(runner, "_simulate_gate")

    def test_has_results(self):
        runner = DefenseRunner()
        assert hasattr(runner, "results")

    def test_has_close(self):
        runner = DefenseRunner()
        assert hasattr(runner, "close")

    def test_initial_results_empty(self):
        runner = DefenseRunner()
        assert runner.results() == []

    def test_jsonl_output_default_false(self):
        runner = DefenseRunner()
        assert runner.jsonl_output is False

    def test_jsonl_output_true(self):
        runner = DefenseRunner(jsonl_output=True)
        assert runner.jsonl_output is True

    def test_gate_evaluation_error_is_runtime_error(self):
        assert issubclass(GateEvaluationError, RuntimeError)


# ===========================================================================
# DefenseRunner — _simulate_gate
# ===========================================================================
class TestSimulateGate:
    def test_tier_1_always_blocked(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1)
        assert runner._simulate_gate(scenario, "G1") is True

    def test_tier_2_always_blocked(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_2)
        assert runner._simulate_gate(scenario, "G1") is True

    def test_tier_3_critical_blocked(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_3, severity=Severity.CRITICAL)
        assert runner._simulate_gate(scenario, "G1") is True

    def test_tier_3_non_critical_hash_based(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_3, severity=Severity.MEDIUM)
        result = runner._simulate_gate(scenario, "G1")
        assert isinstance(result, bool)

    def test_tier_4_hash_based(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_4)
        result = runner._simulate_gate(scenario, "G1")
        assert isinstance(result, bool)

    def test_tier_5_hash_based(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_5)
        result = runner._simulate_gate(scenario, "G1")
        assert isinstance(result, bool)

    def test_tier_6_hash_based(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_6)
        result = runner._simulate_gate(scenario, "G1")
        assert isinstance(result, bool)

    def test_tier_7_never_blocked(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_7)
        assert runner._simulate_gate(scenario, "G1") is False

    def test_tier_1_deterministic(self):
        runner = DefenseRunner(gate_engine=None)
        s1 = make_scenario(scenario_id="A", tier=AttackTier.TIER_1)
        s2 = make_scenario(scenario_id="B", tier=AttackTier.TIER_1)
        assert runner._simulate_gate(s1, "G1") is True
        assert runner._simulate_gate(s2, "G1") is True

    def test_tier_3_same_scenario_deterministic(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(scenario_id="DET-001", tier=AttackTier.TIER_3, severity=Severity.LOW)
        r1 = runner._simulate_gate(scenario, "G1")
        r2 = runner._simulate_gate(scenario, "G1")
        assert r1 == r2


# ===========================================================================
# DefenseRunner — _evaluate_gate
# ===========================================================================
class TestEvaluateGate:
    def test_no_vector_returns_false(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(vector="")
        blocked, source = runner._evaluate_gate(scenario, "G1")
        assert blocked is False
        assert source == "no_vector"

    def test_fail_closed_source_when_no_gate_engine(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1, vector="test")
        blocked, source = runner._evaluate_gate(scenario, "G1")
        assert blocked is True
        assert source == "fail_closed"

    def test_tier_1_blocked_via_fail_closed(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1, vector="test")
        blocked, source = runner._evaluate_gate(scenario, "G1")
        assert blocked is True
        assert source == "fail_closed"

    def test_tier_7_blocked_via_fail_closed(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_7, vector="test")
        blocked, source = runner._evaluate_gate(scenario, "G1")
        assert blocked is True
        assert source == "fail_closed"

    def test_empty_gate_id_returns_false(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(vector="test")
        blocked, source = runner._evaluate_gate(scenario, "")
        assert blocked is False
        assert source == "no_vector"


# ===========================================================================
# DefenseRunner — _try_real_gate
# ===========================================================================
class TestTryRealGate:
    def test_returns_none_when_no_gate_engine(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario()
        result = runner._try_real_gate(scenario, "G1")
        assert result is None

    def test_returns_bool_when_gate_engine_present(self):
        mock_engine = MagicMock()
        mock_result = MagicMock()
        mock_result.passed = True
        mock_result.violations = []
        mock_engine.evaluate.return_value = mock_result
        runner = DefenseRunner(gate_engine=mock_engine)
        scenario = make_scenario()
        with patch("zephyr.gov_enforcement.rule_enforcement.task_types.Task") as mock_task_cls:
            mock_task_cls.return_value = MagicMock()
            result = runner._try_real_gate(scenario, "G1")
        assert isinstance(result, bool)
        assert result is True

    def test_returns_none_on_exception(self):
        mock_engine = MagicMock()
        mock_engine.evaluate.side_effect = RuntimeError("gate error")
        runner = DefenseRunner(gate_engine=mock_engine)
        scenario = make_scenario()
        result = runner._try_real_gate(scenario, "G1")
        assert result is None


# ===========================================================================
# DefenseRunner — run_defense
# ===========================================================================
class TestRunDefense:
    def test_returns_defense_result(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1)
        result = runner.run_defense(scenario)
        assert isinstance(result, DefenseResult)

    def test_blocked_result_for_tier_1(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1, gate_id="prompt_injection_filter")
        result = runner.run_defense(scenario)
        assert result.passed is True
        assert result.gate_id == "G1"
        assert "BLOCKED" in result.detail

    def test_blocked_result_for_tier_7(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_7, gate_id="prompt_injection_filter")
        result = runner.run_defense(scenario)
        assert result.passed is True
        assert result.gate_id == "G1"
        assert "BLOCKED" in result.detail

    def test_result_appended_to_results(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1)
        runner.run_defense(scenario)
        assert len(runner.results()) == 1

    def test_multiple_results_accumulate(self):
        runner = DefenseRunner(gate_engine=None)
        s1 = make_scenario(scenario_id="S1", tier=AttackTier.TIER_1)
        s2 = make_scenario(scenario_id="S2", tier=AttackTier.TIER_2)
        runner.run_defense(s1)
        runner.run_defense(s2)
        assert len(runner.results()) == 2

    def test_results_returns_copy(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1)
        runner.run_defense(scenario)
        r1 = runner.results()
        r1.clear()
        assert len(runner.results()) == 1

    def test_gate_id_mapping_in_result(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1, gate_id="drift_engine.reconcile")
        result = runner.run_defense(scenario)
        assert result.gate_id == "G2"

    def test_unmapped_gate_id_used_as_is(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1, gate_id="CUSTOM_GATE")
        result = runner.run_defense(scenario)
        assert result.gate_id == "CUSTOM_GATE"

    def test_detail_contains_gate_id(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1, gate_id="prompt_injection_filter")
        result = runner.run_defense(scenario)
        assert "G1" in result.detail

    def test_detail_contains_source(self):
        runner = DefenseRunner(gate_engine=None)
        scenario = make_scenario(tier=AttackTier.TIER_1)
        result = runner.run_defense(scenario)
        assert "fail_closed" in result.detail


# ===========================================================================
# DefenseRunner — close & context manager
# ===========================================================================
class TestDefenseRunnerClose:
    def test_close_without_gate_engine(self):
        runner = DefenseRunner(gate_engine=None)
        runner.close()

    def test_close_with_mock_gate_engine(self):
        mock_engine = MagicMock()
        runner = DefenseRunner(gate_engine=mock_engine)
        runner.close()
        mock_engine.close.assert_called_once()

    def test_context_manager(self):
        with DefenseRunner(gate_engine=None) as runner:
            assert runner is not None
            assert hasattr(runner, "run_defense")

    def test_context_manager_closes_gate_engine(self):
        mock_engine = MagicMock()
        with DefenseRunner(gate_engine=mock_engine) as runner:
            assert runner._gate_engine is not None
        mock_engine.close.assert_called_once()

    def test_close_sets_gate_engine_to_none(self):
        mock_engine = MagicMock()
        runner = DefenseRunner(gate_engine=mock_engine)
        runner.close()
        assert runner._gate_engine is None


# ===========================================================================
# RedBlueValidator — 导入与实例化
# ===========================================================================
class TestRedBlueValidatorImport:
    def test_import_success(self):
        assert RedBlueValidator is not None

    def test_instantiation(self):
        validator = RedBlueValidator()
        assert validator is not None

    def test_has_run_adversarial_session(self):
        validator = RedBlueValidator()
        assert hasattr(validator, "run_adversarial_session")

    def test_has_loader(self):
        validator = RedBlueValidator()
        assert hasattr(validator, "_loader")

    def test_has_defense(self):
        validator = RedBlueValidator()
        assert hasattr(validator, "_defense")

    def test_has_recorder(self):
        validator = RedBlueValidator()
        assert hasattr(validator, "_recorder")

    def test_has_steady(self):
        validator = RedBlueValidator()
        assert hasattr(validator, "_steady")

    def test_has_cleanup(self):
        validator = RedBlueValidator()
        assert hasattr(validator, "_cleanup")

    def test_has_blast(self):
        validator = RedBlueValidator()
        assert hasattr(validator, "_blast")

    def test_session_error_is_runtime_error(self):
        assert issubclass(SessionError, RuntimeError)


# ===========================================================================
# RedBlueValidator — run_adversarial_session
# ===========================================================================
class TestRunAdversarialSession:
    def setup_method(self):
        self.validator = RedBlueValidator()
        self.scenarios = [
            make_scenario(scenario_id="S1", tier=AttackTier.TIER_1),
            make_scenario(scenario_id="S2", tier=AttackTier.TIER_1),
        ]
        self.validator._load_and_filter = MagicMock(return_value=self.scenarios)
        self.validator._steady.verify_before_attack = MagicMock()
        from zephyr.security.adversarial_validation.models import SteadyStateSummary
        self.validator._steady.verify_after_attack = MagicMock(return_value=SteadyStateSummary())
        self.validator._cleanup.ensure_clean = MagicMock()

    def test_returns_red_blue_report(self):
        report = self.validator.run_adversarial_session("test-session", tier=AttackTier.TIER_1)
        assert isinstance(report, RedBlueReport)

    def test_session_id_starts_with_rb(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        assert report.session_id.startswith("RB-")

    def test_session_id_unique(self):
        r1 = self.validator.run_adversarial_session("s1", tier=AttackTier.TIER_1)
        r2 = self.validator.run_adversarial_session("s2", tier=AttackTier.TIER_1)
        assert r1.session_id != r2.session_id

    def test_total_is_non_negative(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        assert report.total >= 0

    def test_blocked_plus_bypassed_le_total(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        assert report.blocked + report.bypassed <= report.total

    def test_blocked_rate_computed(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        if report.total > 0:
            expected = round(report.blocked / report.total, 4)
            assert report.blocked_rate == expected
        else:
            assert report.blocked_rate == 0.0

    def test_duration_positive(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        assert report.duration_ms >= 0

    def test_blast_radius_used(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1, blast_radius=BlastRadiusLevel.FILE)
        assert report.blast_radius_used == BlastRadiusLevel.FILE

    def test_with_module_blast_radius(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1, blast_radius=BlastRadiusLevel.MODULE)
        assert report.blast_radius_used == BlastRadiusLevel.MODULE

    def test_scenarios_list_contains_scenario_results(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        for s in report.scenarios:
            assert isinstance(s, ScenarioResult)

    def test_scenario_results_have_valid_result_class(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        for s in report.scenarios:
            assert s.result in (ResultClass.BLOCKED, ResultClass.BYPASSED)

    def test_tier_1_scenarios_all_blocked(self):
        report = self.validator.run_adversarial_session("test", tier=AttackTier.TIER_1)
        if report.total > 0:
            assert report.blocked == report.total
            assert report.bypassed == 0


# ===========================================================================
# RedBlueValidator — _load_and_filter
# ===========================================================================
class TestLoadAndFilter:
    def setup_method(self):
        self.validator = RedBlueValidator()
        self.all_scenarios = [
            make_scenario(scenario_id="S1", tier=AttackTier.TIER_1, status="active"),
            make_scenario(scenario_id="S2", tier=AttackTier.TIER_7, status="active"),
            make_scenario(scenario_id="S3", tier=AttackTier.TIER_1, status="inactive"),
        ]
        self.validator._loader.load = MagicMock(return_value=self.all_scenarios)
        self.validator._blast.filter_scenarios = MagicMock(side_effect=lambda x: x)

    def test_returns_list(self):
        result = self.validator._load_and_filter()
        assert isinstance(result, list)

    def test_filter_by_tier_1(self):
        result = self.validator._load_and_filter(tier=AttackTier.TIER_1)
        for s in result:
            assert s.tier == AttackTier.TIER_1

    def test_filter_by_tier_7(self):
        result = self.validator._load_and_filter(tier=AttackTier.TIER_7)
        for s in result:
            assert s.tier == AttackTier.TIER_7

    def test_all_scenarios_are_active(self):
        result = self.validator._load_and_filter()
        for s in result:
            assert s.status == "active"


# ===========================================================================
# RedBlueValidator — _process_scenario
# ===========================================================================
class TestProcessScenario:
    def test_blocked_scenario(self):
        validator = RedBlueValidator()
        scenario = make_scenario(tier=AttackTier.TIER_1)
        result = validator._process_scenario(scenario)
        assert isinstance(result, ScenarioResult)
        assert result.result == ResultClass.BLOCKED

    def test_bypassed_scenario(self):
        validator = RedBlueValidator()
        scenario = make_scenario(tier=AttackTier.TIER_7)
        # fail-closed 后 TIER_7 不再自然 bypass；mock defense 返回 passed=False
        # 以隔离测试 _process_scenario 的 BYPASSED 映射分支（保留覆盖率）
        validator._defense = MagicMock()
        validator._defense.run_defense.return_value = DefenseResult(
            passed=False, gate_id="G1",
            detail="BYPASSED G1 [mock]: prompt_injection_filter failed to block test_vector",
        )
        result = validator._process_scenario(scenario)
        assert result.result == ResultClass.BYPASSED

    def test_result_has_scenario_id(self):
        validator = RedBlueValidator()
        scenario = make_scenario(scenario_id="PROC-001")
        result = validator._process_scenario(scenario)
        assert result.scenario_id == "PROC-001"

    def test_result_has_name(self):
        validator = RedBlueValidator()
        scenario = make_scenario(name="proc test")
        result = validator._process_scenario(scenario)
        assert result.name == "proc test"

    def test_result_has_gate_id(self):
        validator = RedBlueValidator()
        scenario = make_scenario(gate_id="prompt_injection_filter")
        result = validator._process_scenario(scenario)
        assert result.gate_id == "G1"

    def test_bypassed_has_bypass_entry(self):
        validator = RedBlueValidator()
        scenario = make_scenario(tier=AttackTier.TIER_7)
        # fail-closed 后 TIER_7 不再自然 bypass；mock defense 返回 passed=False
        # 以隔离测试 _process_scenario 的 BYPASSED 映射分支（保留覆盖率）
        validator._defense = MagicMock()
        validator._defense.run_defense.return_value = DefenseResult(
            passed=False, gate_id="G1",
            detail="BYPASSED G1 [mock]: prompt_injection_filter failed to block test_vector",
        )
        result = validator._process_scenario(scenario)
        assert result.bypass_entry is not None

    def test_blocked_has_no_bypass_entry(self):
        validator = RedBlueValidator()
        scenario = make_scenario(tier=AttackTier.TIER_1)
        result = validator._process_scenario(scenario)
        assert result.bypass_entry is None


# ===========================================================================
# RedBlueValidator — _build_report
# ===========================================================================
class TestBuildReport:
    def test_build_report_basic(self):
        from datetime import UTC, datetime

        validator = RedBlueValidator()
        results: list[ScenarioResult] = []
        start = datetime.now(UTC)
        report = validator._build_report("RB-TEST", results, 0, 0, start)
        assert report.session_id == "RB-TEST"
        assert report.total == 0
        assert report.blocked == 0
        assert report.bypassed == 0

    def test_build_report_with_results(self):
        from datetime import UTC, datetime

        validator = RedBlueValidator()
        results = [
            ScenarioResult(
                scenario_id="S1",
                name="test1",
                tier=AttackTier.TIER_1,
                result=ResultClass.BLOCKED,
                gate_id="G1",
            ),
            ScenarioResult(
                scenario_id="S2",
                name="test2",
                tier=AttackTier.TIER_7,
                result=ResultClass.BYPASSED,
                gate_id="G1",
            ),
        ]
        start = datetime.now(UTC)
        report = validator._build_report("RB-TEST", results, 1, 1, start)
        assert report.total == 2
        assert report.blocked == 1
        assert report.bypassed == 1
        assert report.blocked_rate == 0.5

    def test_build_report_duration(self):
        from datetime import UTC, datetime, timedelta

        validator = RedBlueValidator()
        start = datetime.now(UTC) - timedelta(seconds=1)
        report = validator._build_report("RB-TEST", [], 0, 0, start)
        assert report.duration_ms > 0


# ===========================================================================
# CLI — main 入口
# ===========================================================================
class TestCLIMain:
    def test_main_exists(self):
        assert hasattr(cli_mod, "main")
        assert callable(cli_mod.main)

    def test_main_no_command_exits(self):
        with patch("sys.argv", ["cli"]):
            with pytest.raises(SystemExit):
                cli_mod.main()

    def test_main_has_run_subcommand(self):
        with patch("sys.argv", ["cli", "run", "--help"]):
            with pytest.raises(SystemExit):
                cli_mod.main()


# ===========================================================================
# CLI — _run 命令
# ===========================================================================
class TestCLIRun:
    def test_run_function_exists(self):
        assert hasattr(cli_mod, "_run")
        assert callable(cli_mod._run)

    @patch("zephyr.security.adversarial_validation.cli.RedBlueValidator")
    def test_run_calls_validator(self, mock_validator_cls):
        mock_validator = MagicMock()
        mock_report = RedBlueReport(session_id="RB-TEST", total=5, blocked=3, bypassed=2)
        mock_report.blocked_rate = 0.6
        mock_validator.run_adversarial_session.return_value = mock_report
        mock_validator_cls.return_value = mock_validator

        args = MagicMock()
        args.name = "test"
        args.tier = None
        args.blast_radius = None
        cli_mod._run(args)
        mock_validator.run_adversarial_session.assert_called_once()

    @patch("zephyr.security.adversarial_validation.cli.RedBlueValidator")
    def test_run_with_tier(self, mock_validator_cls):
        mock_validator = MagicMock()
        mock_report = RedBlueReport(session_id="RB-TEST")
        mock_validator.run_adversarial_session.return_value = mock_report
        mock_validator_cls.return_value = mock_validator

        args = MagicMock()
        args.name = "test"
        args.tier = "L1"
        args.blast_radius = None
        cli_mod._run(args)
        call_kwargs = mock_validator.run_adversarial_session.call_args
        assert call_kwargs.kwargs.get("tier") is not None or len(call_kwargs.args) >= 2

    @patch("zephyr.security.adversarial_validation.cli.RedBlueValidator")
    def test_run_with_blast_radius(self, mock_validator_cls):
        mock_validator = MagicMock()
        mock_report = RedBlueReport(session_id="RB-TEST")
        mock_validator.run_adversarial_session.return_value = mock_report
        mock_validator_cls.return_value = mock_validator

        args = MagicMock()
        args.name = "test"
        args.tier = None
        args.blast_radius = "MODULE"
        cli_mod._run(args)
        call_kwargs = mock_validator.run_adversarial_session.call_args
        assert call_kwargs.kwargs.get("blast_radius") == BlastRadiusLevel.MODULE or BlastRadiusLevel.MODULE in call_kwargs.args


# ===========================================================================
# CLI — _list 命令
# ===========================================================================
class TestCLIList:
    def test_list_function_exists(self):
        assert hasattr(cli_mod, "_list")
        assert callable(cli_mod._list)

    @patch("zephyr.security.adversarial_validation.cli.ScenarioLoader")
    def test_list_calls_loader(self, mock_loader_cls):
        mock_loader = MagicMock()
        mock_loader.list_all.return_value = []
        mock_loader.list_active.return_value = []
        mock_loader_cls.return_value = mock_loader

        args = MagicMock()
        args.active_only = False
        cli_mod._list(args)
        mock_loader.load.assert_called_once()
        mock_loader.list_all.assert_called_once()

    @patch("zephyr.security.adversarial_validation.cli.ScenarioLoader")
    def test_list_active_only(self, mock_loader_cls):
        mock_loader = MagicMock()
        mock_loader.list_all.return_value = []
        mock_loader.list_active.return_value = []
        mock_loader_cls.return_value = mock_loader

        args = MagicMock()
        args.active_only = True
        cli_mod._list(args)
        mock_loader.list_active.assert_called_once()


# ===========================================================================
# CLI — _report_fn 命令
# ===========================================================================
class TestCLIReport:
    def test_report_function_exists(self):
        assert hasattr(cli_mod, "_report_fn")
        assert callable(cli_mod._report_fn)

    @patch("zephyr.security.adversarial_validation.cli.RedBlueValidator")
    def test_report_calls_validator(self, mock_validator_cls):
        mock_validator = MagicMock()
        mock_report = RedBlueReport(
            session_id="RB-TEST", total=10, blocked=8, bypassed=2, blocked_rate=0.8, duration_ms=100.0
        )
        mock_validator.run_adversarial_session.return_value = mock_report
        mock_validator_cls.return_value = mock_validator

        args = MagicMock()
        args.name = "test"
        args.tier = None
        cli_mod._report_fn(args)
        mock_validator.run_adversarial_session.assert_called_once()


# ===========================================================================
# CLI — _status 命令
# ===========================================================================
class TestCLIStatus:
    def test_status_function_exists(self):
        assert hasattr(cli_mod, "_status")
        assert callable(cli_mod._status)

    @patch("zephyr.security.adversarial_validation.cli.ScenarioLoader")
    def test_status_calls_loader(self, mock_loader_cls):
        mock_loader = MagicMock()
        mock_loader.tier_counts.return_value = {}
        mock_loader.scenario_count = 0
        mock_loader_cls.return_value = mock_loader

        args = MagicMock()
        cli_mod._status(args)
        mock_loader.load.assert_called_once()
        mock_loader.tier_counts.assert_called_once()


# ===========================================================================
# CLI — _gameday 命令
# ===========================================================================
class TestCLIGameDay:
    def test_gameday_function_exists(self):
        assert hasattr(cli_mod, "_gameday")
        assert callable(cli_mod._gameday)

    @patch("zephyr.security.adversarial_validation.cli.GameDayRunner")
    def test_gameday_calls_runner(self, mock_runner_cls):
        mock_runner = MagicMock()
        mock_result = MagicMock()
        mock_result.total_attacks = 5
        mock_result.passed = 3
        mock_result.bypasses = 2
        mock_runner.run_game_day.return_value = mock_result
        mock_runner_cls.return_value = mock_runner

        args = MagicMock()
        args.frequency = "per_commit"
        cli_mod._gameday(args)
        mock_runner.run_game_day.assert_called_once()


# ===========================================================================
# CLI — _onboard 命令
# ===========================================================================
class TestCLIOnboard:
    def test_onboard_function_exists(self):
        assert hasattr(cli_mod, "_onboard")
        assert callable(cli_mod._onboard)

    @patch("zephyr.security.adversarial_validation.cli.ColdStart")
    def test_onboard_calls_coldstart(self, mock_cs_cls):
        mock_cs = MagicMock()
        mock_cs.onboard_module.return_value = "SCEN-001"
        mock_cs_cls.return_value = mock_cs

        args = MagicMock()
        args.module_path = "src/test.py"
        cli_mod._onboard(args)
        mock_cs.onboard_module.assert_called_once_with("src/test.py")

    @patch("zephyr.security.adversarial_validation.cli.ColdStart")
    def test_onboard_already_registered(self, mock_cs_cls):
        mock_cs = MagicMock()
        mock_cs.onboard_module.return_value = None
        mock_cs_cls.return_value = mock_cs

        args = MagicMock()
        args.module_path = "src/test.py"
        cli_mod._onboard(args)
        mock_cs.onboard_module.assert_called_once()


# ===========================================================================
# CLI — dispatch 完整性
# ===========================================================================
class TestCLIDispatch:
    def test_dispatch_has_run(self):
        with patch("sys.argv", ["cli", "run", "--name", "test"]):
            with patch("zephyr.security.adversarial_validation.cli.RedBlueValidator") as mock_v:
                mock_validator = MagicMock()
                mock_report = RedBlueReport(session_id="RB-TEST")
                mock_validator.run_adversarial_session.return_value = mock_report
                mock_v.return_value = mock_validator
                try:
                    cli_mod.main()
                except SystemExit:
                    pass

    def test_dispatch_has_status(self):
        with patch("sys.argv", ["cli", "status"]):
            with patch("zephyr.security.adversarial_validation.cli.ScenarioLoader") as mock_l:
                mock_loader = MagicMock()
                mock_loader.tier_counts.return_value = {}
                mock_loader.scenario_count = 0
                mock_l.return_value = mock_loader
                try:
                    cli_mod.main()
                except SystemExit:
                    pass

    def test_dispatch_has_list(self):
        with patch("sys.argv", ["cli", "list"]):
            with patch("zephyr.security.adversarial_validation.cli.ScenarioLoader") as mock_l:
                mock_loader = MagicMock()
                mock_loader.list_all.return_value = []
                mock_loader.list_active.return_value = []
                mock_l.return_value = mock_loader
                try:
                    cli_mod.main()
                except SystemExit:
                    pass
