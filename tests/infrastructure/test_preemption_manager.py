# [A_test] module_id: SRC-TST-1396 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_preemption_manager
# [INVARIANTS] P0/P1 can preempt P2/P3; preempt with None task_repo returns []; save_state/load_state roundtrip must be lossless
# [MODIFY-GUARD] zephyr.infrastructure.pipeline.preemption_manager
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.raises on invalid input
# [TESTS] —
# [TTL] task_bound


from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
from zephyr.infrastructure.pipeline.preemption_manager import PreemptionManager


def _make_task(task_id, priority, status=TaskStatus.IN_PROGRESS):
    class FakeTask:
        pass

    t = FakeTask()
    t.task_id = task_id
    t.priority = priority
    t.status = status
    return t


def _make_task_card(task_id, priority):
    return _make_task(task_id, priority)


class FakeTaskRepo:
    def __init__(self, tasks=None):
        self._tasks = {t.task_id: t for t in (tasks or [])}

    def list(self, status=None, limit=50):
        result = []
        for t in self._tasks.values():
            if status is None or t.status == status:
                result.append(t)
        return result[:limit]

    def get(self, task_id):
        return self._tasks.get(task_id)

    def transition(self, task_id, new_status, **kwargs):
        t = self._tasks.get(task_id)
        if t is None:
            raise ValueError(f"Task {task_id} not found")
        t.status = new_status
        return t


class TestShouldPreempt:
    def test_p0_preempts_p2(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P0", "P2") is True

    def test_p0_preempts_p3(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P0", "P3") is True

    def test_p1_preempts_p2(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P1", "P2") is True

    def test_p1_preempts_p3(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P1", "P3") is True

    def test_p2_cannot_preempt_p0(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P2", "P0") is False

    def test_p3_cannot_preempt_p1(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P3", "P1") is False

    def test_same_priority_no_preempt(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P0", "P0") is False
        assert mgr.should_preempt("P1", "P1") is False

    def test_p0_cannot_preempt_p1(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("P0", "P1") is False

    def test_empty_string_no_preempt(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("", "P2") is False
        assert mgr.should_preempt("P0", "") is False

    def test_none_no_preempt(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt(None, "P2") is False
        assert mgr.should_preempt("P0", None) is False

    def test_case_insensitive(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.should_preempt("p0", "p2") is True
        assert mgr.should_preempt("P0", "p3") is True


class TestPreempt:
    def test_preempt_with_none_task_repo_returns_empty(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        result = mgr.preempt(card)
        assert result == []

    def test_preempt_low_priority_task(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        dispatched = {"low-001"}
        active = {"low-001"}
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=dispatched,
            active_dispatches=active,
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        records = mgr.preempt(card)
        assert len(records) == 1
        assert records[0].preempted_task_id == "low-001"
        assert records[0].preempted_by_task_id == "high-001"
        assert records[0].preempted_priority == "P3"
        assert low_task.status == TaskStatus.WAITING
        assert "low-001" not in dispatched
        assert "low-001" not in active

    def test_preempt_p2_task(self):
        low_task = _make_task("mid-001", "P2")
        repo = FakeTaskRepo([low_task])
        dispatched = {"mid-001"}
        active = {"mid-001"}
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=dispatched,
            active_dispatches=active,
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P1")
        records = mgr.preempt(card)
        assert len(records) == 1
        assert records[0].preempted_priority == "P2"

    def test_preempt_does_not_affect_high_priority(self):
        other_high = _make_task("other-001", "P1")
        repo = FakeTaskRepo([other_high])
        dispatched = {"other-001"}
        active = {"other-001"}
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=dispatched,
            active_dispatches=active,
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-002", "P0")
        records = mgr.preempt(card)
        assert len(records) == 0
        assert "other-001" in dispatched

    def test_preempt_non_high_priority_card_does_nothing(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        dispatched = {"low-001"}
        active = {"low-001"}
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=dispatched,
            active_dispatches=active,
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("mid-001", "P2")
        records = mgr.preempt(card)
        assert len(records) == 0

    def test_preempt_multiple_low_priority(self):
        low1 = _make_task("low-001", "P3")
        low2 = _make_task("low-002", "P2")
        repo = FakeTaskRepo([low1, low2])
        dispatched = {"low-001", "low-002"}
        active = {"low-001", "low-002"}
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=dispatched,
            active_dispatches=active,
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        records = mgr.preempt(card)
        assert len(records) == 2


class TestResumePreempted:
    def test_resume_preempted_task(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        dispatched = set()
        active = set()
        re_dispatched = []
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=dispatched,
            active_dispatches=active,
            re_dispatch_callback=lambda t: re_dispatched.append(t.task_id),
        )
        card = _make_task_card("high-001", "P0")
        mgr.preempt(card)
        low_task.status = TaskStatus.WAITING
        results = mgr.resume_preempted("high-001")
        assert len(results) == 1
        assert "low-001" in re_dispatched

    def test_resume_no_match_returns_empty(self):
        mgr = PreemptionManager(
            task_repo=FakeTaskRepo(),
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        results = mgr.resume_preempted("nonexistent")
        assert results == []

    def test_resume_with_none_task_repo_returns_empty(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        results = mgr.resume_preempted("any")
        assert results == []

    def test_resume_already_resumed_skips(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        dispatched = set()
        active = set()
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=dispatched,
            active_dispatches=active,
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        mgr.preempt(card)
        low_task.status = TaskStatus.WAITING
        mgr.resume_preempted("high-001")
        results = mgr.resume_preempted("high-001")
        assert results == []


class TestSaveLoadState:
    def test_save_state_empty(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        state = mgr.save_state()
        assert state["preempt_log"] == {}
        assert state["priority_cutoff"] == "P2"

    def test_save_state_with_records(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        mgr.preempt(card)
        state = mgr.save_state()
        assert "low-001" in state["preempt_log"]
        assert state["preempt_log"]["low-001"]["preempted_by_task_id"] == "high-001"

    def test_load_state_roundtrip(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        mgr.preempt(card)
        state = mgr.save_state()

        mgr2 = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        mgr2.load_state(state)
        assert "low-001" in mgr2.log
        assert mgr2.log["low-001"].preempted_by_task_id == "high-001"
        assert mgr2.priority_cutoff == "P2"

    def test_load_state_empty(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        mgr.load_state({})
        assert mgr.log == {}
        assert mgr.priority_cutoff == "P2"


class TestProperties:
    def test_log_is_readonly_copy(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        log = mgr.log
        log["fake"] = "value"
        assert "fake" not in mgr.log

    def test_priority_cutoff_default(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.priority_cutoff == "P2"

    def test_priority_cutoff_custom(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
            priority_cutoff="P3",
        )
        assert mgr.priority_cutoff == "P3"

    def test_active_count_empty(self):
        mgr = PreemptionManager(
            task_repo=None,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        assert mgr.active_count == 0

    def test_active_count_after_preempt(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        mgr.preempt(card)
        assert mgr.active_count == 1

    def test_active_count_after_resume(self):
        low_task = _make_task("low-001", "P3")
        repo = FakeTaskRepo([low_task])
        mgr = PreemptionManager(
            task_repo=repo,
            dispatched_ids=set(),
            active_dispatches=set(),
            re_dispatch_callback=lambda t: None,
        )
        card = _make_task_card("high-001", "P0")
        mgr.preempt(card)
        low_task.status = TaskStatus.WAITING
        mgr.resume_preempted("high-001")
        assert mgr.active_count == 0
