# [A_test] module_id: MOD-GOV_injection_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §16
# [MODULE] zephyr.security.adversarial_validation.injection_engine
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_injection_engine.py
# [TTL] task_bound

from datetime import datetime

import pytest

injection_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.injection_engine",
    reason="injection_engine not available",
)
InjectionEngine = injection_mod.InjectionEngine

blast_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.blast_radius",
    reason="blast_radius not available",
)
BlastRadius = blast_mod.BlastRadius
AbortThresholdError = blast_mod.AbortThresholdError

models_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.models",
    reason="models not available",
)
InjectionResult = models_mod.InjectionResult
InjectionType = models_mod.InjectionType
BlastRadiusLevel = models_mod.BlastRadiusLevel
AttackScenario = models_mod.AttackScenario
AttackTier = models_mod.AttackTier


CRASH_SAFETY_ENV = "INJECTION_CRASH_CONFIRMED"


def _make_scenario(level: BlastRadiusLevel, sid: str = "test-1") -> AttackScenario:
    return AttackScenario(
        scenario_id=sid,
        name="test scenario",
        blast_radius=level,
    )


class TestInjectionEngineImport:
    def test_import_success(self):
        assert InjectionEngine is not None

    def test_models_import_success(self):
        assert InjectionResult is not None
        assert InjectionType is not None
        assert BlastRadiusLevel is not None

    def test_blast_radius_import_success(self):
        assert BlastRadius is not None
        assert AbortThresholdError is not None


class TestInjectionEngineInit:
    def test_default_blast_radius_is_file(self):
        engine = InjectionEngine()
        assert engine.blast_radius == BlastRadiusLevel.FILE

    def test_custom_blast_radius(self):
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.SYSTEM)
        assert engine.blast_radius == BlastRadiusLevel.SYSTEM

    def test_blast_radius_setter(self):
        engine = InjectionEngine()
        engine.blast_radius = BlastRadiusLevel.MODULE
        assert engine.blast_radius == BlastRadiusLevel.MODULE

    def test_empty_history_on_init(self):
        engine = InjectionEngine()
        assert engine.injection_history() == []


class TestInjectionEngineLatency:
    def test_inject_latency_returns_result(self):
        engine = InjectionEngine()
        result = engine.inject("latency", target="module_a", delay_ms=10)
        assert result.injection_type == InjectionType.LATENCY
        assert result.target == "module_a"
        assert "delay" in result.effect
        assert result.error is None

    def test_inject_latency_records_history(self):
        engine = InjectionEngine()
        engine.inject("latency", target="module_a", delay_ms=5)
        history = engine.injection_history()
        assert len(history) == 1
        assert history[0].injection_type == InjectionType.LATENCY

    def test_inject_latency_default_delay(self):
        engine = InjectionEngine()
        result = engine.inject("latency", target="m")
        assert result.injection_type == InjectionType.LATENCY
        assert result.target == "m"

    def test_inject_latency_timestamp_set(self):
        engine = InjectionEngine()
        result = engine.inject("latency", target="m", delay_ms=1)
        assert isinstance(result.timestamp, datetime)


class TestInjectionEngineError:
    def test_inject_error_returns_result(self):
        engine = InjectionEngine()
        result = engine.inject("error", target="module_b", error_message="boom")
        assert result.injection_type == InjectionType.ERROR
        assert result.target == "module_b"
        assert "boom" in result.effect
        assert result.error is None

    def test_inject_error_default_message(self):
        engine = InjectionEngine()
        result = engine.inject("error", target="m")
        assert "Chaos injection" in result.effect

    def test_inject_error_records_history(self):
        engine = InjectionEngine()
        engine.inject("error", target="m", error_message="x")
        assert len(engine.injection_history()) == 1


