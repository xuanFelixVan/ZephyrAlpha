# [A_test] module_id: SRC-TST-1437 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §test
# [MODULE] zephyr.red_blue_validator
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_red_blue_validator_tests.py
# [TTL] task_bound

from __future__ import annotations

import pytest

ar_mod = pytest.importorskip("zephyr.security.adversarial_validation.attack_registry")
br_mod = pytest.importorskip("zephyr.security.adversarial_validation.bypass_recorder")
cg_mod = pytest.importorskip("zephyr.security.adversarial_validation.constitution_guard")
cc_mod = pytest.importorskip("zephyr.security.adversarial_validation.convergence_checker")
dr_mod = pytest.importorskip("zephyr.security.adversarial_validation.defense_runner")
gd_mod = pytest.importorskip("zephyr.security.adversarial_validation.game_day_runner")

# 治本(2026-07-19): run_defense 期望 AttackScenario 对象而非字符串；
# run_game_day 接受 GameDayFrequency 枚举而非 scope 字符串。
models_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.models",
    reason="models not available",
)
AttackScenario = models_mod.AttackScenario
GameDayFrequency = gd_mod.GameDayFrequency

AttackRegistry = ar_mod.AttackRegistry
BypassRecorder = br_mod.BypassRecorder
ConstitutionGuard = cg_mod.ConstitutionGuard
ConvergenceChecker = cc_mod.ConvergenceChecker
ConvergenceResult = cc_mod.ConvergenceResult
DefenseRunner = dr_mod.DefenseRunner
DefenseResult = dr_mod.DefenseResult
GameDayRunner = gd_mod.GameDayRunner
GameDayResult = gd_mod.GameDayResult


class TestAttackRegistry:
    def test_instantiation(self):
        reg = AttackRegistry()
        assert reg is not None

    def test_register_callable(self):
        reg = AttackRegistry()
        reg.register("ATT-001", tier=1, scenario="prompt_injection")

    def test_query_by_tier_callable(self):
        reg = AttackRegistry()
        reg.register("ATT-001", tier=1, scenario="prompt_injection")
        result = reg.query_by_tier(1)
        assert result is None or isinstance(result, list)

    def test_query_by_tier_empty_callable(self):
        reg = AttackRegistry()
        result = reg.query_by_tier(99)
        assert result is None or isinstance(result, list)

    def test_count_callable(self):
        reg = AttackRegistry()
        result = reg.count()
        assert result is None or isinstance(result, int)

    def test_count_after_register_callable(self):
        reg = AttackRegistry()
        reg.register("ATT-010", tier=1, scenario="test")
        result = reg.count()
        assert result is None or isinstance(result, int)

    def test_has_method_register(self):
        reg = AttackRegistry()
        assert hasattr(reg, "register")
        assert callable(reg.register)

    def test_has_method_query_by_tier(self):
        reg = AttackRegistry()
        assert hasattr(reg, "query_by_tier")
        assert callable(reg.query_by_tier)

    def test_has_method_count(self):
        reg = AttackRegistry()
        assert hasattr(reg, "count")
        assert callable(reg.count)


class TestBypassRecorder:
    def test_instantiation(self):
        rec = BypassRecorder()
        assert rec is not None

    def test_record_bypass_callable(self):
        rec = BypassRecorder()
        rec.record_bypass("ATT-001", "GATE-001", "detail info")

    def test_query_bypasses_callable(self):
        rec = BypassRecorder()
        rec.record_bypass("ATT-001", "GATE-001", "detail")
        result = rec.query_bypasses("ATT-001")
        assert result is None or isinstance(result, list)

    def test_query_bypasses_all_callable(self):
        rec = BypassRecorder()
        rec.record_bypass("ATT-001", "GATE-001", "d1")
        rec.record_bypass("ATT-002", "GATE-002", "d2")
        result = rec.query_bypasses()
        assert result is None or isinstance(result, list)

    def test_query_bypasses_empty_callable(self):
        rec = BypassRecorder()
        result = rec.query_bypasses("NONEXISTENT")
        assert result is None or isinstance(result, list)

    def test_has_method_record_bypass(self):
        rec = BypassRecorder()
        assert hasattr(rec, "record_bypass")
        assert callable(rec.record_bypass)

    def test_has_method_query_bypasses(self):
        rec = BypassRecorder()
        assert hasattr(rec, "query_bypasses")
        assert callable(rec.query_bypasses)


