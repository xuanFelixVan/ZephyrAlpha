# [A_test] module_id: SRC-TST-1087 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_guard_self_consistency_auditor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.guard_self_consistency_auditor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_guard_self_consistency_auditor.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.reliability.guard_self_consistency_auditor import (
    GuardHealthRecord,
    GuardSelfConsistencyAuditor,
)


class TestGuardSelfConsistencyAuditorInstantiation:
    def test_default_instantiation(self):
        auditor = GuardSelfConsistencyAuditor()
        assert auditor.guard_records == {}
        assert auditor.deviation_threshold == 3.0
        assert auditor.establish_baseline_after == 50

    def test_custom_parameters(self):
        auditor = GuardSelfConsistencyAuditor(deviation_threshold=2.5, establish_baseline_after=30)
        assert auditor.deviation_threshold == 2.5
        assert auditor.establish_baseline_after == 30

    def test_empty_guard_records(self):
        auditor = GuardSelfConsistencyAuditor()
        assert len(auditor.guard_records) == 0


class TestGuardHealthRecord:
    def test_default_values(self):
        rec = GuardHealthRecord(guard_id="g1")
        assert rec.guard_id == "g1"
        assert rec.pass_count == 0
        assert rec.fail_count == 0
        assert rec.total_count == 0
        assert rec.baseline_pass_rate is None

    def test_custom_values(self):
        rec = GuardHealthRecord(guard_id="g2", pass_count=10, fail_count=5, total_count=15, baseline_pass_rate=0.667)
        assert rec.pass_count == 10
        assert rec.fail_count == 5
        assert rec.total_count == 15
        assert rec.baseline_pass_rate == pytest.approx(0.667, abs=0.01)


class TestRecordOutcome:
    def test_record_pass_creates_new_record(self):
        auditor = GuardSelfConsistencyAuditor()
        auditor.record_outcome("guard_a", passed=True)
        assert "guard_a" in auditor.guard_records
        assert auditor.guard_records["guard_a"].pass_count == 1
        assert auditor.guard_records["guard_a"].fail_count == 0
        assert auditor.guard_records["guard_a"].total_count == 1

    def test_record_fail_creates_new_record(self):
        auditor = GuardSelfConsistencyAuditor()
        auditor.record_outcome("guard_b", passed=False)
        assert "guard_b" in auditor.guard_records
        assert auditor.guard_records["guard_b"].pass_count == 0
        assert auditor.guard_records["guard_b"].fail_count == 1
        assert auditor.guard_records["guard_b"].total_count == 1

    def test_record_multiple_outcomes_same_guard(self):
        auditor = GuardSelfConsistencyAuditor()
        auditor.record_outcome("guard_c", passed=True)
        auditor.record_outcome("guard_c", passed=True)
        auditor.record_outcome("guard_c", passed=False)
        assert auditor.guard_records["guard_c"].pass_count == 2
        assert auditor.guard_records["guard_c"].fail_count == 1
        assert auditor.guard_records["guard_c"].total_count == 3

    def test_baseline_established_after_threshold(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=5)
        for _ in range(4):
            auditor.record_outcome("guard_d", passed=True)
        assert auditor.guard_records["guard_d"].baseline_pass_rate is None
        auditor.record_outcome("guard_d", passed=True)
        assert auditor.guard_records["guard_d"].baseline_pass_rate is not None
        assert auditor.guard_records["guard_d"].baseline_pass_rate == 1.0

    def test_baseline_reflects_actual_rate(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=10)
        for i in range(10):
            auditor.record_outcome("guard_e", passed=(i < 7))
        assert auditor.guard_records["guard_e"].baseline_pass_rate == pytest.approx(0.7)

    def test_multiple_guards_tracked_separately(self):
        auditor = GuardSelfConsistencyAuditor()
        auditor.record_outcome("guard_x", passed=True)
        auditor.record_outcome("guard_y", passed=False)
        assert auditor.guard_records["guard_x"].pass_count == 1
        assert auditor.guard_records["guard_y"].fail_count == 1

    def test_empty_guard_id(self):
        auditor = GuardSelfConsistencyAuditor()
        auditor.record_outcome("", passed=True)
        assert "" in auditor.guard_records
        assert auditor.guard_records[""].pass_count == 1


class TestAuditConsistency:
    def test_empty_records_returns_empty(self):
        auditor = GuardSelfConsistencyAuditor()
        result = auditor.audit_consistency()
        assert result["unhealthy_guards"] == []
        assert result["findings"] == {}
        assert result["total_guards_audited"] == 0

    def test_insufficient_data_skipped(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=5)
        for _ in range(9):
            auditor.record_outcome("guard_f", passed=True)
        result = auditor.audit_consistency()
        assert result["total_guards_audited"] == 0

    def test_healthy_guard(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=10, deviation_threshold=3.0)
        for _ in range(10):
            auditor.record_outcome("guard_h", passed=True)
        for _ in range(10):
            auditor.record_outcome("guard_h", passed=True)
        result = auditor.audit_consistency()
        if "guard_h" in result["findings"]:
            assert result["findings"]["guard_h"]["is_healthy"] is True

    def test_always_pass_detected(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=10, deviation_threshold=0.5)
        for _ in range(10):
            auditor.record_outcome("guard_ap", passed=True)
        for _ in range(90):
            auditor.record_outcome("guard_ap", passed=True)
        result = auditor.audit_consistency()
        if "guard_ap" in result["findings"]:
            finding = result["findings"]["guard_ap"]
            if finding["current_pass_rate"] > 0.95:
                assert finding["status"] in ("always_pass", "healthy")

    def test_always_fail_detected(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=10, deviation_threshold=0.5)
        for _ in range(10):
            auditor.record_outcome("guard_af", passed=True)
        for _ in range(90):
            auditor.record_outcome("guard_af", passed=False)
        result = auditor.audit_consistency()
        if "guard_af" in result["findings"]:
            finding = result["findings"]["guard_af"]
            if finding["current_pass_rate"] < 0.05:
                assert finding["status"] in ("always_fail", "distribution_drifted")

    def test_silent_failures_counted(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=10, deviation_threshold=0.5)
        for _ in range(10):
            auditor.record_outcome("guard_sf", passed=True)
        for _ in range(90):
            auditor.record_outcome("guard_sf", passed=True)
        result = auditor.audit_consistency()
        assert isinstance(result["silent_failures_detected"], int)

    def test_no_baseline_skips_guard(self):
        auditor = GuardSelfConsistencyAuditor(establish_baseline_after=100)
        for _ in range(50):
            auditor.record_outcome("guard_nb", passed=True)
        result = auditor.audit_consistency()
        assert "guard_nb" not in result["findings"]
