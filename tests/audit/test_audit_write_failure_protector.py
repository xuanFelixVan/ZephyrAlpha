# [A_test] module_id: SRC-TST-0368 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_audit_write_failure_protector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_audit_write_failure_protector.py -q
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.gov_audit.writer import AuditWriter
from zephyr.gov_audit.audit_write_failure_protector import AuditWriteProtector


def _make_writer(tmp_path: Path) -> AuditWriter:
    return AuditWriter(data_dir=tmp_path, enable_merkle=False)


class TestAuditWriteProtectorInstantiation:
    def test_creates_instance_with_writer(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        assert protector is not None

    def test_creates_instance_without_writer(self):
        protector = AuditWriteProtector(writer=None)
        assert protector is not None

    def test_is_correct_type(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        assert isinstance(protector, AuditWriteProtector)


class TestCanWrite:
    def test_can_write_initially_true(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        assert protector.can_write() is True

    def test_can_write_after_failures_below_threshold(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        protector.record_failure()
        protector.record_failure()
        assert protector.can_write() is True

    def test_can_write_false_after_max_failures(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        for _ in range(writer._max_write_failures):
            protector.record_failure()
        assert protector.can_write() is False

    def test_can_write_true_when_no_writer(self):
        protector = AuditWriteProtector(writer=None)
        assert protector.can_write() is True


class TestRecordFailure:
    def test_single_failure_still_writable(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        protector.record_failure()
        assert protector.can_write() is True

    def test_failures_increment_write_failure_count(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        protector.record_failure()
        assert writer._write_failures == 1

    def test_exact_max_failures_triggers_readonly(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        for _ in range(writer._max_write_failures):
            protector.record_failure()
        assert writer._readonly is True

    def test_one_below_max_does_not_trigger_readonly(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        for _ in range(writer._max_write_failures - 1):
            protector.record_failure()
        assert writer._readonly is False


class TestReset:
    def test_reset_clears_readonly(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        for _ in range(writer._max_write_failures):
            protector.record_failure()
        assert protector.can_write() is False
        protector.reset()
        assert protector.can_write() is True

    def test_reset_clears_failure_count(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        protector.record_failure()
        protector.record_failure()
        protector.reset()
        assert writer._write_failures == 0

    def test_reset_then_record_failure_again(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        for _ in range(writer._max_write_failures):
            protector.record_failure()
        protector.reset()
        protector.record_failure()
        assert protector.can_write() is True


class TestBoundaryConditions:
    def test_no_writer_can_write_always_true(self):
        protector = AuditWriteProtector(writer=None)
        assert protector.can_write() is True

    def test_no_writer_record_failure_no_crash(self):
        protector = AuditWriteProtector(writer=None)
        protector.record_failure()

    def test_no_writer_reset_no_crash(self):
        protector = AuditWriteProtector(writer=None)
        protector.reset()

    def test_excess_failures_beyond_max_still_readonly(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        for _ in range(writer._max_write_failures + 5):
            protector.record_failure()
        assert protector.can_write() is False

    def test_reset_on_fresh_writer_is_noop(self, tmp_path):
        writer = _make_writer(tmp_path)
        protector = AuditWriteProtector(writer=writer)
        protector.reset()
        assert protector.can_write() is True
        assert writer._write_failures == 0
