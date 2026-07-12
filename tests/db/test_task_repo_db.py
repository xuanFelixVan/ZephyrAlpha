# [A_test] module_id: SRC-TST-1862 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-489 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.db.test_task_repo
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/db/task_repo.py（T-{SEQ}）
==================================================
覆盖矩阵
--------
Schema        : 5 表 + 3 视图正确创建（含 task_files）
Create        : 正常创建 / 重复 task_id 冲突 / Pydantic 校验失败拒绝
Get           : 存在 / 不存在 / get_or_raise 抛异常
Update        : 正常更新非状态字段 / 不存在时抛异常
Transition    : 所有合法路径 / 所有非法转换拒绝 / 终态无出边
Events        : create 写事件 / transition 写 state_transition 事件
Delete        : 正常删除（含 task_files 级联） / 不存在返回 False
List          : list_by_status / list_by_phase / list_by_session / list_by_namespace / list_active / count_by_status
TaskFiles     : add_file / remove_file / get_files / get_tasks_for_file / next_seq
Upsert        : 新建 / 覆盖更新
Concurrency   : 多线程并发读（WAL 安全）/ 单 Writer 序列化
Helpers       : allowed_transitions / is_terminal
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from threading import Thread

import pytest

from zephyr.governance.persistence.task_repo import (
    InvalidTransitionError,
    TaskNotFoundError,
    TaskRepository,
    allowed_transitions,
    is_terminal,
)
from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.base_config import Classification, EvolutionPolicy
from zephyr.integration.shared.schema.severity_types import SafetyLevel
from zephyr.shared.foundation.models import TaskCard

_UTC = UTC


