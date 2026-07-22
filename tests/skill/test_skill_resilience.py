# [A_test] module_id: MOD-GOV_skill_resilience | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_resilience
# [INVARIANTS] SkillResilience.reset() called in every test teardown
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises RuntimeError on exhausted retries
# [TESTS] tests/test_skill_resilience.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

import pytest

from zephyr.autonomy_core.skills.skill_resilience import SkillResilience


@pytest.fixture(autouse=True)
def _reset_resilience():
    yield
    SkillResilience.reset()


class TestSkillResilienceInstantiation:
    def test_class_attributes_exist(self):
        assert SkillResilience.MAX_RETRIES == 3
        assert SkillResilience.BASE_DELAY_S == 1.0
        assert SkillResilience.MAX_DELAY_S == 30.0

    def test_internal_dicts_initially_empty(self):
        SkillResilience.reset()
        assert SkillResilience._failure_count == {}
        assert SkillResilience._last_failure_time == {}
        assert SkillResilience._circuit_open == {}
        assert SkillResilience._circuit_open_until == {}


class TestShouldRetry:
    def test_should_retry_when_no_failures(self):
        assert SkillResilience.should_retry("skill_a") is True

    def test_should_retry_within_limit(self):
        SkillResilience.record_failure("skill_a")
        SkillResilience.record_failure("skill_a")
        assert SkillResilience.should_retry("skill_a") is True

    def test_should_not_retry_at_max(self):
        for _ in range(SkillResilience.MAX_RETRIES):
            SkillResilience.record_failure("skill_a")
        assert SkillResilience.should_retry("skill_a") is False

    def test_should_not_retry_when_circuit_open(self):
        SkillResilience._circuit_open["skill_a"] = True
        SkillResilience._circuit_open_until["skill_a"] = 9999999999.0
        assert SkillResilience.should_retry("skill_a") is False

    def test_should_retry_empty_skill_id(self):
        assert SkillResilience.should_retry("") is True


class TestRecordFailure:
    def test_increments_failure_count(self):
        count = SkillResilience.record_failure("skill_a")
        assert count == 1
        count = SkillResilience.record_failure("skill_a")
        assert count == 2

    def test_opens_circuit_at_max_retries(self):
        for _ in range(SkillResilience.MAX_RETRIES):
            SkillResilience.record_failure("skill_a")
        assert SkillResilience._circuit_open.get("skill_a") is True

    def test_records_last_failure_time(self):
        SkillResilience.record_failure("skill_a")
        assert "skill_a" in SkillResilience._last_failure_time
        assert SkillResilience._last_failure_time["skill_a"] > 0

    def test_independent_skill_ids(self):
        SkillResilience.record_failure("skill_a")
        SkillResilience.record_failure("skill_b")
        assert SkillResilience._failure_count["skill_a"] == 1
        assert SkillResilience._failure_count["skill_b"] == 1


class TestRecordSuccess:
    def test_clears_failure_state(self):
        SkillResilience.record_failure("skill_a")
        SkillResilience.record_failure("skill_a")
        SkillResilience.record_success("skill_a")
        assert "skill_a" not in SkillResilience._failure_count
        assert "skill_a" not in SkillResilience._last_failure_time
        assert "skill_a" not in SkillResilience._circuit_open
        assert "skill_a" not in SkillResilience._circuit_open_until

    def test_record_success_on_never_failed_skill(self):
        SkillResilience.record_success("skill_never_failed")
        assert "skill_never_failed" not in SkillResilience._failure_count


class TestRetryWithBackoff:
    def test_succeeds_on_first_try(self):
        result, attempts = SkillResilience.retry_with_backoff("skill_ok", lambda: 42)
        assert result == 42
        assert attempts == 1

    def test_retries_and_succeeds(self):
        call_count = 0

        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("transient")
            return "ok"

        with patch("zephyr.autonomy_core.skills.skill_resilience.time.sleep"):
            result, attempts = SkillResilience.retry_with_backoff("skill_flaky", flaky, max_retries=3)
        assert result == "ok"
        assert attempts == 2

    def test_raises_after_all_retries_exhausted(self):
        def always_fail():
            raise RuntimeError("boom")

        with patch("zephyr.autonomy_core.skills.skill_resilience.time.sleep"):
            with pytest.raises(RuntimeError, match="boom"):
                SkillResilience.retry_with_backoff("skill_dead", always_fail, max_retries=2)

    def test_uses_default_max_retries(self):
        call_count = 0

        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with patch("zephyr.autonomy_core.skills.skill_resilience.time.sleep"):
            with pytest.raises(ValueError):
                SkillResilience.retry_with_backoff("skill_dead2", always_fail)
        assert call_count == SkillResilience.MAX_RETRIES


class TestIsCircuitOpen:
    def test_not_open_by_default(self):
        assert SkillResilience.is_circuit_open("skill_a") is False

    def test_open_when_set_and_not_expired(self):
        SkillResilience._circuit_open["skill_a"] = True
        SkillResilience._circuit_open_until["skill_a"] = 9999999999.0
        assert SkillResilience.is_circuit_open("skill_a") is True

    def test_auto_closes_when_expired(self):
        SkillResilience._circuit_open["skill_a"] = True
        SkillResilience._circuit_open_until["skill_a"] = 0.0
        assert SkillResilience.is_circuit_open("skill_a") is False
        assert SkillResilience._circuit_open["skill_a"] is False


class TestReset:
    def test_reset_specific_skill(self):
        SkillResilience.record_failure("skill_a")
        SkillResilience.record_failure("skill_b")
        SkillResilience.reset("skill_a")
        assert "skill_a" not in SkillResilience._failure_count
        assert "skill_b" in SkillResilience._failure_count

    def test_reset_all_skills(self):
        SkillResilience.record_failure("skill_a")
        SkillResilience.record_failure("skill_b")
        SkillResilience.reset()
        assert SkillResilience._failure_count == {}
        assert SkillResilience._circuit_open == {}

    def test_reset_none_arg_clears_all(self):
        SkillResilience.record_failure("skill_x")
        SkillResilience.reset(None)
        assert SkillResilience._failure_count == {}
