# [A_test] module_id: SRC-TST-1728 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_teardown_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_teardown_manager.py
# [TTL] task_bound


from zephyr.orchestrator.lifecycle.teardown_manager import (
    CLEANUP_SYSTEMS,
    CleanupTarget,
    TeardownManager,
)


class TestCleanupTargetModel:
    def test_create_default(self):
        target = CleanupTarget(system="orchestrator")
        assert target.system == "orchestrator"
        assert target.resource_type == ""
        assert target.resource_id == ""
        assert target.status == "pending"

    def test_create_with_all_fields(self):
        target = CleanupTarget(
            system="database",
            resource_type="task_context",
            resource_id="T-1",
            status="cleaned",
        )
        assert target.system == "database"
        assert target.resource_type == "task_context"
        assert target.resource_id == "T-1"
        assert target.status == "cleaned"


class TestCleanupSystemsConstant:
    def test_has_seven_systems(self):
        assert len(CLEANUP_SYSTEMS) == 7

    def test_contains_orchestrator(self):
        assert "orchestrator" in CLEANUP_SYSTEMS

    def test_contains_database(self):
        assert "database" in CLEANUP_SYSTEMS

    def test_contains_vector_memory(self):
        assert "vector-memory" in CLEANUP_SYSTEMS

    def test_contains_feedback_loop(self):
        assert "feedback-loop" in CLEANUP_SYSTEMS


class TestTeardownManagerInstantiation:
    def test_create_instance(self):
        mgr = TeardownManager()
        assert mgr is not None

    def test_has_teardown_method(self):
        mgr = TeardownManager()
        assert callable(mgr.teardown)

    def test_has_get_records_method(self):
        mgr = TeardownManager()
        assert callable(mgr.get_records)

    def test_initial_no_records(self):
        mgr = TeardownManager()
        assert mgr.get_records() == []


class TestTeardown:
    def test_teardown_returns_targets(self):
        mgr = TeardownManager()
        targets = mgr.teardown("T-1", "CANCELLED")
        assert isinstance(targets, list)
        assert len(targets) == len(CLEANUP_SYSTEMS)

    def test_teardown_targets_have_correct_system(self):
        mgr = TeardownManager()
        targets = mgr.teardown("T-1", "FAILED")
        systems = [t.system for t in targets]
        for sys in CLEANUP_SYSTEMS:
            assert sys in systems

    def test_teardown_targets_have_task_id(self):
        mgr = TeardownManager()
        targets = mgr.teardown("T-42", "CANCELLED")
        for target in targets:
            assert target.resource_id == "T-42"

    def test_teardown_targets_are_cleaned(self):
        mgr = TeardownManager()
        targets = mgr.teardown("T-1", "FAILED")
        for target in targets:
            assert target.status == "cleaned"

    def test_teardown_records_cleanup(self):
        mgr = TeardownManager()
        mgr.teardown("T-1", "CANCELLED")
        records = mgr.get_records()
        assert len(records) == 1
        assert records[0]["task_id"] == "T-1"
        assert records[0]["reason"] == "CANCELLED"

    def test_teardown_multiple_tasks(self):
        mgr = TeardownManager()
        mgr.teardown("T-1", "CANCELLED")
        mgr.teardown("T-2", "FAILED")
        records = mgr.get_records()
        assert len(records) == 2

    def test_teardown_record_has_targets_count(self):
        mgr = TeardownManager()
        mgr.teardown("T-1", "CANCELLED")
        records = mgr.get_records()
        assert records[0]["targets"] == len(CLEANUP_SYSTEMS)

    def test_teardown_record_has_timestamp(self):
        mgr = TeardownManager()
        mgr.teardown("T-1", "CANCELLED")
        records = mgr.get_records()
        assert "timestamp" in records[0]


class TestGetRecords:
    def test_returns_copy(self):
        mgr = TeardownManager()
        mgr.teardown("T-1", "CANCELLED")
        records = mgr.get_records()
        records.clear()
        assert len(mgr.get_records()) == 1

    def test_empty_initially(self):
        mgr = TeardownManager()
        assert mgr.get_records() == []
