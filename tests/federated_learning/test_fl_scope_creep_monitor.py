# [A_test] module_id: SRC-TST-1003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_scope_creep_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.scope_creep_monitor
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_scope_creep_monitor.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.scope_creep_monitor import ScopeCreepMonitor, ScopeEvent


class TestScopeCreepMonitorInstantiation:
    def test_default_construction(self):
        scm = ScopeCreepMonitor()
        assert scm.events == []
        assert scm.max_tolerance == 1

    def test_custom_tolerance(self):
        scm = ScopeCreepMonitor(max_tolerance=3)
        assert scm.max_tolerance == 3


class TestAudit:
    def test_audit_within_tolerance(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("action-1", authorized_level=2, actual_scope=3)
        assert result is True

    def test_audit_exceeds_tolerance(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("action-2", authorized_level=2, actual_scope=4)
        assert result is False

    def test_audit_exact_match(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("action-3", authorized_level=2, actual_scope=2)
        assert result is True

    def test_audit_appends_event(self):
        scm = ScopeCreepMonitor()
        scm.audit("action-1", 2, 3)
        assert len(scm.events) == 1
        assert isinstance(scm.events[0], ScopeEvent)


class TestViolationCount:
    def test_no_violations(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        scm.audit("a1", 2, 2)
        scm.audit("a2", 2, 3)
        assert scm.violation_count() == 0

    def test_with_violations(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        scm.audit("a1", 2, 2)
        scm.audit("a2", 2, 4)
        scm.audit("a3", 1, 5)
        assert scm.violation_count() == 2


class TestBoundaries:
    def test_audit_zero_scope(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("a1", 0, 0)
        assert result is True

    def test_audit_negative_scope(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("a1", 2, -1)
        assert result is True

    def test_violation_count_empty(self):
        scm = ScopeCreepMonitor()
        assert scm.violation_count() == 0

    def test_zero_tolerance(self):
        scm = ScopeCreepMonitor(max_tolerance=0)
        result = scm.audit("a1", 2, 3)
        assert result is False
