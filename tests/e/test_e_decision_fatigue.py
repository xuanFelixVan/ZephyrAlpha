# [A_test] module_id: MOD-GOV_e_decision_fatigue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_decision_fatigue
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.decision_fatigue import (
    EisenhowerPriority,
    TaskTriage,
    filter_priority,
    triage,
)


class TestEisenhowerPriority:
    def test_four_members(self):
        assert len(EisenhowerPriority) == 4

    def test_values(self):
        assert EisenhowerPriority.P0_DO_NOW.value == "P0"
        assert EisenhowerPriority.P1_SCHEDULE.value == "P1"
        assert EisenhowerPriority.P2_DELEGATE.value == "P2"
        assert EisenhowerPriority.P3_ELIMINATE.value == "P3"


class TestTaskTriage:
    def test_default_instantiation(self):
        t = TaskTriage(task_id="T-1", description="test")
        assert t.task_id == "T-1"
        assert t.description == "test"
        assert t.urgent is False
        assert t.important is False
        assert t.priority == EisenhowerPriority.P3_ELIMINATE

    def test_classify_urgent_important(self):
        t = TaskTriage(task_id="T-1", description="urgent+important", urgent=True, important=True)
        p = t.classify()
        assert p == EisenhowerPriority.P0_DO_NOW
        assert t.priority == EisenhowerPriority.P0_DO_NOW

    def test_classify_important_not_urgent(self):
        t = TaskTriage(task_id="T-2", description="important", urgent=False, important=True)
        p = t.classify()
        assert p == EisenhowerPriority.P1_SCHEDULE

    def test_classify_urgent_not_important(self):
        t = TaskTriage(task_id="T-3", description="urgent", urgent=True, important=False)
        p = t.classify()
        assert p == EisenhowerPriority.P2_DELEGATE

    def test_classify_neither(self):
        t = TaskTriage(task_id="T-4", description="neither", urgent=False, important=False)
        p = t.classify()
        assert p == EisenhowerPriority.P3_ELIMINATE


class TestTriage:
    def test_empty_list(self):
        result = triage([])
        assert len(result) == 4
        for p in EisenhowerPriority:
            assert result[p] == []

    def test_distributes_to_priorities(self):
        tasks = [
            TaskTriage(task_id="1", description="urgent+important", urgent=True, important=True),
            TaskTriage(task_id="2", description="important", urgent=False, important=True),
            TaskTriage(task_id="3", description="urgent", urgent=True, important=False),
            TaskTriage(task_id="4", description="neither", urgent=False, important=False),
        ]
        result = triage(tasks)
        assert len(result[EisenhowerPriority.P0_DO_NOW]) == 1
        assert len(result[EisenhowerPriority.P1_SCHEDULE]) == 1
        assert len(result[EisenhowerPriority.P2_DELEGATE]) == 1
        assert len(result[EisenhowerPriority.P3_ELIMINATE]) == 1

    def test_all_urgent_important(self):
        tasks = [
            TaskTriage(task_id="1", description="a", urgent=True, important=True),
            TaskTriage(task_id="2", description="b", urgent=True, important=True),
        ]
        result = triage(tasks)
        assert len(result[EisenhowerPriority.P0_DO_NOW]) == 2


class TestFilterPriority:
    def test_filters_matching(self):
        tasks = [
            TaskTriage(task_id="1", description="urgent+important", urgent=True, important=True),
            TaskTriage(task_id="2", description="neither", urgent=False, important=False),
        ]
        triage(tasks)
        result = filter_priority(tasks, EisenhowerPriority.P0_DO_NOW)
        assert len(result) == 1
        assert result[0].task_id == "1"

    def test_empty_when_no_match(self):
        tasks = [TaskTriage(task_id="1", description="neither", urgent=False, important=False)]
        triage(tasks)
        result = filter_priority(tasks, EisenhowerPriority.P0_DO_NOW)
        assert result == []