class TestConstitutionGuard:
    def test_instantiation(self):
        guard = ConstitutionGuard()
        assert guard is not None

    def test_validate_constitution_callable(self):
        guard = ConstitutionGuard()
        result = guard.validate_constitution("RULE-001")
        assert result is None or isinstance(result, bool)

    def test_get_guarded_rules_callable(self):
        guard = ConstitutionGuard()
        result = guard.get_guarded_rules()
        assert result is None or isinstance(result, list)

    def test_has_method_validate_constitution(self):
        guard = ConstitutionGuard()
        assert hasattr(guard, "validate_constitution")
        assert callable(guard.validate_constitution)

    def test_has_method_get_guarded_rules(self):
        guard = ConstitutionGuard()
        assert hasattr(guard, "get_guarded_rules")
        assert callable(guard.get_guarded_rules)


class TestConvergenceChecker:
    def test_instantiation(self):
        checker = ConvergenceChecker()
        assert checker is not None

    def test_check_convergence_callable(self):
        checker = ConvergenceChecker()
        result = checker.check_convergence("phase-1")
        assert result is None or isinstance(result, ConvergenceResult)

    def test_convergence_result_fields(self):
        field_names = list(ConvergenceResult.__annotations__.keys())
        assert "status" in field_names
        assert "bypass_count" in field_names
        assert "total_attacks" in field_names

    def test_has_method_check_convergence(self):
        checker = ConvergenceChecker()
        assert hasattr(checker, "check_convergence")
        assert callable(checker.check_convergence)


class TestDefenseRunner:
    def test_instantiation(self):
        runner = DefenseRunner()
        assert runner is not None

    def test_run_defense_callable(self):
        runner = DefenseRunner()
        # 治本(2026-07-19): run_defense 接受 AttackScenario 对象而非字符串 ID
        scenario = AttackScenario(scenario_id="ATT-001", name="test")
        result = runner.run_defense(scenario)
        assert result is None or isinstance(result, DefenseResult)

    def test_defense_result_fields(self):
        field_names = list(DefenseResult.__annotations__.keys())
        assert "passed" in field_names
        assert "gate_id" in field_names
        assert "detail" in field_names

    def test_has_method_run_defense(self):
        runner = DefenseRunner()
        assert hasattr(runner, "run_defense")
        assert callable(runner.run_defense)


class TestGameDayRunner:
    def test_instantiation(self):
        runner = GameDayRunner()
        assert runner is not None

    def test_run_game_day_callable(self):
        runner = GameDayRunner()
        # 治本(2026-07-19): run_game_day 接受 GameDayFrequency 枚举而非 scope 字符串
        result = runner.run_game_day(frequency=GameDayFrequency.MONTHLY)
        assert result is None or isinstance(result, GameDayResult)

    def test_run_game_day_custom_scope(self):
        runner = GameDayRunner()
        # 治本(2026-07-19): 不同 frequency 对应不同 scope，DAILY 对应 module 级
        result = runner.run_game_day(frequency=GameDayFrequency.DAILY)
        assert result is None or isinstance(result, GameDayResult)

    def test_game_day_result_fields(self):
        field_names = list(GameDayResult.__annotations__.keys())
        assert "total_attacks" in field_names
        assert "bypasses" in field_names
        assert "passed" in field_names

    def test_has_method_run_game_day(self):
        runner = GameDayRunner()
        assert hasattr(runner, "run_game_day")
        assert callable(runner.run_game_day)
