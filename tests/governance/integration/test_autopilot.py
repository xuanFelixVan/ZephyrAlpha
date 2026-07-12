# [A_test] module_id: SRC-TST-0392 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-350 | docs/03_modules/_cross_layer/database/blueprint.md | §auto-pilot
# [MODULE] tests.test_autopilot
# [INVARIANTS] All tests use temp DB files; concurrent tests use ThreadPoolExecutor; claim_next verified via Event Sourcing atomicity
# [MODIFY-GUARD] If AutoPilot.scan() or claim_next() changes API, MUST update these tests
# [CONSUMERS] CI pipeline (pytest)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertions; test_claim_and_execute_cycle MUST verify status transitions
# [TESTS] self
# [TTL] task_bound
"""test_autopilot.py — AutoPilot 端到端测试

覆盖：
- test_status_report — 状态报告生成正确
- test_scan_ready_tasks — 扫描按优先级排序
- test_claim_and_execute_cycle — 创建→认领→执行→完成 全链路
- test_concurrent_claim — 两个 AutoPilot 实例同时认领（验证 Event Sourcing 不冲突）
- test_no_tasks — 无 READY 任务时优雅返回
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.base_config import Classification
from zephyr.integration.shared.schema.execution_model import ExecutionModel
from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
from zephyr.shared.foundation.models import TaskCard
from zephyr.trading.autopilot import AutoPilot


def _make_test_task(
    task_id: str, title: str, priority: Priority = Priority.P2, batch_id: str = "test-batch"
) -> TaskCard:
    now = datetime.now(UTC)
    return TaskCard(
        task_id=task_id,
        namespace=TaskNamespace.DW,
        seq=int(task_id.split("-")[1]) if "-" in task_id else 1,
        title=title,
        description=f"根因：AutoPilot 测试需要。治根：创建符合 GOV-TASK-001 v3.1.0 颗粒度门禁的测试任务卡。施工步骤：(1) 构造 TaskCard 实例。验收标准：任务卡创建成功且通过粒度门禁。测试任务: {title}",
        status=TaskStatus.PENDING,
        priority=priority,
        phase=1,
        execution_model=ExecutionModel.claude,
        safety_level=SafetyLevel.M,
        directive="TEST-001",
        classification=Classification.INTERNAL,
        estimate_hours=0.1,
        files_in_scope=[f"d:\\test\\{task_id}.py"],
        deliverables=[f"d:\\test\\{task_id}.py"],
        acceptance=["测试通过"],
        source_blueprint="MOD-INF-012B",
        source_section="§test",
        allowed_touch=["d:\\test\\test.py"],
        applicable_rules=[{"module_id": "RULE-ZERO", "section": "test", "reason": "测试"}],
        rollback_instructions="git checkout",
        post_sync_standard=["echo test"],
        dependency_type="none",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_autopilot.db"


@pytest.fixture()
def repo(db_path: Path) -> TaskRepository:
    return TaskRepository(db_path, enable_gate=False)


@pytest.fixture()
def autopilot(repo: TaskRepository, db_path: Path) -> AutoPilot:
    return AutoPilot("test-session-001", db_path)


class TestAutoPilotBasic:
    def test_status_report_no_tasks(self, autopilot: AutoPilot):
        report = autopilot.status_report()
        assert "AutoPilot Status Report" in report
        assert "test-session-001" in report
        assert "没有待办任务" in report or "READY" in report

    def test_status_report_with_tasks(self, repo: TaskRepository, autopilot: AutoPilot):
        t = _make_test_task("DW-9001", "测试任务A", Priority.P1)
        result = repo.create(t, allow_direct_create=True)
        repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (result.task_id,))
        repo._conn.commit()

        report = autopilot.status_report()
        assert "测试任务A" in report

    def test_scan_ready_tasks(self, repo: TaskRepository, autopilot: AutoPilot):
        for i, pri in enumerate([Priority.P0, Priority.P2, Priority.P1, Priority.P1]):
            t = _make_test_task(f"DW-901{i}", f"任务-{i}", pri)
            r = repo.create(t, allow_direct_create=True)
            repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r.task_id,))
        repo._conn.commit()

        grouped = autopilot.scan()
        assert "test-batch" in grouped
        tasks = grouped["test-batch"]
        assert len(tasks) == 4
        priorities = [t.priority for t in tasks]
        assert priorities[0] == Priority.P0

    def test_scan_empty(self, autopilot: AutoPilot):
        grouped = autopilot.scan()
        assert grouped == {}

    def test_claim_next(self, repo: TaskRepository, autopilot: AutoPilot):
        t = _make_test_task("DW-9100", "可认领任务", Priority.P1)
        r = repo.create(t, allow_direct_create=True)
        repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r.task_id,))
        repo._conn.commit()

        claimed = autopilot.claim_next("test-batch")
        assert claimed is not None
        assert claimed.task_id == "DW-9100"
        assert claimed.status == TaskStatus.IN_PROGRESS

    def test_claim_next_empty_batch(self, autopilot: AutoPilot):
        claimed = autopilot.claim_next("nonexistent-batch")
        assert claimed is None

    def test_claim_next_no_batch_id(self, repo: TaskRepository, autopilot: AutoPilot):
        """任务没有 batch_id（__no_batch__），claim_next 不应认领"""
        t = _make_test_task("DW-9101", "无批次任务")
        r = repo.create(t, allow_direct_create=True)
        repo._conn.execute("UPDATE tasks SET status='READY' WHERE task_id=?", (r.task_id,))
        repo._conn.commit()

        claimed = autopilot.claim_next("__no_batch__")
        assert claimed is None

    def test_run_cycle(self, repo: TaskRepository, autopilot: AutoPilot):
        for i in range(5):
            t = _make_test_task(f"DW-902{i}", f"周期任务-{i}", Priority.P1 if i < 3 else Priority.P2)
            r = repo.create(t, allow_direct_create=True)
            repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r.task_id,))
        repo._conn.commit()

        claimed = autopilot.run_cycle(max_tasks=3)
        assert 1 <= len(claimed) <= 3
        for c in claimed:
            assert c.status == TaskStatus.IN_PROGRESS

    def test_run_cycle_no_tasks(self, autopilot: AutoPilot):
        claimed = autopilot.run_cycle()
        assert claimed == []


class TestClaimAndExecuteCycle:
    def test_full_cycle(self, repo: TaskRepository, autopilot: AutoPilot):
        t = _make_test_task("DW-9200", "全链路测试", Priority.P0)
        r = repo.create(t, allow_direct_create=True)
        repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r.task_id,))
        repo._conn.commit()

        claimed = autopilot.claim_next("test-batch")
        assert claimed is not None
        assert claimed.task_id == "DW-9200"
        assert claimed.status == TaskStatus.IN_PROGRESS

        repo._conn.execute(
            "UPDATE tasks SET status='COMPLETED', completed_at=? WHERE task_id=?",
            (datetime.now(UTC).isoformat(), claimed.task_id),
        )
        repo._conn.commit()

        finished = repo.get("DW-9200")
        assert finished.status == TaskStatus.COMPLETED

        claimed2 = autopilot.claim_next("test-batch")
        assert claimed2 is None

    def test_dependency_blocks_claim(self, repo: TaskRepository, autopilot: AutoPilot):
        t_parent = _make_test_task("DW-9210", "父任务", Priority.P1)
        r_parent = repo.create(t_parent, allow_direct_create=True)
        repo._conn.execute(
            "UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r_parent.task_id,)
        )
        repo._conn.commit()

        t_child = _make_test_task("DW-9211", "子任务（依赖父任务）", Priority.P1)
        t_child.depends_on = ["DW-9210"]
        r_child = repo.create(t_child, allow_direct_create=True)
        repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r_child.task_id,))
        repo._conn.commit()

        claimed = autopilot.claim_next("test-batch")
        assert claimed is not None
        assert claimed.task_id == "DW-9210"


class TestConcurrentClaim:
    def test_two_autopilots_claim_different_tasks(self, repo: TaskRepository, db_path: Path):
        import time

        for i in range(10):
            t = _make_test_task(f"DW-93{i:02d}", f"并发任务-{i}", Priority.P1)
            r = repo.create(t, allow_direct_create=True)
            repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r.task_id,))
        repo._conn.commit()

        time.sleep(0.1)

        claimed_ids: list[str] = []

        def claim_from_session(session_id: str) -> str | None:
            ap = AutoPilot(session_id, db_path)
            t = ap.claim_next("test-batch")
            return t.task_id if t else None

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(claim_from_session, f"test-session-{i:03d}") for i in range(4)]
            for f in as_completed(futures):
                result = f.result()
                if result:
                    claimed_ids.append(result)

        assert len(claimed_ids) == 4
        assert len(set(claimed_ids)) == 4

    def test_100_concurrent_claim_single_task(self, repo: TaskRepository, db_path: Path):
        """100 个 session 同时抢 1 个任务 → 只有 1 个成功"""
        t = _make_test_task("DW-9400", "抢手任务", Priority.P0)
        r = repo.create(t, allow_direct_create=True)
        repo._conn.execute("UPDATE tasks SET status='READY', batch_id='test-batch' WHERE task_id=?", (r.task_id,))
        repo._conn.commit()

        results: list[str | None] = []

        def try_claim(session_id: str) -> str | None:
            ap = AutoPilot(session_id, db_path)
            t = ap.claim_next("test-batch")
            return t.task_id if t else None

        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(try_claim, f"cs-{i:04d}") for i in range(100)]
            for f in as_completed(futures):
                results.append(f.result())

        successes = [r for r in results if r is not None]
        assert len(successes) == 1
        assert successes[0] == "DW-9400"
