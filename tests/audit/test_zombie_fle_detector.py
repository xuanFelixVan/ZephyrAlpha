# [A_test] module_id: SRC-TST-1813 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_zombie_fle_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.zombie_fle_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_zombie_fle_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.zombie_fle_detector import (
    CognitionTest,
    CognitiveState,
    ZombieFLEDetector,
)


class TestCognitiveState:
    def test_alive_value(self):
        assert CognitiveState.ALIVE.value == "ALIVE"

    def test_degraded_value(self):
        assert CognitiveState.DEGRADED.value == "DEGRADED"

    def test_zombie_value(self):
        assert CognitiveState.ZOMBIE.value == "ZOMBIE"

    def test_all_states_count(self):
        assert len(CognitiveState) == 3


class TestCognitionTest:
    def test_creation(self):
        ct = CognitionTest(test_id="cog-0", sent_at=1000.0)
        assert ct.test_id == "cog-0"
        assert ct.sent_at == 1000.0
        assert ct.responded_at is None
        assert ct.passed is False

    def test_with_response(self):
        ct = CognitionTest(test_id="cog-1", sent_at=1000.0, responded_at=1001.0, passed=True)
        assert ct.responded_at == 1001.0
        assert ct.passed is True

    def test_is_dataclass(self):
        ct = CognitionTest(test_id="x", sent_at=0.0)
        assert hasattr(ct, "__dataclass_fields__")


class TestZombieFLEDetectorInstantiation:
    def test_default_params(self):
        zfd = ZombieFLEDetector()
        assert zfd.tests == []
        assert zfd.state == CognitiveState.ALIVE
        assert zfd.test_interval == 300.0
        assert zfd.max_consecutive_failures == 3
        assert zfd.consecutive_fails == 0

    def test_custom_params(self):
        zfd = ZombieFLEDetector(
            test_interval=60.0,
            max_consecutive_failures=5,
        )
        assert zfd.test_interval == 60.0
        assert zfd.max_consecutive_failures == 5


class TestSendTest:
    def test_returns_cognition_test(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        assert isinstance(test, CognitionTest)

    def test_appends_to_tests(self):
        zfd = ZombieFLEDetector()
        zfd.send_test()
        zfd.send_test()
        assert len(zfd.tests) == 2

    def test_test_id_increments(self):
        zfd = ZombieFLEDetector()
        t1 = zfd.send_test()
        t2 = zfd.send_test()
        assert t1.test_id != t2.test_id

    def test_sent_at_is_set(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        assert test.sent_at > 0

    def test_initial_test_not_passed(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        assert test.passed is False


class TestVerifyResponse:
    def test_pass_resets_consecutive_fails(self):
        zfd = ZombieFLEDetector()
        zfd.consecutive_fails = 2
        test = zfd.send_test()
        zfd.verify_response(test.test_id, passed=True)
        assert zfd.consecutive_fails == 0

    def test_pass_sets_alive(self):
        zfd = ZombieFLEDetector()
        zfd.state = CognitiveState.ZOMBIE
        test = zfd.send_test()
        zfd.verify_response(test.test_id, passed=True)
        assert zfd.state == CognitiveState.ALIVE

    def test_fail_increments_consecutive(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        zfd.verify_response(test.test_id, passed=False)
        assert zfd.consecutive_fails == 1

    def test_max_failures_triggers_zombie(self):
        zfd = ZombieFLEDetector(max_consecutive_failures=3)
        for _ in range(3):
            test = zfd.send_test()
            zfd.verify_response(test.test_id, passed=False)
        assert zfd.state == CognitiveState.ZOMBIE

    def test_interleaved_pass_resets(self):
        zfd = ZombieFLEDetector(max_consecutive_failures=3)
        test1 = zfd.send_test()
        zfd.verify_response(test1.test_id, passed=False)
        test2 = zfd.send_test()
        zfd.verify_response(test2.test_id, passed=False)
        test3 = zfd.send_test()
        zfd.verify_response(test3.test_id, passed=True)
        assert zfd.state == CognitiveState.ALIVE
        assert zfd.consecutive_fails == 0

    def test_test_marked_passed(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        zfd.verify_response(test.test_id, passed=True)
        assert test.passed is True
        assert test.responded_at is not None

    def test_test_marked_failed(self):
        zfd = ZombieFLEDetector()
        test = zfd.send_test()
        zfd.verify_response(test.test_id, passed=False)
        assert test.passed is False
        assert test.responded_at is not None

    def test_unknown_test_id_no_crash(self):
        zfd = ZombieFLEDetector()
        zfd.verify_response("nonexistent", passed=True)
        assert zfd.consecutive_fails == 0