class TestInjectionEngineCrash:
    def test_inject_crash_requires_high_blast_radius_file(self):
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.FILE)
        with pytest.raises(PermissionError):
            engine.inject("crash", target="m")

    def test_inject_crash_requires_high_blast_radius_module(self):
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.MODULE)
        with pytest.raises(PermissionError):
            engine.inject("crash", target="m")

    def test_inject_crash_allowed_at_cross_module(self, monkeypatch):
        monkeypatch.delenv(CRASH_SAFETY_ENV, raising=False)
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.CROSS_MODULE)
        result = engine.inject("crash", target="m")
        assert result.injection_type == InjectionType.CRASH
        assert result.effect == "aborted_by_safety_check"
        assert result.error is not None
        assert CRASH_SAFETY_ENV in result.error

    def test_inject_crash_allowed_at_system(self, monkeypatch):
        monkeypatch.delenv(CRASH_SAFETY_ENV, raising=False)
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.SYSTEM)
        result = engine.inject("crash", target="m")
        assert result.injection_type == InjectionType.CRASH
        assert result.effect == "aborted_by_safety_check"

    def test_inject_crash_aborted_by_safety_check(self, monkeypatch):
        monkeypatch.delenv(CRASH_SAFETY_ENV, raising=False)
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.CROSS_MODULE)
        result = engine.inject("crash", target="m")
        assert result.injection_type == InjectionType.CRASH
        assert result.effect == "aborted_by_safety_check"
        assert result.error is not None
        assert CRASH_SAFETY_ENV in result.error

    def test_inject_crash_confirmed_calls_os_exit(self, monkeypatch):
        monkeypatch.setenv(CRASH_SAFETY_ENV, "yes")
        exit_calls = []

        def fake_exit(code):
            exit_calls.append(code)
            raise SystemExit(code)

        monkeypatch.setattr("os._exit", fake_exit)
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.SYSTEM)
        with pytest.raises(SystemExit):
            engine.inject("crash", target="m")
        assert exit_calls == [1]


class TestInjectionEngineExitCode:
    def test_inject_exit_code_requires_high_blast_radius(self):
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.FILE)
        with pytest.raises(PermissionError):
            engine.inject("exit_code", target="m")

    def test_inject_exit_code_requires_cross_module_minimum(self):
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.MODULE)
        with pytest.raises(PermissionError):
            engine.inject("exit_code", target="m")

    def test_inject_exit_code_aborted_by_safety_check(self, monkeypatch):
        monkeypatch.delenv(CRASH_SAFETY_ENV, raising=False)
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.CROSS_MODULE)
        result = engine.inject("exit_code", target="m", exit_code=99)
        assert result.injection_type == InjectionType.EXIT_CODE
        assert result.effect == "aborted_by_safety_check"
        assert result.error is not None
        assert CRASH_SAFETY_ENV in result.error

    def test_inject_exit_code_confirmed_calls_sys_exit(self, monkeypatch):
        monkeypatch.setenv(CRASH_SAFETY_ENV, "yes")
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.SYSTEM)
        with pytest.raises(SystemExit) as exc_info:
            engine.inject("exit_code", target="m", exit_code=42)
        assert exc_info.value.code == 42

    def test_inject_exit_code_custom_code(self, monkeypatch):
        monkeypatch.setenv(CRASH_SAFETY_ENV, "yes")
        engine = InjectionEngine(blast_radius=BlastRadiusLevel.SYSTEM)
        with pytest.raises(SystemExit) as exc_info:
            engine.inject("exit_code", target="m", exit_code=7)
        assert exc_info.value.code == 7


class TestInjectionEngineUnknownType:
    def test_unknown_type_raises_value_error(self):
        engine = InjectionEngine()
        with pytest.raises(ValueError) as exc_info:
            engine.inject("unknown_type", target="m")
        assert "Unknown injection type" in str(exc_info.value)

    def test_unknown_type_error_lists_valid_types(self):
        engine = InjectionEngine()
        with pytest.raises(ValueError) as exc_info:
            engine.inject("bogus", target="m")
        msg = str(exc_info.value)
        assert "latency" in msg
        assert "error" in msg
        assert "crash" in msg
        assert "exit_code" in msg

    def test_unknown_type_not_recorded_in_history(self):
        engine = InjectionEngine()
        with pytest.raises(ValueError):
            engine.inject("bogus", target="m")
        assert engine.injection_history() == []


class TestInjectionEngineRecoverVerify:
    def test_recover_clears_history(self):
        engine = InjectionEngine()
        engine.inject("latency", target="m", delay_ms=1)
        assert len(engine.injection_history()) == 1
        assert engine.recover() is True
        assert engine.injection_history() == []

    def test_recover_marks_recovered(self):
        engine = InjectionEngine()
        engine.inject("latency", target="m", delay_ms=1)
        history = engine.injection_history()
        assert history[0].recovered is False
        engine.recover()
        assert history[0].recovered is True

    def test_recover_returns_true(self):
        engine = InjectionEngine()
        assert engine.recover() is True

    def test_verify_empty_returns_true(self):
        engine = InjectionEngine()
        assert engine.verify() is True

    def test_verify_after_recover_returns_true(self):
        engine = InjectionEngine()
        engine.inject("latency", target="m", delay_ms=1)
        engine.recover()
        assert engine.verify() is True

    def test_verify_false_when_not_recovered(self):
        engine = InjectionEngine()
        engine.inject("latency", target="m", delay_ms=1)
        # not recovered yet
        assert engine.verify() is False


