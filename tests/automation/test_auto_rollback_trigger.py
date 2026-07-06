# [A_test] module_id: SRC-TST-0380 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_auto_rollback_trigger
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.rollback.auto_rollback_trigger import (
    AutoGuardResult,
    AutoRollbackTrigger,
    ActionType,
    FailureCategory,
    TriggerDecision,
)


class TestFailureCategory:
    def test_hard_value(self):
        assert FailureCategory.HARD == "hard_failure"

    def test_soft_value(self):
        assert FailureCategory.SOFT == "soft_failure"

    def test_transient_value(self):
        assert FailureCategory.TRANSIENT == "transient"

    def test_all_categories(self):
        values = {c.value for c in FailureCategory}
        assert values == {"hard_failure", "soft_failure", "transient"}


class TestAutoGuardResult:
    def test_instantiation(self):
        r = AutoGuardResult(
            source="CI",
            gate_id="G0",
            task_id="T1",
            passed=False,
            error_message="build failed",
            error_code=1,
        )
        assert r.source == "CI"
        assert r.passed is False
        assert r.error_code == 1

    def test_default_metadata(self):
        r = AutoGuardResult(
            source="lint",
            gate_id="G1",
            task_id="T2",
            passed=True,
            error_message="",
            error_code=0,
        )
        assert r.metadata == {}

    def test_custom_metadata(self):
        r = AutoGuardResult(
            source="x",
            gate_id="g",
            task_id="t",
            passed=False,
            error_message="",
            error_code=1,
            metadata={"key": "val"},
        )
        assert r.metadata == {"key": "val"}


class TestTriggerDecision:
    def test_instantiation(self):
        td = TriggerDecision(
            category=FailureCategory.HARD,
            action=ActionType.ROLLBACK,
            reason="critical failure",
        )
        assert td.category == FailureCategory.HARD
        assert td.should_rollback is True
        assert td.retry_allowed is False


class TestAutoRollbackTriggerInstantiation:
    def test_default_max_retries(self):
        trigger = AutoRollbackTrigger()
        assert trigger._max_retries == 3

    def test_custom_max_retries(self):
        trigger = AutoRollbackTrigger(max_retries=5)
        assert trigger._max_retries == 5

    def test_empty_retry_counts(self):
        trigger = AutoRollbackTrigger()
        assert trigger.retry_counts == {}


class TestClassifyHardFailure:
    def test_drift_detector_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="drift-detector",
            gate_id="G6",
            task_id="T1",
            passed=False,
            error_message="drift detected",
            error_code=2,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.HARD
        assert decision.should_rollback is True
        assert decision.action == "ROLLBACK_IMMEDIATE"

    def test_ci_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="CI",
            gate_id="G0",
            task_id="T2",
            passed=False,
            error_message="pipeline failed",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.HARD

    def test_g6_secrets_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="G6_secrets",
            gate_id="G6",
            task_id="T3",
            passed=False,
            error_message="secrets leak",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.HARD

    def test_hard_pattern_in_error_message(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="unknown",
            gate_id="G0",
            task_id="T4",
            passed=False,
            error_message="corruption detected in db",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.HARD

    def test_kill_switch_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="kill_switch",
            gate_id="KS",
            task_id="T5",
            passed=False,
            error_message="emergency stop",
            error_code=99,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.HARD


class TestClassifySoftFailure:
    def test_lint_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="lint",
            gate_id="G1",
            task_id="T6",
            passed=False,
            error_message="style error",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.SOFT
        assert decision.should_rollback is False
        assert decision.action == "FORWARD_FIX_PREFERRED"
        assert decision.forward_fix_allowed is True

    def test_syntax_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="syntax",
            gate_id="G0",
            task_id="T7",
            passed=False,
            error_message="syntax error",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.SOFT

    def test_soft_pattern_in_error_message(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="unknown",
            gate_id="G0",
            task_id="T8",
            passed=False,
            error_message="indentation error at line 5",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.SOFT

    def test_passed_result_classified_soft(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="any",
            gate_id="G0",
            task_id="T9",
            passed=True,
            error_message="",
            error_code=0,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.SOFT


class TestClassifyTransient:
    def test_timeout_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="timeout",
            gate_id="G0",
            task_id="T10",
            passed=False,
            error_message="request timed out",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.TRANSIENT
        assert decision.action == "RETRY"
        assert decision.retry_allowed is True

    def test_network_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="network",
            gate_id="G0",
            task_id="T11",
            passed=False,
            error_message="connection refused",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.TRANSIENT

    def test_transient_pattern_in_error_message(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="unknown",
            gate_id="G0",
            task_id="T12",
            passed=False,
            error_message="temporary failure, retry later",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.TRANSIENT

    def test_rate_limit_source(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="rate_limit",
            gate_id="G0",
            task_id="T13",
            passed=False,
            error_message="too many requests",
            error_code=429,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.TRANSIENT


class TestTransientRetryExhaustion:
    def test_retries_exhausted_upgrades_to_soft(self):
        trigger = AutoRollbackTrigger(max_retries=2)
        key_base = "T14:G0"
        for i in range(2):
            result = AutoGuardResult(
                source="timeout",
                gate_id="G0",
                task_id="T14",
                passed=False,
                error_message="timeout",
                error_code=1,
            )
            decision = trigger.classify(result)
        result3 = AutoGuardResult(
            source="timeout",
            gate_id="G0",
            task_id="T14",
            passed=False,
            error_message="timeout",
            error_code=1,
        )
        decision = trigger.classify(result3)
        assert decision.action == "UPGRADE_TO_SOFT"
        assert decision.retry_allowed is False
        assert decision.forward_fix_allowed is True

    def test_retry_counts_tracked(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="timeout",
            gate_id="G0",
            task_id="T15",
            passed=False,
            error_message="timeout",
            error_code=1,
        )
        trigger.classify(result)
        assert "T15:G0" in trigger.retry_counts
        assert trigger.retry_counts["T15:G0"] == 1


class TestProcessGuardResult:
    def test_process_guard_result_delegates_to_classify(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="drift-detector",
            gate_id="G6",
            task_id="T16",
            passed=False,
            error_message="drift detected",
            error_code=1,
        )
        decision = trigger.process_guard_result(result)
        assert decision.category == FailureCategory.HARD
        assert decision.should_rollback is True


class TestDefaultClassification:
    def test_unknown_source_and_message_defaults_to_soft(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="custom_checker",
            gate_id="GX",
            task_id="T17",
            passed=False,
            error_message="unknown issue occurred",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.SOFT

    def test_empty_error_message(self):
        trigger = AutoRollbackTrigger()
        result = AutoGuardResult(
            source="custom",
            gate_id="GX",
            task_id="T18",
            passed=False,
            error_message="",
            error_code=1,
        )
        decision = trigger.classify(result)
        assert decision.category == FailureCategory.SOFT
