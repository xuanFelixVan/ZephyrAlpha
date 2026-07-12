# [A_test] module_id: SRC-TST-0544 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_cold_start_conservative_mode
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cold_start_conservative_mode
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_cold_start_conservative_mode.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.cold_start_conservative_mode import (
    ColdStartConservativeMode,
    ColdStartPhase,
)


class TestColdStartPhase:
    def test_collect_only_value(self):
        assert ColdStartPhase.COLLECT_ONLY.value == "collect_only"

    def test_with_detect_value(self):
        assert ColdStartPhase.WITH_DETECT.value == "with_detect"

    def test_with_diagnose_value(self):
        assert ColdStartPhase.WITH_DIAGNOSE.value == "with_diagnose"

    def test_full_enabled_value(self):
        assert ColdStartPhase.FULL_ENABLED.value == "full_enabled"

    def test_all_phases_count(self):
        assert len(ColdStartPhase) == 4


class TestColdStartConservativeModeInstantiation:
    def test_default_params(self):
        cscm = ColdStartConservativeMode()
        assert cscm.started_at == 0.0
        assert cscm.current_cycle == 0
        assert cscm.phase == ColdStartPhase.COLLECT_ONLY
        assert cscm.threshold_multiplier == 3.0

    def test_blocked_actions_default(self):
        cscm = ColdStartConservativeMode()
        assert "SELF_UPGRADE" in cscm.blocked_actions
        assert "PROMPT_EVOLVE" in cscm.blocked_actions
        assert "KNOWLEDGE_INJECT" in cscm.blocked_actions


class TestColdStartConservativeModeStart:
    def test_start_resets_state(self):
        cscm = ColdStartConservativeMode()
        cscm.current_cycle = 50
        cscm.phase = ColdStartPhase.WITH_DETECT
        cscm.start()
        assert cscm.current_cycle == 0
        assert cscm.phase == ColdStartPhase.COLLECT_ONLY
        assert cscm.started_at > 0


class TestColdStartConservativeModeTick:
    def test_tick_increments_cycle(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        cscm.tick()
        assert cscm.current_cycle == 1

    def test_tick_transitions_to_with_detect(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        for _ in range(100):
            cscm.tick()
        assert cscm.phase == ColdStartPhase.WITH_DETECT

    def test_tick_transitions_to_with_diagnose(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        for _ in range(300):
            cscm.tick()
        assert cscm.phase == ColdStartPhase.WITH_DIAGNOSE

    def test_tick_transitions_to_full_enabled(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        for _ in range(500):
            cscm.tick()
        assert cscm.phase == ColdStartPhase.FULL_ENABLED


class TestColdStartConservativeModeIsWarm:
    def test_not_warm_initially(self):
        cscm = ColdStartConservativeMode()
        assert cscm.is_warm() is False

    def test_warm_after_full_transition(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        for _ in range(500):
            cscm.tick()
        assert cscm.is_warm() is True


class TestColdStartConservativeModeThresholdMultiplier:
    def test_initial_multiplier(self):
        cscm = ColdStartConservativeMode()
        mult = cscm.current_threshold_multiplier()
        assert mult >= 1.0

    def test_full_enabled_multiplier_is_one(self):
        cscm = ColdStartConservativeMode()
        cscm.phase = ColdStartPhase.FULL_ENABLED
        assert cscm.current_threshold_multiplier() == 1.0


class TestColdStartConservativeModeIsActionAllowed:
    def test_collect_action_allowed_in_collect_only(self):
        cscm = ColdStartConservativeMode()
        cscm.phase = ColdStartPhase.COLLECT_ONLY
        assert cscm.is_action_allowed("COLLECT_METRICS") is True

    def test_blocked_action_not_allowed_in_collect_only(self):
        cscm = ColdStartConservativeMode()
        cscm.phase = ColdStartPhase.COLLECT_ONLY
        assert cscm.is_action_allowed("SELF_UPGRADE") is False

    def test_all_actions_allowed_in_full_enabled(self):
        cscm = ColdStartConservativeMode()
        cscm.phase = ColdStartPhase.FULL_ENABLED
        assert cscm.is_action_allowed("SELF_UPGRADE") is True
        assert cscm.is_action_allowed("ANY_ACTION") is True

    def test_detect_action_allowed_in_with_detect(self):
        cscm = ColdStartConservativeMode()
        cscm.phase = ColdStartPhase.WITH_DETECT
        assert cscm.is_action_allowed("DETECT_ANOMALY") is True

    def test_diagnose_action_allowed_in_with_diagnose(self):
        cscm = ColdStartConservativeMode()
        cscm.phase = ColdStartPhase.WITH_DIAGNOSE
        assert cscm.is_action_allowed("DIAGNOSE_ROOT") is True


class TestColdStartConservativeModeStatusReport:
    def test_status_report_keys(self):
        cscm = ColdStartConservativeMode()
        cscm.start()
        report = cscm.status_report()
        assert "phase" in report
        assert "cycle" in report
        assert "is_warm" in report
        assert "threshold_multiplier" in report
        assert "elapsed_seconds" in report

    def test_status_report_before_start(self):
        cscm = ColdStartConservativeMode()
        report = cscm.status_report()
        assert report["elapsed_seconds"] == 0


class TestColdStartConservativeModeBoundary:
    def test_elapsed_cycles_before_start(self):
        cscm = ColdStartConservativeMode()
        assert cscm.elapsed_cycles() == 0

    def test_empty_action_type(self):
        cscm = ColdStartConservativeMode()
        cscm.phase = ColdStartPhase.COLLECT_ONLY
        result = cscm.is_action_allowed("")
        assert result is True