class TestInjectionResultModel:
    def test_injection_result_defaults(self):
        result = InjectionResult(injection_type=InjectionType.LATENCY)
        assert result.target == ""
        assert result.effect == "injected"
        assert result.error is None
        assert result.recovered is False
        assert isinstance(result.timestamp, datetime)

    def test_injection_result_with_all_fields(self):
        ts = datetime.now()
        result = InjectionResult(
            injection_type=InjectionType.ERROR,
            target="mod_x",
            effect="boom",
            timestamp=ts,
            error="some error",
            recovered=True,
        )
        assert result.injection_type == InjectionType.ERROR
        assert result.target == "mod_x"
        assert result.effect == "boom"
        assert result.timestamp == ts
        assert result.error == "some error"
        assert result.recovered is True

    def test_injection_result_invalid_type_raises(self):
        with pytest.raises(Exception):
            InjectionResult(injection_type="not_a_real_type")

    def test_injection_result_each_type(self):
        for itype in InjectionType:
            result = InjectionResult(injection_type=itype)
            assert result.injection_type == itype


class TestBlastRadiusInit:
    def test_default_level_is_file(self):
        br = BlastRadius()
        assert br.current_level == BlastRadiusLevel.FILE

    def test_custom_initial_level(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.MODULE)
        assert br.current_level == BlastRadiusLevel.MODULE

    def test_custom_initial_level_system(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        assert br.current_level == BlastRadiusLevel.SYSTEM

    def test_not_aborted_on_init(self):
        br = BlastRadius()
        assert br.aborted is False


class TestBlastRadiusEscalationFileToModule:
    def test_escalation_file_to_module_by_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.FILE)
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.FILE
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.FILE
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.MODULE

    def test_file_level_no_escalation_below_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.FILE)
        br.record_bypass(s)
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.FILE


class TestBlastRadiusEscalationModuleToCrossModule:
    def test_escalation_module_to_cross_module_by_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.MODULE)
        s = _make_scenario(BlastRadiusLevel.MODULE)
        for _ in range(5):
            br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.CROSS_MODULE

    def test_module_level_no_escalation_below_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.MODULE)
        s = _make_scenario(BlastRadiusLevel.MODULE)
        for _ in range(4):
            br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.MODULE


class TestBlastRadiusEscalationCrossModuleToSystem:
    def test_escalation_cross_module_to_system_by_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.CROSS_MODULE)
        s = _make_scenario(BlastRadiusLevel.CROSS_MODULE)
        for _ in range(8):
            br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.SYSTEM

    def test_cross_module_level_no_escalation_below_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.CROSS_MODULE)
        s = _make_scenario(BlastRadiusLevel.CROSS_MODULE)
        for _ in range(7):
            br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.CROSS_MODULE


class TestBlastRadiusEscalationByHigherLevel:
    def test_escalation_by_higher_level_scenario(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.MODULE)
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.MODULE

    def test_escalation_skips_levels_via_system_scenario(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.SYSTEM)
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.SYSTEM

    def test_escalation_via_cross_module_scenario(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.CROSS_MODULE)
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.CROSS_MODULE

    def test_record_bypass_returns_current_level(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.FILE)
        result = br.record_bypass(s)
        assert result == BlastRadiusLevel.FILE

    def test_record_bypass_returns_escalated_level(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.MODULE)
        result = br.record_bypass(s)
        assert result == BlastRadiusLevel.MODULE


