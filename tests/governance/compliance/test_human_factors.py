# [A_test] module_id: MOD-GOV_human_factors | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_human_factors
# [INVARIANTS] 疲劳/情绪检测不可禁用;人因告警必须升级
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_human_factors.py
# [TTL] task_bound

import time

from zephyr.governance.escalation.human_factors import HumanFactors


class TestHumanFactorsInit:
    def test_instantiation(self):
        hf = HumanFactors()
        assert hf._notification_count == {}
        assert hf._last_notified == {}
        assert hf._min_interval_s == 300
        assert hf._max_per_hour == 12

    def test_multiple_instances_independent(self):
        hf1 = HumanFactors()
        hf2 = HumanFactors()
        hf1.should_notify("owner_a")
        assert "owner_a" not in hf2._last_notified


class TestShouldNotify:
    def test_first_notification_allowed(self):
        hf = HumanFactors()
        allowed, reason = hf.should_notify("owner_1")
        assert allowed is True
        assert reason == "OK"

    def test_notification_count_increments_across_intervals(self):
        hf = HumanFactors()
        hf._min_interval_s = 0
        hf.should_notify("owner_1")
        assert hf._notification_count["owner_1"] == 1
        hf.should_notify("owner_1")
        assert hf._notification_count["owner_1"] == 2

    def test_notification_count_no_increment_when_rejected(self):
        hf = HumanFactors()
        hf.should_notify("owner_1")
        hf.should_notify("owner_1")
        assert hf._notification_count["owner_1"] == 1

    def test_different_owners_independent(self):
        hf = HumanFactors()
        allowed_a, _ = hf.should_notify("owner_a")
        allowed_b, _ = hf.should_notify("owner_b")
        assert allowed_a is True
        assert allowed_b is True
        assert hf._notification_count["owner_a"] == 1
        assert hf._notification_count["owner_b"] == 1

    def test_too_frequent_rejected(self):
        hf = HumanFactors()
        hf.should_notify("owner_1")
        allowed, reason = hf.should_notify("owner_1")
        assert allowed is False
        assert reason == "Too frequent"

    def test_allowed_after_interval_passes(self):
        hf = HumanFactors()
        hf._min_interval_s = 1
        hf.should_notify("owner_1")
        hf._last_notified["owner_1"] = time.time() - 2
        allowed, reason = hf.should_notify("owner_1")
        assert allowed is True
        assert reason == "OK"

    def test_rate_limit_check_uses_last_notified_window(self):
        hf = HumanFactors()
        hf._max_per_hour = 1
        hf._last_notified["owner_1"] = time.time() - 100
        allowed, reason = hf.should_notify("owner_1")
        assert allowed is False
        assert reason == "Rate limited"

    def test_rate_limit_not_triggered_when_outside_window(self):
        hf = HumanFactors()
        hf._max_per_hour = 1
        hf._last_notified["owner_1"] = time.time() - 3601
        allowed, reason = hf.should_notify("owner_1")
        assert allowed is True
        assert reason == "OK"


class TestShouldNotifyBoundary:
    def test_empty_owner_id(self):
        hf = HumanFactors()
        allowed, reason = hf.should_notify("")
        assert allowed is True
        assert reason == "OK"

    def test_none_owner_id_accepted_as_key(self):
        hf = HumanFactors()
        allowed, reason = hf.should_notify(None)
        assert allowed is True
        assert reason == "OK"

    def test_numeric_owner_id(self):
        hf = HumanFactors()
        allowed, reason = hf.should_notify("12345")
        assert allowed is True
        assert reason == "OK"

    def test_unicode_owner_id(self):
        hf = HumanFactors()
        allowed, reason = hf.should_notify("用户_001")
        assert allowed is True
        assert reason == "OK"

    def test_very_long_owner_id(self):
        hf = HumanFactors()
        long_id = "x" * 10000
        allowed, reason = hf.should_notify(long_id)
        assert allowed is True
        assert reason == "OK"

    def test_min_interval_exact_boundary(self):
        hf = HumanFactors()
        hf._min_interval_s = 100
        hf.should_notify("owner_1")
        hf._last_notified["owner_1"] = time.time() - 100
        allowed, reason = hf.should_notify("owner_1")
        assert allowed is True
        assert reason == "OK"

    def test_min_interval_just_below_boundary(self):
        hf = HumanFactors()
        hf._min_interval_s = 100
        hf.should_notify("owner_1")
        hf._last_notified["owner_1"] = time.time() - 99.9
        allowed, reason = hf.should_notify("owner_1")
        assert allowed is False
        assert reason == "Too frequent"
