# [A_test] module_id: SRC-TST-0885 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_external_validation_checkpoint
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_external_validation_checkpoint.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.external_validation_checkpoint import (
    EscalationReason,
    ExternalValidationCheckpoint,
)


class TestEscalationReason:
    def test_enum_values(self):
        assert EscalationReason.CONSECUTIVE_SELF_MOD_FAILURES.value == "consecutive_self_mod_failures"
        assert EscalationReason.LOW_GUARD_CONSENSUS.value == "low_guard_consensus"
        assert EscalationReason.UNKNOWN_STATE_SPACE.value == "unknown_state_space"
        assert EscalationReason.CRITICAL_METRIC_DEVIATION.value == "critical_metric_deviation"


class TestExternalValidationCheckpointInstantiation:
    def test_default_instantiation(self):
        checkpoint = ExternalValidationCheckpoint()
        assert checkpoint.consecutive_self_mod_failures == 0
        assert checkpoint.max_consecutive_failures == 3
        assert checkpoint.guard_consensus_threshold == 0.6
        assert checkpoint.known_state_space_hash == ""
        assert checkpoint.escalation_log == []
        assert checkpoint.owner_alerted is False

    def test_custom_parameters(self):
        checkpoint = ExternalValidationCheckpoint(max_consecutive_failures=5, guard_consensus_threshold=0.8)
        assert checkpoint.max_consecutive_failures == 5
        assert checkpoint.guard_consensus_threshold == 0.8

    def test_is_dataclass(self):
        checkpoint = ExternalValidationCheckpoint()
        assert hasattr(checkpoint, "__dataclass_fields__")


class TestRecordSelfModFailure:
    def test_first_failure_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint()
        result = checkpoint.record_self_mod_failure()
        assert result is None
        assert checkpoint.consecutive_self_mod_failures == 1

    def test_second_failure_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.record_self_mod_failure()
        result = checkpoint.record_self_mod_failure()
        assert result is None
        assert checkpoint.consecutive_self_mod_failures == 2

    def test_third_failure_triggers_escalation(self):
        checkpoint = ExternalValidationCheckpoint(max_consecutive_failures=3)
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        result = checkpoint.record_self_mod_failure()
        assert result == EscalationReason.CONSECUTIVE_SELF_MOD_FAILURES.value
        assert checkpoint.owner_alerted is True

    def test_escalation_logged(self):
        checkpoint = ExternalValidationCheckpoint(max_consecutive_failures=3)
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        assert len(checkpoint.escalation_log) == 1
        assert checkpoint.escalation_log[0]["reason"] == "consecutive_self_mod_failures"


class TestRecordSelfModSuccess:
    def test_resets_consecutive_failures(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_success()
        assert checkpoint.consecutive_self_mod_failures == 0

    def test_success_then_failure_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint(max_consecutive_failures=3)
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_success()
        checkpoint.record_self_mod_failure()
        assert checkpoint.consecutive_self_mod_failures == 1


class TestCheckGuardConsensus:
    def test_high_consensus_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint(guard_consensus_threshold=0.6)
        result = checkpoint.check_guard_consensus(agree_count=7, total_count=10)
        assert result is None

    def test_low_consensus_triggers_escalation(self):
        checkpoint = ExternalValidationCheckpoint(guard_consensus_threshold=0.6)
        result = checkpoint.check_guard_consensus(agree_count=3, total_count=10)
        assert result == EscalationReason.LOW_GUARD_CONSENSUS.value

    def test_zero_total_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint(guard_consensus_threshold=0.6)
        result = checkpoint.check_guard_consensus(agree_count=0, total_count=0)
        assert result is None

    def test_exact_threshold_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint(guard_consensus_threshold=0.6)
        result = checkpoint.check_guard_consensus(agree_count=6, total_count=10)
        assert result is None

    def test_just_below_threshold_escalation(self):
        checkpoint = ExternalValidationCheckpoint(guard_consensus_threshold=0.6)
        result = checkpoint.check_guard_consensus(agree_count=5, total_count=10)
        assert result == EscalationReason.LOW_GUARD_CONSENSUS.value


class TestCheckStateSpace:
    def test_no_known_hash_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint()
        result = checkpoint.check_state_space("abc123")
        assert result is None

    def test_matching_hash_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.register_known_state("abc123")
        result = checkpoint.check_state_space("abc123")
        assert result is None

    def test_unknown_hash_triggers_escalation(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.register_known_state("abc123")
        result = checkpoint.check_state_space("xyz789")
        assert result == EscalationReason.UNKNOWN_STATE_SPACE.value

    def test_registered_variant_no_escalation(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.register_known_state("abc123")
        checkpoint.register_known_state("def456")
        result = checkpoint.check_state_space("def456")
        assert result is None


class TestRegisterKnownState:
    def test_sets_known_hash(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.register_known_state("hash1")
        assert checkpoint.known_state_space_hash == "hash1"

    def test_registers_variant(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.register_known_state("hash1")
        checkpoint.register_known_state("hash2")
        assert checkpoint._hash_in_known_variants("hash1")
        assert checkpoint._hash_in_known_variants("hash2")


class TestGetPendingEscalations:
    def test_no_escalations(self):
        checkpoint = ExternalValidationCheckpoint()
        assert checkpoint.get_pending_escalations() == []

    def test_pending_after_escalation(self):
        checkpoint = ExternalValidationCheckpoint(max_consecutive_failures=3)
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        pending = checkpoint.get_pending_escalations()
        assert len(pending) == 1

    def test_acknowledged_not_pending(self):
        checkpoint = ExternalValidationCheckpoint(max_consecutive_failures=3)
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.acknowledge(0)
        pending = checkpoint.get_pending_escalations()
        assert len(pending) == 0


class TestAcknowledge:
    def test_acknowledge_valid_index(self):
        checkpoint = ExternalValidationCheckpoint(max_consecutive_failures=3)
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.record_self_mod_failure()
        checkpoint.acknowledge(0)
        assert checkpoint.escalation_log[0]["acknowledged"] is True

    def test_acknowledge_invalid_index_no_error(self):
        checkpoint = ExternalValidationCheckpoint()
        checkpoint.acknowledge(0)
        checkpoint.acknowledge(-1)
        checkpoint.acknowledge(99)
