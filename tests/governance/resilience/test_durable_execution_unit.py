# [A_test] module_id: MOD-GOV_durable_execution_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-631 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_durable_execution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for durable_execution.py
"""

import tempfile

from zephyr.shared.resilience.durable_execution import (
    ActivityResult,
    ActivityStatus,
    ProgressSnapshot,
    SimpleActivity,
    WorkflowManager,
)


class TestActivityResult:
    def test_completed(self):
        result = ActivityResult(activity_name="parse", status=ActivityStatus.COMPLETED, output={"ok": True})
        assert result.status == ActivityStatus.COMPLETED
        assert result.output == {"ok": True}

    def test_failed(self):
        result = ActivityResult(activity_name="broken", status=ActivityStatus.FAILED, error="boom")
        assert result.status == ActivityStatus.FAILED
        assert result.error == "boom"


class TestProgressSnapshot:
    def test_create(self):
        snapshot = ProgressSnapshot(workflow_id="wf1")
        assert snapshot.workflow_id == "wf1"
        assert snapshot.version == 1


class TestSimpleActivity:
    def test_execute(self):
        def my_fn(ctx):
            return {"result": ctx.get("value", 0) + 1}

        activity = SimpleActivity("increment", my_fn)
        output = activity.execute({"value": 5})
        assert output == {"result": 6}

    def test_name_property(self):
        activity = SimpleActivity("parse", lambda ctx: {})
        assert activity.name == "parse"

    def test_checkpoint_and_resume(self):
        activity = SimpleActivity("test", lambda ctx: {"ok": True})
        data = activity.checkpoint_data()
        assert data == {"name": "test"}
        activity.resume(data)


class TestWorkflowManager:
    def test_add_and_run(self):
        manager = WorkflowManager(workflow_id="wf1")

        def step1(ctx):
            return {"step": 1}

        def step2(ctx):
            return {"step": 2}

        manager.add_activity(SimpleActivity("step1", step1))
        manager.add_activity(SimpleActivity("step2", step2))

        results = manager.run({})
        assert len(results) == 2
        assert results["step1"].status == ActivityStatus.COMPLETED
        assert results["step2"].status == ActivityStatus.COMPLETED
        assert results["step1"].output == {"step": 1}
        assert results["step2"].output == {"step": 2}

    def test_run_stops_on_failure(self):
        manager = WorkflowManager(workflow_id="wf1")

        def good(ctx):
            return {"ok": True}

        def bad(ctx):
            raise RuntimeError("boom")

        def never(ctx):
            return {"never": "should not run"}

        manager.add_activity(SimpleActivity("good", good))
        manager.add_activity(SimpleActivity("bad", bad))
        manager.add_activity(SimpleActivity("never", never))

        results = manager.run({})
        assert len(results) == 2
        assert results["good"].status == ActivityStatus.COMPLETED
        assert results["bad"].status == ActivityStatus.FAILED
        assert "never" not in results

    def test_save_and_load_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WorkflowManager(workflow_id="wf1", snapshot_dir=tmpdir)

            def step1(ctx):
                return {"s1": "done"}

            def step2(ctx):
                return {"s2": "done"}

            manager.add_activity(SimpleActivity("step1", step1))
            manager.add_activity(SimpleActivity("step2", step2))

            manager.run({})
            snapshot = manager.save_snapshot()
            assert len(snapshot.completed_activities) == 2

            loaded = manager.load_snapshot()
            assert loaded is not None
            assert len(loaded.completed_activities) == 2
            assert "step1" in loaded.completed_activities
            assert "step2" in loaded.completed_activities

    def test_resume_skips_completed(self):
        execution_order: list[str] = []

        def step1(ctx):
            execution_order.append("step1")
            return {"s1": "ok"}

        def step2(ctx):
            execution_order.append("step2")
            return {"s2": "ok"}

        manager = WorkflowManager(workflow_id="wf1")
        manager.add_activity(SimpleActivity("step1", step1))
        manager.add_activity(SimpleActivity("step2", step2))

        manager.run({})
        assert execution_order == ["step1", "step2"]
        assert manager.completed_activities == ["step1", "step2"]

        snapshot = manager.save_snapshot()

        manager2 = WorkflowManager(workflow_id="wf1")
        manager2.add_activity(SimpleActivity("step1", step1))
        manager2.add_activity(SimpleActivity("step2", step2))

        results = manager2.resume({})
        assert "step1" in results
        assert "step2" in results
        assert results["step1"].status == ActivityStatus.COMPLETED
        assert results["step2"].status == ActivityStatus.COMPLETED

    def test_resume_no_snapshot_runs_all(self):
        manager = WorkflowManager(workflow_id="fresh_wf")
        executed: list[str] = []

        def step1(ctx):
            executed.append("step1")
            return {}

        manager.add_activity(SimpleActivity("step1", step1))
        manager.resume({})
        assert "step1" in executed

    def test_progress_empty(self):
        manager = WorkflowManager(workflow_id="wf1")
        assert manager.progress == 0.0

    def test_progress_partial(self):
        manager = WorkflowManager(workflow_id="wf1")
        manager.add_activity(SimpleActivity("a", lambda ctx: {}))
        manager.add_activity(SimpleActivity("b", lambda ctx: {}))
        manager.run({})
        assert manager.progress == 1.0

    def test_pending_activities(self):
        manager = WorkflowManager(workflow_id="wf1")

        def fail(ctx):
            raise RuntimeError("fail")

        manager.add_activity(SimpleActivity("a", lambda ctx: {}))
        manager.add_activity(SimpleActivity("b", fail))
        manager.add_activity(SimpleActivity("c", lambda ctx: {}))

        manager.run({})
        pending = manager.pending_activities
        assert "c" in pending
        assert "a" not in pending

    def test_get_result(self):
        manager = WorkflowManager(workflow_id="wf1")
        manager.add_activity(SimpleActivity("task", lambda ctx: {"x": 1}))
        manager.run({})
        result = manager.get_result("task")
        assert result is not None
        assert result.output == {"x": 1}

    def test_get_result_nonexistent(self):
        manager = WorkflowManager(workflow_id="wf1")
        assert manager.get_result("nope") is None

    def test_reset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WorkflowManager(workflow_id="wf1", snapshot_dir=tmpdir)
            manager.add_activity(SimpleActivity("a", lambda ctx: {}))
            manager.run({})
            manager.save_snapshot()
            manager.reset()
            assert manager.progress == 0
            assert manager.completed_activities == []

            loaded = manager.load_snapshot()
            assert loaded is None
