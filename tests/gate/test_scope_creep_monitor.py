# [A_test] module_id: SRC-TST-1536 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_scope_creep_monitor
# [INVARIANTS] Scope audit must be deterministic for same inputs
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.scope_creep_monitor import ScopeCreepMonitor, ScopeEvent


class TestScopeEvent:
    def test_creation(self):
        se = ScopeEvent(action_id="a1", authorized_level=2, actual_scope=3)
        assert se.action_id == "a1"
        assert se.authorized_level == 2
        assert se.actual_scope == 3
        assert se.timestamp == ""


class TestScopeCreepMonitorInstantiation:
    def test_default_values(self):
        scm = ScopeCreepMonitor()
        assert scm.events == []
        assert scm.max_tolerance == 1

    def test_custom_tolerance(self):
        scm = ScopeCreepMonitor(max_tolerance=2)
        assert scm.max_tolerance == 2


class TestAudit:
    def test_within_tolerance_returns_true(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("a1", authorized_level=2, actual_scope=3)
        assert result is True

    def test_exact_match_returns_true(self):
        scm = ScopeCreepMonitor()
        result = scm.audit("a1", authorized_level=2, actual_scope=2)
        assert result is True

    def test_exceeds_tolerance_returns_false(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("a1", authorized_level=2, actual_scope=4)
        assert result is False

    def test_appends_event(self):
        scm = ScopeCreepMonitor()
        scm.audit("a1", authorized_level=2, actual_scope=3)
        assert len(scm.events) == 1
        assert scm.events[0].action_id == "a1"

    def test_zero_authorized_zero_scope(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        result = scm.audit("a1", authorized_level=0, actual_scope=0)
        assert result is True


class TestViolationCount:
    def test_no_violations(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        scm.audit("a1", authorized_level=2, actual_scope=3)
        assert scm.violation_count() == 0

    def test_one_violation(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        scm.audit("a1", authorized_level=2, actual_scope=4)
        assert scm.violation_count() == 1

    def test_multiple_events_mixed(self):
        scm = ScopeCreepMonitor(max_tolerance=1)
        scm.audit("a1", authorized_level=2, actual_scope=3)
        scm.audit("a2", authorized_level=2, actual_scope=4)
        assert scm.violation_count() == 1

    def test_no_events(self):
        scm = ScopeCreepMonitor()
        assert scm.violation_count() == 0