class TestBlastRadiusAbortThreshold:
    def test_abort_at_system_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        s = _make_scenario(BlastRadiusLevel.SYSTEM)
        for _ in range(14):
            br.record_bypass(s)
        assert br.aborted is False
        with pytest.raises(AbortThresholdError):
            br.record_bypass(s)
        assert br.aborted is True

    def test_abort_error_message_contains_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        s = _make_scenario(BlastRadiusLevel.SYSTEM)
        for _ in range(14):
            br.record_bypass(s)
        with pytest.raises(AbortThresholdError) as exc_info:
            br.record_bypass(s)
        msg = str(exc_info.value)
        assert "15" in msg
        assert "SYSTEM" in msg

    def test_no_abort_below_system_level(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.FILE)
        for _ in range(3):
            br.record_bypass(s)
        assert br.aborted is False
        assert br.current_level == BlastRadiusLevel.MODULE

    def test_no_abort_at_cross_module_threshold(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.CROSS_MODULE)
        s = _make_scenario(BlastRadiusLevel.CROSS_MODULE)
        for _ in range(8):
            br.record_bypass(s)
        assert br.aborted is False
        assert br.current_level == BlastRadiusLevel.SYSTEM

    def test_abort_threshold_error_is_runtime_error(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        s = _make_scenario(BlastRadiusLevel.SYSTEM)
        for _ in range(14):
            br.record_bypass(s)
        with pytest.raises(RuntimeError):
            br.record_bypass(s)


class TestBlastRadiusFilterScenarios:
    def test_filter_at_file_level(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        scenarios = [
            _make_scenario(BlastRadiusLevel.FILE, "s1"),
            _make_scenario(BlastRadiusLevel.MODULE, "s2"),
            _make_scenario(BlastRadiusLevel.SYSTEM, "s3"),
        ]
        filtered = br.filter_scenarios(scenarios)
        assert len(filtered) == 1
        assert filtered[0].scenario_id == "s1"

    def test_filter_at_module_level(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.MODULE)
        scenarios = [
            _make_scenario(BlastRadiusLevel.FILE, "s1"),
            _make_scenario(BlastRadiusLevel.MODULE, "s2"),
            _make_scenario(BlastRadiusLevel.CROSS_MODULE, "s3"),
            _make_scenario(BlastRadiusLevel.SYSTEM, "s4"),
        ]
        filtered = br.filter_scenarios(scenarios)
        assert len(filtered) == 2
        ids = [s.scenario_id for s in filtered]
        assert "s1" in ids
        assert "s2" in ids

    def test_filter_at_cross_module_level(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.CROSS_MODULE)
        scenarios = [
            _make_scenario(BlastRadiusLevel.FILE, "s1"),
            _make_scenario(BlastRadiusLevel.MODULE, "s2"),
            _make_scenario(BlastRadiusLevel.CROSS_MODULE, "s3"),
            _make_scenario(BlastRadiusLevel.SYSTEM, "s4"),
        ]
        filtered = br.filter_scenarios(scenarios)
        assert len(filtered) == 3

    def test_filter_at_system_level_keeps_all(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        scenarios = [
            _make_scenario(BlastRadiusLevel.FILE, "s1"),
            _make_scenario(BlastRadiusLevel.MODULE, "s2"),
            _make_scenario(BlastRadiusLevel.CROSS_MODULE, "s3"),
            _make_scenario(BlastRadiusLevel.SYSTEM, "s4"),
        ]
        filtered = br.filter_scenarios(scenarios)
        assert len(filtered) == 4

    def test_filter_empty_list(self):
        br = BlastRadius()
        assert br.filter_scenarios([]) == []

    def test_filter_returns_new_list(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        scenarios = [_make_scenario(BlastRadiusLevel.FILE, "s1")]
        filtered = br.filter_scenarios(scenarios)
        assert filtered is not scenarios


class TestBlastRadiusReset:
    def test_reset_returns_to_file(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        br.reset()
        assert br.current_level == BlastRadiusLevel.FILE

    def test_reset_clears_aborted(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        s = _make_scenario(BlastRadiusLevel.SYSTEM)
        for _ in range(15):
            try:
                br.record_bypass(s)
            except AbortThresholdError:
                break
        assert br.aborted is True
        br.reset()
        assert br.aborted is False

    def test_reset_clears_bypass_counts(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.FILE)
        br.record_bypass(s)
        br.reset()
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.FILE
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.FILE

    def test_reset_after_escalation(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s = _make_scenario(BlastRadiusLevel.MODULE)
        br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.MODULE
        br.reset()
        assert br.current_level == BlastRadiusLevel.FILE

    def test_reset_idempotent(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        br.reset()
        br.reset()
        assert br.current_level == BlastRadiusLevel.FILE
        assert br.aborted is False


class TestBlastRadiusProgressiveEscalation:
    def test_full_escalation_path_file_to_system(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.FILE)
        s_file = _make_scenario(BlastRadiusLevel.FILE)
        for _ in range(3):
            br.record_bypass(s_file)
        assert br.current_level == BlastRadiusLevel.MODULE

        s_module = _make_scenario(BlastRadiusLevel.MODULE)
        for _ in range(5):
            br.record_bypass(s_module)
        assert br.current_level == BlastRadiusLevel.CROSS_MODULE

        s_cross = _make_scenario(BlastRadiusLevel.CROSS_MODULE)
        for _ in range(8):
            br.record_bypass(s_cross)
        assert br.current_level == BlastRadiusLevel.SYSTEM

    def test_system_level_does_not_escalate_further(self):
        br = BlastRadius(initial_level=BlastRadiusLevel.SYSTEM)
        s = _make_scenario(BlastRadiusLevel.SYSTEM)
        for _ in range(14):
            br.record_bypass(s)
        assert br.current_level == BlastRadiusLevel.SYSTEM
