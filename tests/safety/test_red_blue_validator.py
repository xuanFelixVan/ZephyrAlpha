# [A_test] module_id: MOD-GOV_red_blue_validator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.2-4.4
# [MODULE] zephyr.security.adversarial_validation.validator
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_red_blue_validator_tests.py
# [TTL] task_bound

from datetime import UTC, datetime

import pytest

validator_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.validator",
    reason="validator not available",
)
RedBlueValidator = validator_mod.RedBlueValidator
SessionError = validator_mod.SessionError

defense_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.defense_runner",
    reason="defense_runner not available",
)
DefenseRunner = defense_mod.DefenseRunner
GateEvaluationError = defense_mod.GateEvaluationError

gameday_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.game_day_runner",
    reason="game_day_runner not available",
)
GameDayRunner = gameday_mod.GameDayRunner
GameDayFrequency = gameday_mod.GameDayFrequency
GameDayError = gameday_mod.GameDayError

models_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.models",
    reason="models not available",
)
RedBlueReport = models_mod.RedBlueReport
DefenseResult = models_mod.DefenseResult
AttackScenario = models_mod.AttackScenario
AttackTier = models_mod.AttackTier
BlastRadiusLevel = models_mod.BlastRadiusLevel


class TestRedBlueValidatorImport:
    def test_import_success(self):
        assert RedBlueValidator is not None

    def test_instantiation(self):
        validator = RedBlueValidator()
        assert validator is not None
        assert hasattr(validator, "run_adversarial_session")
        assert hasattr(validator, "_loader")
        assert hasattr(validator, "_defense")
        assert hasattr(validator, "_recorder")
        assert hasattr(validator, "_steady")
        assert hasattr(validator, "_cleanup")
        assert hasattr(validator, "_blast")

    def test_session_error_class(self):
        assert issubclass(SessionError, RuntimeError)


class TestDefenseRunnerImport:
    def test_import_success(self):
        assert DefenseRunner is not None

    def test_instantiation(self):
        runner = DefenseRunner()
        assert runner is not None
        assert hasattr(runner, "run_defense")
        assert hasattr(runner, "_gate_engine")
        assert hasattr(runner, "_results")
        assert hasattr(runner, "jsonl_output")

    def test_instantiation_with_jsonl(self):
        runner = DefenseRunner(jsonl_output=True)
        assert runner.jsonl_output is True

    def test_gate_evaluation_error_class(self):
        assert issubclass(GateEvaluationError, RuntimeError)


class TestGameDayRunnerImport:
    def test_import_success(self):
        assert GameDayRunner is not None

    def test_instantiation(self):
        runner = GameDayRunner()
        assert runner is not None
        assert hasattr(runner, "run_game_day")
        assert hasattr(runner, "run_full_cycle")
        assert hasattr(runner, "_validator")

    def test_game_day_frequency_enum(self):
        assert hasattr(GameDayFrequency, "PER_COMMIT")
        assert hasattr(GameDayFrequency, "DAILY")
        assert hasattr(GameDayFrequency, "WEEKLY")
        assert hasattr(GameDayFrequency, "MONTHLY")

    def test_game_day_error_class(self):
        assert issubclass(GameDayError, RuntimeError)


class TestGameDayFrequencyValues:
    def test_per_commit_has_tier(self):
        freq = GameDayFrequency.PER_COMMIT
        assert hasattr(freq, "tier")
        assert hasattr(freq, "blast_radius")

    def test_daily_has_tier(self):
        freq = GameDayFrequency.DAILY
        assert hasattr(freq, "tier")
        assert hasattr(freq, "blast_radius")

    def test_weekly_has_tier(self):
        freq = GameDayFrequency.WEEKLY
        assert hasattr(freq, "tier")
        assert hasattr(freq, "blast_radius")

    def test_monthly_has_tier(self):
        freq = GameDayFrequency.MONTHLY
        assert hasattr(freq, "tier")
        assert hasattr(freq, "blast_radius")


class TestRedBlueReportModel:
    def test_default_values(self):
        report = RedBlueReport(session_id="test-session")
        assert report.session_id == "test-session"
        assert report.total == 0
        assert report.blocked == 0
        assert report.bypassed == 0
        assert report.blocked_rate == 0.0
        assert report.new_bypass_entries == 0
        assert report.new_constitution_articles == 0
        assert report.cleanup_verified is False
        assert report.circuit_breaker_open is False

    def test_compute_blocked_rate(self):
        report = RedBlueReport(session_id="test", total=10, blocked=8)
        rate = report.compute_blocked_rate()
        assert rate == 0.8
        assert report.blocked_rate == 0.8

    def test_compute_blocked_rate_zero_total(self):
        report = RedBlueReport(session_id="test", total=0)
        rate = report.compute_blocked_rate()
        assert rate == 0.0


class TestDefenseResultModel:
    def test_creation(self):
        result = DefenseResult(passed=True, gate_id="G6", detail="blocked")
        assert result.passed is True
        assert result.gate_id == "G6"
        assert result.detail == "blocked"

    def test_failed_result(self):
        result = DefenseResult(passed=False, gate_id="G7", detail="bypassed")
        assert result.passed is False
        assert result.gate_id == "G7"


class TestAttackTierEnum:
    def test_tier_values_exist(self):
        assert hasattr(AttackTier, "TIER_1")
        assert hasattr(AttackTier, "TIER_2")
        assert hasattr(AttackTier, "TIER_3")


class TestBlastRadiusLevelEnum:
    def test_level_values_exist(self):
        assert hasattr(BlastRadiusLevel, "FILE")
