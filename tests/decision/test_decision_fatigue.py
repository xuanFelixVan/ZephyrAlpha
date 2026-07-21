# [A_test] module_id: MOD-GOV_decision_fatigue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-375 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_decision_fatigue
# [INVARIANTS] classify always returns valid EisenhowerPriority; triage covers all priorities
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_decision_fatigue.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.decision_fatigue import (
    EisenhowerPriority,
    TaskTriage,
    filter_priority,
    triage,
)


class TestEisenhowerPriority:
    def test_all_priorities(self):
        expected = {"P0", "P1", "P2", "P3"}
        actual = {p.value for p in EisenhowerPriority}
        assert actual == expected


class TestTaskTriage:
    def test_creation_defaults(self):
        t = TaskTriage(task_id="T1", description="desc")
        assert t.urgent is False
        assert t.important is False
        assert t.priority == EisenhowerPriority.P3_ELIMINATE

    def test_classify_p0(self):
        t = TaskTriage(task_id="T1", description="d", urgent=True, important=True)
        result = t.classify()
        assert result == EisenhowerPriority.P0_DO_NOW

    def test_classify_p1(self):
        t = TaskTriage(task_id="T1", description="d", urgent=False, important=True)
        result = t.classify()
        assert result == EisenhowerPriority.P1_SCHEDULE

    def test_classify_p2(self):
        t = TaskTriage(task_id="T1", description="d", urgent=True, important=False)
        result = t.classify()
        assert result == EisenhowerPriority.P2_DELEGATE

    def test_classify_p3(self):
        t = TaskTriage(task_id="T1", description="d", urgent=False, important=False)
        result = t.classify()
        assert result == EisenhowerPriority.P3_ELIMINATE


class TestTriage:
    def test_triage_empty_list(self):
        result = triage([])
        for p in EisenhowerPriority:
            assert result[p] == []

    def test_triage_classifies_all(self):
        tasks = [
            TaskTriage(task_id="T1", description="a", urgent=True, important=True),
            TaskTriage(task_id="T2", description="b", urgent=False, important=True),
            TaskTriage(task_id="T3", description="c", urgent=True, important=False),
            TaskTriage(task_id="T4", description="d", urgent=False, important=False),
        ]
        result = triage(tasks)
        assert len(result[EisenhowerPriority.P0_DO_NOW]) == 1
        assert len(result[EisenhowerPriority.P1_SCHEDULE]) == 1
        assert len(result[EisenhowerPriority.P2_DELEGATE]) == 1
        assert len(result[EisenhowerPriority.P3_ELIMINATE]) == 1

    def test_triage_modifies_task_priority(self):
        tasks = [TaskTriage(task_id="T1", description="d", urgent=True, important=True)]
        triage(tasks)
        assert tasks[0].priority == EisenhowerPriority.P0_DO_NOW


class TestFilterPriority:
    def test_filter_returns_matching(self):
        tasks = [
            TaskTriage(task_id="T1", description="a", urgent=True, important=True),
            TaskTriage(task_id="T2", description="b", urgent=False, important=False),
        ]
        triage(tasks)
        p0 = filter_priority(tasks, EisenhowerPriority.P0_DO_NOW)
        assert len(p0) == 1
        assert p0[0].task_id == "T1"

    def test_filter_no_match(self):
        tasks = [TaskTriage(task_id="T1", description="a", urgent=False, important=False)]
        triage(tasks)
        p0 = filter_priority(tasks, EisenhowerPriority.P0_DO_NOW)
        assert p0 == []


class TestBoundary:
    def test_triage_all_same_priority(self):
        tasks = [TaskTriage(task_id=f"T{i}", description="d", urgent=True, important=True) for i in range(5)]
        result = triage(tasks)
        assert len(result[EisenhowerPriority.P0_DO_NOW]) == 5
        assert len(result[EisenhowerPriority.P1_SCHEDULE]) == 0