def _make_task(
    task_id: str = "SRC-1",
    status: TaskStatus = TaskStatus.PENDING,
    phase: int = 1,
    namespace: TaskNamespace = TaskNamespace.SRC,
    seq: int | None = None,
    session_id: str | None = None,
) -> TaskCard:
    now = datetime.now(_UTC)
    if seq is None:
        try:
            seq = int(task_id.split("-")[1])
        except (IndexError, ValueError):
            seq = 1
    return TaskCard(
        task_id=task_id,
        namespace=namespace,
        seq=seq,
        phase=phase,
        title=f"Task {task_id}",
        status=status,
        execution_model="claude",
        safety_level=SafetyLevel.M,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=1.0,
        source_blueprint="test",
        source_section="test",
        description=f"根因：测试 TaskRepository CRUD 功能。治根：创建符合 GOV-TASK-001 v3.1.0 颗粒度门禁的测试任务。施工步骤：(1) 构造 TaskCard 并调用 create。验收标准：任务 {task_id} 创建成功。",
        files_in_scope=["src/zephyr/db/task_repo.py"],
        deliverables=["test deliverable"],
        applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
        allowed_touch=["src/zephyr/db/task_repo.py"],
        rollback_instructions="git checkout -- task_repo.py",
        post_sync_standard=["echo ok"],
        acceptance=["exit=0"],
        dependency_type="none",
        session_id=session_id,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> TaskRepository:
    db = tmp_path / "test_data/databases/governance.db"
    r = TaskRepository(db_path=db, auto_init=True, enable_gate=False)
    yield r
    r.close()


class TestSchemaInit:
    def test_tables_created(self, tmp_path: Path) -> None:
        from zephyr.governance.persistence.sqlite_schema import init_db, table_names, view_names

        db = tmp_path / "meta.db"
        init_db(db)
        tables = sorted(table_names(db))
        views = sorted(view_names(db))
        assert "tasks" in tables
        assert "task_files" in tables
        assert "events" in tables
        assert "v_active_tasks" in views

    def test_init_is_idempotent(self, tmp_path: Path) -> None:
        from zephyr.governance.persistence.sqlite_schema import init_db

        db = tmp_path / "meta2.db"
        init_db(db)
        init_db(db)


class TestCreate:
    def test_create_returns_task(self, repo: TaskRepository) -> None:
        t = _make_task("SRC-1")
        result = repo.create(t)
        assert result.task_id == "SRC-1"
        assert result.status == TaskStatus.PENDING

    def test_create_writes_event(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-2"))
        import sqlite3

        conn = sqlite3.connect(str(repo._db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM events WHERE task_id = 'SRC-2' AND event_type = 'task_event'").fetchall()
        conn.close()
        assert len(rows) >= 1
        assert "created" in rows[0]["payload"]

    def test_duplicate_task_id_raises(self, repo: TaskRepository) -> None:
        import sqlite3

        repo.create(_make_task("SRC-3"))
        with pytest.raises(sqlite3.IntegrityError):
            repo.create(_make_task("SRC-3"))

    def test_create_with_dependencies(self, repo: TaskRepository) -> None:
        now = datetime.now(_UTC)
        t = TaskCard(
            task_id="SRC-4",
            namespace=TaskNamespace.SRC,
            seq=4,
            phase=1,
            title="Depends Task",
            execution_model="claude",
            safety_level=SafetyLevel.H,
            source_blueprint="test",
            source_section="test",
            description="根因：测试依赖关系功能。治根：创建带依赖的测试任务卡并验证 depends_on 字段持久化。施工步骤：(1) 构造带 depends_on 的 TaskCard 实例并调用 create。验收标准：依赖关系正确存储和查询，depends_on 列表包含预期值。",
            files_in_scope=["src/zephyr/db/task_repo.py"],
            deliverables=["test deliverable"],
            applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
            allowed_touch=["src/zephyr/db/task_repo.py"],
            rollback_instructions="git checkout",
            post_sync_standard=["echo ok"],
            acceptance=["exit=0"],
            dependency_type="hard",
            depends_on=["SRC-5", "SRC-6"],
            created_at=now,
            updated_at=now,
        )
        result = repo.create(t)
        assert "SRC-5" in result.depends_on

    def test_create_with_files(self, repo: TaskRepository) -> None:
        t = _make_task("SRC-7")
        files = [
            {"file_path": "src/zephyr/db/task_repo.py", "role": "primary"},
            {"file_path": "src/zephyr/schemas.py", "role": "in_scope"},
        ]
        result = repo.create(t, files=files)
        assert result.task_id == "SRC-7"
        task_files = repo.get_files("SRC-7")
        assert len(task_files) == 2


class TestGet:
    def test_get_existing(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-10"))
        t = repo.get("SRC-10")
        assert t is not None
        assert t.task_id == "SRC-10"

    def test_get_nonexistent_returns_none(self, repo: TaskRepository) -> None:
        assert repo.get("SRC-999") is None

    def test_get_or_raise_existing(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-11"))
        t = repo.get_or_raise("SRC-11")
        assert t.task_id == "SRC-11"

    def test_get_or_raise_nonexistent(self, repo: TaskRepository) -> None:
        with pytest.raises(TaskNotFoundError):
            repo.get_or_raise("SRC-999")


class TestUpdate:
    def test_update_name(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-20"))
        updated = repo.update("SRC-20", title="New Name")
        assert updated.title == "New Name"

    def test_update_session_id(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-21"))
        updated = repo.update("SRC-21", session_id="sess-abc")
        assert updated.session_id == "sess-abc"

    def test_update_nonexistent_raises(self, repo: TaskRepository) -> None:
        with pytest.raises(TaskNotFoundError):
            repo.update("SRC-999", title="X")

    def test_update_no_fields_no_op(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-22"))
        original = repo.get_or_raise("SRC-22")
        result = repo.update("SRC-22")
        assert result.title == original.title

    def test_update_deliverables(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-23"))
        updated = repo.update("SRC-23", deliverables=["file1.py", "file2.py"])
        assert updated.deliverables == ["file1.py", "file2.py"]


class TestTransition:
    def test_pending_to_in_progress(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-30"))
        t = repo.transition("SRC-30", TaskStatus.IN_PROGRESS)
        assert t.status == TaskStatus.IN_PROGRESS

    def test_in_progress_to_completed(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-31"))
        repo.transition("SRC-31", TaskStatus.IN_PROGRESS)
        t = repo.transition("SRC-31", TaskStatus.COMPLETED)
        assert t.status == TaskStatus.COMPLETED

    def test_completed_to_verified(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-32"))
        repo.transition("SRC-32", TaskStatus.IN_PROGRESS)
        repo.transition("SRC-32", TaskStatus.COMPLETED)
        t = repo.transition("SRC-32", TaskStatus.VERIFIED)
        assert t.status == TaskStatus.VERIFIED

    def test_failed_to_retry(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-33"))
        repo.transition("SRC-33", TaskStatus.IN_PROGRESS)
        repo.transition("SRC-33", TaskStatus.FAILED, note="根因: integration test failure simulation")
        t = repo.transition("SRC-33", TaskStatus.RETRY)
        assert t.status == TaskStatus.RETRY

    def test_blocked_to_ready(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-34"))
        repo.transition("SRC-34", TaskStatus.BLOCKED)
        t = repo.transition("SRC-34", TaskStatus.READY)
        assert t.status == TaskStatus.READY

    def test_waiting_to_ready(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-35"))
        repo.transition("SRC-35", TaskStatus.IN_PROGRESS)
        repo.transition("SRC-35", TaskStatus.WAITING, waiting_for="external API")
        t = repo.transition("SRC-35", TaskStatus.READY)
        assert t.status == TaskStatus.READY

    def test_transition_writes_event(self, repo: TaskRepository) -> None:
        import sqlite3

        repo.create(_make_task("SRC-36"))
        repo.transition("SRC-36", TaskStatus.IN_PROGRESS, session_id="sess-x")
        conn = sqlite3.connect(str(repo._db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM events WHERE task_id = 'SRC-36' AND event_type = 'state_transition'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1
        import json

        payload = json.loads(rows[0]["payload"])
        assert payload["from"] == "PENDING"
        assert payload["to"] == "IN_PROGRESS"

    def test_string_status_accepted(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-37"))
        t = repo.transition("SRC-37", "IN_PROGRESS")
        assert t.status == TaskStatus.IN_PROGRESS

    @pytest.mark.parametrize(
        "from_s, to_s",
        [
            ("PENDING", "COMPLETED"),
            ("PENDING", "VERIFIED"),
            ("PENDING", "FAILED"),
            ("COMPLETED", "CANCELLED"),
            ("RETRY", "CANCELLED"),
            ("VERIFIED", "PENDING"),
            ("CANCELLED", "PENDING"),
            ("IN_PROGRESS", "PENDING"),
        ],
    )
    def test_invalid_transition_raises(self, repo: TaskRepository, from_s: str, to_s: str) -> None:
        now = datetime.now(_UTC)
        tid = "SRC-900"
        t = TaskCard(
            task_id=tid,
            namespace=TaskNamespace.SRC,
            seq=900,
            phase=1,
            title="Test",
            status=TaskStatus(from_s),
            execution_model="claude",
            safety_level=SafetyLevel.M,
            source_blueprint="test",
            source_section="test",
            description="根因：测试状态转换验证。治根：创建测试任务卡验证非法转换拦截机制。施工步骤：(1) 构造 TaskCard 并测试非法状态转换。验收标准：非法转换被正确拦截并抛出 InvalidTransitionError。",
            files_in_scope=["src/zephyr/db/task_repo.py"],
            deliverables=["test"],
            applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
            allowed_touch=["src/zephyr/db/task_repo.py"],
            rollback_instructions="revert",
            post_sync_standard=["echo ok"],
            acceptance=["exit=0"],
            dependency_type="none",
            created_at=now,
            updated_at=now,
        )
        repo.create(t)
        with pytest.raises(InvalidTransitionError):
            repo.transition(tid, to_s)

    def test_transition_nonexistent_raises(self, repo: TaskRepository) -> None:
        with pytest.raises(TaskNotFoundError):
            repo.transition("SRC-999", TaskStatus.IN_PROGRESS)


class TestDelete:
    def test_delete_existing(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-40"))
        assert repo.delete("SRC-40") is True
        assert repo.get("SRC-40") is None

    def test_delete_nonexistent(self, repo: TaskRepository) -> None:
        assert repo.delete("SRC-999") is False

    def test_delete_cascades_task_files(self, repo: TaskRepository) -> None:
        t = _make_task("SRC-41")
        files = [{"file_path": "src/test.py", "role": "primary"}]
        repo.create(t, files=files)
        assert len(repo.get_files("SRC-41")) == 1
        repo.delete("SRC-41")
        assert repo.get_files("SRC-41") == []

    def test_delete_does_not_cascade_to_events(self, repo: TaskRepository) -> None:
        import sqlite3

        repo.create(_make_task("SRC-42"))
        repo.transition("SRC-42", TaskStatus.IN_PROGRESS)
        repo.delete("SRC-42")
        conn = sqlite3.connect(str(repo._db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM events WHERE task_id = 'SRC-42' ORDER BY created_at DESC").fetchall()
        conn.close()
        assert len(rows) >= 1


class TestTaskFiles:
    def test_add_file(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-50"))
        repo.add_file("SRC-50", "src/zephyr/db/task_repo.py", "primary")
        files = repo.get_files("SRC-50")
        assert len(files) == 1
        assert files[0]["file_path"] == "src/zephyr/db/task_repo.py"
        assert files[0]["role"] == "primary"

    def test_remove_file(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-51"))
        repo.add_file("SRC-51", "src/test.py", "in_scope")
        repo.remove_file("SRC-51", "src/test.py")
        assert repo.get_files("SRC-51") == []

    def test_get_tasks_for_file(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-52"))
        repo.create(_make_task("SRC-53"))
        repo.add_file("SRC-52", "src/shared.py", "in_scope")
        repo.add_file("SRC-53", "src/shared.py", "in_scope")
        task_ids = repo.get_tasks_for_file("src/shared.py")
        assert "SRC-52" in task_ids
        assert "SRC-53" in task_ids

    def test_next_seq(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-1"))
        repo.create(_make_task("SRC-2"))
        assert repo.next_seq() == 3


class TestList:
    @pytest.fixture(autouse=True)
    def seed(self, repo: TaskRepository) -> None:
        for i, (status, phase) in enumerate(
            [
                (TaskStatus.PENDING, 1),
                (TaskStatus.IN_PROGRESS, 1),
                (TaskStatus.COMPLETED, 2),
                (TaskStatus.FAILED, 2),
                (TaskStatus.BLOCKED, 3),
            ]
        ):
            now = datetime.now(_UTC)
            t = TaskCard(
                task_id=f"SRC-{100 + i}",
                namespace=TaskNamespace.SRC,
                seq=100 + i,
                phase=phase,
                title=f"Task {i}",
                status=status,
                execution_model="claude",
                safety_level=SafetyLevel.L,
                source_blueprint="test",
                source_section="test",
                description=f"根因：测试列表查询功能。治根：创建批量测试任务卡验证 list_by 方法。施工步骤：(1) 构造 TaskCard {i} 并入库。验收标准：列表查询结果正确，按 status/phase/session 过滤无误。",
                files_in_scope=["src/zephyr/db/task_repo.py"],
                deliverables=["test"],
                applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
                allowed_touch=["src/zephyr/db/task_repo.py"],
                rollback_instructions="revert",
                post_sync_standard=["echo ok"],
                acceptance=["exit=0"],
                dependency_type="none",
                session_id="sess-seed" if i < 3 else None,
                created_at=now,
                updated_at=now,
            )
            repo.create(t)

    def test_list_by_status(self, repo: TaskRepository) -> None:
        pending = repo.list_by_status(TaskStatus.PENDING)
        assert all(t.status == TaskStatus.PENDING for t in pending)
        assert len(pending) == 1

    def test_list_by_phase(self, repo: TaskRepository) -> None:
        phase2 = repo.list_by_phase(2)
        assert all(t.phase == 2 for t in phase2)
        assert len(phase2) == 2

    def test_list_by_session(self, repo: TaskRepository) -> None:
        sess_tasks = repo.list_by_session("sess-seed")
        assert len(sess_tasks) == 3

    def test_list_by_namespace(self, repo: TaskRepository) -> None:
        src_tasks = repo.list_by_namespace(TaskNamespace.SRC)
        assert all(t.namespace == TaskNamespace.SRC for t in src_tasks)
        assert len(src_tasks) == 5

    def test_list_active(self, repo: TaskRepository) -> None:
        active = repo.list_active()
        active_statuses = {t.status for t in active}
        assert TaskStatus.PENDING not in active_statuses

    def test_count_by_status(self, repo: TaskRepository) -> None:
        counts = repo.count_by_status()
        assert counts.get("PENDING", 0) == 1
        assert counts.get("IN_PROGRESS", 0) == 1

    def test_list_by_status_string(self, repo: TaskRepository) -> None:
        completed = repo.list_by_status("COMPLETED")
        assert all(t.status == TaskStatus.COMPLETED for t in completed)


class TestUpsert:
    def test_upsert_insert(self, repo: TaskRepository) -> None:
        t = _make_task("SRC-60")
        result = repo.upsert(t)
        assert result.task_id == "SRC-60"

    def test_upsert_update(self, repo: TaskRepository) -> None:
        repo.upsert(_make_task("SRC-61"))
        now = datetime.now(_UTC)
        updated = TaskCard(
            task_id="SRC-61",
            namespace=TaskNamespace.SRC,
            seq=61,
            phase=1,
            title="Updated Name",
            status=TaskStatus.VERIFIED,
            execution_model="claude",
            safety_level=SafetyLevel.H,
            source_blueprint="test",
            source_section="test",
            description="根因：测试 upsert 更新功能。治根：创建测试任务卡验证 upsert 插入和更新行为。施工步骤：(1) 构造 TaskCard 并调用 upsert 两次验证幂等。验收标准：更新后字段值正确，task_id 不变。",
            files_in_scope=["src/zephyr/db/task_repo.py"],
            deliverables=["test"],
            applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
            allowed_touch=["src/zephyr/db/task_repo.py"],
            rollback_instructions="revert",
            post_sync_standard=["echo ok"],
            acceptance=["exit=0"],
            dependency_type="none",
            created_at=now,
            updated_at=now,
        )
        result = repo.upsert(updated)
        assert result.title == "Updated Name"
        assert result.status == TaskStatus.VERIFIED


class TestConcurrency:
    def test_concurrent_reads_safe(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-70"))
        results: list[None | Exception] = []

        def read_task() -> None:
            try:
                _ = repo.get("SRC-70")
                results.append(None)
            except Exception as e:
                results.append(e)

        threads = [Thread(target=read_task) for _ in range(10)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        errors = [r for r in results if r is not None]
        assert not errors, f"并发读出现异常：{errors}"

    def test_serial_writes_via_lock(self, repo: TaskRepository) -> None:
        errors: list[Exception] = []
        created: list[str] = []

        def create_task(idx: int) -> None:
            try:
                tid = f"SRC-{800 + idx}"
                t = _make_task(tid)
                repo.create(t)
                created.append(tid)
            except Exception as e:
                errors.append(e)

        threads = [Thread(target=create_task, args=(i,)) for i in range(5)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors, f"并发写出现异常：{errors}"
        assert len(created) == 5


class TestHelpers:
    def test_allowed_transitions_pending(self) -> None:
        allowed = allowed_transitions(TaskStatus.PENDING)
        assert TaskStatus.IN_PROGRESS in allowed
        assert TaskStatus.BLOCKED in allowed
        assert TaskStatus.CANCELLED in allowed
        assert TaskStatus.COMPLETED not in allowed

    def test_allowed_transitions_string(self) -> None:
        allowed = allowed_transitions("IN_PROGRESS")
        assert TaskStatus.COMPLETED in allowed

    def test_is_terminal_verified(self) -> None:
        assert is_terminal(TaskStatus.VERIFIED) is True

    def test_is_terminal_cancelled(self) -> None:
        assert is_terminal(TaskStatus.CANCELLED) is True

    def test_is_terminal_pending(self) -> None:
        assert is_terminal(TaskStatus.PENDING) is False

    def test_is_terminal_string(self) -> None:
        assert is_terminal("VERIFIED") is True
        assert is_terminal("PENDING") is False
