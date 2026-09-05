# [A_test] module_id: MOD-GOV_task_repo_batch_api | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md | §task-system
# [MODULE] tests.governance.persistence.test_task_repo_batch_api
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] get_distinct_batch_ids/get_task_batch_ids 只读; 空串/NULL batch_id 不入返回值; 软删行排除
# [MODIFY-GUARD] src/zephyr/governance/persistence/task_repo.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on invalid status literal
# [TESTS] —
# [A_module] module_id=MOD-TASK_SYSTEM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""单元测试：TaskRepository batch_id 公开读取 API（AI-AUDIT13-002 主项①）

覆盖矩阵
--------
get_distinct_batch_ids : IN_PROGRESS 批次去重 / 无批次排除 / 空串排除 / 软删排除 / 字符串入参 / 非法状态码
get_task_batch_ids     : task_id->batch_id 映射 / 无批次排除 / 多批次映射 / NULL 排除 / 软删排除 / 字符串入参

语义对齐旁路 SQL（src/zephyr/trading/conductor.py:173 / src/zephyr/trading/autopilot.py:109,160），
供 AI-06 下一轮接线收敛。注：batch_id 是 tasks 表内部列（TaskCard 不承载），
测试中以直接 SQL 写入 batch_id 模拟批次分配数据（生产 INSERT/_serialize_for_db 不含该列）。
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.shared.foundation.models import TaskCard
from zephyr.shared.schema.base_config import Classification, EvolutionPolicy
from zephyr.shared.schema.severity_types import SafetyLevel

_UTC = UTC


def _make_task(
    task_id: str = "SRC-1",
    status: TaskStatus = TaskStatus.PENDING,
    phase: int = 1,
    namespace: TaskNamespace = TaskNamespace.SRC,
    seq: int | None = None,
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
        description=f"根因：测试 TaskRepository batch_id 公开 API。治根：验证 get_distinct_batch_ids/get_task_batch_ids 语义。施工步骤：(1) 建卡 (2) 写入 batch_id。验收标准：API 返回与旁路 SQL 语义一致。",
        files_in_scope=["src/zephyr/governance/persistence/task_repo.py"],
        deliverables=["test deliverable"],
        applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
        allowed_touch=["src/zephyr/governance/persistence/task_repo.py"],
        rollback_instructions="git checkout -- task_repo.py",
        post_sync_standard=["echo ok"],
        acceptance=["exit=0"],
        dependency_type="none",
        session_id=None,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> TaskRepository:
    db = tmp_path / "test_data/databases/governance.db"
    r = TaskRepository(db_path=db, auto_init=True, enable_gate=False)
    yield r
    r.close()


def _make_in_progress_with_batch(repo: TaskRepository, task_id: str, batch_id: str | None) -> None:
    """建卡推进到 IN_PROGRESS 并写入 batch_id（batch_id 为内部列，测试直接 SQL 准备数据）。"""
    repo.create(_make_task(task_id))
    repo.transition(task_id, TaskStatus.IN_PROGRESS)
    with repo._write_tx() as conn:
        conn.execute("UPDATE tasks SET batch_id = ? WHERE task_id = ?", (batch_id, task_id))


class TestGetDistinctBatchIds:
    def test_in_progress_batch_dedup(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        _make_in_progress_with_batch(repo, "SRC-2", "batch-B")
        # 同批次第二个任务不产生重复 batch_id
        _make_in_progress_with_batch(repo, "SRC-3", "batch-A")
        result = repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS)
        assert sorted(result) == ["batch-A", "batch-B"]

    def test_unbatched_status_returns_empty(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-1"))
        repo.transition("SRC-1", TaskStatus.IN_PROGRESS)
        # batch_id 为 NULL（无批次任务）-> 不入返回值
        assert repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS) == []

    def test_empty_string_batch_id_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "")
        assert repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS) == []

    def test_soft_deleted_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        repo.delete("SRC-1")
        assert repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS) == []

    def test_string_status_accepted(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        assert repo.get_distinct_batch_ids("IN_PROGRESS") == ["batch-A"]

    def test_invalid_status_raises(self, repo: TaskRepository) -> None:
        with pytest.raises(ValueError):
            repo.get_distinct_batch_ids("NOT_A_STATUS")


class TestGetTaskBatchIds:
    def test_claimed_task_mapping(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {"SRC-1": "batch-A"}

    def test_unbatched_task_not_in_mapping(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-1"))
        repo.transition("SRC-1", TaskStatus.IN_PROGRESS)
        # 无批次任务不在映射中，调用方以哨兵值兜底（对齐 autopilot COALESCE 语义）
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {}

    def test_multiple_batches_mapping(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        _make_in_progress_with_batch(repo, "SRC-2", "batch-B")
        _make_in_progress_with_batch(repo, "SRC-3", "batch-A")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {
            "SRC-1": "batch-A",
            "SRC-3": "batch-A",
            "SRC-2": "batch-B",
        }

    def test_null_batch_id_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        with repo._write_tx() as conn:
            conn.execute("UPDATE tasks SET batch_id = NULL WHERE task_id = 'SRC-1'")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {}

    def test_soft_deleted_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        repo.delete("SRC-1")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {}

    def test_string_status_accepted(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        assert repo.get_task_batch_ids("IN_PROGRESS") == {"SRC-1": "batch-A"}
