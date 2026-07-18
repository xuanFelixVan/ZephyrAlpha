# [A_test] module_id: SRC-TST-1947 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-564 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_durable_execution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/durable_execution.py
==================================================
覆盖矩阵：
  ActivityStatus：
    - 枚举值完整性 × 1
  ActivityResult：
    - 构造 × 1
  ProgressSnapshot：
    - 构造 & 默认值 × 1
  SimpleActivity：
    - 实现 Activity Protocol × 2
    - checkpoint_data / resume × 2
  WorkflowManager：
    - 初始化 & 创建 snapshot 目录 × 1
    - add_activity / add_activities × 2
    - completed_activities / pending_activities × 2
    - progress × 2
    - run 正常流程 × 1
    - run 失败中断 × 1
    - save_snapshot / load_snapshot × 2
    - resume 从快照恢复 × 1
    - resume 无快照回退到 run × 1
    - get_result × 2
    - reset × 1

Safety: HIGH（Durable Execution 是长流程可靠性根基）
"""

import os
from pathlib import Path

from zephyr.shared.resilience.durable_execution import (
    Activity,
    ActivityResult,
    ActivityStatus,
    ProgressSnapshot,
    SimpleActivity,
    WorkflowManager,
)


class TestActivityStatus:
    def test_all_statuses(self):
        values = {s.value for s in ActivityStatus}
        assert "pending" in values
        assert "running" in values
        assert "completed" in values
        assert "failed" in values
        assert "skipped" in values


class TestActivityResult:
    def test_construction(self):
        r = ActivityResult(
            activity_name="parse",
            status=ActivityStatus.COMPLETED,
            output={"files": 5},
        )
        assert r.activity_name == "parse"
        assert r.status == ActivityStatus.COMPLETED
        assert r.output == {"files": 5}


class TestProgressSnapshot:
    def test_construction(self):
        snap = ProgressSnapshot(
            workflow_id="wf-1",
            completed_activities=["parse"],
            current_activity="index",
            version=1,
        )
        assert snap.workflow_id == "wf-1"
        assert snap.completed_activities == ["parse"]
        assert snap.current_activity == "index"


class TestSimpleActivity:
    def test_implements_activity_protocol(self):
        def my_fn(ctx):
            return {"done": True}

        act = SimpleActivity("test-act", my_fn)
        assert isinstance(act, Activity)
        assert act.name == "test-act"

    def test_execute(self):
        act = SimpleActivity("double", lambda ctx: {"value": ctx["x"] * 2})
        result = act.execute({"x": 21})
        assert result["value"] == 42

    def test_checkpoint_data(self):
        act = SimpleActivity("id", lambda ctx: ctx)
        cp = act.checkpoint_data()
        assert cp == {"name": "id"}

    def test_resume_noop(self):
        act = SimpleActivity("id", lambda ctx: ctx)
        act.resume({})


class TestWorkflowManagerInit:
    def test_creates_snapshot_dir(self, tmp_path):
        snap_dir = str(tmp_path / "snapshots")
        manager = WorkflowManager(
            workflow_id="wf-test",
            snapshot_dir=snap_dir,
        )
        assert os.path.isdir(snap_dir)


class TestWorkflowActivities:
    def test_add_activity(self):
        manager = WorkflowManager(workflow_id="wf")
        act = SimpleActivity("a1", lambda ctx: {})
        manager.add_activity(act)
        assert len(manager.activities) == 1

    def test_add_activities(self):
        manager = WorkflowManager(workflow_id="wf")
        manager.add_activities(
            [
                SimpleActivity("a1", lambda ctx: {}),
                SimpleActivity("a2", lambda ctx: {}),
            ]
        )
        assert len(manager.activities) == 2


class TestWorkflowProgress:
    def test_completed_activities_empty_initially(self):
        manager = WorkflowManager(workflow_id="wf")
        manager.add_activity(SimpleActivity("a1", lambda ctx: {"ok": True}))
        assert manager.completed_activities == []

    def test_pending_activities_initially(self):
        manager = WorkflowManager(workflow_id="wf")
        manager.add_activity(SimpleActivity("a1", lambda ctx: {}))
        assert manager.pending_activities == ["a1"]

    def test_progress_zero_initially(self):
        manager = WorkflowManager(workflow_id="wf")
        manager.add_activity(SimpleActivity("a1", lambda ctx: {}))
        assert manager.progress == 0.0

    def test_progress_empty_activities(self):
        manager = WorkflowManager(workflow_id="wf")
        assert manager.progress == 0.0


class TestWorkflowRun:
    def test_run_all_activities(self):
        manager = WorkflowManager(workflow_id="wf")
        manager.add_activity(SimpleActivity("a1", lambda ctx: {"result": "r1"}))
        manager.add_activity(SimpleActivity("a2", lambda ctx: {"result": "r2"}))

        results = manager.run({"input": "test"})
        assert len(results) == 2
        assert results["a1"].status == ActivityStatus.COMPLETED
        assert results["a2"].status == ActivityStatus.COMPLETED
        assert manager.progress == 1.0

    def test_run_stops_on_failure(self):
        manager = WorkflowManager(workflow_id="wf")
        manager.add_activity(SimpleActivity("a1", lambda ctx: {"ok": True}))
        manager.add_activity(SimpleActivity("fail", lambda ctx: (_ for _ in ()).throw(RuntimeError("boom"))))
        manager.add_activity(SimpleActivity("a3", lambda ctx: {"ok": True}))

        results = manager.run({})
        assert "a1" in results
        assert results["a1"].status == ActivityStatus.COMPLETED
        assert results["fail"].status == ActivityStatus.FAILED
        assert "a3" not in results


class TestWorkflowSnapshot:
    def test_save_and_load_snapshot(self, tmp_path):
        snap_dir = str(tmp_path / "snaps")
        manager = WorkflowManager(workflow_id="wf", snapshot_dir=snap_dir)
        manager.add_activity(SimpleActivity("a1", lambda ctx: {"v": 1}))
        manager.add_activity(SimpleActivity("a2", lambda ctx: {"v": 2}))
        manager.run({})

        manager.save_snapshot()
        snap_path = Path(snap_dir) / "wf.snapshot.json"
        assert snap_path.exists()

        loaded = manager.load_snapshot()
        assert loaded is not None
        assert loaded.workflow_id == "wf"
        assert "a1" in loaded.completed_activities
        assert "a2" in loaded.completed_activities

    def test_load_snapshot_nonexistent(self, tmp_path):
        snap_dir = str(tmp_path / "empty")
        manager = WorkflowManager(workflow_id="wf", snapshot_dir=snap_dir)
        assert manager.load_snapshot() is None


class TestWorkflowResume:
    def test_resume_skips_completed(self, tmp_path):
        snap_dir = str(tmp_path / "snaps")
        manager = WorkflowManager(workflow_id="wf", snapshot_dir=snap_dir)
        counter = {"value": 0}

        def count_activity(ctx):
            counter["value"] += 1
            return {"count": counter["value"]}

        manager.add_activity(SimpleActivity("a1", count_activity))
        manager.add_activity(SimpleActivity("a2", count_activity))
        manager.add_activity(SimpleActivity("a3", count_activity))

        results = manager.run({})
        assert counter["value"] == 3
        manager.save_snapshot()

        manager2 = WorkflowManager(workflow_id="wf", snapshot_dir=snap_dir)
        manager2.add_activity(SimpleActivity("a1", count_activity))
        manager2.add_activity(SimpleActivity("a2", count_activity))
        manager2.add_activity(SimpleActivity("a3", count_activity))
        results2 = manager2.resume({})
        assert counter["value"] == 3
        assert "a1" in results2
        assert "a2" in results2
        assert "a3" in results2

    def test_resume_runs_all_when_no_snapshot(self, tmp_path):
        snap_dir = str(tmp_path / "empty")
        manager = WorkflowManager(workflow_id="wf", snapshot_dir=snap_dir)
        manager.add_activity(SimpleActivity("a1", lambda ctx: {"ok": True}))
        results = manager.resume({})
        assert "a1" in results
        assert results["a1"].status == ActivityStatus.COMPLETED


class TestWorkflowGetResult:
    def test_get_result(self):
        manager = WorkflowManager(workflow_id="wf")
        manager.add_activity(SimpleActivity("a1", lambda ctx: {"r": 1}))
        manager.run({})
        r = manager.get_result("a1")
        assert r is not None
        assert r.activity_name == "a1"

    def test_get_result_nonexistent(self):
        manager = WorkflowManager(workflow_id="wf")
        assert manager.get_result("nonexistent") is None


class TestWorkflowReset:
    def test_reset(self, tmp_path):
        snap_dir = str(tmp_path / "snaps")
        manager = WorkflowManager(workflow_id="wf", snapshot_dir=snap_dir)
        manager.add_activity(SimpleActivity("a1", lambda ctx: {"k": "v"}))
        manager.run({})
        manager.save_snapshot()

        manager.reset()
        assert manager.completed_activities == []
        assert manager.get_result("a1") is None

        snap_path = Path(snap_dir) / "wf.snapshot.json"
        assert not snap_path.exists()
