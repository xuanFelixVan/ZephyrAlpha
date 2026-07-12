# [A_test] module_id: SRC-TST-0451 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_brain_integration
# [INVARIANTS] 大脑集成不可断开
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI;drift_engine
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_brain_integration_root.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.brain_integration import (
    ClosedLoopResult,
    FullProbeResult,
    L0StartupResult,
    L1ReadinessResult,
    L2LivenessResult,
    L3ReconcileResult,
    ProbeStatus,
    execute_closed_loop,
    execute_full_probe,
)


class TestProbeStatus:
    def test_has_expected_values(self):
        assert ProbeStatus.PASS == "PASS"
        assert ProbeStatus.WARN == "WARN"
        assert ProbeStatus.FAIL == "FAIL"
        assert ProbeStatus.SKIPPED == "SKIPPED"


class TestL0StartupResult:
    def test_defaults(self):
        r = L0StartupResult()
        assert r.phase == "L0_STARTUP"
        assert r.status == ProbeStatus.SKIPPED
        assert r.env_ok is False
        assert r.core_integrity_ok is False
        assert r.db_ok is False
        assert r.errors == []
        assert r.warnings == []


class TestL1ReadinessResult:
    def test_defaults(self):
        r = L1ReadinessResult()
        assert r.phase == "L1_READINESS"
        assert r.status == ProbeStatus.SKIPPED
        assert r.startup_check_ok is False
        assert r.gate_selfcheck_ok is False


class TestL2LivenessResult:
    def test_defaults(self):
        r = L2LivenessResult()
        assert r.phase == "L2_LIVENESS"
        assert r.status == ProbeStatus.SKIPPED
        assert r.scan_events_found == 0
        assert r.orphan_resources == 0


class TestL3ReconcileResult:
    def test_defaults(self):
        r = L3ReconcileResult()
        assert r.phase == "L3_RECONCILE"
        assert r.status == ProbeStatus.SKIPPED
        assert r.verify_events_remaining == -1


class TestFullProbeResult:
    def test_defaults(self):
        r = FullProbeResult()
        assert r.classification == "PENDING"
        assert r.total_errors == 0
        assert r.total_warnings == 0
        assert isinstance(r.l0, L0StartupResult)
        assert isinstance(r.l1, L1ReadinessResult)
        assert isinstance(r.l2, L2LivenessResult)
        assert isinstance(r.l3, L3ReconcileResult)

    def test_mark_completed_sets_timestamp(self):
        r = FullProbeResult()
        assert r.completed_at == ""
        r.mark_completed()
        assert r.completed_at != ""

    def test_mark_completed_classifies_healthy(self):
        r = FullProbeResult()
        r.l0.status = ProbeStatus.PASS
        r.l1.status = ProbeStatus.PASS
        r.l2.scan_events_found = 0
        r.mark_completed()
        assert r.classification == "HEALTHY"

    def test_mark_completed_classifies_startup_failed(self):
        r = FullProbeResult()
        r.l0.status = ProbeStatus.FAIL
        r.mark_completed()
        assert r.classification == "STARTUP_FAILED"

    def test_mark_completed_classifies_not_ready(self):
        r = FullProbeResult()
        r.l0.status = ProbeStatus.PASS
        r.l1.status = ProbeStatus.FAIL
        r.mark_completed()
        assert r.classification == "NOT_READY"

    def test_mark_completed_classifies_recovered(self):
        r = FullProbeResult()
        r.l0.status = ProbeStatus.PASS
        r.l1.status = ProbeStatus.PASS
        r.l2.scan_events_found = 5
        r.l3.verify_events_remaining = 0
        r.mark_completed()
        assert r.classification == "RECOVERED"

    def test_mark_completed_classifies_partially_recovered(self):
        r = FullProbeResult()
        r.l0.status = ProbeStatus.PASS
        r.l1.status = ProbeStatus.PASS
        r.l2.scan_events_found = 5
        r.l3.verify_events_remaining = 2
        r.l3.fix_applied = 3
        r.mark_completed()
        assert r.classification == "PARTIALLY_RECOVERED"

    def test_mark_completed_classifies_recovery_failed(self):
        r = FullProbeResult()
        r.l0.status = ProbeStatus.PASS
        r.l1.status = ProbeStatus.PASS
        r.l2.scan_events_found = 5
        r.l3.verify_events_remaining = 5
        r.l3.fix_applied = 0
        r.l3.fix_failed = 3
        r.mark_completed()
        assert r.classification == "RECOVERY_FAILED"

    def test_mark_completed_classifies_unresolved(self):
        r = FullProbeResult()
        r.l0.status = ProbeStatus.PASS
        r.l1.status = ProbeStatus.PASS
        r.l2.scan_events_found = 5
        r.l3.verify_events_remaining = 5
        r.l3.fix_applied = 0
        r.l3.fix_failed = 0
        r.mark_completed()
        assert r.classification == "UNRESOLVED"

    def test_summary_returns_string(self):
        r = FullProbeResult()
        s = r.summary()
        assert isinstance(s, str)
        assert "probe=" in s

    def test_mark_completed_counts_errors(self):
        r = FullProbeResult()
        r.l0.errors = ["err1"]
        r.l1.errors = ["err2", "err3"]
        r.mark_completed()
        assert r.total_errors == 3

    def test_mark_completed_counts_warnings(self):
        r = FullProbeResult()
        r.l0.warnings = ["w1"]
        r.l2.warnings = ["w2"]
        r.mark_completed()
        assert r.total_warnings == 2


class TestExecuteFullProbe:
    def test_returns_full_probe_result(self):
        result = execute_full_probe(project_root=".")
        assert isinstance(result, FullProbeResult)
        assert result.classification != "PENDING"


class TestAliases:
    def test_execute_closed_loop_is_execute_full_probe(self):
        assert execute_closed_loop is execute_full_probe

    def test_closed_loop_result_is_full_probe_result(self):
        assert ClosedLoopResult is FullProbeResult
