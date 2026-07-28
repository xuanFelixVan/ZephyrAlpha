# [A_test] module_id: MOD-GOV_escalation_loop_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_loop_detector
# [INVARIANTS] 跨模块循环检测不可跳过;DFS必须覆盖所有活跃升级
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_escalation_loop_detector.py
# [TTL] task_bound


from zephyr.governance.escalation.escalation_loop_detector import EscalationLoopDetector


class TestEscalationLoopDetectorInstantiation:
    def test_instantiation(self):
        eld = EscalationLoopDetector()
        assert eld is not None

    def test_empty_history(self):
        eld = EscalationLoopDetector()
        assert eld.history == []


class TestRecordTransition:
    def test_record_adds_two_entries(self):
        eld = EscalationLoopDetector()
        eld.record_transition("T-1", "L1", "L2")
        assert len(eld.history) == 2

    def test_record_multiple_transitions(self):
        eld = EscalationLoopDetector()
        eld.record_transition("T-1", "L1", "L2")
        eld.record_transition("T-1", "L2", "L3")
        assert len(eld.history) == 4

    def test_record_different_tasks(self):
        eld = EscalationLoopDetector()
        eld.record_transition("T-1", "L1", "L2")
        eld.record_transition("T-2", "L1", "L2")
        assert len(eld.history) == 4


class TestDetectLoop:
    def test_no_history_no_loop(self):
        eld = EscalationLoopDetector()
        assert eld.detect_loop() is False

    def test_few_transitions_no_loop(self):
        eld = EscalationLoopDetector()
        eld.record_transition("T-1", "L1", "L2")
        eld.record_transition("T-1", "L2", "L3")
        assert eld.detect_loop() is False

    def test_loop_detected(self):
        eld = EscalationLoopDetector()
        for _ in range(3):
            eld.record_transition("T-1", "L1", "L2")
        assert eld.detect_loop() is True

    def test_loop_per_task(self):
        eld = EscalationLoopDetector()
        for _ in range(3):
            eld.record_transition("T-1", "L1", "L2")
        eld.record_transition("T-2", "L1", "L2")
        assert eld.detect_loop() is True

    def test_no_loop_spread_across_tasks(self):
        eld = EscalationLoopDetector()
        for i in range(6):
            eld.record_transition(f"T-{i}", "L1", "L2")
        assert eld.detect_loop() is False

    def test_custom_window(self):
        eld = EscalationLoopDetector()
        for _ in range(3):
            eld.record_transition("T-1", "L1", "L2")
        assert eld.detect_loop(window_s=0) is False
